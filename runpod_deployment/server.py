"""
Orpheus TTS Streaming Server for RunPod Deployment
Enhanced with health checks, error handling, and production optimizations
"""

from flask import Flask, Response, request, jsonify, send_file
import struct
import logging
import sys
import os
import time
import re
import asyncio
from datetime import datetime
from typing import AsyncIterator, List
from queue import Queue
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for model engines
tts_engine = None
llm_engine = None
model_loaded = False
model_load_error = None

def initialize_models():
    """Initialize both Orpheus TTS and Gemma 2 2B LLM models"""
    global tts_engine, llm_engine, model_loaded, model_load_error

    try:
        logger.info("Starting model initialization...")
        from orpheus_tts import OrpheusModel
        from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams

        # ===== Orpheus TTS Model =====
        tts_model_name = os.getenv("TTS_MODEL_NAME", "canopylabs/orpheus-tts-0.1-finetune-prod")
        tts_max_model_len = int(os.getenv("TTS_MAX_MODEL_LEN", "2048"))

        # ===== Gemma 2 2B LLM Model =====
        llm_model_name = os.getenv("LLM_MODEL_NAME", "google/gemma-2-2b-it")
        llm_max_model_len = int(os.getenv("LLM_MAX_MODEL_LEN", "2048"))

        # GPU memory allocation strategy
        # Total VRAM: 20GB (RTX A4500) = 19.67GB usable
        #
        # CRITICAL ISSUE: vLLM models share GPU memory but each calculates allocation independently
        # When TTS loads first with 35%, it takes 6.89GB
        # When LLM tries to load with 25%, it calculates 4.92GB from TOTAL (not remaining)
        # But only ~12.78GB remains, so 4.92GB leaves NO room for KV cache!
        #
        # SOLUTION: Reduce TTS allocation to leave more room for LLM
        #
        # Memory breakdown (from logs):
        # - Orpheus TTS: 6.18GB weights (needs ~0.5GB KV cache minimum)
        # - Gemma 2 2B: 4.90GB weights (needs ~0.5GB KV cache minimum)
        # - SNAC decoder: ~1GB (shared compute)
        # - PyTorch overhead: ~0.5GB
        # - Total minimum: ~13.6GB
        #
        # Strategy: Conservative allocations with room for KV caches
        tts_gpu_memory = float(os.getenv("TTS_GPU_MEMORY_UTILIZATION", "0.33"))  # 33% = 6.49GB (6.18GB weights + 0.31GB KV)
        llm_gpu_memory = float(os.getenv("LLM_GPU_MEMORY_UTILIZATION", "0.28"))  # 28% = 5.51GB (4.90GB weights + 0.61GB KV)
        #
        # Expected usage:
        # - TTS: 6.49GB
        # - LLM: 5.51GB
        # - Total: 12.00GB, leaving 7.67GB for SNAC, overhead, and safety margin ✅

        logger.info("="*70)
        logger.info("LOADING ORPHEUS TTS MODEL")
        logger.info("="*70)
        logger.info(f"Model: {tts_model_name}")
        logger.info(f"Max model length: {tts_max_model_len}")
        logger.info(f"GPU memory allocation: {tts_gpu_memory*100:.0f}%")

        tts_engine = OrpheusModel(
            model_name=tts_model_name,
            max_model_len=tts_max_model_len,
            gpu_memory_utilization=tts_gpu_memory,
            max_num_seqs=1,
            disable_log_stats=False
        )

        logger.info("✅ Orpheus TTS model loaded successfully!")

        logger.info("="*70)
        logger.info("LOADING GEMMA 2 2B LLM MODEL")
        logger.info("="*70)
        logger.info(f"Model: {llm_model_name}")
        logger.info(f"Max model length: {llm_max_model_len}")
        logger.info(f"GPU memory allocation: {llm_gpu_memory*100:.0f}%")

        # Initialize Gemma 2 2B with vLLM
        llm_engine_args = AsyncEngineArgs(
            model=llm_model_name,
            max_model_len=llm_max_model_len,
            gpu_memory_utilization=llm_gpu_memory,
            dtype="bfloat16",
            trust_remote_code=True,
            max_num_seqs=2,  # Allow 2 concurrent requests (LLM + TTS)
            disable_log_stats=False
        )

        llm_engine = AsyncLLMEngine.from_engine_args(llm_engine_args)

        logger.info("✅ Gemma 2 2B LLM model loaded successfully!")
        logger.info("="*70)
        logger.info("ALL MODELS LOADED - READY FOR CONVERSATIONAL AI")
        logger.info("="*70)

        model_loaded = True
        return True

    except Exception as e:
        model_load_error = str(e)
        logger.error(f"Failed to load models: {e}", exc_info=True)
        return False

