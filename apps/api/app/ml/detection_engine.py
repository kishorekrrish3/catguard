import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class DetectionTypeML(str, Enum):
    illegal_logging = "illegal_logging"
    encroachment = "encroachment"
    fire_risk = "fire_risk"
    vegetation_loss = "vegetation_loss"
    suspicious_activity = "suspicious_activity"
    flood_risk = "flood_risk"


@dataclass
class DetectionResult:
    detection_type: str
    confidence: float
    severity: str
    lat: float
    lng: float
    bounding_box: Optional[List[float]] = None  # [minx, miny, maxx, maxy]
    metadata: dict = field(default_factory=dict)


class MockDetectionEngine:
    """
    Mock ML inference engine that produces realistic detection results.

    To replace with a real model:
    1. Load ONNX/YOLOv8 model in __init__
    2. Implement _run_model(image_path) -> list of raw predictions
    3. Override analyze_image() to call _run_model() and parse results

    Example real integration:
        from ultralytics import YOLO
        self.model = YOLO("catguard_yolov8.pt")
    """

    TYPE_SEVERITY_MAP = {
        "illegal_logging": ["critical", "high"],
        "encroachment": ["high", "medium"],
        "fire_risk": ["critical", "high", "medium"],
        "vegetation_loss": ["high", "medium", "low"],
        "suspicious_activity": ["medium", "low"],
        "flood_risk": ["high", "medium"],
    }

    def analyze_image(self, image_url: str, zone_id: str, base_lat: float = 10.5, base_lng: float = 76.5) -> List[DetectionResult]:
        """
        Analyze an image URL and return detection results.
        Uses zone_id as seed for reproducible results per zone.
        """
        rng = np.random.default_rng(abs(hash(zone_id)) % (2**31))

        num_detections = rng.integers(0, 4)
        results = []

        detection_types = list(DetectionTypeML)

        for _ in range(num_detections):
            det_type = rng.choice(detection_types).value
            confidence = float(rng.uniform(0.55, 0.98))
            severity_options = self.TYPE_SEVERITY_MAP.get(det_type, ["medium"])
            severity = rng.choice(severity_options)

            lat_offset = rng.uniform(-0.05, 0.05)
            lng_offset = rng.uniform(-0.05, 0.05)

            results.append(DetectionResult(
                detection_type=det_type,
                confidence=round(confidence, 3),
                severity=severity,
                lat=base_lat + lat_offset,
                lng=base_lng + lng_offset,
                metadata={"image_url": image_url, "model_version": "mock-v1.0"},
            ))

        return results

    @staticmethod
    def calculate_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        """
        Normalized Difference Vegetation Index
        NDVI = (NIR - RED) / (NIR + RED)
        Range: -1 to 1. Healthy vegetation > 0.3
        """
        red = red_band.astype(np.float64)
        nir = nir_band.astype(np.float64)
        denominator = nir + red
        ndvi = np.where(denominator == 0, 0.0, (nir - red) / denominator)
        return np.clip(ndvi, -1, 1)

    @staticmethod
    def calculate_savi(red_band: np.ndarray, nir_band: np.ndarray, L: float = 0.5) -> np.ndarray:
        """
        Soil-Adjusted Vegetation Index
        SAVI = ((NIR - RED) / (NIR + RED + L)) * (1 + L)
        L = 0.5 is standard soil adjustment factor
        """
        red = red_band.astype(np.float64)
        nir = nir_band.astype(np.float64)
        denominator = nir + red + L
        savi = np.where(denominator == 0, 0.0, ((nir - red) / denominator) * (1 + L))
        return np.clip(savi, -1, 1)

    @staticmethod
    def estimate_vegetation_cover(ndvi: np.ndarray, threshold: float = 0.3) -> float:
        """Return fraction of pixels with NDVI above threshold (0.0 to 1.0)."""
        if ndvi.size == 0:
            return 0.0
        healthy_pixels = np.sum(ndvi > threshold)
        return float(healthy_pixels / ndvi.size)

    @staticmethod
    def generate_mock_ndvi(zone_id: str, date_str: str) -> dict:
        """Generate realistic mock NDVI metrics for a zone on a given date."""
        rng = np.random.default_rng(abs(hash(f"{zone_id}{date_str}")) % (2**31))
        base = rng.uniform(0.45, 0.75)
        return {
            "ndvi_mean": round(float(base), 4),
            "ndvi_min": round(float(base - rng.uniform(0.1, 0.25)), 4),
            "ndvi_max": round(float(min(base + rng.uniform(0.1, 0.2), 0.95)), 4),
            "savi_mean": round(float(base * 0.85), 4),
            "vegetation_cover_pct": round(float(rng.uniform(65, 95)), 1),
        }


detection_engine = MockDetectionEngine()
