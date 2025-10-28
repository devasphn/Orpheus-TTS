# Orpheus TTS RunPod Deployment Guide

Complete step-by-step guide for deploying Orpheus TTS streaming inference server on RunPod platform.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [RunPod Instance Setup](#runpod-instance-setup)
3. [Docker Image Deployment](#docker-image-deployment)
4. [Network Configuration](#network-configuration)
5. [Testing the Deployment](#testing-the-deployment)
6. [Performance Optimization](#performance-optimization)
7. [Cost Efficiency Tips](#cost-efficiency-tips)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You'll Need
- RunPod account (sign up at [runpod.io](https://www.runpod.io))
- Credit card or crypto for RunPod credits
- Docker Hub account (optional, for custom images)
- Basic knowledge of Docker and REST APIs

### Recommended GPU Specifications

**Minimum Requirements:**
- GPU: NVIDIA RTX 3060 (12GB VRAM) or better
- VRAM: 12GB minimum
- Model size: ~6GB when loaded

**Recommended for Production:**
- GPU: NVIDIA RTX 4090, A5000, or A6000
- VRAM: 24GB
- Better performance and headroom for concurrent requests

**Budget Options:**
- RTX 3090 (24GB) - Good balance of cost and performance
- RTX A4000 (16GB) - Adequate for moderate load

---

## RunPod Instance Setup

### Step 1: Create a RunPod Account

1. Go to [runpod.io](https://www.runpod.io)
2. Sign up for an account
3. Add credits to your account (minimum $10 recommended)

### Step 2: Deploy a GPU Pod

1. **Navigate to Pods**
   - Click on "Pods" in the left sidebar
   - Click "+ Deploy" button

2. **Select GPU Type**
   - Choose "GPU Cloud" (on-demand) or "Secure Cloud" (dedicated)
   - Filter by GPU type (recommended: RTX 3090, RTX 4090, or A5000)
   - Sort by price to find the best deal
   - Click "Deploy" on your chosen GPU

3. **Configure Pod Template**
   - **Template**: Select "RunPod PyTorch" or "RunPod Tensorflow" as base
   - **Container Image**: We'll use a custom image (see next section)
   - **Container Disk**: 20GB minimum (for model cache)
   - **Volume Disk**: Optional, 50GB if you want persistent storage
   - **Expose HTTP Ports**: `8080` (this is critical!)
   - **Expose TCP Ports**: Leave empty unless needed

4. **Environment Variables** (Optional but recommended)
   ```
   MODEL_NAME=canopylabs/orpheus-tts-0.1-finetune-prod
   MAX_MODEL_LEN=2048
   PORT=8080
   ```

5. **Deploy the Pod**
   - Review your configuration
   - Click "Deploy On-Demand" or "Deploy"
   - Wait for the pod to start (usually 1-2 minutes)

---

## Docker Image Deployment

You have two options: use a pre-built image or build your own.

### Option A: Build and Push Custom Docker Image

1. **Clone the Repository**
   ```bash
   git clone https://github.com/canopyai/Orpheus-TTS.git
   cd Orpheus-TTS/runpod_deployment
   ```

2. **Build the Docker Image**
   ```bash
   docker build -t your-dockerhub-username/orpheus-tts-runpod:latest .
   ```

3. **Push to Docker Hub**
   ```bash
   docker login
   docker push your-dockerhub-username/orpheus-tts-runpod:latest
   ```

4. **Use in RunPod**
   - In the pod configuration, set Container Image to:
     ```
     your-dockerhub-username/orpheus-tts-runpod:latest
     ```

### Option B: Use RunPod Template with Manual Setup

1. **Select Base Template**
   - Use "RunPod PyTorch 2.0" template
   - Container Image: `runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel`

2. **Add Startup Commands** (in "Docker Command" field)
   ```bash
   bash -c "pip install orpheus-speech && pip install vllm==0.7.3 && pip install flask gunicorn && python /workspace/server.py"
   ```

3. **Upload Files via RunPod Web Terminal**
   - After pod starts, click "Connect" → "Start Web Terminal"
   - Upload `server.py` to `/workspace/`
   - Make it executable and run

---

## Network Configuration

### Exposing the API Endpoint Publicly

1. **HTTP Ports Configuration**
   - In pod settings, ensure port `8080` is exposed
   - RunPod will automatically assign a public URL

2. **Find Your Public URL**
   - Go to your pod details page
   - Look for "Connect" button
   - Find "HTTP Service" section
   - Your URL will be: `https://[pod-id]-8080.proxy.runpod.net`
   - Example: `https://abc123def456-8080.proxy.runpod.net`

3. **Test Connectivity**
   ```bash
   curl https://your-pod-id-8080.proxy.runpod.net/health
   ```

### Security Considerations

- RunPod URLs are publicly accessible by default
- Consider implementing API key authentication for production
- Use HTTPS (provided by RunPod automatically)
- Monitor usage to prevent abuse

---

## Testing the Deployment

### Method 1: Using the Test Client Script

1. **Install Requirements Locally**
   ```bash
   pip install requests
   ```

2. **Run the Test Client**
   ```bash
   python test_client.py https://your-pod-id-8080.proxy.runpod.net
   ```

3. **Expected Output**
   - Health check passes
   - Lists available voices
   - Generates test audio files
   - Saves WAV files locally

### Method 2: Manual Testing with cURL

1. **Health Check**
   ```bash
   curl https://your-pod-id-8080.proxy.runpod.net/health
   ```

2. **List Voices**
   ```bash
   curl https://your-pod-id-8080.proxy.runpod.net/voices
   ```

3. **Generate Speech (GET)**
   ```bash
   curl "https://your-pod-id-8080.proxy.runpod.net/tts?prompt=Hello%20world&voice=tara" \
     --output test.wav
   ```

4. **Generate Speech (POST)**
   ```bash
   curl -X POST https://your-pod-id-8080.proxy.runpod.net/tts \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Hello from RunPod!",
       "voice": "tara",
       "temperature": 0.4,
       "max_tokens": 2000
     }' \
     --output test.wav
   ```

### Method 3: Browser Testing

1. Open your browser
2. Navigate to: `https://your-pod-id-8080.proxy.runpod.net/`
3. You should see API information
4. Test TTS: `https://your-pod-id-8080.proxy.runpod.net/tts?prompt=Hello%20world&voice=tara`
5. Browser should download a WAV file

### Method 4: Using the HTML Client

1. Copy the `client.html` from `realtime_streaming_example/`
2. Edit line 16 to set your RunPod URL:
   ```javascript
   const base_url = `https://your-pod-id-8080.proxy.runpod.net`;
   ```
3. Open the HTML file in a browser
4. Enter text and click "Play Audio"

---

## Performance Optimization

### 1. Model Loading Optimization

The model takes 30-120 seconds to load on first request. To pre-load:

**Add to startup script:**
```bash
python -c "from orpheus_tts import OrpheusModel; OrpheusModel('canopylabs/orpheus-tts-0.1-finetune-prod')"
```

### 2. vLLM Configuration

Optimize vLLM settings via environment variables:

```bash
VLLM_WORKER_MULTIPROC_METHOD=spawn
CUDA_VISIBLE_DEVICES=0
```

### 3. Concurrent Requests

For production, use Gunicorn instead of Flask dev server:

```bash
gunicorn -w 1 -b 0.0.0.0:8080 --timeout 300 server:app
```

Note: Use only 1 worker due to GPU memory constraints

### 4. Caching Strategy

- Enable persistent volume in RunPod to cache models
- Mount volume to `/root/.cache/huggingface`
- Reduces cold start time significantly

### 5. Streaming Latency Optimization

**Current latency:** ~200ms
**Optimized latency:** ~100ms with input streaming

To reduce latency:
- Use smaller `max_tokens` values when possible
- Adjust `temperature` (lower = faster, less variation)
- Consider using fp8 quantization for faster inference

---

## Cost Efficiency Tips

### 1. Choose the Right GPU

**Cost vs Performance Analysis:**

| GPU Type | VRAM | Hourly Cost* | Best For |
|----------|------|--------------|----------|
| RTX 3060 | 12GB | $0.20-0.30 | Testing, low volume |
| RTX 3090 | 24GB | $0.40-0.60 | Production, good value |
| RTX 4090 | 24GB | $0.80-1.20 | High performance needs |
| A5000 | 24GB | $0.60-0.90 | Enterprise, reliability |
| A6000 | 48GB | $1.00-1.50 | Heavy concurrent load |

*Prices vary by region and availability

### 2. Use Spot Instances (Community Cloud)

- Save 50-70% compared to Secure Cloud
- Risk: Can be terminated with 15-second notice
- Good for: Development, testing, non-critical workloads
- Not recommended for: Production services requiring high uptime

### 3. Auto-Stop Configuration

Configure auto-stop to prevent unnecessary charges:

1. Go to pod settings
2. Set "Stop After" to 15-30 minutes of inactivity
3. Pod will auto-stop when idle
4. Restart manually when needed

### 4. Volume Management

- **Container Disk**: Keep minimal (20GB)
- **Volume Disk**: Only if you need persistent model cache
- Delete volumes when not in use

### 5. Monitoring and Alerts

- Set up billing alerts in RunPod dashboard
- Monitor GPU utilization (aim for >70% when active)
- Track requests per hour to optimize instance size

### 6. Batch Processing

If processing multiple requests:
- Queue requests instead of parallel processing
- Reduces memory overhead
- Allows using smaller/cheaper GPUs

---

## Troubleshooting

### Issue 1: Model Not Loading

**Symptoms:**
- Health check returns "unhealthy"
- 503 errors on /tts endpoint

**Solutions:**
1. Check pod logs for errors:
   ```bash
   # In RunPod web terminal
   docker logs $(docker ps -q)
   ```

2. Verify GPU is available:
   ```bash
   nvidia-smi
   ```

3. Check VRAM usage:
   ```bash
   watch -n 1 nvidia-smi
   ```

4. Increase container disk size (model cache needs space)

5. Try a different vLLM version:
   ```bash
   pip install vllm==0.6.0  # or 0.7.0, 0.7.3
   ```

### Issue 2: Out of Memory (OOM)

**Symptoms:**
- CUDA out of memory errors
- Pod crashes during inference

**Solutions:**
1. Reduce `max_model_len`:
   ```bash
   export MAX_MODEL_LEN=1024
   ```

2. Use a GPU with more VRAM (24GB recommended)

3. Reduce concurrent requests (use 1 Gunicorn worker)

4. Clear GPU cache between requests (already handled in code)

### Issue 3: Slow Inference

**Symptoms:**
- Takes >30 seconds to generate audio
- Timeouts on client side

**Solutions:**
1. Check GPU utilization:
   ```bash
   nvidia-smi
   ```

2. Verify you're using GPU, not CPU:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should be True
   ```

3. Reduce `max_tokens` parameter

4. Use a faster GPU (RTX 4090 or A5000)

5. Check network latency (RunPod region selection)

### Issue 4: Connection Refused / 502 Errors

**Symptoms:**
- Can't connect to pod URL
- 502 Bad Gateway errors

**Solutions:**
1. Verify port 8080 is exposed in pod settings

2. Check if server is running:
   ```bash
   curl http://localhost:8080/health
   ```

3. Restart the pod

4. Check firewall settings (usually not an issue on RunPod)

5. Verify the public URL format:
   ```
   https://[pod-id]-8080.proxy.runpod.net
   ```

### Issue 5: Audio Quality Issues

**Symptoms:**
- Distorted audio
- Choppy playback
- Missing audio chunks

**Solutions:**
1. Check the WAV file size (should be >100KB for typical prompts)

2. Verify sample rate is 24000 Hz:
   ```bash
   ffprobe output.wav
   ```

3. Try different voice models

4. Adjust generation parameters:
   - `temperature`: 0.3-0.6 (lower = more consistent)
   - `repetition_penalty`: 1.0-1.3
   - `top_p`: 0.8-0.95

5. Check for frame skipping (known issue mentioned in README)

### Issue 6: High Costs

**Symptoms:**
- Unexpected high bills
- Pod running when not needed

**Solutions:**
1. Enable auto-stop (see Cost Efficiency section)

2. Check for stuck pods:
   ```bash
   # In RunPod dashboard, check all running pods
   ```

3. Use Community Cloud instead of Secure Cloud

4. Monitor usage with RunPod's billing dashboard

5. Set up spending limits in account settings

---

## Advanced Configuration

### Using Gunicorn for Production

Replace the CMD in Dockerfile or startup script:

```bash
gunicorn -w 1 \
  -b 0.0.0.0:8080 \
  --timeout 300 \
  --worker-class sync \
  --access-logfile - \
  --error-logfile - \
  server:app
```

### Adding Authentication

Add API key authentication to `server.py`:

```python
from functools import wraps
from flask import request, jsonify

API_KEY = os.getenv("API_KEY", "your-secret-key")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/tts', methods=['GET', 'POST'])
@require_api_key
def tts():
    # ... existing code
```

### Custom Voice Fine-tuning

To use your own fine-tuned model:

1. Upload model to Hugging Face
2. Set environment variable:
   ```bash
   MODEL_NAME=your-username/your-model-name
   ```
3. Restart the pod

### Monitoring and Logging

Add logging to external service:

```python
import logging
from logging.handlers import HTTPHandler

# Add to server.py
handler = HTTPHandler('your-logging-service.com', '/log', method='POST')
logger.addHandler(handler)
```

---

## API Reference

### Endpoints

#### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-01-15T10:30:00"
}
```

#### GET /voices
List available voices

**Response:**
```json
{
  "voices": ["tara", "zoe", "zac", "jess", "leo", "mia", "julia", "leah"],
  "default": "tara"
}
```

#### GET /tts
Generate speech (GET method)

**Parameters:**
- `prompt` (required): Text to convert to speech
- `voice` (optional): Voice name (default: "tara")
- `temperature` (optional): 0.0-1.0 (default: 0.4)
- `top_p` (optional): 0.0-1.0 (default: 0.9)
- `max_tokens` (optional): Max tokens to generate (default: 2000)
- `repetition_penalty` (optional): 1.0-2.0 (default: 1.1)

**Response:** WAV audio file (streaming)

#### POST /tts
Generate speech (POST method)

**Request Body:**
```json
{
  "prompt": "Your text here",
  "voice": "tara",
  "temperature": 0.4,
  "top_p": 0.9,
  "max_tokens": 2000,
  "repetition_penalty": 1.1
}
```

**Response:** WAV audio file (streaming)

---

## Support and Resources

### Official Resources
- [Orpheus TTS GitHub](https://github.com/canopyai/Orpheus-TTS)
- [RunPod Documentation](https://docs.runpod.io)
- [vLLM Documentation](https://docs.vllm.ai)

### Community
- [RunPod Discord](https://discord.gg/runpod)
- [Orpheus TTS Issues](https://github.com/canopyai/Orpheus-TTS/issues)

### Getting Help
1. Check this troubleshooting guide first
2. Search existing GitHub issues
3. Check RunPod community forums
4. Create a new issue with:
   - Pod configuration
   - Error logs
   - Steps to reproduce

---

## Conclusion

You now have a complete production-ready Orpheus TTS streaming server running on RunPod!

**Next Steps:**
1. Test thoroughly with your use case
2. Monitor performance and costs
3. Optimize based on your traffic patterns
4. Consider implementing authentication for production
5. Set up monitoring and alerting

**Remember:**
- Start with a smaller GPU for testing
- Enable auto-stop to save costs
- Monitor your usage regularly
- Keep your Docker image updated

Happy streaming! 🎙️