def create_wav_header(sample_rate=24000, bits_per_sample=16, channels=1):
    """Create WAV file header for streaming audio"""
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = 0

    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,
        b'WAVE',
        b'fmt ',
        16,
        1,
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size
    )
    return header

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences intelligently for TTS processing.
    Handles common abbreviations and edge cases.
    """
    # Handle common abbreviations that shouldn't trigger sentence breaks
    text = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|e\.g|i\.e)\.\s', r'\1<PERIOD> ', text)

    # Split on sentence boundaries
    sentences = re.split(r'([.!?]+\s+)', text)

    # Restore abbreviations
    sentences = [s.replace('<PERIOD>', '.') for s in sentences]

    # Combine split parts and filter empty strings
    result = []
    current = ""
    for part in sentences:
        current += part
        if re.search(r'[.!?]+\s*$', current.strip()):
            result.append(current.strip())
            current = ""

    # Add any remaining text
    if current.strip():
        result.append(current.strip())

    return [s for s in result if s]

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for RunPod"""
    if model_loaded:
        return jsonify({
            'status': 'healthy',
            'models': {
                'tts': tts_engine is not None,
                'llm': llm_engine is not None
            },
            'features': {
                'text_to_speech': True,
                'conversational_ai': True,
                'streaming': True
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    else:
        return jsonify({
            'status': 'unhealthy',
            'model_loaded': False,
            'error': model_load_error,
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - serves the web UI"""
    try:
        # Get the directory where server.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Try to serve the new conversational AI UI first
        html_v2_path = os.path.join(current_dir, 'web_ui_v2.html')
        if os.path.exists(html_v2_path):
            return send_file(html_v2_path)

        # Fallback to old TTS-only UI
        html_path = os.path.join(current_dir, 'web_ui.html')
        if os.path.exists(html_path):
            return send_file(html_path)
        else:
            # Fallback to API information if HTML not found
            return jsonify({
                'service': 'Orpheus Conversational AI & TTS API',
                'version': '2.0.0',
                'models': {
                    'llm': 'Gemma 2 2B Instruct (conversational AI)',
                    'tts': 'Orpheus TTS 3B (text-to-speech)'
                },
                'endpoints': {
                    '/chat': 'Conversational AI with voice response (POST with JSON: {message, voice, history})',
                    '/tts': 'Generate speech from text (GET/POST with prompt and voice)',
                    '/health': 'Health check endpoint',
                    '/voices': 'List available voices',
                    '/models': 'Get model information'
                },
                'model_loaded': model_loaded,
                'note': 'Web UI not found. Please ensure web_ui.html is in the same directory as server.py'
            })
    except Exception as e:
        logger.error(f"Error serving web UI: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def get_models():
    """Get information about loaded models"""
    return jsonify({
        'llm': {
            'name': 'Gemma 2 2B Instruct',
            'provider': 'Google',
            'parameters': '2B',
            'license': 'Gemma Terms of Use (Commercial use allowed)',
            'license_url': 'https://ai.google.dev/gemma/terms',
            'capabilities': ['conversational_ai', 'streaming', 'instruction_following'],
            'loaded': llm_engine is not None
        },
        'tts': {
            'name': 'Orpheus TTS',
            'provider': 'Canopy Labs',
            'parameters': '3B',
            'license': 'Apache 2.0',
            'capabilities': ['text_to_speech', 'voice_cloning', 'streaming', 'emotion_control'],
            'voices': ["tara", "zoe", "zac", "jess", "leo", "mia", "julia", "leah"],
            'loaded': tts_engine is not None
        }
    })

@app.route('/voices', methods=['GET'])
def list_voices():
    """List available voices"""
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503

    voices = ["tara", "zoe", "zac", "jess", "leo", "mia", "julia", "leah"]
    return jsonify({
        'voices': voices,
        'default': 'tara',
        'description': 'Available voices for Orpheus TTS'
    })

@app.route('/tts', methods=['GET', 'POST'])
def tts():
    """Text-to-speech streaming endpoint"""
    if not model_loaded:
        return jsonify({
            'error': 'Model not loaded',
            'details': model_load_error
        }), 503
    
    try:
        # Get parameters from request
        if request.method == 'POST':
            data = request.get_json()
            prompt = data.get('prompt', '')
            voice = data.get('voice', 'tara')
            temperature = float(data.get('temperature', 0.4))
            top_p = float(data.get('top_p', 0.9))
            max_tokens = int(data.get('max_tokens', 2000))
            repetition_penalty = float(data.get('repetition_penalty', 1.1))
        else:
            prompt = request.args.get('prompt', '')
            voice = request.args.get('voice', 'tara')
            temperature = float(request.args.get('temperature', 0.4))
            top_p = float(request.args.get('top_p', 0.9))
            max_tokens = int(request.args.get('max_tokens', 2000))
            repetition_penalty = float(request.args.get('repetition_penalty', 1.1))
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        logger.info(f"Generating speech for prompt: {prompt[:50]}... (voice: {voice})")
        start_time = time.time()
        
        def generate_audio_stream():
            try:
                # Send WAV header first
                yield create_wav_header()

                # Generate speech tokens
                syn_tokens = tts_engine.generate_speech(
                    prompt=prompt,
                    voice=voice,
                    repetition_penalty=repetition_penalty,
                    stop_token_ids=[128258],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                
                chunk_count = 0
                for chunk in syn_tokens:
                    chunk_count += 1
                    yield chunk
                
                elapsed = time.time() - start_time
                logger.info(f"Generated {chunk_count} chunks in {elapsed:.2f}s")
                
            except Exception as e:
                logger.error(f"Error during audio generation: {e}", exc_info=True)
                # Can't send JSON error in the middle of streaming, log it
        
        return Response(generate_audio_stream(), mimetype='audio/wav')
    
    except Exception as e:
        logger.error(f"Error in TTS endpoint: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """
    Conversational AI endpoint with voice response.
    Streams LLM response as audio in real-time.

    Request JSON:
    {
        "message": "User's message",
        "voice": "tara" (optional, default: tara),
        "history": [] (optional, list of {role, content} dicts),
        "stream_text": false (optional, if true returns text stream instead of audio)
    }
    """
    if not model_loaded:
        return jsonify({
            'error': 'Models not loaded',
            'details': model_load_error
        }), 503

    try:
        data = request.get_json()
        user_message = data.get('message', '')
        voice = data.get('voice', 'tara')
        history = data.get('history', [])
        stream_text = data.get('stream_text', False)

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        logger.info(f"Chat request: {user_message[:50]}... (voice: {voice})")
        start_time = time.time()

        # Build conversation prompt for Gemma 2
        conversation = ""
        for msg in history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                conversation += f"User: {content}\n"
            elif role == 'assistant':
                conversation += f"Assistant: {content}\n"

        conversation += f"User: {user_message}\nAssistant:"

        if stream_text:
            # Stream text only (for debugging/testing)
            def generate_text_stream():
                from vllm import SamplingParams

                sampling_params = SamplingParams(
                    temperature=0.7,
                    top_p=0.9,
                    max_tokens=512,
                    stop=["User:", "\n\n"]
                )

                request_id = f"chat-{int(time.time()*1000)}"

                async def stream_results():
                    results_generator = llm_engine.generate(
                        conversation,
                        sampling_params,
                        request_id
                    )

                    async for request_output in results_generator:
                        text = request_output.outputs[0].text
                        yield text

                # Run async generator in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    gen = stream_results()
                    while True:
                        try:
                            text = loop.run_until_complete(gen.__anext__())
                            yield text.encode('utf-8')
                        except StopAsyncIteration:
                            break
                finally:
                    loop.close()

            return Response(generate_text_stream(), mimetype='text/plain')

        else:
            # Stream audio response (LLM → TTS pipeline)
            # IMPORTANT: Sequential execution to avoid vLLM engine conflicts
            def generate_conversational_audio():
                from vllm import SamplingParams

                try:
                    # Send WAV header first
                    yield create_wav_header()

                    # Sampling parameters for LLM
                    sampling_params = SamplingParams(
                        temperature=0.7,
                        top_p=0.9,
                        max_tokens=512,
                        stop=["User:", "\n\n"]
                    )

                    request_id = f"chat-{int(time.time()*1000)}"

                    # ===== STEP 1: Generate complete LLM response =====
                    # We must complete LLM generation BEFORE starting TTS to avoid
                    # vLLM engine conflicts (both use AsyncLLMEngine with shared CUDA context)

                    logger.info("Step 1: Generating LLM response...")
                    llm_start = time.time()

                    async def get_llm_response():
                        """Generate complete text response from LLM"""
                        results_generator = llm_engine.generate(
                            conversation,
                            sampling_params,
                            request_id
                        )

                        full_text = ""
                        async for request_output in results_generator:
                            full_text = request_output.outputs[0].text

                        return full_text

                    # Run LLM generation to completion
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        llm_response = loop.run_until_complete(get_llm_response())
                    finally:
                        loop.close()

                    llm_elapsed = time.time() - llm_start
                    logger.info(f"LLM response generated in {llm_elapsed:.2f}s: {llm_response[:100]}...")

                    # ===== STEP 2: Split into sentences =====
                    sentences = split_into_sentences(llm_response)
                    logger.info(f"Split into {len(sentences)} sentences")

                    # ===== STEP 3: Process each sentence through TTS =====
                    # Now safe to use TTS engine since LLM is complete
                    logger.info("Step 2: Generating TTS audio...")
                    tts_start = time.time()
                    chunk_count = 0

                    for i, sentence in enumerate(sentences):
                        if not sentence.strip():
                            continue

                        logger.info(f"TTS sentence {i+1}/{len(sentences)}: {sentence[:50]}...")

                        # Generate speech for this sentence
                        syn_tokens = tts_engine.generate_speech(
                            prompt=sentence,
                            voice=voice,
                            repetition_penalty=1.1,
                            stop_token_ids=[128258],
                            max_tokens=1000,
                            temperature=0.4,
                            top_p=0.9
                        )

                        for chunk in syn_tokens:
                            chunk_count += 1
                            yield chunk

                    tts_elapsed = time.time() - tts_start
                    total_elapsed = time.time() - start_time

                    logger.info(f"Chat complete:")
                    logger.info(f"  - LLM: {llm_elapsed:.2f}s")
                    logger.info(f"  - TTS: {tts_elapsed:.2f}s ({chunk_count} chunks)")
                    logger.info(f"  - Total: {total_elapsed:.2f}s")

                except Exception as e:
                    logger.error(f"Error during conversational audio generation: {e}", exc_info=True)

            return Response(generate_conversational_audio(), mimetype='audio/wav')

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("="*70)
    logger.info("ORPHEUS CONVERSATIONAL AI & TTS SERVER")
    logger.info("="*70)
    logger.info("Features:")
    logger.info("  - Conversational AI (Gemma 2 2B)")
    logger.info("  - Text-to-Speech (Orpheus TTS 3B)")
    logger.info("  - Streaming audio responses")
    logger.info("  - 8 voice options")
    logger.info("="*70)

    # Initialize models on startup
    if not initialize_models():
        logger.error("Failed to initialize models. Server will start but won't be functional.")

    # Get port from environment or use default
    port = int(os.getenv('PORT', 8080))

    logger.info(f"Starting Flask server on port {port}...")
    logger.info("="*70)

    # Run with threading enabled for better performance
    app.run(
        host='0.0.0.0',
        port=port,
        threaded=True,
        debug=False
    )

