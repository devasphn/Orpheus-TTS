# Orpheus Conversational AI - Examples

This directory contains example scripts and tools for using the Orpheus Conversational AI pipeline.

## 📁 Files

### `chat_example.py`
Interactive examples demonstrating how to use the `/chat` endpoint.

**Features**:
- Quick test
- Multi-turn conversations with history
- Test all 8 voices
- Text-only streaming (debugging)
- Custom messages

**Usage**:
```bash
python chat_example.py
```

**Examples**:

```python
# Simple chat
from chat_example import chat_with_voice

chat_with_voice(
    "Hello, how are you?",
    voice="tara",
    save_to="response.wav"
)

# Multi-turn conversation
history = [
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello! How can I help?"}
]

chat_with_voice(
    "Tell me a joke",
    voice="zoe",
    history=history,
    save_to="joke.wav"
)
```

---

### `benchmark_chat.py`
Performance benchmarking tool for measuring latency and throughput.

**Features**:
- Quick benchmark (single message)
- Comprehensive benchmark (short/medium/long messages)
- LLM-only benchmark (text stream)
- Custom message benchmarking
- Statistical analysis (mean, std dev)

**Usage**:
```bash
python benchmark_chat.py
```

**Metrics Measured**:
- Total response time
- Time to first chunk (TTFC)
- File size
- Estimated throughput (tokens/s)

**Example Output**:
```
BENCHMARK SUMMARY
======================================================================
Message: Hello, how are you?...
Voice: tara
Successful runs: 3

Average total time:        2.45s
Average time to 1st chunk: 0.687s
Average file size:         156.3 KB
Average throughput:        42.3 tok/s

Standard deviation:
  Total time: ±0.12s
  Throughput: ±1.8 tok/s
======================================================================
```

---

## 🚀 Quick Start

### 1. Start the server
```bash
cd /workspace/Orpheus-TTS/runpod_deployment
python server.py
```

### 2. Run examples
```bash
cd examples

# Interactive chat examples
python chat_example.py

# Performance benchmarks
python benchmark_chat.py
```

---

## 📊 Expected Performance

Based on RTX A4500 (20GB VRAM):

| Metric | Value |
|--------|-------|
| Time to first audio | 650-750ms |
| LLM throughput | 200-300 tok/s |
| TTS throughput | 42 tok/s |
| Pipeline throughput | 42 tok/s (TTS-limited) |

---

## 🎯 Use Cases

### Voice Assistant
```python
# Continuous conversation loop
history = []

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    
    audio_file = chat_with_voice(user_input, history=history)
    
    # Play audio (platform-specific)
    # os.system(f"aplay {audio_file}")  # Linux
    # os.system(f"afplay {audio_file}")  # Mac
    
    # Update history (you'd need to transcribe or use text stream)
    history.append({"role": "user", "content": user_input})
    # history.append({"role": "assistant", "content": response_text})
```

### API Integration
```python
import requests

def get_voice_response(message, voice="tara"):
    """Get voice response from conversational AI"""
    response = requests.post(
        "http://localhost:8080/chat",
        json={"message": message, "voice": voice},
        stream=True
    )
    
    with open("response.wav", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    return "response.wav"

# Use in your application
audio_file = get_voice_response("What's the weather like?")
```

### Batch Processing
```python
# Generate voice responses for multiple messages
messages = [
    "Hello!",
    "How are you?",
    "Tell me a joke",
    "Goodbye!"
]

for i, message in enumerate(messages):
    chat_with_voice(
        message,
        voice="tara",
        save_to=f"response_{i}.wav"
    )
```

---

## 🐛 Troubleshooting

### Connection Error
```
❌ Could not connect to server. Is it running?
```

**Solution**: Make sure the server is running on port 8080:
```bash
cd /workspace/Orpheus-TTS/runpod_deployment
python server.py
```

### Timeout Error
```
❌ Request timed out after 60 seconds
```

**Solution**: Increase timeout or reduce message length:
```python
response = requests.post(
    url,
    json=payload,
    stream=True,
    timeout=120  # Increase to 120 seconds
)
```

### Slow Performance
If throughput is significantly below 42 tok/s:
1. Check GPU utilization: `nvidia-smi dmon`
2. Check server logs for errors
3. Ensure no other processes are using GPU
4. Verify SNAC_DEVICE=cuda is set

---

## 📚 Additional Resources

- **Main Documentation**: `../CONVERSATIONAL_AI_GUIDE.md`
- **Performance Analysis**: `../PERFORMANCE_ANALYSIS.md`
- **API Reference**: See server.py for endpoint details

---

## ✅ Next Steps

1. **Test the examples**: Run `chat_example.py` to verify everything works
2. **Benchmark your system**: Run `benchmark_chat.py` to measure performance
3. **Integrate into your app**: Use the example code as a starting point
4. **Customize**: Modify examples for your specific use case

Enjoy building with Orpheus Conversational AI! 🎉

