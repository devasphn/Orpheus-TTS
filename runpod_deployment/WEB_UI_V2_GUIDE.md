# Orpheus Conversational AI - Web UI Guide

## 🎉 New Web Interface!

The updated web UI (`web_ui_v2.html`) now includes **both** Conversational AI and Text-to-Speech features in a single, modern interface.

---

## 🚀 Quick Start

### **Access the Web UI**

Once your server is running:

```
http://localhost:8080/
```

Or if deployed on RunPod:
```
https://your-runpod-id-8080.proxy.runpod.net/
```

---

## 📱 Features

### **1. Conversational AI Tab** 💬

**What it does:**
- Chat with Gemma 2 2B LLM
- Get voice responses from Orpheus TTS
- Maintain conversation history
- Choose from 8 different voices

**How to use:**
1. Type your message in the text area
2. Select a voice (default: Tara)
3. Click "Send Message"
4. Wait for the AI to respond
5. Audio will auto-play when ready

**Features:**
- ✅ Real-time conversation
- ✅ Streaming audio responses
- ✅ Conversation history maintained
- ✅ Voice selection per message
- ✅ Auto-play audio responses
- ✅ Clear chat button

**Example conversation:**
```
You: Hello, how are you?
AI: [Audio plays] "I'm doing well, thank you for asking! How can I help you today?"

You: Tell me a joke
AI: [Audio plays] "Why did the programmer quit his job? Because he didn't get arrays!"
```

---

### **2. Text-to-Speech Tab** 🔊

**What it does:**
- Direct text-to-speech conversion
- No conversation context
- Quick audio generation

**How to use:**
1. Switch to "Text-to-Speech" tab
2. Enter text to convert
3. Select voice
4. Click "Generate Speech"
5. Listen to the audio

**Use cases:**
- Generate audio for specific text
- Test different voices
- Create audio files without conversation

---

## 🎨 Interface Features

### **Status Bar**

Shows real-time server status:
- **Server Status**: Online/Offline indicator
- **Model Status**: TTS and LLM loading status
  - ✅ = Model loaded successfully
  - ❌ = Model not loaded

**Example:**
```
🟢 Server: Online | TTS: ✅ | LLM: ✅
```

---

### **Voice Options**

8 high-quality voices available:

| Voice | Description | Best For |
|-------|-------------|----------|
| **Tara** | Default, professional | General use, announcements |
| **Zoe** | Friendly, warm | Casual conversations |
| **Zac** | Male, clear | Male voice preference |
| **Jess** | Energetic | Upbeat content |
| **Leo** | Male, deep | Authoritative content |
| **Mia** | Soft, gentle | Calm, soothing content |
| **Julia** | Professional | Business, formal |
| **Leah** | Expressive | Storytelling, narration |

---

## 💡 Tips & Tricks

### **Conversation Tips**

1. **Keep messages concise**: Shorter messages = faster responses
2. **Use natural language**: Talk like you would to a person
3. **Build on context**: Reference previous messages in the conversation
4. **Clear chat when switching topics**: Start fresh for unrelated topics

### **Performance Tips**

1. **First response is slower**: Model warm-up takes ~2-3 seconds
2. **Subsequent responses are faster**: Models stay loaded
3. **Expected latency**: 
   - Time to first audio: ~700ms
   - Total response time: 2-5 seconds (depending on length)

### **Voice Selection Tips**

1. **Match voice to content**: 
   - Professional content → Tara, Julia
   - Casual chat → Zoe, Jess
   - Male voice → Zac, Leo
2. **Experiment**: Try different voices for the same message
3. **Consistency**: Use the same voice for a conversation thread

---

## 🔧 Keyboard Shortcuts

- **Enter**: Send message (in chat input)
- **Shift + Enter**: New line (in chat input)

---

## 🐛 Troubleshooting

### **Issue: Server shows "Offline"**

**Solution:**
1. Check if server is running: `python server.py`
2. Verify port 8080 is accessible
3. Check firewall settings

### **Issue: Models show ❌**

**Solution:**
1. Wait for models to load (can take 1-2 minutes on first start)
2. Check server logs for errors
3. Verify GPU memory is sufficient (need ~12GB for both models)

### **Issue: No audio plays**

