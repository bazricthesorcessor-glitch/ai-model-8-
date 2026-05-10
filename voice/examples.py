"""
Voice module examples - how to use speech-to-text and text-to-speech.
"""

from voice import VoiceTransformer, speech_to_text, text_to_speech, VoiceBackend


def example_1_quick_tts():
    """Example 1: Quick text-to-speech."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Quick Text-to-Speech")
    print("=" * 70)

    text = "Hello world! This is a text to speech example."
    success, audio, error = text_to_speech(text, backend="mock")

    if success:
        print(f"✓ Generated {len(audio)} bytes of audio")
        print(f"  Text: {text}")
        print(f"  Audio preview: {audio[:50]}...")
    else:
        print(f"✗ Error: {error}")


def example_2_quick_stt():
    """Example 2: Quick speech-to-text."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Quick Speech-to-Text")
    print("=" * 70)

    # Simulate audio data
    fake_audio = b"fake audio data from microphone"
    success, text, error = speech_to_text(fake_audio, backend="mock")

    if success:
        print(f"✓ Recognized speech")
        print(f"  Audio size: {len(fake_audio)} bytes")
        print(f"  Recognized: {text}")
    else:
        print(f"✗ Error: {error}")


def example_3_transformer_init():
    """Example 3: Initialize VoiceTransformer."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: VoiceTransformer Initialization")
    print("=" * 70)

    # Create transformer with specific backends
    transformer = VoiceTransformer(
        stt_backend="mock",
        tts_backend="mock"
    )
    print(f"✓ Created transformer")
    print(f"  STT backend: {transformer.stt_backend}")
    print(f"  TTS backend: {transformer.tts_backend}")

    # Use it
    success, text, _ = transformer.speech_to_text(b"audio")
    print(f"  STT result: {text[:50]}...")

    success, audio, _ = transformer.text_to_speech("hello")
    print(f"  TTS result: {len(audio)} bytes")


def example_4_multiple_languages():
    """Example 4: Multiple language support."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Multiple Languages")
    print("=" * 70)

    languages = {
        "en-US": "Hello",
        "es-ES": "Hola",
        "fr-FR": "Bonjour",
        "de-DE": "Hallo",
        "ja-JP": "こんにちは",
    }

    for lang_code, greeting in languages.items():
        success, audio, error = text_to_speech(
            greeting,
            language=lang_code,
            backend="mock"
        )
        if success:
            print(f"✓ {lang_code:10} → {greeting:15} ({len(audio)} bytes)")
        else:
            print(f"✗ {lang_code:10} → Error: {error}")


def example_5_adjust_rate():
    """Example 5: Adjust speech rate."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Adjust Speech Rate")
    print("=" * 70)

    text = "This is a test message"
    rates = [0.5, 0.75, 1.0, 1.25, 1.5]

    for rate in rates:
        success, audio, error = text_to_speech(
            text,
            rate=rate,
            backend="mock"
        )
        if success:
            speed_label = "slow" if rate < 1.0 else ("normal" if rate == 1.0 else "fast")
            print(f"✓ Rate {rate:.2f} ({speed_label:6}) → {len(audio)} bytes")
        else:
            print(f"✗ Rate {rate:.2f} → Error: {error}")


def example_6_error_handling():
    """Example 6: Error handling."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Error Handling")
    print("=" * 70)

    transformer = VoiceTransformer(stt_backend="mock", tts_backend="mock")

    # Empty audio
    print("\n• Testing empty audio:")
    success, text, error = transformer.speech_to_text(b"")
    if not success:
        print(f"  ✓ Rejected: {error}")

    # Empty text
    print("\n• Testing empty text:")
    success, audio, error = transformer.text_to_speech("")
    if not success:
        print(f"  ✓ Rejected: {error}")

    # Invalid rate (too high)
    print("\n• Testing invalid rate (3.0):")
    success, audio, error = transformer.text_to_speech("test", rate=3.0)
    if not success:
        print(f"  ✓ Rejected: {error}")

    # Invalid rate (too low)
    print("\n• Testing invalid rate (0.1):")
    success, audio, error = transformer.text_to_speech("test", rate=0.1)
    if not success:
        print(f"  ✓ Rejected: {error}")


