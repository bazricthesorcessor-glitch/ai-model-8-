"""
Voice module - speech to text and text to speech conversion.
Pure input/output transformation, no logic or decision making.
Stateless, optional dependency.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import subprocess
import json
from config import endpoint_of


class VoiceBackend(Enum):
    """Supported voice backends."""
    SYSTEM = "system"           # System TTS (espeak/spd-say)
    OLLAMA = "ollama"           # Ollama Whisper for STT
    GOOGLE = "google"           # Google Cloud Speech-to-Text
    AZURE = "azure"             # Azure Speech Services
    MOCK = "mock"               # Testing only


@dataclass
class SpeechSegment:
    """A speech input segment."""
    audio_bytes: bytes
    language: str = "en-US"
    sample_rate: int = 16000


@dataclass
class TextOutput:
    """Text to be converted to speech."""
    text: str
    language: str = "en-US"
    rate: float = 1.0  # speech rate (0.5 to 2.0)


class VoiceTransformer:
    """
    Pure voice transformation - no decisions, just conversion.
    Transforms speech ↔ text using configured backend.
    """

    def __init__(self, stt_backend: str = "ollama", tts_backend: str = "system"):
        """
        Initialize voice transformer.

        Args:
            stt_backend: Speech-to-text backend (ollama, google, azure, mock)
            tts_backend: Text-to-speech backend (system, google, azure, mock)
        """
        self.stt_backend = stt_backend
        self.tts_backend = tts_backend

        # Verify backends are supported
        valid_backends = {b.value for b in VoiceBackend}
        if stt_backend not in valid_backends:
            raise ValueError(f"Invalid STT backend: {stt_backend}")
        if tts_backend not in valid_backends:
            raise ValueError(f"Invalid TTS backend: {tts_backend}")

    # ========================================================================
    # SPEECH-TO-TEXT (Audio → Text)
    # ========================================================================

    def speech_to_text(
        self,
        audio_bytes: bytes,
        language: str = "en-US",
        timeout: int = 30
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Convert speech audio to text.

        Args:
            audio_bytes: Audio data (typically WAV or MP3)
            language: Language code (e.g., "en-US", "es-ES", "fr-FR")
            timeout: Request timeout in seconds

        Returns:
            (success: bool, text: str, error: Optional[str])

        Examples:
            success, text, error = transformer.speech_to_text(audio_bytes)
            if success:
                print(f"Recognized: {text}")
            else:
                print(f"Error: {error}")
        """
        if not audio_bytes:
            return False, "", "Audio data is empty"

        if self.stt_backend == "mock":
            return self._stt_mock(audio_bytes, language)
        elif self.stt_backend == "ollama":
            return self._stt_ollama(audio_bytes, language, timeout)
        elif self.stt_backend == "google":
            return self._stt_google(audio_bytes, language, timeout)
        elif self.stt_backend == "azure":
            return self._stt_azure(audio_bytes, language, timeout)
        else:
            return False, "", f"Unknown STT backend: {self.stt_backend}"

    def _stt_mock(self, audio_bytes: bytes, language: str) -> Tuple[bool, str, Optional[str]]:
        """Mock speech-to-text for testing."""
        # Simple mock: convert bytes to hex and return as text
        hex_str = audio_bytes[:50].hex()
        return True, f"Mock: audio segment ({len(audio_bytes)} bytes, {language})", None

    def _stt_ollama(
        self, audio_bytes: bytes, language: str, timeout: int
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Use Ollama Whisper for speech-to-text.
        Requires: ollama run whisper
        """
        try:
            # Write audio to temp file (Whisper needs file input)
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                temp_path = f.name

            # Call Ollama Whisper API
            # Note: Ollama's Whisper integration is through HTTP API
            import requests

            try:
                response = requests.post(
                    f"{endpoint_of('ollama')}/api/transcribe",
                    json={
                        "model": "whisper:base",
                        "language": language,
                        "file": temp_path,
                    },
                    timeout=timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    text = data.get("text", "")
                    return True, text, None
                else:
                    return False, "", f"Ollama Whisper error: {response.status_code}"

            finally:
                # Clean up temp file
                import os
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except ImportError:
            return False, "", "requests library not installed for Ollama"
        except Exception as e:
            return False, "", f"Ollama Whisper error: {str(e)}"

    def _stt_google(
        self, audio_bytes: bytes, language: str, timeout: int
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Use Google Cloud Speech-to-Text.
        Requires: google-cloud-speech library and GCP credentials
        """
        try:
            from google.cloud import speech

            client = speech.SpeechClient()
            audio = speech.RecognitionAudio(content=audio_bytes)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language,
            )

            response = client.recognize(config=config, audio=audio)

            if response.results:
                text = "".join(
                    result.alternatives[0].transcript
                    for result in response.results
                    if result.alternatives
                )
                return True, text, None
            else:
                return False, "", "No speech detected"

        except ImportError:
            return False, "", "google-cloud-speech not installed"
        except Exception as e:
            return False, "", f"Google STT error: {str(e)}"

    def _stt_azure(
        self, audio_bytes: bytes, language: str, timeout: int
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Use Azure Speech Services.
        Requires: azure-cognitiveservices-speech library and API key
        """
        try:
            import azure.cognitiveservices.speech as speechsdk
            import os

            speech_key = os.getenv("AZURE_SPEECH_KEY")
            speech_region = os.getenv("AZURE_SPEECH_REGION", "eastus")

            if not speech_key:
                return False, "", "AZURE_SPEECH_KEY environment variable not set"

            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key, region=speech_region
            )
            speech_config.speech_recognition_language = language

            audio_config = speechsdk.AudioConfig(use_default_microphone=False)
            # Note: In real implementation, would use audio from bytes
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_config
            )

            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return True, result.text, None
            else:
                return False, "", f"Azure STT failed: {result.reason}"

        except ImportError:
            return False, "", "azure-cognitiveservices-speech not installed"
        except Exception as e:
            return False, "", f"Azure STT error: {str(e)}"

    # ========================================================================
    # TEXT-TO-SPEECH (Text → Audio)
    # ========================================================================

    def text_to_speech(
        self,
        text: str,
        language: str = "en-US",
        rate: float = 1.0,
        output_file: Optional[str] = None,
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Convert text to speech audio.

        Args:
            text: Text to convert
            language: Language code (e.g., "en-US", "es-ES")
            rate: Speech rate (0.5 to 2.0, default 1.0)
            output_file: Optional file to save audio (if None, returns bytes)

        Returns:
            (success: bool, audio_bytes: Optional[bytes], error: Optional[str])

        Examples:
            success, audio, error = transformer.text_to_speech("Hello world")
            if success:
                with open("output.wav", "wb") as f:
                    f.write(audio)
            else:
                print(f"Error: {error}")
        """
        if not text or not text.strip():
            return False, None, "Text is empty"

        if rate < 0.5 or rate > 2.0:
            return False, None, f"Rate must be between 0.5 and 2.0 (got {rate})"

        if self.tts_backend == "mock":
            return self._tts_mock(text, language, rate)
        elif self.tts_backend == "system":
            return self._tts_system(text, language, rate, output_file)
        elif self.tts_backend == "google":
            return self._tts_google(text, language, rate, output_file)
        elif self.tts_backend == "azure":
            return self._tts_azure(text, language, rate, output_file)
        else:
            return False, None, f"Unknown TTS backend: {self.tts_backend}"

    def _tts_mock(
        self, text: str, language: str, rate: float
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """Mock text-to-speech for testing."""
        # Return mock audio (just the text encoded as bytes)
        audio = f"Mock audio: {text} ({language}, rate={rate})".encode()
        return True, audio, None

    def _tts_system(
        self,
        text: str,
        language: str,
        rate: float,
        output_file: Optional[str],
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Use system TTS (espeak, spd-say, etc.).
        Works on Linux/macOS, needs system TTS installed.
        """
        try:
            # Detect available system TTS
            tts_cmd = None

            # Try espeak first (Linux)
            try:
                subprocess.run(
                    ["which", "espeak"],
                    capture_output=True,
                    check=True,
                    timeout=2
                )
                tts_cmd = "espeak"
            except:
                pass

            # Try spd-say (Linux with speech-dispatcher)
            if not tts_cmd:
                try:
                    subprocess.run(
                        ["which", "spd-say"],
                        capture_output=True,
                        check=True,
                        timeout=2
                    )
                    tts_cmd = "spd-say"
                except:
                    pass

            # Try say (macOS)
            if not tts_cmd:
                try:
                    subprocess.run(
                        ["which", "say"],
                        capture_output=True,
                        check=True,
                        timeout=2
                    )
                    tts_cmd = "say"
                except:
                    pass

            if not tts_cmd:
                return False, None, "No system TTS found (install espeak or spd-say)"

            # Build command based on TTS tool
            if tts_cmd == "espeak":
                cmd = ["espeak", "-a", str(int(rate * 100)), text]
            elif tts_cmd == "spd-say":
                cmd = ["spd-say", "-r", str(int((rate - 1) * 50)), text]
            elif tts_cmd == "say":
                cmd = ["say", "-r", str(int(rate * 200)), text]
            else:
                return False, None, f"Unsupported TTS: {tts_cmd}"

            # Add output file if specified
            if output_file:
                cmd.extend(["-o", output_file])

            # Run TTS command
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                text=False
            )

            if result.returncode != 0:
                error = result.stderr.decode() if result.stderr else "Unknown error"
                return False, None, f"TTS failed: {error}"

            # If output file, read it; otherwise return stdout
            if output_file:
                try:
                    with open(output_file, "rb") as f:
                        audio = f.read()
                    return True, audio, None
                except Exception as e:
                    return False, None, f"Failed to read output file: {str(e)}"
            else:
                audio = result.stdout
                return True, audio, None

        except subprocess.TimeoutExpired:
            return False, None, "TTS command timed out"
        except Exception as e:
            return False, None, f"System TTS error: {str(e)}"

    def _tts_google(
        self,
        text: str,
        language: str,
        rate: float,
        output_file: Optional[str],
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Use Google Cloud Text-to-Speech.
        Requires: google-cloud-texttospeech library and GCP credentials
        """
        try:
            from google.cloud import texttospeech

            client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code=language, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=rate,
            )

            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            audio = response.audio_content

            if output_file:
                with open(output_file, "wb") as f:
                    f.write(audio)

            return True, audio, None

        except ImportError:
            return False, None, "google-cloud-texttospeech not installed"
        except Exception as e:
            return False, None, f"Google TTS error: {str(e)}"

    def _tts_azure(
        self,
        text: str,
        language: str,
        rate: float,
        output_file: Optional[str],
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Use Azure Speech Services.
        Requires: azure-cognitiveservices-speech library and API key
        """
        try:
            import azure.cognitiveservices.speech as speechsdk
            import os

            speech_key = os.getenv("AZURE_SPEECH_KEY")
            speech_region = os.getenv("AZURE_SPEECH_REGION", "eastus")

            if not speech_key:
                return False, None, "AZURE_SPEECH_KEY environment variable not set"

            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key, region=speech_region
            )
            speech_config.speech_synthesis_language = language

            # Output to bytes if no file specified
            if output_file:
                audio_config = speechsdk.audio.AudioOutputConfig(
                    filename=output_file
                )
            else:
                audio_config = speechsdk.audio.AudioOutputConfig(
                    use_default_speaker=False
                )

            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=audio_config
            )

            result = synthesizer.speak_text(text)

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                if output_file:
                    with open(output_file, "rb") as f:
                        audio = f.read()
                else:
                    audio = result.audio
                return True, audio, None
            else:
                return False, None, f"Azure TTS failed: {result.reason}"

        except ImportError:
            return False, None, "azure-cognitiveservices-speech not installed"
        except Exception as e:
            return False, None, f"Azure TTS error: {str(e)}"


# ============================================================================
# Convenience Functions (Stateless Helpers)
# ============================================================================

def speech_to_text(
    audio_bytes: bytes,
    language: str = "en-US",
    backend: str = "ollama",
) -> Tuple[bool, str, Optional[str]]:
    """
    Convert speech to text (convenience function).

    Args:
        audio_bytes: Audio data
        language: Language code
        backend: STT backend to use

    Returns:
        (success, text, error)
    """
    transformer = VoiceTransformer(stt_backend=backend)
    return transformer.speech_to_text(audio_bytes, language)


def text_to_speech(
    text: str,
    language: str = "en-US",
    rate: float = 1.0,
    backend: str = "system",
) -> Tuple[bool, Optional[bytes], Optional[str]]:
    """
    Convert text to speech (convenience function).

    Args:
        text: Text to convert
        language: Language code
        rate: Speech rate (0.5 to 2.0)
        backend: TTS backend to use

    Returns:
        (success, audio_bytes, error)
    """
    transformer = VoiceTransformer(tts_backend=backend)
    return transformer.text_to_speech(text, language, rate)
