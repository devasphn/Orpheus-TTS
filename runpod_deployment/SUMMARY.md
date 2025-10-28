# Orpheus TTS RunPod Deployment - Summary

## 📦 What's Included

This complete deployment package contains everything you need to deploy Orpheus TTS on RunPod:

### Core Files
1. **`Dockerfile`** - Production-ready Docker image with CUDA 12.1, Python 3.10, and all dependencies
2. **`server.py`** - Enhanced Flask server with health checks, error handling, and streaming support
3. **`startup.sh`** - Container initialization script with system diagnostics
4. **`requirements.txt`** - Pinned Python dependencies for reproducible builds

### Documentation
5. **`RUNPOD_DEPLOYMENT.md`** - Complete 600+ line deployment guide covering:
   - Step-by-step setup instructions
   - GPU recommendations and pricing
   - Network configuration
   - Performance optimization
   - Cost efficiency strategies
   - Comprehensive troubleshooting
   - API reference
   - Advanced configurations

6. **`QUICK_START.md`** - 5-minute quick start guide for rapid deployment
7. **`DEPLOYMENT_CHECKLIST.md`** - Interactive checklist to track deployment progress
8. **`README.md`** - Overview and quick reference

### Testing & Utilities
9. **`test_client.py`** - Comprehensive test script to verify deployment
10. **`.dockerignore`** - Optimized Docker build context

---

## 🎯 Deployment Options

### Option 1: Docker Image (Recommended for Production)
**Best for:** Production deployments, reproducible environments

**Steps:**
1. Build Docker image: `docker build -t your-name/orpheus-tts-runpod .`
2. Push to Docker Hub: `docker push your-name/orpheus-tts-runpod`
3. Deploy on RunPod with your image URL
4. Expose port 8080
5. Done!

**Pros:**
- Fully automated setup
- Reproducible builds
- Faster deployment
- Version control

**Cons:**
- Requires Docker Hub account
- Initial build time

### Option 2: Manual Setup (Quick Start)
**Best for:** Testing, development, quick experiments

**Steps:**
1. Deploy RunPod pod with PyTorch base image
2. Upload `server.py` via web terminal
3. Run: `pip install orpheus-speech flask && pip install vllm==0.7.3`
4. Run: `python server.py`
5. Done!

**Pros:**
- No Docker build needed
- Quick to test
- Easy to modify

**Cons:**
- Manual setup each time
- Less reproducible
- Slower startup

---

## 💰 Cost Estimates

### GPU Options & Pricing

| Scenario | GPU | VRAM | Cost/Hour | Cost/Day* | Best For |
|----------|-----|------|-----------|-----------|----------|
| **Testing** | RTX 3060 | 12GB | $0.25 | $2.00 | Development, low volume |
| **Production** | RTX 3090 | 24GB | $0.50 | $4.00 | Most deployments |
| **High Performance** | RTX 4090 | 24GB | $1.00 | $8.00 | High traffic, low latency |
| **Enterprise** | A5000 | 24GB | $0.75 | $6.00 | Reliability critical |

*Assuming 8 hours/day active use with auto-stop enabled

### Monthly Cost Examples

**Light Usage** (2 hours/day, RTX 3090):
- $0.50/hour × 2 hours × 30 days = **$30/month**

**Medium Usage** (8 hours/day, RTX 3090):
- $0.50/hour × 8 hours × 30 days = **$120/month**

**Heavy Usage** (24/7, RTX 3090):
- $0.50/hour × 24 hours × 30 days = **$360/month**

**Cost Savings Tips:**
- Enable auto-stop: Save 50-70%
- Use Community Cloud: Save 50-70% (less reliable)
- Batch requests: Reduce idle time
- Right-size GPU: Don't overpay for unused capacity

---

## 🚀 Performance Specifications

### Latency
- **First request:** 30-120 seconds (model loading)
- **Subsequent requests:** ~200ms streaming latency
- **Optimized:** ~100ms with input streaming