def example_7_chain_stt_tts():
    """Example 7: Chain STT and TTS (speech passthrough)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Chain STT → TTS (Speech Passthrough)")
    print("=" * 70)

    transformer = VoiceTransformer(stt_backend="mock", tts_backend="mock")

    # Simulate audio input
    input_audio = b"fake audio from microphone"
    print(f"1. Input audio: {len(input_audio)} bytes")

    # Convert to text
    success1, text, _ = transformer.speech_to_text(input_audio)
    if success1:
        print(f"2. Recognized: {text}")

        # Convert back to speech
        success2, output_audio, _ = transformer.text_to_speech(text)
        if success2:
            print(f"3. Output audio: {len(output_audio)} bytes")
            print(f"✓ Complete speech passthrough cycle")
        else:
            print(f"✗ TTS failed")
    else:
        print(f"✗ STT failed")


def example_8_backend_selection():
    """Example 8: Choose backend based on availability."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Backend Selection")
    print("=" * 70)

    backends = {
        "mock": "For testing (always works)",
        "system": "System TTS (espeak, spd-say, say)",
        "ollama": "Ollama Whisper (local, self-hosted)",
        "google": "Google Cloud Speech (high quality, cloud)",
        "azure": "Azure Speech Services (high quality, cloud)",
    }

    print("\nAvailable TTS backends:")
    for backend, description in backends.items():
        print(f"  {backend:10} → {description}")

    # Try system backend (will use mock if not available)
    transformer = VoiceTransformer(stt_backend="mock", tts_backend="mock")
    success, audio, error = transformer.text_to_speech("System TTS test")

    if success:
        print(f"\n✓ Successfully used TTS backend: {transformer.tts_backend}")
    else:
        print(f"\n✗ Backend unavailable: {error}")


def example_9_stateless_design():
    """Example 9: Stateless design (independent operations)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Stateless Design")
    print("=" * 70)

    transformer = VoiceTransformer(stt_backend="mock", tts_backend="mock")

    # Multiple independent operations
    operations = [
        ("speech_to_text", b"audio1", "en-US"),
        ("speech_to_text", b"audio2", "es-ES"),
        ("text_to_speech", "Hello", "en-US"),
        ("text_to_speech", "Hola", "es-ES"),
    ]

    for i, (op, input_data, lang) in enumerate(operations, 1):
        if op == "speech_to_text":
            success, result, error = transformer.speech_to_text(input_data, language=lang)
            result_str = f"{len(result)} chars" if success else f"Error: {error}"
        else:
            success, result, error = transformer.text_to_speech(input_data, language=lang)
            result_str = f"{len(result)} bytes" if success else f"Error: {error}"

        status = "✓" if success else "✗"
        print(f"{status} Operation {i}: {op} ({lang}) → {result_str}")

    print(f"\n✓ All operations independent, no state retained")


def example_10_integration_pattern():
    """Example 10: Integration with main system."""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Integration with Main System")
    print("=" * 70)

    print("""
In main.py, you could integrate voice like:

    from voice import text_to_speech

    # In interactive mode:
    def process_user_input(user_input):
        # ... existing processing ...

        # Add voice output
        success, audio, error = text_to_speech(
            result_text,
            backend="system"  # Use system TTS
        )

        if success:
            # Play audio (would need audio playback library)
            play_audio(audio)

        return result


Or with voice input:

    from voice import speech_to_text

    # Instead of text input():
    # Listen for speech, convert to text
    user_input, error = speech_to_text(
        capture_audio(),
        backend="ollama"  # Use Ollama Whisper
    )

    # Process text normally
    process_user_input(user_input)
""")


def run_all_examples():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("VOICE MODULE - USAGE EXAMPLES")
    print("=" * 70)

    example_1_quick_tts()
    example_2_quick_stt()
    example_3_transformer_init()
    example_4_multiple_languages()
    example_5_adjust_rate()
    example_6_error_handling()
    example_7_chain_stt_tts()
    example_8_backend_selection()
    example_9_stateless_design()
    example_10_integration_pattern()

    print("\n" + "=" * 70)
    print("✓ All examples completed")
    print("=" * 70)


if __name__ == "__main__":
    run_all_examples()
