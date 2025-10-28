"""
Test client for Orpheus TTS RunPod deployment
Tests the streaming TTS API and saves output to WAV files
"""

import requests
import sys
import time
from urllib.parse import urlencode

def test_health_check(base_url):
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_voices_endpoint(base_url):
    """Test the voices listing endpoint"""
    print("\nTesting voices endpoint...")
    try:
        response = requests.get(f"{base_url}/voices", timeout=10)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Available voices: {data.get('voices', [])}")
        print(f"Default voice: {data.get('default', 'N/A')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_tts_streaming(base_url, prompt, voice="tara", output_file="output.wav"):
    """Test the TTS streaming endpoint"""
    print(f"\nTesting TTS streaming with voice '{voice}'...")
    print(f"Prompt: {prompt}")
    
    try:
        # Prepare parameters
        params = {
            'prompt': prompt,
            'voice': voice,
            'temperature': 0.4,
            'top_p': 0.9,
            'max_tokens': 2000,
            'repetition_penalty': 1.1
        }
        
        # Make streaming request
        print("Sending request...")
        start_time = time.time()
        
        response = requests.get(
            f"{base_url}/tts",
            params=params,
            stream=True,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Save streaming audio to file
        print(f"Receiving audio stream and saving to {output_file}...")
        bytes_received = 0
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bytes_received += len(chunk)
        
        elapsed = time.time() - start_time
        
        print(f"✓ Success!")
        print(f"  - Received {bytes_received:,} bytes")
        print(f"  - Time elapsed: {elapsed:.2f} seconds")
        print(f"  - Saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_tts_post(base_url, prompt, voice="tara", output_file="output_post.wav"):
    """Test the TTS endpoint using POST method"""
    print(f"\nTesting TTS with POST method...")
    print(f"Prompt: {prompt}")
    
    try:
        # Prepare JSON payload
        payload = {
            'prompt': prompt,
            'voice': voice,
            'temperature': 0.4,
            'top_p': 0.9,
            'max_tokens': 2000,
            'repetition_penalty': 1.1
        }
        
        # Make POST request
        print("Sending POST request...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/tts",
            json=payload,
            stream=True,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Save streaming audio to file
        print(f"Receiving audio stream and saving to {output_file}...")
        bytes_received = 0
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bytes_received += len(chunk)
        
        elapsed = time.time() - start_time
        
        print(f"✓ Success!")
        print(f"  - Received {bytes_received:,} bytes")
        print(f"  - Time elapsed: {elapsed:.2f} seconds")
        print(f"  - Saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_client.py <base_url>")
        print("Example: python test_client.py https://your-runpod-id.runpod.net")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("=" * 60)
    print("Orpheus TTS RunPod Deployment Test Client")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print()
    
    # Test 1: Health check
    if not test_health_check(base_url):
        print("\n❌ Health check failed. Server may not be ready.")
        print("Wait a few minutes for the model to load and try again.")
        sys.exit(1)
    
    # Test 2: List voices
    test_voices_endpoint(base_url)
    
    # Test 3: TTS streaming with GET
    test_prompt = "Hello! This is a test of the Orpheus text to speech system running on RunPod."
    test_tts_streaming(base_url, test_prompt, voice="tara", output_file="test_output_get.wav")
    
    # Test 4: TTS streaming with POST
    test_tts_post(base_url, test_prompt, voice="zoe", output_file="test_output_post.wav")
    
    # Test 5: Different voice
    test_tts_streaming(
        base_url,
        "The quick brown fox jumps over the lazy dog.",
        voice="leo",
        output_file="test_output_leo.wav"
    )
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nCheck the generated WAV files to verify audio quality.")

if __name__ == "__main__":
    main()

