# Orpheus TTS RunPod - Quick Start Guide

## 🚀 5-Minute Deployment

### Step 1: Sign Up for RunPod
1. Go to https://www.runpod.io
2. Create account and add $10+ credits

### Step 2: Deploy Pod
1. Click **"Pods"** → **"+ Deploy"**
2. Select GPU: **RTX 3090** (24GB) or better
3. Configure:
   ```
   Container Image: runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel
   Expose HTTP Ports: 8080
   Container Disk: 20GB
   ```
4. Click **"Deploy On-Demand"**

### Step 3: Setup Server
1. Wait for pod to start (1-2 min)
2. Click **"Connect"** → **"Start Web Terminal"**
3. Run setup commands:
   ```bash
   # Install dependencies
   pip install orpheus-speech flask
   pip install vllm==0.7.3
   
   # Download server script
   wget https://raw.githubusercontent.com/canopyai/Orpheus-TTS/main/runpod_deployment/server.py
   
   # Start server
   python server.py
   ```

### Step 4: Get Your URL
1. In pod details, find **"HTTP Service"**
2. Your URL: `https://[pod-id]-8080.proxy.runpod.net`
3. Copy this URL

### Step 5: Test It
```bash
# Health check
curl https://your-pod-id-8080.proxy.runpod.net/health

# Generate speech
curl "https://your-pod-id-8080.proxy.runpod.net/tts?prompt=Hello%20world&voice=tara" \
  --output test.wav
```

## ✅ You're Done!

Your TTS server is now running. Play the `test.wav` file to hear the result.

---

## 🎯 Common Commands

### Generate Speech (Browser)
```
https://your-pod-id-8080.proxy.runpod.net/tts?prompt=Your%20text%20here&voice=tara
```

### Generate Speech (Python)
```python
import requests

url = "https://your-pod-id-8080.proxy.runpod.net/tts"
params = {
    "prompt": "Hello from Python!",
    "voice": "tara"
}

response = requests.get(url, params=params)
with open("output.wav", "wb") as f:
    f.write(response.content)
```

### Available Voices
- tara (default)
- zoe
- zac
- jess
- leo
- mia
- julia
- leah

---

## 💡 Tips

**Save Money:**
- Enable auto-stop after 15 min idle
- Use Community Cloud (cheaper, less reliable)
- Stop pod when not in use

**Better Performance:**
- Use RTX 4090 or A5000 for faster generation
- Reduce `max_tokens` for shorter responses
- Pre-load model on startup

**Troubleshooting:**
- Model loading takes 30-120 seconds on first request
- Check `/health` endpoint to verify model is loaded
- If OOM error, use GPU with 24GB VRAM

---

## 📖 Full Documentation

For complete guide, see [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md)

## 🆘 Need Help?

1. Check [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md) troubleshooting section
2. GitHub Issues: https://github.com/canopyai/Orpheus-TTS/issues
3. RunPod Discord: https://discord.gg/runpod

