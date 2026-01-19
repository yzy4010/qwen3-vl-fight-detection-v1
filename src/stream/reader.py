from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import cv2


@dataclass
class FrameData:
    frame: Any
    timestamp: float


class VideoStreamReader:
    def __init__(self, source: str) -> None:
        self._source = source

    def read(self) -> Iterable[FrameData]:
        capture = cv2.VideoCapture(self._source)
        if not capture.isOpened():
            raise ValueError(f"Unable to open video source: {self._source}")
        try:
            while True:
                success, frame = capture.read()
                if not success:
                    break
                timestamp = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                yield FrameData(frame=frame, timestamp=timestamp)
        finally:
            capture.release()
