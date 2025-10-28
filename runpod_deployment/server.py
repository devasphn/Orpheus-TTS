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
from datetime import datetime

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

# Global variable for the model engine
engine = None
model_loaded = False
model_load_error = None

def initialize_model():
    """Initialize the Orpheus TTS model"""
    global engine, model_loaded, model_load_error
    
    try:
        logger.info("Starting model initialization...")
        from orpheus_tts import OrpheusModel

        # Get model configuration from environment variables
        model_name = os.getenv("MODEL_NAME", "canopylabs/orpheus-tts-0.1-finetune-prod")
        max_model_len = int(os.getenv("MAX_MODEL_LEN", "2048"))
        gpu_memory_utilization = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.9"))

        logger.info(f"Loading model: {model_name}")
        logger.info(f"Max model length: {max_model_len}")
        logger.info(f"GPU memory utilization: {gpu_memory_utilization}")

        # Pass vLLM engine parameters via **kwargs
        # These get forwarded to AsyncEngineArgs in OrpheusModel._setup_engine()
        engine = OrpheusModel(
            model_name=model_name,
            max_model_len=max_model_len,
            gpu_memory_utilization=gpu_memory_utilization
        )
        
        model_loaded = True
        logger.info("Model loaded successfully!")
        return True
        
    except Exception as e:
        model_load_error = str(e)
        logger.error(f"Failed to load model: {e}", exc_info=True)
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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for RunPod"""
    if model_loaded:
        return jsonify({
            'status': 'healthy',
            'model_loaded': True,
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
        html_path = os.path.join(current_dir, 'web_ui.html')

        if os.path.exists(html_path):
            return send_file(html_path)
        else:
            # Fallback to API information if HTML not found
            return jsonify({
                'service': 'Orpheus TTS Streaming API',
                'version': '1.0.0',
                'endpoints': {
                    '/tts': 'Generate speech from text (GET with ?prompt=text&voice=name)',
                    '/health': 'Health check endpoint',
                    '/voices': 'List available voices'
                },
                'model_loaded': model_loaded,
                'note': 'Web UI not found. Please ensure web_ui.html is in the same directory as server.py'
            })
    except Exception as e:
        logger.error(f"Error serving web UI: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/voices', methods=['GET'])
def list_voices():
    """List available voices"""
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    voices = ["tara", "zoe", "zac", "jess", "leo", "mia", "julia", "leah"]
    return jsonify({
        'voices': voices,
        'default': 'tara'
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
                syn_tokens = engine.generate_speech(
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

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Orpheus TTS Server for RunPod...")
    
    # Initialize model on startup
    if not initialize_model():
        logger.error("Failed to initialize model. Server will start but won't be functional.")
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 8080))
    
    logger.info(f"Starting Flask server on port {port}...")
    
    # Run with threading enabled for better performance
    app.run(
        host='0.0.0.0',
        port=port,
        threaded=True,
        debug=False
    )

