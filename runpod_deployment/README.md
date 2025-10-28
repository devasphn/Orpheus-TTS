# Orpheus TTS RunPod Deployment

This directory contains everything you need to deploy Orpheus TTS streaming inference server on RunPod.

## 📁 Files Included

- **`RUNPOD_DEPLOYMENT.md`** - Complete step-by-step deployment guide
- **`Dockerfile`** - Docker image configuration for RunPod
- **`server.py`** - Enhanced Flask server with health checks and error handling
- **`startup.sh`** - Container initialization script
- **`requirements.txt`** - Python dependencies
- **`test_client.py`** - Test script to verify deployment
- **`README.md`** - This file

## 🚀 Quick Start

### 1. Build Docker Image (Optional)

If you want to use a custom Docker image:

```bash
# Build the image
docker build -t your-dockerhub-username/orpheus-tts-runpod:latest .

# Push to Docker Hub
docker login
docker push your-dockerhub-username/orpheus-tts-runpod:latest
```

### 2. Deploy on RunPod

1. Go to [runpod.io](https://www.runpod.io) and create an account
2. Click "Pods" → "+ Deploy"
3. Select a GPU (recommended: RTX 3090 or better with 24GB VRAM)
4. Configure:
   - **Container Image**: `your-dockerhub-username/orpheus-tts-runpod:latest`
   - **Expose HTTP Ports**: `8080`
   - **Container Disk**: 20GB minimum
5. Click "Deploy"

### 3. Test Your Deployment

Once your pod is running:

```bash
# Get your pod URL from RunPod dashboard
# It will look like: https://abc123def456-8080.proxy.runpod.net

# Test with the client script
python test_client.py https://your-pod-id-8080.proxy.runpod.net
```

## 📖 Full Documentation

See **[RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md)** for:
- Detailed setup instructions
- GPU recommendations
- Network configuration
- Performance optimization
- Cost efficiency tips
- Troubleshooting guide
- API reference

## 🎯 Key Features

- ✅ Streaming audio generation
- ✅ Multiple voice support (8 voices)
- ✅ Health check endpoint
- ✅ GET and POST API methods
- ✅ Production-ready error handling
- ✅ Optimized for RunPod infrastructure
- ✅ ~200ms latency (reducible to ~100ms)

## 💰 Estimated Costs

| GPU Type | VRAM | Hourly Cost* | Best For |
|----------|------|--------------|----------|
| RTX 3060 | 12GB | $0.20-0.30 | Testing |
| RTX 3090 | 24GB | $0.40-0.60 | Production |
| RTX 4090 | 24GB | $0.80-1.20 | High performance |

*Prices vary by region and availability

## 🔧 Environment Variables

Configure these in RunPod pod settings:

```bash
MODEL_NAME=canopylabs/orpheus-tts-0.1-finetune-prod
MAX_MODEL_LEN=2048
PORT=8080
```

## 📝 API Endpoints

- `GET /health` - Health check
- `GET /voices` - List available voices
- `GET /tts?prompt=text&voice=tara` - Generate speech (GET)
- `POST /tts` - Generate speech (POST with JSON)

## 🐛 Troubleshooting

**Model not loading?**
- Check GPU is available: `nvidia-smi`
- Increase container disk size
- Check logs in RunPod web terminal

**Out of memory?**
- Use GPU with 24GB VRAM
- Reduce `MAX_MODEL_LEN` to 1024
- Ensure only 1 worker process

**Slow inference?**
- Check GPU utilization
- Use faster GPU (RTX 4090 or A5000)
- Reduce `max_tokens` parameter

See full troubleshooting guide in [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md)

## 📚 Resources

- [Orpheus TTS GitHub](https://github.com/canopyai/Orpheus-TTS)
- [RunPod Documentation](https://docs.runpod.io)
- [vLLM Documentation](https://docs.vllm.ai)

## 🤝 Support

For issues:
1. Check [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md) troubleshooting section
2. Search [GitHub Issues](https://github.com/canopyai/Orpheus-TTS/issues)
3. Create a new issue with logs and configuration

## 📄 License

This deployment configuration follows the Orpheus TTS project license.

---

**Ready to deploy?** Start with [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md) for complete instructions!

