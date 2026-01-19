from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List

from stream.reader import FrameTuple


@dataclass
class WindowConfig:
    size_seconds: float


@dataclass
class WindowBatch:
    frames: list[FrameTuple]
    start: float
    end: float


class SlidingWindow:
    def __init__(self, config: WindowConfig) -> None:
        self._config = config

    def iterate(self, frames: Iterable[FrameTuple]) -> Iterator[WindowBatch]:
        buffer: List[FrameTuple] = []
        window_start = None
        for frame in frames:
            timestamp = frame[1]
            if window_start is None:
                window_start = timestamp
            buffer.append(frame)
            if timestamp - window_start >= self._config.size_seconds:
                window_end = timestamp
                yield WindowBatch(frames=list(buffer), start=window_start, end=window_end)
                buffer = []
                window_start = None
        if buffer:
            window_end = buffer[-1][1]
            yield WindowBatch(frames=list(buffer), start=window_start or 0.0, end=window_end)
