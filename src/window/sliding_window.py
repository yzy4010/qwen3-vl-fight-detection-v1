from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List

from stream.reader import FrameData


@dataclass
class WindowConfig:
    window_seconds: float
    stride_seconds: float
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
        window_start: float | None = None
        window_end: float | None = None
        for frame in frames:
            if window_start is None:
                window_start = frame.timestamp
                window_end = window_start + self._config.window_seconds
            buffer.append(frame)
            while window_end is not None and frame.timestamp >= window_end:
                window_frames = [f for f in buffer if window_start <= f.timestamp <= window_end]
                if window_frames:
                    actual_start = window_frames[0].timestamp
                    actual_end = window_frames[-1].timestamp
                    yield WindowBatch(
                        frames=window_frames,
                        start=actual_start,
                        end=actual_end,
                    )
                window_start += self._config.stride_seconds
                window_end = window_start + self._config.window_seconds
                buffer = [f for f in buffer if f.timestamp >= window_start]
        if window_start is not None and window_end is not None:
            window_frames = [f for f in buffer if window_start <= f.timestamp <= window_end]
            if window_frames:
                actual_start = window_frames[0].timestamp
                actual_end = window_frames[-1].timestamp
                yield WindowBatch(frames=window_frames, start=actual_start, end=actual_end)
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
