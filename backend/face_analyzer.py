"""
Face Analyzer for Air Mouse Backend

Handles face distance measurement and ratio analysis logic.
Ported from provided Python script, removing GUI dependencies.
"""

import numpy as np
import math
from typing import Dict, Tuple, List, Any


class FaceAnalyzer:
    def __init__(self):
        # Configuration targets
        self.TARGET_RATIO = 0.135  # Target face width ratio (approx 1m)
        self.TOLERANCE = 0.005  # Distance tolerance

    def get_2d_distance(self, p1, p2) -> float:
        """Calculate Euclidean distance between two 2D points."""
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def calculate_score(
        self, val: float, target: float, tolerance: float = 0.1
    ) -> float:
        """Calculate score based on how close val is to target."""
        if target == 0:
            return 0
        ratio = val / target

        if (1.0 - tolerance) <= ratio <= (1.0 + tolerance):
            return 100.0

        diff = min(abs(ratio - (1.0 - tolerance)), abs(ratio - (1.0 + tolerance)))
        score = 100 * np.exp(-3.5 * diff)
        return max(0, min(100, score))

    def get_rank(self, score: float) -> str:
        """Get rank string from score."""
        if score >= 96:
            return "SSS"
        elif score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        else:
            return "C"

    def check_precision_distance(
        self, landmarks, frame_width: int, frame_height: int
    ) -> Tuple[str, float, float]:
        """
        Check if user is at the correct distance.
        Returns: (status, current_ratio, target_ratio)
        Status: WAIT, PERFECT, TOO_CLOSE, TOO_FAR, BAD_POSE
        """
        if not landmarks:
            return "WAIT", 0.0, self.TARGET_RATIO

        # Convert landmarks to pixel coordinates
        pts = [(lm.x * frame_width, lm.y * frame_height) for lm in landmarks]

        # Face width (Check points 234 and 454)
        # Note: landmarks index must match FaceMesh topology
        if len(pts) <= 454:
            return "WAIT", 0.0, self.TARGET_RATIO

        face_w_px = self.get_2d_distance(pts[234], pts[454])
        current_ratio = face_w_px / frame_width
        diff = current_ratio - self.TARGET_RATIO

        status = "WAIT"
        if abs(diff) < self.TOLERANCE:
            status = "PERFECT"
        elif diff > 0:
            status = "TOO_CLOSE"
        else:
            status = "TOO_FAR"

        # Pose check (Nose alignment)
        # Point 1 (Nose tip), Center of 234-454
        center_x = (pts[234][0] + pts[454][0]) / 2
        if abs(pts[1][0] - center_x) > face_w_px * 0.08:
            status = "BAD_POSE"

        return status, current_ratio, self.TARGET_RATIO

    def analyze_ratio(
        self, landmarks, frame_width: int, frame_height: int
    ) -> Dict[str, Any]:
        """
        Analyze face ratios and calculate total score.
        Returns detailed score dict.
        """
        if not landmarks or len(landmarks) <= 454:
            return {"total": 0, "rank": "C", "details": {}}

        # Convert to pixels
        pts = [(lm.x * frame_width, lm.y * frame_height) for lm in landmarks]

        # Calculate metrics
        eye_l = self.get_2d_distance(pts[33], pts[133])
        eye_r = self.get_2d_distance(pts[362], pts[263])
        UNIT = (eye_l + eye_r) / 2

        if UNIT == 0:
            return {"total": 0, "rank": "C", "details": {}}

        r_gap = self.get_2d_distance(pts[133], pts[362]) / UNIT
        r_width = self.get_2d_distance(pts[234], pts[454]) / UNIT

        # Face shape: Forehead(10) to Chin(152) / Width
        r_shape = self.get_2d_distance(pts[10], pts[152]) / self.get_2d_distance(
            pts[234], pts[454]
        )

        # Chin ratio: Nose(2) to Chin(152) / Bridge(168) to Nose(2)
        # Using alternative points if 168/2 are close
        r_vert = self.get_2d_distance(pts[2], pts[152]) / (
            self.get_2d_distance(pts[168], pts[2]) + 0.001
        )

        # Calculate scores
        s1 = self.calculate_score(r_gap, 1.1, 0.15)
        s2 = self.calculate_score(r_width, 4.5, 0.1)
        s3 = self.calculate_score(r_shape, 1.4, 0.1)
        s4 = self.calculate_score(r_vert, 0.9, 0.15)

        # Weighted total
        total = (s1 + s2 + s3 * 1.5 + s4) / 4.5
        if total > 85:
            total = min(99, total * 1.05)

        return {
            "total": round(total, 1),
            "rank": self.get_rank(total),
            "details": {
                "Eye Gap": {"score": int(s1), "val": round(r_gap, 2)},
                "Face Width": {"score": int(s2), "val": round(r_width, 2)},
                "Face Shape": {"score": int(s3), "val": round(r_shape, 2)},
                "Chin Ratio": {"score": int(s4), "val": round(r_vert, 2)},
            },
        }
