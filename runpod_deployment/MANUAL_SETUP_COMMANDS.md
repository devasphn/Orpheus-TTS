# RunPod Web Terminal - Manual Setup Commands

Complete step-by-step commands to set up Orpheus TTS with Web UI on RunPod.

## 📋 Prerequisites

- RunPod pod with GPU (RTX 3090 or better recommended)
- Port 8080 exposed in pod settings
- Web terminal access

---

## 🚀 Step-by-Step Setup Commands

### Step 1: Navigate to Workspace Directory

```bash
cd /workspace
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/devasphn/Orpheus-TTS.git
```

**Expected output:** Repository cloned successfully

### Step 3: Navigate to Deployment Directory

```bash
cd Orpheus-TTS/runpod_deployment
```

### Step 4: Install System Packages (if needed)

Most RunPod images have these pre-installed, but run this to be sure:

```bash
apt-get update && apt-get install -y wget curl git
```

**Note:** If you get permission errors, the packages are likely already installed. You can skip this step.

### Step 5: Create Python Virtual Environment

```bash
python3 -m venv venv
```

**Expected output:** Virtual environment created in `venv/` directory

### Step 6: Activate Virtual Environment

```bash
source venv/bin/activate
```

**Expected output:** Your prompt should now show `(venv)` at the beginning

### Step 7: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 8: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:** All packages installed successfully
**Time:** ~2-3 minutes

### Step 9: Install vLLM (Specific Version)

```bash
pip install vllm==0.7.3
```

**Expected output:** vLLM 0.7.3 installed
**Time:** ~1-2 minutes

**Important:** This must be done AFTER installing orpheus-speech to ensure compatibility.

### Step 10: Pre-download the Model (Optional but Recommended)

This step downloads the model before starting the server to avoid delays on first request:

```bash
python3 -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('canopylabs/orpheus-tts-0.1-finetune-prod')"
```

**Expected output:** Model files downloaded to cache
**Time:** ~2-5 minutes (depending on network speed)

### Step 11: Make Startup Script Executable

```bash
chmod +x startup.sh
```

### Step 12: Start the Server

**Option A: Using Python directly (Recommended for testing)**

```bash
python server.py
```

**Option B: Using the startup script**

```bash
./startup.sh
```

**Expected output:**
```
==========================================
Orpheus TTS RunPod Deployment
==========================================

System Information:
-------------------
Python version: Python 3.10.x
CUDA available: True
GPU name: NVIDIA GeForce RTX 3090
...

Starting Orpheus TTS Server...
==========================================

 * Serving Flask app 'server'
 * Running on http://0.0.0.0:8080
```

**Time to start:** 30-120 seconds (model loading)

---

## 🌐 Access the Web UI

### Step 13: Get Your Public URL

1. In RunPod dashboard, go to your pod details
2. Look for "HTTP Service" section
3. Your URL will be: `https://[pod-id]-8080.proxy.runpod.net`

### Step 14: Open in Browser

Open your browser and navigate to:
```
https://your-pod-id-8080.proxy.runpod.net
```

You should see the Orpheus TTS Web UI with:
- ✅ Voice selection dropdown
- ✅ Text input area
- ✅ Generate button
- ✅ Audio player on the right

---

## ✅ Verification Steps

### Test 1: Check Health Endpoint

In a new terminal or browser:
```bash
curl https://your-pod-id-8080.proxy.runpod.net/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-01-15T10:30:00"
}
```

### Test 2: Generate Speech via Web UI

1. Open the web UI in your browser
2. Select a voice (e.g., "Tara")
3. Enter text: "Hello, this is a test"
4. Click "Generate Speech"
5. Wait 3-5 seconds
6. Audio player should appear with playback controls
7. Click play to hear the generated speech

### Test 3: Test Different Voices

Try generating speech with different voices:
- Tara (default, female)
- Zoe (female)
- Zac (male)
- Jess (female)
- Leo (male)
- Mia (female)
- Julia (female)
- Leah (female)