**Solution:**
1. Check browser audio permissions
2. Verify audio is not muted
3. Try a different browser (Chrome/Firefox recommended)
4. Check server logs for generation errors

### **Issue: Response is very slow**

**Expected behavior:**
- First response: 2-5 seconds (model warm-up)
- Subsequent responses: 2-3 seconds

**If slower:**
1. Check GPU utilization: `nvidia-smi`
2. Verify no other processes using GPU
3. Check server logs for errors

### **Issue: Chat history not maintained**

**Solution:**
1. Don't refresh the page (clears history)
2. Use "Clear Chat" button to intentionally reset
3. History is client-side only (not saved on server)

---

## 📊 Performance Expectations

### **Latency Breakdown**

For a typical question: "Hello, how are you?"

```
User sends message
    ↓
[50-100ms]  LLM: Time to first token
[400ms]     LLM: Generate response (~100 tokens @ 250 tok/s)
[50ms]      Sentence detection
[200ms]     TTS: First sentence processing
    ↓
[~700ms]    FIRST AUDIO PLAYS ✅
    ↓
[2-3s]      Complete response
```

### **Throughput**

- **LLM**: 200-300 tokens/s (text generation)
- **TTS**: 42 tokens/s (audio generation)
- **End-to-end**: 42 tokens/s (TTS-limited)

---

## 🎯 Use Cases

### **1. Voice Assistant**
```
User: What's the weather like today?
AI: [Responds with weather information in natural voice]
```

### **2. Interactive Storytelling**
```
User: Tell me a story about a dragon
AI: [Narrates a story with expressive voice]
User: What happened next?
AI: [Continues the story with context]
```

### **3. Educational Content**
```
User: Explain quantum physics simply
AI: [Provides explanation in clear, professional voice]
User: Can you give an example?
AI: [Provides example with context from previous explanation]
```

### **4. Customer Service Simulation**
```
User: I need help with my order
AI: [Responds in helpful, professional voice]
User: My order number is 12345
AI: [Continues conversation with context]
```

---

## 🔐 Security Notes

1. **No authentication**: Current UI has no login system
2. **Client-side history**: Conversation history stored in browser only
3. **No data persistence**: Refresh clears all history
4. **Public access**: Anyone with URL can access (if deployed publicly)

**For production:**
- Add authentication layer
- Implement rate limiting
- Add conversation logging (server-side)
- Use HTTPS

---

## 📁 File Structure

```
runpod_deployment/
├── web_ui_v2.html          # New conversational AI UI (THIS FILE)
├── web_ui.html             # Old TTS-only UI (fallback)
├── server.py               # Backend server (updated to serve v2)
└── ...
```

---

## 🆚 Comparison: Old vs New UI

| Feature | Old UI (web_ui.html) | New UI (web_ui_v2.html) |
|---------|---------------------|------------------------|
| **Text-to-Speech** | ✅ | ✅ |
| **Conversational AI** | ❌ | ✅ |
| **Chat History** | ❌ | ✅ |
| **Voice Selection** | ✅ | ✅ |
| **Auto-play Audio** | ❌ | ✅ |
| **Status Indicators** | ✅ | ✅ (Enhanced) |
| **Tabs** | ❌ | ✅ |
| **Modern Design** | ✅ | ✅ (Improved) |

---

## 🚀 Future Enhancements

Potential features for future versions:

- [ ] Speech-to-text input (microphone support)
- [ ] Save/export conversation history
- [ ] Download audio files
- [ ] Conversation templates
- [ ] Multi-language support
- [ ] Voice cloning interface
- [ ] Emotion control sliders
- [ ] Real-time audio streaming (chunk-by-chunk)
- [ ] User authentication
- [ ] Conversation sharing

---

## 📝 Summary

**What you get:**
- ✅ Modern, responsive web interface
- ✅ Conversational AI with voice responses
- ✅ Direct text-to-speech conversion
- ✅ 8 voice options
- ✅ Real-time status monitoring
- ✅ Chat history management
- ✅ Auto-playing audio responses

**How to use:**
1. Start server: `python server.py`
2. Open browser: `http://localhost:8080/`
3. Start chatting!

**Performance:**
- ~700ms to first audio
- 2-3s for complete responses
- Conversation history maintained

Enjoy your new conversational AI voice assistant! 🎉

