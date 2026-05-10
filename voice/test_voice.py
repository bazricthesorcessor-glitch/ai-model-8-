"""
Voice module tests - speech to text and text to speech conversion.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import VoiceTransformer, speech_to_text, text_to_speech, VoiceBackend


def test_voice_transformer_init():
    """Test 1: VoiceTransformer initialization."""
    print("\n" + "=" * 70)
    print("TEST 1: VoiceTransformer Initialization")
    print("=" * 70)

    # Valid backends
    transformer = VoiceTransformer(stt_backend="mock", tts_backend="mock")
    assert transformer.stt_backend == "mock"
    assert transformer.tts_backend == "mock"
    print(f"✓ Mock backend initialized")

    transformer = VoiceTransformer(stt_backend="ollama", tts_backend="system")
    assert transformer.stt_backend == "ollama"
    assert transformer.tts_backend == "system"
    print(f"✓ Ollama + System backend initialized")

    # Invalid backend
    try:
        transformer = VoiceTransformer(stt_backend="invalid")
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"✓ Invalid backend rejected: {e}")

    print("\n✓ TEST 1 PASSED")


def test_speech_to_text_mock():
    """Test 2: Speech-to-text with mock backend."""
    print("\n" + "=" * 70)
    print("TEST 2: Speech-to-Text (Mock Backend)")
    print("=" * 70)

    transformer = VoiceTransformer(stt_backend="mock")

    # Test with audio bytes
    audio = b"fake audio data"
    success, text, error = transformer.speech_to_text(audio)

    assert success, f"STT failed: {error}"
    assert text, "No text returned"
    assert "Mock" in text, "Mock text not found"
    print(f"✓ STT mock: {text[:50]}...")

    # Test with empty audio
    success, text, error = transformer.speech_to_text(b"")
    assert not success, "Empty audio should fail"
    assert error, "No error message"
    print(f"✓ Empty audio rejected: {error}")

    # Test with different language
    success, text, error = transformer.speech_to_text(audio, language="es-ES")
    assert success, f"STT with language failed: {error}"
    assert "es-ES" in text, "Language not in mock response"
    print(f"✓ Language parameter passed: {text[:50]}...")

    print("\n✓ TEST 2 PASSED")


def test_text_to_speech_mock():
    """Test 3: Text-to-speech with mock backend."""
    print("\n" + "=" * 70)
    print("TEST 3: Text-to-Speech (Mock Backend)")
    print("=" * 70)

    transformer = VoiceTransformer(tts_backend="mock")

    # Test with text
    success, audio, error = transformer.text_to_speech("Hello world")

    assert success, f"TTS failed: {error}"
    assert audio, "No audio returned"
    assert isinstance(audio, bytes), "Audio should be bytes"
    print(f"✓ TTS mock: {len(audio)} bytes")

    # Test with empty text
    success, audio, error = transformer.text_to_speech("")
    assert not success, "Empty text should fail"
    assert error, "No error message"
    print(f"✓ Empty text rejected: {error}")

    # Test with different rate
    success, audio, error = transformer.text_to_speech("Hello", rate=0.8)
    assert success, f"TTS with rate failed: {error}"
    assert "0.8" in audio.decode(), "Rate not in mock response"
    print(f"✓ Rate parameter passed")

    # Test with invalid rate
    success, audio, error = transformer.text_to_speech("Hello", rate=3.0)
    assert not success, "Invalid rate should fail"
    assert error, "No error message"
    print(f"✓ Invalid rate rejected: {error}")

    print("\n✓ TEST 3 PASSED")


def test_convenience_functions():
    """Test 4: Convenience functions."""
    print("\n" + "=" * 70)
    print("TEST 4: Convenience Functions")
    print("=" * 70)

    # Test STT convenience function
    audio = b"test audio"
    success, text, error = speech_to_text(audio, backend="mock")
    assert success, f"STT function failed: {error}"
    assert text, "No text returned"
    print(f"✓ speech_to_text() works: {text[:40]}...")

    # Test TTS convenience function
    success, audio, error = text_to_speech("Test", backend="mock")
    assert success, f"TTS function failed: {error}"
    assert audio, "No audio returned"
    print(f"✓ text_to_speech() works: {len(audio)} bytes")

    print("\n✓ TEST 4 PASSED")


def test_backend_enum():
    """Test 5: VoiceBackend enum."""
    print("\n" + "=" * 70)
    print("TEST 5: VoiceBackend Enum")
    print("=" * 70)

    # Check all backends exist
    backends = [b.value for b in VoiceBackend]
    expected = ["system", "ollama", "google", "azure", "mock"]

    for backend in expected:
        assert backend in backends, f"Missing backend: {backend}"
        print(f"✓ Backend available: {backend}")

    print("\n✓ TEST 5 PASSED")


def test_language_codes():
    """Test 6: Language code handling."""
    print("\n" + "=" * 70)
    print("TEST 6: Language Code Handling")
    print("=" * 70)

    transformer = VoiceTransformer(stt_backend="mock", tts_backend="mock")

    languages = ["en-US", "es-ES", "fr-FR", "de-DE", "ja-JP"]

    for lang in languages:
        # STT
        success, text, error = transformer.speech_to_text(b"test", language=lang)
        assert success, f"STT with {lang} failed"
        assert lang in text, f"Language not in response: {text}"
        print(f"✓ STT language {lang} works")

        # TTS
        success, audio, error = transformer.text_to_speech("test", language=lang)
        assert success, f"TTS with {lang} failed"
        assert lang in audio.decode(), f"Language not in response"
        print(f"✓ TTS language {lang} works")

    print("\n✓ TEST 6 PASSED")


def test_stateless_design():
    """Test 7: Stateless design (no state retained)."""
    print("\n" + "=" * 70)
    print("TEST 7: Stateless Design")
    print("=" * 70)

    # Create multiple transformers with different backends
    t1 = VoiceTransformer(stt_backend="mock")
    t2 = VoiceTransformer(stt_backend="mock")

    # Run same operation on both
    success1, text1, _ = t1.speech_to_text(b"audio1")
    success2, text2, _ = t2.speech_to_text(b"audio1")

    # Results should be independent
    assert success1 == success2, "Results differ between instances"
    print(f"✓ Each instance is independent")

    # Test convenience functions multiple times
    for i in range(3):
        success, text, error = speech_to_text(b"test", backend="mock")
        assert success, f"Call {i} failed"
    print(f"✓ Convenience functions are stateless")

    print("\n✓ TEST 7 PASSED")


def test_error_handling():
    """Test 8: Error handling."""
    print("\n" + "=" * 70)
    print("TEST 8: Error Handling")
    print("=" * 70)

    transformer = VoiceTransformer(stt_backend="mock", tts_backend="mock")

    # STT errors
    success, text, error = transformer.speech_to_text(b"")
    assert not success and error, "Empty audio error handling"
    print(f"✓ STT error handling: {error}")

    # TTS errors
    success, audio, error = transformer.text_to_speech("")
    assert not success and error, "Empty text error handling"
    print(f"✓ TTS error handling: {error}")

    # Invalid rate
    success, audio, error = transformer.text_to_speech("test", rate=5.0)
    assert not success and error, "Invalid rate error handling"
    print(f"✓ Invalid rate error: {error}")

    # Invalid language (should still work in mock)
    success, text, error = transformer.speech_to_text(b"test", language="xx-XX")
    assert success, "Mock should accept any language"
    print(f"✓ Language validation deferred to backend")

    print("\n✓ TEST 8 PASSED")


def test_output_types():
    """Test 9: Output types."""
    print("\n" + "=" * 70)
    print("TEST 9: Output Types")
    print("=" * 70)

    transformer = VoiceTransformer(stt_backend="mock", tts_backend="mock")

    # STT returns tuple of (bool, str, Optional[str])
    result = transformer.speech_to_text(b"test")
    assert isinstance(result, tuple), "STT should return tuple"
    assert len(result) == 3, "STT tuple should have 3 elements"
    success, text, error = result
    assert isinstance(success, bool), "Success should be bool"
    assert isinstance(text, str), "Text should be str"
    assert error is None or isinstance(error, str), "Error should be Optional[str]"
    print(f"✓ STT returns (bool, str, Optional[str])")

    # TTS returns tuple of (bool, Optional[bytes], Optional[str])
    result = transformer.text_to_speech("test")
    assert isinstance(result, tuple), "TTS should return tuple"
    assert len(result) == 3, "TTS tuple should have 3 elements"
    success, audio, error = result
    assert isinstance(success, bool), "Success should be bool"
    assert audio is None or isinstance(audio, bytes), "Audio should be Optional[bytes]"
    assert error is None or isinstance(error, str), "Error should be Optional[str]"
    print(f"✓ TTS returns (bool, Optional[bytes], Optional[str])")

    print("\n✓ TEST 9 PASSED")


def test_input_output_only():
    """Test 10: Pure input/output transformation (no logic)."""
    print("\n" + "=" * 70)
    print("TEST 10: Pure Input/Output Transformation")
    print("=" * 70)

    transformer = VoiceTransformer(stt_backend="mock", tts_backend="mock")

    # No state changes
    state_before = (transformer.stt_backend, transformer.tts_backend)

    for i in range(5):
        transformer.speech_to_text(f"audio{i}".encode())
        transformer.text_to_speech(f"text{i}")

    state_after = (transformer.stt_backend, transformer.tts_backend)
    assert state_before == state_after, "State should not change"
    print(f"✓ No state changes during operations")

    # No side effects
    audio_input = b"test audio"
    success, text, _ = transformer.speech_to_text(audio_input)
    assert audio_input == b"test audio", "Input audio modified"
    print(f"✓ No side effects on input")

    # Deterministic for same input (with mock)
    text_input = "test text"
    _, audio1, _ = transformer.text_to_speech(text_input)
    _, audio2, _ = transformer.text_to_speech(text_input)
    assert audio1 == audio2, "Same input should produce same output"
    print(f"✓ Deterministic transformation")

    print("\n✓ TEST 10 PASSED")


def run_all_tests():
    """Run all voice module tests."""
    print("\n" + "=" * 70)
    print("VOICE MODULE TEST SUITE")
    print("=" * 70)

    tests = [
        test_voice_transformer_init,
        test_speech_to_text_mock,
        test_text_to_speech_mock,
        test_convenience_functions,
        test_backend_enum,
        test_language_codes,
        test_stateless_design,
        test_error_handling,
        test_output_types,
        test_input_output_only,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
