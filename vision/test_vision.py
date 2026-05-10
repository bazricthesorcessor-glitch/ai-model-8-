"""
Vision module tests - screen capture and analysis.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision import VisionAnalyzer, capture_screen, extract_text, detect_elements, analyze_screen, VisionBackend, Element, ScreenData


def test_vision_analyzer_init():
    """Test 1: VisionAnalyzer initialization."""
    print("\n" + "=" * 70)
    print("TEST 1: VisionAnalyzer Initialization")
    print("=" * 70)

    # Valid backends
    analyzer = VisionAnalyzer(backend="mock")
    assert analyzer.backend == "mock"
    print(f"✓ Mock backend initialized")

    analyzer = VisionAnalyzer(backend="tesseract")
    assert analyzer.backend == "tesseract"
    print(f"✓ Tesseract backend initialized")

    # Invalid backend
    try:
        analyzer = VisionAnalyzer(backend="invalid")
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"✓ Invalid backend rejected: {e}")

    print("\n✓ TEST 1 PASSED")


def test_screen_capture_mock():
    """Test 2: Screen capture with mock backend."""
    print("\n" + "=" * 70)
    print("TEST 2: Screen Capture (Mock Backend)")
    print("=" * 70)

    analyzer = VisionAnalyzer(backend="mock")

    # Full screen capture (will fail if PIL not available, that's OK)
    success, image, error = analyzer.capture_screen()

    if success:
        assert isinstance(image, bytes), "Image should be bytes"
        assert len(image) > 0, "Image data should not be empty"
        print(f"✓ Screen capture: {len(image)} bytes")
    else:
        assert "PIL" in error or "Pillow" in error
        print(f"✓ Capture requires PIL: {error}")

    print("\n✓ TEST 2 PASSED")


def test_text_extraction_mock():
    """Test 3: Text extraction with mock backend."""
    print("\n" + "=" * 70)
    print("TEST 3: Text Extraction (Mock Backend)")
    print("=" * 70)

    analyzer = VisionAnalyzer(backend="mock")

    # Test with image bytes
    fake_image = b"fake image data"
    success, text, error = analyzer.extract_text(fake_image)

    assert success, f"OCR failed: {error}"
    assert text, "No text returned"
    assert "Mock" in text, "Mock text not found"
    print(f"✓ OCR mock: {text[:50]}...")

    # Test with empty image
    success, text, error = analyzer.extract_text(b"")
    assert not success, "Empty image should fail"
    assert error, "No error message"
    print(f"✓ Empty image rejected: {error}")

    print("\n✓ TEST 3 PASSED")


def test_element_detection_mock():
    """Test 4: Element detection with mock backend."""
    print("\n" + "=" * 70)
    print("TEST 4: Element Detection (Mock Backend)")
    print("=" * 70)

    analyzer = VisionAnalyzer(backend="mock")

    # Test element detection
    fake_image = b"fake image"
    success, elements, error = analyzer.detect_elements(fake_image)

    assert success, f"Detection failed: {error}"
    assert isinstance(elements, list), "Should return list"
    assert len(elements) > 0, "Should detect elements"
    print(f"✓ Detected {len(elements)} elements")

    # Check element structure
    element = elements[0]
    assert isinstance(element, Element), "Should be Element objects"
    assert element.type, "Element should have type"
    assert element.location, "Element should have location"
    assert 0 <= element.confidence <= 1, "Confidence should be 0-1"
    print(f"✓ Element structure valid: {element.type} at {element.location}")

    # Test with empty image
    success, elements, error = analyzer.detect_elements(b"")
    assert not success, "Empty image should fail"
    print(f"✓ Empty image rejected: {error}")

    print("\n✓ TEST 4 PASSED")


def test_convenience_functions():
    """Test 5: Convenience functions."""
    print("\n" + "=" * 70)
    print("TEST 5: Convenience Functions")
    print("=" * 70)

    # Test extract_text function
    success, text, error = extract_text(b"test image", backend="mock")
    assert success, f"OCR function failed: {error}"
    assert text, "No text returned"
    print(f"✓ extract_text() works: {text[:40]}...")

    # Test detect_elements function
    success, elements, error = detect_elements(b"test image", backend="mock")
    assert success, f"Detection function failed: {error}"
    assert isinstance(elements, list), "Should return list"
    print(f"✓ detect_elements() works: {len(elements)} elements")

    print("\n✓ TEST 5 PASSED")


def test_backend_enum():
    """Test 6: VisionBackend enum."""
    print("\n" + "=" * 70)
    print("TEST 6: VisionBackend Enum")
    print("=" * 70)

    # Check all backends exist
    backends = [b.value for b in VisionBackend]
    expected = ["mock", "tesseract", "paddle", "google", "azure", "yolo"]

    for backend in expected:
        assert backend in backends, f"Missing backend: {backend}"
        print(f"✓ Backend available: {backend}")

    print("\n✓ TEST 6 PASSED")


def test_element_structure():
    """Test 7: Element and ScreenData structure."""
    print("\n" + "=" * 70)
    print("TEST 7: Element and ScreenData Structure")
    print("=" * 70)

    # Test Element creation
    element = Element(
        type="button",
        text="Click me",
        location=(100, 200, 50, 30),
        confidence=0.95
    )

    assert element.type == "button"
    assert element.text == "Click me"
    assert element.location == (100, 200, 50, 30)
    assert element.confidence == 0.95
    print(f"✓ Element structure valid")

    # Test ScreenData creation
    screen_data = ScreenData(
        timestamp=123456.789,
        resolution=(1920, 1080),
        text="Sample text on screen",
        elements=[element],
        layout={"element_count": 1}
    )

    assert screen_data.resolution == (1920, 1080)
    assert len(screen_data.elements) == 1
    assert screen_data.text == "Sample text on screen"
    print(f"✓ ScreenData structure valid: {screen_data.resolution}")

    print("\n✓ TEST 7 PASSED")


def test_error_handling():
    """Test 8: Error handling."""
    print("\n" + "=" * 70)
    print("TEST 8: Error Handling")
    print("=" * 70)

    analyzer = VisionAnalyzer(backend="mock")

    # Empty image errors
    success, text, error = analyzer.extract_text(b"")
    assert not success and error, "Empty image error handling"
    print(f"✓ Extract text error: {error}")

    success, elements, error = analyzer.detect_elements(b"")
    assert not success and error, "Empty image error handling"
    print(f"✓ Element detection error: {error}")

    # Unsupported backend for detection
    analyzer2 = VisionAnalyzer(backend="tesseract")
    success, elements, error = analyzer2.detect_elements(b"test")
    # Tesseract doesn't support element detection
    # Should return error
    if not success:
        print(f"✓ Unsupported operation error: {error}")

    print("\n✓ TEST 8 PASSED")


def test_stateless_design():
    """Test 9: Stateless design (no state retained)."""
    print("\n" + "=" * 70)
    print("TEST 9: Stateless Design")
    print("=" * 70)

    # Create multiple analyzers
    a1 = VisionAnalyzer(backend="mock")
    a2 = VisionAnalyzer(backend="mock")

    # Run same operation on both
    success1, text1, _ = a1.extract_text(b"test1")
    success2, text2, _ = a2.extract_text(b"test1")

    # Results should be independent
    assert success1 == success2, "Results differ between instances"
    print(f"✓ Each instance is independent")

    # Test convenience functions multiple times
    for i in range(3):
        success, text, error = extract_text(b"test", backend="mock")
        assert success, f"Call {i} failed"
    print(f"✓ Convenience functions are stateless")

    print("\n✓ TEST 9 PASSED")


def test_pure_transformation():
    """Test 10: Pure transformation (no logic)."""
    print("\n" + "=" * 70)
    print("TEST 10: Pure Input/Output Transformation")
    print("=" * 70)

    analyzer = VisionAnalyzer(backend="mock")

    # No state changes
    state_before = analyzer.backend

    for i in range(5):
        analyzer.extract_text(f"image{i}".encode())
        analyzer.detect_elements(f"image{i}".encode())

    state_after = analyzer.backend
    assert state_before == state_after, "State should not change"
    print(f"✓ No state changes during operations")

    # No side effects on input
    image_input = b"test image"
    success, text, _ = analyzer.extract_text(image_input)
    assert image_input == b"test image", "Input image modified"
    print(f"✓ No side effects on input")

    # Deterministic for same input (with mock)
    image = b"test"
    _, text1, _ = analyzer.extract_text(image)
    _, text2, _ = analyzer.extract_text(image)
    assert text1 == text2, "Same input should produce same output"
    print(f"✓ Deterministic transformation")

    print("\n✓ TEST 10 PASSED")


def run_all_tests():
    """Run all vision module tests."""
    print("\n" + "=" * 70)
    print("VISION MODULE TEST SUITE")
    print("=" * 70)

    tests = [
        test_vision_analyzer_init,
        test_screen_capture_mock,
        test_text_extraction_mock,
        test_element_detection_mock,
        test_convenience_functions,
        test_backend_enum,
        test_element_structure,
        test_error_handling,
        test_stateless_design,
        test_pure_transformation,
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
