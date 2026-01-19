from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class ModelResult:
    video_time: tuple[float, float]
    event: str
    confidence: float
    scene_description: str
    evidence: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "video_time": [self.video_time[0], self.video_time[1]],
            "event": self.event,
            "confidence": self.confidence,
            "scene_description": self.scene_description,
            "evidence": self.evidence,
        }


class VideoAnalyzerModel(ABC):
    @abstractmethod
    def analyze_window(
        self,
        frames: Sequence[Any],
        video_time: tuple[float, float],
    ) -> ModelResult:
        raise NotImplementedError
