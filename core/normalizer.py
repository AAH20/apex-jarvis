"""
APEX_JARVIS Sub-Pixel Continuous Coordinate Normalizer.
Retina-invariant affine mapping of OS desktop display coordinates into [0.0, 1.0].
"""

from typing import Tuple


class CoordinateNormalizer:
    def __init__(self, display_width: int = 1920, display_height: int = 1080, scale_factor: float = 1.0):
        self.width = display_width
        self.height = display_height
        self.scale_factor = scale_factor

    def normalize(self, x: float, y: float) -> Tuple[float, float]:
        norm_x = max(0.0, min(1.0, (x / self.scale_factor) / self.width))
        norm_y = max(0.0, min(1.0, (y / self.scale_factor) / self.height))
        return (round(norm_x, 6), round(norm_y, 6))

    def denormalize(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        x = int(norm_x * self.width * self.scale_factor)
        y = int(norm_y * self.height * self.scale_factor)
        return (x, y)
