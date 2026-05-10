"""
Vision module - screen capture and analysis.
Pure perception/transformation, no logic or decision making.
Stateless, optional dependency.
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import subprocess
import json
import time


class VisionBackend(Enum):
    """Supported vision backends."""
    MOCK = "mock"               # Testing only
    TESSERACT = "tesseract"     # Local OCR (tesseract)
    PADDLE = "paddle"           # PaddleOCR (local)
    GOOGLE = "google"           # Google Cloud Vision
    AZURE = "azure"             # Azure Computer Vision
    YOLO = "yolo"               # YOLO object detection


@dataclass
class Element:
    """Detected screen element."""
    type: str                   # "button", "text", "input", "image", "icon"
    text: str                   # extracted text or label
    location: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float = 1.0     # confidence score (0.0-1.0)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScreenData:
    """Structured screen analysis result."""
    timestamp: float            # when captured
    resolution: Tuple[int, int]  # (width, height)
    text: str                   # all extracted text
    elements: List[Element]     # detected elements
    layout: Dict[str, Any]      # spatial relationships
    background_color: Optional[str] = None
    font_info: Optional[Dict] = None


class VisionAnalyzer:
    """
    Pure screen perception - no decisions, just analysis.
    Transforms image ↔ structured data using configured backend.
    """

    def __init__(self, backend: str = "mock"):
        """
        Initialize vision analyzer.

        Args:
            backend: Vision backend (mock, tesseract, paddle, google, azure, yolo)
        """
        self.backend = backend

        # Verify backend is supported
        valid_backends = {b.value for b in VisionBackend}
        if backend not in valid_backends:
            raise ValueError(f"Invalid vision backend: {backend}")

    # ========================================================================
    # SCREEN CAPTURE
    # ========================================================================

    def capture_screen(
        self,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Capture screen or region.

        Args:
            region: Optional region (x, y, width, height) to capture.
                   If None, captures full screen.

        Returns:
            (success: bool, image_bytes: Optional[bytes], error: Optional[str])
        """
        try:
            from PIL import ImageGrab

            if region:
                x, y, w, h = region
                bbox = (x, y, x + w, y + h)
                image = ImageGrab.grab(bbox=bbox)
            else:
                image = ImageGrab.grab()

            # Convert to bytes
            import io
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()

            return True, image_bytes, None

        except ImportError:
            return False, None, "Pillow (PIL) library not installed"
        except Exception as e:
            return False, None, f"Screen capture error: {str(e)}"

    # ========================================================================
    # TEXT EXTRACTION (OCR)
    # ========================================================================

    def extract_text(
        self,
        image_bytes: bytes
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from image using OCR.

        Args:
            image_bytes: Image data (PNG, JPG, etc.)

        Returns:
            (success: bool, text: str, error: Optional[str])
        """
        if not image_bytes:
            return False, "", "Image data is empty"

        if self.backend == "mock":
            return self._ocr_mock(image_bytes)
        elif self.backend == "tesseract":
            return self._ocr_tesseract(image_bytes)
        elif self.backend == "paddle":
            return self._ocr_paddle(image_bytes)
        elif self.backend == "google":
            return self._ocr_google(image_bytes)
        elif self.backend == "azure":
            return self._ocr_azure(image_bytes)
        else:
            return False, "", f"Unknown OCR backend: {self.backend}"

    def _ocr_mock(self, image_bytes: bytes) -> Tuple[bool, str, Optional[str]]:
        """Mock OCR for testing."""
        hex_preview = image_bytes[:50].hex()
        return True, f"Mock OCR: extracted text from image ({len(image_bytes)} bytes, preview: {hex_preview})", None

    def _ocr_tesseract(
        self, image_bytes: bytes
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Use Tesseract OCR.
        Requires: tesseract-ocr installed, pytesseract library
        """
        try:
            import pytesseract
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)

            if not text or not text.strip():
                return False, "", "No text detected in image"

            return True, text.strip(), None

        except ImportError:
            return False, "", "pytesseract or Tesseract not installed"
        except Exception as e:
            return False, "", f"Tesseract OCR error: {str(e)}"

    def _ocr_paddle(
        self, image_bytes: bytes
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Use PaddleOCR (local, no dependencies needed).
        Requires: paddleocr library
        """
        try:
            from paddleocr import PaddleOCR
            from PIL import Image
            import io

            ocr = PaddleOCR(use_angle_cls=True, lang='en')
            image = Image.open(io.BytesIO(image_bytes))

            # Save temporarily for PaddleOCR
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                image.save(f.name)
                temp_path = f.name

            try:
                result = ocr.ocr(temp_path, cls=True)
                texts = [line[0][1] for line in result[0]] if result else []
                text = " ".join(texts)

                if not text or not text.strip():
                    return False, "", "No text detected in image"

                return True, text.strip(), None

            finally:
                import os
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except ImportError:
            return False, "", "paddleocr library not installed"
        except Exception as e:
            return False, "", f"PaddleOCR error: {str(e)}"

    def _ocr_google(self, image_bytes: bytes) -> Tuple[bool, str, Optional[str]]:
        """
        Use Google Cloud Vision OCR.
        Requires: google-cloud-vision library and GCP credentials
        """
        try:
            from google.cloud import vision

            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=image_bytes)
            response = client.text_detection(image=image)

            if response.text_annotations:
                text = response.text_annotations[0].description
                return True, text, None
            else:
                return False, "", "No text detected in image"

        except ImportError:
            return False, "", "google-cloud-vision not installed"
        except Exception as e:
            return False, "", f"Google Vision OCR error: {str(e)}"

    def _ocr_azure(self, image_bytes: bytes) -> Tuple[bool, str, Optional[str]]:
        """
        Use Azure Computer Vision OCR.
        Requires: azure-cognitiveservices-vision-computervision library and API key
        """
        try:
            from azure.cognitiveservices.vision.computervision import ComputerVisionClient
            from msrest.authentication import CognitiveServicesCredentials
            import os

            api_key = os.getenv("AZURE_VISION_KEY")
            endpoint = os.getenv("AZURE_VISION_ENDPOINT", "https://eastus.api.cognitive.microsoft.com/")

            if not api_key:
                return False, "", "AZURE_VISION_KEY environment variable not set"

            client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(api_key))
            results = client.read_in_stream(image_bytes, raw=True)

            text_results = []
            for page in results:
                for line in page.get("lines", []):
                    text_results.append(line.get("text", ""))

            text = " ".join(text_results)
            if not text or not text.strip():
                return False, "", "No text detected in image"

            return True, text.strip(), None

        except ImportError:
            return False, "", "azure-cognitiveservices-vision-computervision not installed"
        except Exception as e:
            return False, "", f"Azure Vision OCR error: {str(e)}"

    # ========================================================================
    # ELEMENT DETECTION
    # ========================================================================

    def detect_elements(
        self,
        image_bytes: bytes
    ) -> Tuple[bool, List[Element], Optional[str]]:
        """
        Detect UI elements (buttons, text fields, etc.) in image.

        Args:
            image_bytes: Image data

        Returns:
            (success: bool, elements: List[Element], error: Optional[str])
        """
        if not image_bytes:
            return False, [], "Image data is empty"

        if self.backend == "mock":
            return self._detect_mock(image_bytes)
        elif self.backend == "yolo":
            return self._detect_yolo(image_bytes)
        elif self.backend == "google":
            return self._detect_google(image_bytes)
        else:
            # Other backends don't support element detection
            return False, [], f"Element detection not supported for backend: {self.backend}"

    def _detect_mock(self, image_bytes: bytes) -> Tuple[bool, List[Element], Optional[str]]:
        """Mock element detection for testing."""
        elements = [
            Element(
                type="button",
                text="OK",
                location=(100, 100, 50, 30),
                confidence=0.95
            ),
            Element(
                type="text",
                text="Sample Dialog",
                location=(150, 50, 200, 30),
                confidence=0.99
            ),
            Element(
                type="input",
                text="Type here...",
                location=(100, 150, 200, 30),
                confidence=0.85
            ),
        ]
        return True, elements, None

    def _detect_yolo(self, image_bytes: bytes) -> Tuple[bool, List[Element], Optional[str]]:
        """
        Use YOLO for object detection.
        Requires: ultralytics library
        """
        try:
            from ultralytics import YOLO
            from PIL import Image
            import io

            model = YOLO("yolov8n.pt")
            image = Image.open(io.BytesIO(image_bytes))
            results = model(image)

            elements = []
            for result in results:
                for box in result.boxes:
                    x, y, w, h = box.xywh[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]

                    element = Element(
                        type=class_name,
                        text=class_name,
                        location=(int(x), int(y), int(w), int(h)),
                        confidence=confidence
                    )
                    elements.append(element)

            return True, elements, None

        except ImportError:
            return False, [], "ultralytics library not installed"
        except Exception as e:
            return False, [], f"YOLO detection error: {str(e)}"

    def _detect_google(self, image_bytes: bytes) -> Tuple[bool, List[Element], Optional[str]]:
        """
        Use Google Cloud Vision for element detection.
        Requires: google-cloud-vision library
        """
        try:
            from google.cloud import vision

            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=image_bytes)
            response = client.label_detection(image=image)

            elements = []
            for label in response.label_annotations:
                element = Element(
                    type="detected_object",
                    text=label.description,
                    location=(0, 0, 100, 100),  # Placeholder
                    confidence=label.score
                )
                elements.append(element)

            return True, elements, None

        except ImportError:
            return False, [], "google-cloud-vision not installed"
        except Exception as e:
            return False, [], f"Google Vision detection error: {str(e)}"

    # ========================================================================
    # FULL SCREEN ANALYSIS
    # ========================================================================

    def analyze_screen(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        extract_text_flag: bool = True,
        detect_elements_flag: bool = True,
    ) -> Tuple[bool, Optional[ScreenData], Optional[str]]:
        """
        Capture and analyze screen.

        Args:
            region: Optional region (x, y, width, height) to analyze
            extract_text_flag: Whether to extract text
            detect_elements_flag: Whether to detect elements

        Returns:
            (success: bool, screen_data: Optional[ScreenData], error: Optional[str])
        """
        # Capture screen
        success, image_bytes, error = self.capture_screen(region)
        if not success:
            return False, None, error

        # Get screen resolution
        try:
            from PIL import ImageGrab
            if region:
                x, y, w, h = region
                resolution = (w, h)
            else:
                screen = ImageGrab.grab()
                resolution = screen.size
        except:
            resolution = (1920, 1080)  # Default fallback

        # Extract text if requested
        text = ""
        if extract_text_flag:
            success_text, text, _ = self.extract_text(image_bytes)
            if not success_text:
                text = ""

        # Detect elements if requested
        elements = []
        if detect_elements_flag:
            success_elements, elements, _ = self.detect_elements(image_bytes)
            if not success_elements:
                elements = []

        # Build screen data
        screen_data = ScreenData(
            timestamp=time.time(),
            resolution=resolution,
            text=text,
            elements=elements,
            layout={
                "element_count": len(elements),
                "text_length": len(text),
                "region": region
            }
        )

        return True, screen_data, None


# ============================================================================
# Convenience Functions (Stateless Helpers)
# ============================================================================

def capture_screen(
    region: Optional[Tuple[int, int, int, int]] = None,
    backend: str = "mock",
) -> Tuple[bool, Optional[bytes], Optional[str]]:
    """
    Capture screen (convenience function).

    Args:
        region: Optional region (x, y, width, height)
        backend: Vision backend to use

    Returns:
        (success, image_bytes, error)
    """
    analyzer = VisionAnalyzer(backend=backend)
    return analyzer.capture_screen(region)


def extract_text(
    image_bytes: bytes,
    backend: str = "mock",
) -> Tuple[bool, str, Optional[str]]:
    """
    Extract text from image (convenience function).

    Args:
        image_bytes: Image data
        backend: OCR backend to use

    Returns:
        (success, text, error)
    """
    analyzer = VisionAnalyzer(backend=backend)
    return analyzer.extract_text(image_bytes)


def detect_elements(
    image_bytes: bytes,
    backend: str = "mock",
) -> Tuple[bool, List[Element], Optional[str]]:
    """
    Detect elements in image (convenience function).

    Args:
        image_bytes: Image data
        backend: Detection backend to use

    Returns:
        (success, elements, error)
    """
    analyzer = VisionAnalyzer(backend=backend)
    return analyzer.detect_elements(image_bytes)


def analyze_screen(
    region: Optional[Tuple[int, int, int, int]] = None,
    backend: str = "mock",
) -> Tuple[bool, Optional[ScreenData], Optional[str]]:
    """
    Analyze screen (convenience function).

    Args:
        region: Optional region to analyze
        backend: Vision backend to use

    Returns:
        (success, screen_data, error)
    """
    analyzer = VisionAnalyzer(backend=backend)
    return analyzer.analyze_screen(region)
