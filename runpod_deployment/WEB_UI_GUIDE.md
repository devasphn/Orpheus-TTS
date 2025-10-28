# Orpheus TTS Web UI - User Guide

## 🎨 Web UI Features

The Orpheus TTS Web UI provides a beautiful, user-friendly interface for text-to-speech generation.

### Interface Components

#### 1. **Status Bar** (Top)
- **Status Indicator:** Green dot when model is ready, gray when loading
- **Model Info:** Displays current model version
- **Real-time Updates:** Automatically checks server health

#### 2. **Left Panel - Input Controls**

**Voice Selector**
- Dropdown menu with 8 available voices
- Voices include: Tara, Zoe, Zac, Jess, Leo, Mia, Julia, Leah
- Default: Tara

**Text Input Area**
- Large textarea for entering text
- Supports multi-line text
- Pre-filled with example text
- Placeholder guidance

**Action Buttons**
- **Generate Speech:** Creates audio from text
- **Clear:** Clears the text input

#### 3. **Right Panel - Audio Player**

**Audio Player Container**
- Displays placeholder before generation
- Shows loading spinner during generation
- HTML5 audio player with controls:
  - Play/Pause button
  - Progress bar
  - Volume control
  - Download option
- Auto-plays generated audio (if browser allows)

#### 4. **Notification System**

**Success Messages** (Green)
- Confirms successful speech generation
- Auto-dismisses after 5 seconds

**Error Messages** (Red)
- Displays error details
- Auto-dismisses after 5 seconds

---

## 🎯 How to Use

### Basic Usage

1. **Open the Web UI**
   - Navigate to: `https://your-pod-id-8080.proxy.runpod.net`
   - Wait for status indicator to turn green

2. **Select a Voice**
   - Click the voice dropdown
   - Choose from 8 available voices
   - Each voice has unique characteristics

3. **Enter Your Text**
   - Click in the text area
   - Type or paste your text
   - Multi-line text is supported

4. **Generate Speech**
   - Click "Generate Speech" button
   - Wait 3-5 seconds for processing
   - Audio player will appear automatically

5. **Listen to Audio**
   - Audio auto-plays (if browser allows)
   - Use player controls to play/pause
   - Adjust volume as needed
   - Download audio if desired

### Advanced Usage

**Testing Different Voices**
1. Enter the same text
2. Generate with different voices
3. Compare voice characteristics
4. Choose the best voice for your use case

**Long Text Processing**
- The system supports up to 2000 tokens
- Longer text takes more time to process
- Consider breaking very long text into chunks

**Batch Generation**
1. Generate first audio
2. Change voice or text
3. Generate again
4. Previous audio remains playable until new generation

---

## 🎨 Voice Characteristics

### Available Voices

| Voice | Gender | Characteristics | Best For |
|-------|--------|-----------------|----------|
| **Tara** | Female | Warm, friendly, clear | General purpose, default |
| **Zoe** | Female | Energetic, expressive | Engaging content |
| **Zac** | Male | Deep, authoritative | Professional content |
| **Jess** | Female | Soft, gentle | Calm narration |
| **Leo** | Male | Strong, confident | Announcements |
| **Mia** | Female | Bright, cheerful | Upbeat content |
| **Julia** | Female | Elegant, refined | Formal content |
| **Leah** | Female | Natural, conversational | Casual content |

---

## 🔧 Technical Details

### Audio Specifications
- **Format:** WAV (uncompressed)
- **Sample Rate:** 24,000 Hz
- **Bit Depth:** 16-bit
- **Channels:** Mono (1 channel)
- **Streaming:** Yes, real-time generation

### Generation Parameters
- **Temperature:** 0.4 (controls randomness)
- **Top P:** 0.9 (nucleus sampling)
- **Max Tokens:** 2000 (maximum length)
- **Repetition Penalty:** 1.1 (reduces repetition)

### Browser Compatibility
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Opera
- ✅ Mobile browsers

### Performance
- **First Generation:** 30-120 seconds (model loading)
- **Subsequent Generations:** 3-5 seconds
- **Streaming Latency:** ~200ms
- **Network Usage:** 1-5 MB per request

---

## 🎨 UI Customization

The Web UI is fully customizable. Edit `web_ui.html` to:

### Change Colors
```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your brand colors */
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

### Modify Layout
```css
/* Current: 2-column layout */
.main-content {
    grid-template-columns: 1fr 1fr;
}

/* Change to single column */
.main-content {
    grid-template-columns: 1fr;
}
```

### Add Your Logo
```html
<h1>🎙️ Orpheus TTS</h1>

<!-- Replace with -->
<h1><img src="your-logo.png" alt="Logo"> Your Brand</h1>
```

---

## 🐛 Troubleshooting

### Web UI Not Loading

**Symptom:** Blank page or 404 error

**Solutions:**
1. Verify `web_ui.html` is in the same directory as `server.py`
2. Check server logs for errors
3. Try accessing `/health` endpoint directly
4. Clear browser cache and reload

### Audio Not Playing

**Symptom:** Audio player appears but no sound

**Solutions:**
1. Check browser console (F12) for errors
2. Verify browser supports WAV format
3. Check system volume and browser volume
4. Try a different browser
5. Disable browser extensions that might block audio

### Generation Takes Too Long

**Symptom:** Waiting more than 30 seconds

**Solutions:**
1. First generation takes longer (model loading)
2. Check server logs for progress
3. Verify GPU is available: `nvidia-smi`
4. Reduce text length
5. Check network connection

### Status Shows "Unhealthy"

**Symptom:** Red/gray status indicator

**Solutions:**
1. Wait 1-2 minutes for model to load
2. Check server logs for errors
3. Verify GPU has enough memory
4. Restart the server
5. Check `/health` endpoint response

### CORS Errors

**Symptom:** Browser console shows CORS errors

**Solutions:**
1. Ensure you're accessing via the RunPod proxy URL
2. Don't mix HTTP and HTTPS
3. Use the same domain for all requests
4. Check browser security settings

---

## 📱 Mobile Usage

The Web UI is responsive and works on mobile devices:

### Mobile Features
- ✅ Touch-friendly controls
- ✅ Responsive layout
- ✅ Mobile audio playback
- ✅ Optimized for small screens

### Mobile Tips
1. Use landscape mode for better layout
2. Ensure stable internet connection
3. Allow audio playback in browser settings
4. Use headphones for better audio quality

---

## 🔒 Security Considerations

### Current Setup
- ✅ HTTPS via RunPod proxy
- ✅ No authentication (public access)
- ⚠️ Anyone with URL can access

### Adding Authentication

To add basic authentication, modify `server.py`:

```python
from functools import wraps
from flask import request, jsonify

API_KEY = "your-secret-key"

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# Apply to endpoints
@app.route('/tts', methods=['GET', 'POST'])
@require_api_key
def tts():
    # ... existing code
```

Then update `web_ui.html` to include the API key in requests.

---

## 📊 Usage Analytics

To track usage, you can add logging to `server.py`:

```python
@app.route('/tts', methods=['GET', 'POST'])
def tts():
    # Log request
    logger.info(f"TTS Request - Voice: {voice}, Text Length: {len(prompt)}")
    
    # ... existing code
```

---

## 🎉 Best Practices

### For Best Results

1. **Text Quality**
   - Use proper punctuation
   - Avoid special characters
   - Break long text into sentences
   - Use natural language

2. **Voice Selection**
   - Test multiple voices
   - Match voice to content type
   - Consider audience preferences
   - Use consistent voice for series

3. **Performance**
   - Pre-load model before heavy usage
   - Monitor GPU memory
   - Use appropriate text length
   - Cache frequently used audio

4. **User Experience**
   - Provide clear instructions
   - Show loading indicators
   - Handle errors gracefully
   - Enable audio download

---

## 🔄 Updates and Maintenance

### Updating the Web UI

1. Edit `web_ui.html`
2. Save changes
3. Refresh browser (Ctrl+F5 for hard refresh)
4. No server restart needed

### Updating the Server

1. Stop the server (Ctrl+C)
2. Edit `server.py`
3. Save changes
4. Restart: `python server.py`

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review `MANUAL_SETUP_COMMANDS.md`
3. Check server logs
4. Consult `RUNPOD_DEPLOYMENT.md`
5. Open GitHub issue

---

**Enjoy creating natural-sounding speech with Orpheus TTS! 🎙️✨**

