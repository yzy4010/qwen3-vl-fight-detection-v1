from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np


@dataclass
class PipelineConfig:
    window_seconds: float = 2.0
    sample_fps: int = 5
    max_frames: int = 10


@dataclass
class PipelineResult:
    frame_count: int
    avg_brightness: float
    frame_size: Tuple[int, int]
    fps: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_count": self.frame_count,
            "avg_brightness": self.avg_brightness,
            "frame_size": {"width": self.frame_size[0], "height": self.frame_size[1]},
            "fps": self.fps,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class FrameSampler:
    def __init__(self, config: PipelineConfig) -> None:
        self.config = config

    def run(self, source: str) -> PipelineResult:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"Unable to open input: {source}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
        if fps <= 0:
            fps = float(self.config.sample_fps)

        frame_interval = max(int(round(fps / max(self.config.sample_fps, 1))), 1)
        max_frames = self._compute_max_frames(fps)

        frames: list[np.ndarray] = []
        frame_index = 0
        while len(frames) < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_index % frame_interval == 0:
                frames.append(frame)
            frame_index += 1

        cap.release()

        if not frames:
            raise RuntimeError("No frames were sampled from the input.")

        avg_brightness = self._compute_avg_brightness(frames)
        height, width = frames[0].shape[:2]

        return PipelineResult(
            frame_count=len(frames),
            avg_brightness=avg_brightness,
            frame_size=(width, height),
            fps=fps,
        )

    def _compute_max_frames(self, fps: float) -> int:
        window_frames = int(round(self.config.window_seconds * fps))
        return max(1, min(self.config.max_frames, window_frames))

    @staticmethod
    def _compute_avg_brightness(frames: list[np.ndarray]) -> float:
        values = [float(np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))) for frame in frames]
        return float(np.mean(values))


def run_pipeline(source: str, config: PipelineConfig) -> PipelineResult:
    sampler = FrameSampler(config)
    return sampler.run(source)
