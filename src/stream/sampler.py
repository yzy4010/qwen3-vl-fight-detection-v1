from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

from stream.reader import FrameTuple


@dataclass
class SamplingConfig:
    fps: float


class FrameSampler:
    def __init__(self, config: SamplingConfig) -> None:
        self._config = config

    def sample(self, frames: Iterable[FrameTuple]) -> Iterator[FrameTuple]:
        min_interval = 1.0 / self._config.fps if self._config.fps > 0 else 0.0
        last_time = None
        for frame, timestamp in frames:
            if last_time is None or timestamp - last_time >= min_interval:
                last_time = timestamp
                yield frame, timestamp
