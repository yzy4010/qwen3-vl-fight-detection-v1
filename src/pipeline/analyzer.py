from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence

import cv2
from PIL import Image

from model.base import ModelResult, VideoAnalyzerModel
from stream.reader import FrameTuple
from window.sliding_window import WindowBatch


@dataclass
class ResizeConfig:
    width: int
    height: int


@dataclass
class PipelineConfig:
    max_frames_per_window: int


class VideoAnalyzerPipeline:
    def __init__(
        self,
        model: VideoAnalyzerModel,
        resize_config: ResizeConfig,
        pipeline_config: PipelineConfig,
    ) -> None:
        self._model = model
        self._resize = resize_config
        self._pipeline = pipeline_config

    def analyze(self, windows: Iterable[WindowBatch]) -> Iterator[ModelResult]:
        for window in windows:
            frames = self._prepare_frames(window.frames)
            yield self._model.analyze_window(frames, (window.start, window.end))

    def _prepare_frames(self, frames: Sequence[FrameTuple]) -> list[Image.Image]:
        selected = frames[: self._pipeline.max_frames_per_window]
        prepared: list[Image.Image] = []
        for frame_data in selected:
            resized = cv2.resize(
                frame_data[0],
                (self._resize.width, self._resize.height),
                interpolation=cv2.INTER_AREA,
            )
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            prepared.append(Image.fromarray(rgb))
        return prepared


def format_result(result: ModelResult) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False)
