from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List

from stream.reader import FrameData


@dataclass
class WindowConfig:
    size_seconds: float


@dataclass
class WindowBatch:
    frames: list[FrameData]
    start: float
    end: float


class SlidingWindow:
    def __init__(self, config: WindowConfig) -> None:
        self._config = config

    def iterate(self, frames: Iterable[FrameData]) -> Iterator[WindowBatch]:
        buffer: List[FrameData] = []
        window_start = None
        for frame in frames:
            if window_start is None:
                window_start = frame.timestamp
            buffer.append(frame)
            if frame.timestamp - window_start >= self._config.size_seconds:
                window_end = frame.timestamp
                yield WindowBatch(frames=list(buffer), start=window_start, end=window_end)
                buffer = []
                window_start = None
        if buffer:
            window_end = buffer[-1].timestamp
            yield WindowBatch(frames=list(buffer), start=window_start or 0.0, end=window_end)
