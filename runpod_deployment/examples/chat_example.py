#!/usr/bin/env python3
"""
Example: Conversational AI with Voice Response
Demonstrates how to use the /chat endpoint for voice conversations
"""

import requests
import json
import time
from pathlib import Path

# Server configuration
SERVER_URL = "http://localhost:8080"

def chat_with_voice(message, voice="tara", history=None, save_to=None):
    """
    Send a message to the conversational AI and get voice response
    
    Args:
        message: User's message
        voice: Voice name (tara, zoe, zac, jess, leo, mia, julia, leah)
        history: Conversation history (list of {role, content} dicts)
        save_to: Path to save audio file (optional)
    
    Returns:
        Path to saved audio file
    """
    if history is None:
        history = []
    
    print(f"\n{'='*70}")
    print(f"User: {message}")
    print(f"Voice: {voice}")
    print(f"{'='*70}")
    
    # Prepare request
    payload = {
        "message": message,
        "voice": voice,
        "history": history
    }
    
    # Send request
    print("Sending request to server...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{SERVER_URL}/chat",
            json=payload,
            stream=True,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Error: Server returned status {response.status_code}")
            print(response.text)
            return None
        
        # Save audio to file
        if save_to is None:
            save_to = f"response_{int(time.time())}.wav"
        
        save_path = Path(save_to)
        
        print(f"Receiving audio stream...")
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        elapsed = time.time() - start_time
        file_size = save_path.stat().st_size / 1024  # KB
        
        print(f"✅ Response received in {elapsed:.2f}s")
        print(f"✅ Audio saved to: {save_path} ({file_size:.1f} KB)")
        print(f"{'='*70}\n")
        
        return str(save_path)
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def chat_with_text_stream(message, history=None):
    """
    Get text-only response (for debugging/testing)
    
    Args:
        message: User's message
        history: Conversation history
    
    Returns:
        Generated text response
    """
    if history is None:
        history = []
    
    payload = {
        "message": message,
        "history": history,
        "stream_text": True
    }
    
    print(f"\nUser: {message}")
    print("Assistant: ", end="", flush=True)
    
    try:
        response = requests.post(
            f"{SERVER_URL}/chat",
            json=payload,
            stream=True,
            timeout=60
        )
        
        full_text = ""
        for chunk in response.iter_content(chunk_size=1):
            if chunk:
                text = chunk.decode('utf-8')
                print(text, end="", flush=True)
                full_text += text
        
        print("\n")
        return full_text
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def multi_turn_conversation():
    """
    Example: Multi-turn conversation with history
    """
    print("\n" + "="*70)
    print("MULTI-TURN CONVERSATION EXAMPLE")
    print("="*70)
    
    history = []
    voice = "tara"
    
    # Turn 1
    message1 = "Hello! What's your name?"
    audio1 = chat_with_voice(message1, voice=voice, history=history, save_to="turn1.wav")
    
    # Simulate assistant response (in real app, you'd transcribe the audio or use text stream)
    assistant_response1 = "Hello! I'm an AI assistant. I don't have a personal name, but you can call me Assistant. How can I help you today?"
    history.append({"role": "user", "content": message1})
    history.append({"role": "assistant", "content": assistant_response1})
    
    # Turn 2
    message2 = "Can you tell me a fun fact about space?"
    audio2 = chat_with_voice(message2, voice=voice, history=history, save_to="turn2.wav")
    
    print("✅ Multi-turn conversation complete!")
    print(f"   - Turn 1 audio: turn1.wav")
    print(f"   - Turn 2 audio: turn2.wav")

def test_different_voices():
    """
    Example: Test different voices
    """
    print("\n" + "="*70)
    print("TESTING DIFFERENT VOICES")
    print("="*70)
    
    message = "Hello! This is a test of the voice synthesis system."
    voices = ["tara", "zoe", "zac", "jess", "leo", "mia", "julia", "leah"]
    
    for voice in voices:
        audio_file = chat_with_voice(
            message,
            voice=voice,
            save_to=f"voice_{voice}.wav"
        )
        
        if audio_file:
            print(f"✅ {voice}: {audio_file}")
        else:
            print(f"❌ {voice}: Failed")
        
        time.sleep(1)  # Brief pause between requests
    
    print("\n✅ All voices tested!")
    print("   Listen to the generated files to compare voices.")

def quick_test():
    """
    Quick test of the chat endpoint
    """
    print("\n" + "="*70)
    print("QUICK TEST")
    print("="*70)
    
    # Simple question
    chat_with_voice(
        "What is 2 plus 2?",
        voice="tara",
        save_to="quick_test.wav"
    )

def main():
    """
    Main function - run examples
    """
    print("\n" + "="*70)
    print("ORPHEUS CONVERSATIONAL AI - EXAMPLES")
    print("="*70)
    print("\nAvailable examples:")
    print("1. Quick test")
    print("2. Multi-turn conversation")
    print("3. Test different voices")
    print("4. Text-only stream (debugging)")
    print("5. Custom message")
    print("0. Exit")
    
    while True:
        choice = input("\nSelect example (0-5): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            quick_test()
        elif choice == "2":
            multi_turn_conversation()
        elif choice == "3":
            test_different_voices()
        elif choice == "4":
            message = input("Enter message: ")
            chat_with_text_stream(message)
        elif choice == "5":
            message = input("Enter message: ")
            voice = input("Enter voice (default: tara): ").strip() or "tara"
            filename = input("Save to (default: response.wav): ").strip() or "response.wav"
            chat_with_voice(message, voice=voice, save_to=filename)
        else:
            print("Invalid choice. Please select 0-5.")

if __name__ == "__main__":
    main()

