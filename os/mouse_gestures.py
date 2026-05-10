"""
Mouse Gesture Recognizer - Recognize gestures like swipes, circles, etc.
Used for celestial dot gestures and intuitive window management.
"""

from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import math
import time


class GestureType(Enum):
    """Recognized gesture types"""
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    CIRCLE_CW = "circle_clockwise"
    CIRCLE_CCW = "circle_counter_clockwise"
    PINCH_IN = "pinch_in"
    PINCH_OUT = "pinch_out"
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    DRAG = "drag"


@dataclass
class Point:
    """2D point"""
    x: float
    y: float
    timestamp: float = 0.0

    def distance_to(self, other: 'Point') -> float:
        """Distance to another point"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def direction_to(self, other: 'Point') -> str:
        """Direction to another point"""
        dx = other.x - self.x
        dy = other.y - self.y
        angle = math.atan2(dy, dx)
        angle_deg = math.degrees(angle)

        if -45 <= angle_deg <= 45:
            return "right"
        elif 45 < angle_deg <= 135:
            return "down"
        elif 135 < angle_deg or angle_deg <= -135:
            return "left"
        else:
            return "up"


@dataclass
class Gesture:
    """Recognized gesture"""
    type: GestureType
    start_point: Point
    end_point: Point
    duration: float
    distance: float
    metadata: Dict = None


class MouseGestureRecognizer:
    """
    Recognize mouse gestures from point sequences.
    Celestial dot aware - recognizes swipes, circles, and complex patterns.
    """

    def __init__(self, threshold_distance: float = 20.0, threshold_time: float = 0.5):
        """
        Initialize gesture recognizer.

        Args:
            threshold_distance: Minimum pixels for swipe gesture
            threshold_time: Maximum seconds for gesture
        """
        self.threshold_distance = threshold_distance
        self.threshold_time = threshold_time
        self.gesture_callbacks: Dict[GestureType, List[Callable]] = {}

    def register_gesture_handler(self, gesture_type: GestureType, callback: Callable):
        """Register callback for gesture"""
        if gesture_type not in self.gesture_callbacks:
            self.gesture_callbacks[gesture_type] = []
        self.gesture_callbacks[gesture_type].append(callback)

    def analyze_points(self, points: List[Point]) -> Optional[Gesture]:
        """
        Analyze sequence of points to recognize gesture.

        Args:
            points: List of points forming gesture

        Returns:
            Recognized Gesture or None
        """
        if len(points) < 2:
            return None

        start = points[0]
        end = points[-1]
        distance = start.distance_to(end)
        duration = end.timestamp - start.timestamp if start.timestamp > 0 else 0

        # Check if too slow
        if duration > self.threshold_time and duration > 0:
            return self._recognize_long_gesture(points)

        # Check direction for swipe
        direction = start.direction_to(end)

        # Recognize swipe gestures
        if distance > self.threshold_distance:
            gesture_map = {
                "up": GestureType.SWIPE_UP,
                "down": GestureType.SWIPE_DOWN,
                "left": GestureType.SWIPE_LEFT,
                "right": GestureType.SWIPE_RIGHT,
            }

            gesture_type = gesture_map.get(direction)
            if gesture_type:
                return Gesture(
                    type=gesture_type,
                    start_point=start,
                    end_point=end,
                    duration=duration,
                    distance=distance,
                    metadata={"direction": direction}
                )

        # Recognize circle
        circle_gesture = self._recognize_circle(points)
        if circle_gesture:
            return circle_gesture

        # Recognize tap/drag
        if distance < self.threshold_distance:
            return Gesture(
                type=GestureType.TAP,
                start_point=start,
                end_point=end,
                duration=duration,
                distance=distance
            )

        return None

    def _recognize_long_gesture(self, points: List[Point]) -> Optional[Gesture]:
        """Recognize gestures that take longer (circle, etc.)"""
        if len(points) < 3:
            return None

        return self._recognize_circle(points)

    def _recognize_circle(self, points: List[Point]) -> Optional[Gesture]:
        """Recognize circle gesture"""
        if len(points) < 4:
            return None

        try:
            # Calculate center of points
            center_x = sum(p.x for p in points) / len(points)
            center_y = sum(p.y for p in points) / len(points)
            center = Point(center_x, center_y)

            # Calculate distances from center (should be consistent for circle)
            distances = [p.distance_to(center) for p in points]
            avg_distance = sum(distances) / len(distances)
            variance = sum((d - avg_distance) ** 2 for d in distances) / len(distances)

            # Low variance = circle
            if variance < 100:  # Threshold for circle detection
                # Determine direction (clockwise vs counter-clockwise)
                direction = self._detect_circle_direction(points, center)

                gesture_type = (
                    GestureType.CIRCLE_CW if direction == "cw"
                    else GestureType.CIRCLE_CCW
                )

                return Gesture(
                    type=gesture_type,
                    start_point=points[0],
                    end_point=points[-1],
                    duration=points[-1].timestamp - points[0].timestamp if points[0].timestamp > 0 else 0,
                    distance=avg_distance * 2,  # Diameter
                    metadata={"center": center, "direction": direction}
                )
        except Exception:
            pass

        return None

    def _detect_circle_direction(self, points: List[Point], center: Point) -> str:
        """Detect if circle is clockwise or counter-clockwise"""
        if len(points) < 3:
            return "cw"

        # Use cross product to determine direction
        total_angle_change = 0

        for i in range(1, len(points) - 1):
            p1 = points[i - 1]
            p2 = points[i]
            p3 = points[i + 1]

            # Vectors from center
            v1 = (p1.x - center.x, p1.y - center.y)
            v2 = (p2.x - center.x, p2.y - center.y)

            # Cross product
            cross = v1[0] * v2[1] - v1[1] * v2[0]
            total_angle_change += cross

        return "cw" if total_angle_change > 0 else "ccw"

    def trigger_callbacks(self, gesture: Gesture):
        """Trigger callbacks for recognized gesture"""
        if gesture.type in self.gesture_callbacks:
            for callback in self.gesture_callbacks[gesture.type]:
                try:
                    callback(gesture)
                except Exception as e:
                    print(f"Gesture callback error: {e}")

    # ========================================================================
    # CELESTIAL DOT GESTURES (Custom gesture patterns)
    # ========================================================================

    def recognize_celestial_dot_pattern(self, points: List[Point]) -> Optional[str]:
        """
        Recognize celestial dot patterns for special operations.
        Patterns: swipe up = maximize, swipe down = minimize, etc.
        """
        gesture = self.analyze_points(points)
        if not gesture:
            return None

        gesture_to_action = {
            GestureType.SWIPE_UP: "maximize",
            GestureType.SWIPE_DOWN: "minimize",
            GestureType.SWIPE_LEFT: "previous_workspace",
            GestureType.SWIPE_RIGHT: "next_workspace",
            GestureType.CIRCLE_CW: "rotate_window",
            GestureType.CIRCLE_CCW: "rotate_window_reverse",
            GestureType.PINCH_IN: "zoom_in",
            GestureType.PINCH_OUT: "zoom_out",
        }

        return gesture_to_action.get(gesture.type)

    def get_gesture_info(self, gesture: Gesture) -> Dict[str, any]:
        """Get detailed gesture information"""
        return {
            "type": gesture.type.value,
            "start": (gesture.start_point.x, gesture.start_point.y),
            "end": (gesture.end_point.x, gesture.end_point.y),
            "distance": gesture.distance,
            "duration": gesture.duration,
            "speed": gesture.distance / gesture.duration if gesture.duration > 0 else 0,
            "metadata": gesture.metadata or {}
        }
