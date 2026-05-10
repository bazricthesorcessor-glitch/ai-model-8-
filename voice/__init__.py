"""
Voice module - speech to text and text to speech conversion.
Pure input/output transformation, no logic or decision making.

Two main functions:
- speech_to_text(audio_bytes) → text
- text_to_speech(text) → audio_bytes

Supports multiple backends: Ollama Whisper, Google Cloud, Azure, System TTS
"""

from .voice import (
    VoiceTransformer,
    VoiceBackend,
    SpeechSegment,
    TextOutput,
    speech_to_text,
    text_to_speech,
)

__all__ = [
    "VoiceTransformer",
    "VoiceBackend",
    "SpeechSegment",
    "TextOutput",
    "speech_to_text",
    "text_to_speech",
]