### Throughput
- **Single request:** 5-10 seconds for typical prompt
- **Concurrent requests:** Limited by VRAM (1-2 concurrent on 24GB)
- **Audio quality:** 24kHz, 16-bit WAV

### Resource Usage
- **Model size:** ~6GB VRAM when loaded
- **Disk space:** 20GB minimum (for model cache)
- **CPU:** Minimal (GPU-accelerated)
- **Network:** ~1-5 MB per request (varies by length)

---

## 🔧 Technical Stack

### Software
- **Base OS:** Ubuntu 22.04
- **CUDA:** 12.1.0 with cuDNN 8
- **Python:** 3.10
- **PyTorch:** 2.0+
- **vLLM:** 0.7.3 (optimized for stability)
- **Web Server:** Flask (dev) or Gunicorn (production)

### Model
- **Architecture:** Llama-3B backbone
- **Model:** canopylabs/orpheus-tts-0.1-finetune-prod
- **Voices:** 8 (tara, zoe, zac, jess, leo, mia, julia, leah)
- **Audio Codec:** SNAC (24kHz)

---

## 📊 API Overview

### Endpoints

```
GET  /              - API information
GET  /health        - Health check
GET  /voices        - List available voices
GET  /tts           - Generate speech (query params)
POST /tts           - Generate speech (JSON body)
```

### Example Usage

**cURL:**
```bash
curl "https://your-pod-8080.proxy.runpod.net/tts?prompt=Hello&voice=tara" -o output.wav
```

**Python:**
```python
import requests
response = requests.get("https://your-pod-8080.proxy.runpod.net/tts", 
                       params={"prompt": "Hello", "voice": "tara"})
with open("output.wav", "wb") as f:
    f.write(response.content)
```

**JavaScript:**
```javascript
const url = "https://your-pod-8080.proxy.runpod.net/tts?prompt=Hello&voice=tara";
fetch(url)
  .then(res => res.blob())
  .then(blob => {
    const audio = new Audio(URL.createObjectURL(blob));
    audio.play();
  });
```

---

## ✅ Success Checklist

Your deployment is successful when:

- [x] Health endpoint returns `{"status": "healthy", "model_loaded": true}`
- [x] TTS endpoint generates clear audio
- [x] Latency is <5 seconds for typical prompts
- [x] Multiple requests work without errors
- [x] Costs are within budget
- [x] Auto-stop is configured (if needed)

---

## 📚 Documentation Guide

**Start here based on your needs:**

1. **First-time deployment?** → Read `QUICK_START.md`
2. **Need detailed instructions?** → Read `RUNPOD_DEPLOYMENT.md`
3. **Want to track progress?** → Use `DEPLOYMENT_CHECKLIST.md`
4. **Having issues?** → Check `RUNPOD_DEPLOYMENT.md` troubleshooting section
5. **Need API reference?** → See `RUNPOD_DEPLOYMENT.md` API section

---

## 🆘 Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Model not loading | Wait 2 minutes, check `/health` endpoint |
| Out of memory | Use GPU with 24GB VRAM |
| Slow inference | Check GPU utilization with `nvidia-smi` |
| Connection refused | Verify port 8080 is exposed |
| High costs | Enable auto-stop in pod settings |
| Audio quality issues | Adjust temperature (0.3-0.6) |

Full troubleshooting guide in `RUNPOD_DEPLOYMENT.md`

---

## 🔗 Resources

- **Orpheus TTS:** https://github.com/canopyai/Orpheus-TTS
- **RunPod Docs:** https://docs.runpod.io
- **vLLM Docs:** https://docs.vllm.ai
- **Support:** https://github.com/canopyai/Orpheus-TTS/issues

---

## 🎉 Next Steps

1. Choose your deployment option (Docker or Manual)
2. Follow the appropriate guide
3. Test with `test_client.py`
4. Integrate into your application
5. Monitor costs and performance
6. Optimize based on your usage patterns

**Ready to deploy?** Start with `QUICK_START.md` or `RUNPOD_DEPLOYMENT.md`!

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-15  
**Maintained by:** Orpheus TTS Community