---

## 🔧 Troubleshooting

### Issue: "Model not loaded" error

**Solution:**
Wait 1-2 minutes for the model to load, then refresh the page. Check the terminal for loading progress.

### Issue: "Connection refused" or 502 error

**Solution:**
1. Verify port 8080 is exposed in RunPod pod settings
2. Check if server is running: `ps aux | grep python`
3. Restart the server

### Issue: "CUDA out of memory"

**Solution:**
1. Use a GPU with at least 24GB VRAM
2. Restart the pod to clear GPU memory
3. Reduce MAX_MODEL_LEN environment variable

### Issue: Web UI not loading

**Solution:**
1. Verify `web_ui.html` is in the same directory as `server.py`
2. Check server logs for errors
3. Try accessing `/health` endpoint to verify server is running

### Issue: Audio not playing

**Solution:**
1. Check browser console for errors (F12)
2. Verify audio format is supported (WAV should work in all browsers)
3. Try a different browser (Chrome, Firefox, Edge)
4. Check if browser is blocking auto-play

---

## 📝 Complete Command Summary (Copy-Paste Ready)

```bash
# Navigate to workspace
cd /workspace

# Clone repository
git clone https://github.com/devasphn/Orpheus-TTS.git

# Navigate to deployment directory
cd Orpheus-TTS/runpod_deployment

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install vLLM
pip install vllm==0.7.3

# Pre-download model (optional but recommended)
python3 -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('canopylabs/orpheus-tts-0.1-finetune-prod')"

# Make startup script executable
chmod +x startup.sh

# Start the server
python server.py
```

**Total setup time:** ~5-10 minutes (including model download)

---

## 🎯 Quick Start (Minimal Commands)

If you're in a hurry and the RunPod image already has most dependencies:

```bash
cd /workspace && \
git clone https://github.com/devasphn/Orpheus-TTS.git && \
cd Orpheus-TTS/runpod_deployment && \
pip install orpheus-speech flask && \
pip install vllm==0.7.3 && \
python server.py
```

Then open: `https://your-pod-id-8080.proxy.runpod.net`

---

## 🔄 Restarting the Server

If you need to restart the server later:

```bash
# Navigate to directory
cd /workspace/Orpheus-TTS/runpod_deployment

# Activate virtual environment (if using one)
source venv/bin/activate

# Start server
python server.py
```

---

## 🛑 Stopping the Server

To stop the server:
1. Press `Ctrl + C` in the terminal where the server is running
2. Wait for graceful shutdown

---

## 💡 Pro Tips

1. **Keep the terminal open:** Don't close the terminal window while the server is running
2. **Monitor GPU usage:** Run `nvidia-smi` in another terminal to check GPU utilization
3. **Check logs:** Server logs appear in the terminal - watch for errors
4. **Test incrementally:** Test each voice to ensure quality
5. **Save your URL:** Bookmark your RunPod URL for easy access

---

## 📊 Expected Performance

- **First request:** 30-120 seconds (model loading)
- **Subsequent requests:** 3-5 seconds for typical text
- **Streaming latency:** ~200ms
- **Audio quality:** 24kHz, 16-bit WAV
- **GPU memory usage:** ~6GB VRAM

---

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review server logs in the terminal
3. Check RunPod pod status and GPU availability
4. Verify all files are present: `ls -la`
5. Ensure port 8080 is exposed in pod settings

---

## ✅ Success Checklist

- [ ] Repository cloned successfully
- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] vLLM 0.7.3 installed
- [ ] Model pre-downloaded (optional)
- [ ] Server started successfully
- [ ] Web UI loads in browser
- [ ] Health check returns "healthy"
- [ ] Can select different voices
- [ ] Can generate speech
- [ ] Audio plays correctly in browser

---

**You're all set! Enjoy using Orpheus TTS! 🎉**

