#!/usr/bin/env python3
"""
Voice input wrapper for Hyprland AI Agent
Supports both keyboard and voice (STT) input
"""

import subprocess
import sys
import os

try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
    import json
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    print("⚠️  Vosk not installed. Voice input disabled. Install: pip install vosk pyaudio")


class VoiceInput:
    """Handle speech-to-text input"""

    def __init__(self):
        if not VOSK_AVAILABLE:
            raise RuntimeError("Vosk dependencies not installed")

        # Load vosk model
        model_path = os.path.expanduser("~/.local/share/vosk/models/en-us")
        if not os.path.exists(model_path):
            print("Downloading Vosk model...")
            model_path = "en-us"

        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model, 16000)

    def listen(self) -> str:
        """Listen for voice input and return text"""
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=16000,
                       input=True, frames_per_buffer=4096)

        print("🎤 Listening...")

        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if len(data) == 0:
                break

            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())
                if 'result' in result and result['result']:
                    text = ' '.join([r['conf'] for r in result['result']])
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return text

        stream.stop_stream()
        stream.close()
        p.terminate()
        return ""


def main():
    """Voice input interface"""
    if not VOSK_AVAILABLE:
        print("Voice input requires: pip install vosk pyaudio")
        sys.exit(1)

    voice = VoiceInput()

    print("🎤 Voice Input Mode")
    print("Press Ctrl+C to exit")

    while True:
        try:
            text = voice.listen()
            if text:
                print(f"You said: {text}")
                print("Sending to agent...")
                # Send to agent via socket or subprocess
        except KeyboardInterrupt:
            print("\nExiting voice mode...")
            break


if __name__ == "__main__":
    main()
