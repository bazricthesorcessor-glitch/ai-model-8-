"""
Vision module examples - how to capture and analyze screens.
"""

from vision import VisionAnalyzer, capture_screen, extract_text, detect_elements, analyze_screen, VisionBackend


def example_1_quick_capture():
    """Example 1: Quick screen capture."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Quick Screen Capture")
    print("=" * 70)

    success, image, error = capture_screen(backend="mock")

    if success:
        print(f"✓ Captured {len(image)} bytes")
        print(f"  Image preview: {image[:50]}...")
    else:
        print(f"✗ Error: {error}")


def example_2_quick_ocr():
    """Example 2: Quick text extraction (OCR)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Quick Text Extraction (OCR)")
    print("=" * 70)

    # Simulate image data
    fake_image = b"fake image data from screen"
    success, text, error = extract_text(fake_image, backend="mock")

    if success:
        print(f"✓ Extracted text")
        print(f"  Image size: {len(fake_image)} bytes")
        print(f"  Recognized: {text}")
    else:
        print(f"✗ Error: {error}")


def example_3_analyzer_init():
    """Example 3: Initialize VisionAnalyzer."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: VisionAnalyzer Initialization")
    print("=" * 70)

    # Create analyzer with specific backend
    analyzer = VisionAnalyzer(backend="mock")
    print(f"✓ Created analyzer")
    print(f"  Backend: {analyzer.backend}")

    # Use it for text extraction
    success, text, _ = analyzer.extract_text(b"sample image")
    if success:
        print(f"  Extract result: {text[:50]}...")

    # Use it for element detection
    success, elements, _ = analyzer.detect_elements(b"sample image")
    if success:
        print(f"  Detected {len(elements)} elements")


def example_4_detect_elements():
    """Example 4: Detect UI elements."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Detect UI Elements")
    print("=" * 70)

    analyzer = VisionAnalyzer(backend="mock")

    success, elements, error = analyzer.detect_elements(b"screen data")

    if success:
        print(f"✓ Detected {len(elements)} elements")
        for i, elem in enumerate(elements, 1):
            x, y, w, h = elem.location
            print(f"  {i}. {elem.type:10} '{elem.text:20}' at ({x}, {y}) {elem.confidence:.0%}")
    else:
        print(f"✗ Error: {error}")


def example_5_region_capture():
    """Example 5: Capture specific screen region."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Capture Specific Region")
    print("=" * 70)

    regions = [
        (0, 0, 500, 300),      # Top-left
        (1000, 0, 500, 300),   # Top-right
        (500, 500, 400, 200),  # Center
    ]

    for i, region in enumerate(regions, 1):
        x, y, w, h = region
        success, image, error = capture_screen(region=region, backend="mock")

        if success:
            print(f"✓ Region {i}: ({x}, {y}, {w}x{h}) → {len(image)} bytes")
        else:
            print(f"✗ Region {i}: Error - {error}")


def example_6_analyze_full_screen():
    """Example 6: Analyze entire screen."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Analyze Full Screen")
    print("=" * 70)

    analyzer = VisionAnalyzer(backend="mock")

    success, screen_data, error = analyzer.analyze_screen()

    if success:
        print(f"✓ Screen analysis complete")
        print(f"  Resolution: {screen_data.resolution}")
        print(f"  Text length: {len(screen_data.text)} chars")
        print(f"  Elements: {len(screen_data.elements)}")
    else:
        print(f"✗ Error: {error}")


def example_7_ocr_workflow():
    """Example 7: OCR workflow (detect text from screen)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: OCR Workflow")
    print("=" * 70)

    analyzer = VisionAnalyzer(backend="mock")

    # Step 1: Capture screen (mock won't actually fail)
    success1, image, _ = analyzer.capture_screen()
    if not success1:
        print("✗ Failed to capture")
        return

    print(f"✓ Step 1: Captured {len(image)} bytes")

    # Step 2: Extract text
    success2, text, _ = analyzer.extract_text(image)
    if not success2:
        print("✗ Failed to extract text")
        return

    print(f"✓ Step 2: Extracted text ({len(text)} chars)")

    # Step 3: Detect elements
    success3, elements, _ = analyzer.detect_elements(image)
    if not success3:
        print("✗ Failed to detect elements")
        return

    print(f"✓ Step 3: Detected {len(elements)} elements")
    print(f"✓ Complete OCR workflow executed")


def example_8_backend_options():
    """Example 8: Available backends."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Available Vision Backends")
    print("=" * 70)

    backends = {
        "mock": "For testing (always works)",
        "tesseract": "Tesseract OCR (local, offline)",
        "paddle": "PaddleOCR (local, offline)",
        "google": "Google Cloud Vision (cloud, high quality)",
        "azure": "Azure Computer Vision (cloud, high quality)",
        "yolo": "YOLO object detection (local, fast)",
    }

    print("\nAvailable backends:")
    for backend, description in backends.items():
        print(f"  {backend:12} → {description}")

    # Try mock backend
    analyzer = VisionAnalyzer(backend="mock")
    success, text, error = analyzer.extract_text(b"test")

    if success:
        print(f"\n✓ Successfully used mock backend")
    else:
        print(f"\n✗ Backend unavailable: {error}")


def example_9_error_handling():
    """Example 9: Error handling."""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Error Handling")
    print("=" * 70)

    analyzer = VisionAnalyzer(backend="mock")

    # Empty image
    print("\n• Testing empty image:")
    success, text, error = analyzer.extract_text(b"")
    if not success:
        print(f"  ✓ Rejected: {error}")

    # Invalid backend
    print("\n• Testing invalid backend:")
    try:
        analyzer3 = VisionAnalyzer(backend="invalid")
        print(f"  ✗ Should have failed")
    except ValueError as e:
        print(f"  ✓ Rejected: {e}")


def example_10_integration_pattern():
    """Example 10: Integration with main system."""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Integration with Main System")
    print("=" * 70)

    print("""
In main.py, you could integrate vision like:

    from vision import analyze_screen

    # Monitor screen for state changes:
    def monitor_screen():
        success, screen_data, error = analyze_screen(backend="tesseract")

        if success:
            elements = screen_data.elements
            text = screen_data.text

            # Find specific button
            for elem in elements:
                if "OK" in elem.text:
                    click_button(elem.location)

    # Or use for validation:
    def verify_action_result(expected_text):
        success, screen_data, error = analyze_screen()

        if success:
            if expected_text in screen_data.text:
                return True  # Action succeeded

        return False
""")


def run_all_examples():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("VISION MODULE - USAGE EXAMPLES")
    print("=" * 70)

    example_1_quick_capture()
    example_2_quick_ocr()
    example_3_analyzer_init()
    example_4_detect_elements()
    example_5_region_capture()
    example_6_analyze_full_screen()
    example_7_ocr_workflow()
    example_8_backend_options()
    example_9_error_handling()
    example_10_integration_pattern()

    print("\n" + "=" * 70)
    print("✓ All examples completed")
    print("=" * 70)


if __name__ == "__main__":
    run_all_examples()
