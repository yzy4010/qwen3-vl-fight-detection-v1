from __future__ import annotations

from dataclasses import dataclass
import os
import time
from typing import Any, Iterable, Iterator, Optional, Tuple
from urllib.parse import urlparse

import cv2

from src.utils.logging_utils import get_logger


FrameTuple = Tuple[Any, float]


@dataclass
class ReaderConfig:
    open_timeout: Optional[float] = None
    reconnect: bool = False


class StreamOpenError(RuntimeError):
    """视频/流打开失败时抛出。"""


class VideoFrameReader:
    """统一的视频帧读取器，支持本地文件与流。"""

    def __init__(
        self,
        source: str,
        config: Optional[ReaderConfig] = None,
        logger_name: str = "stream.reader",
    ) -> None:
        self._raw_source = source
        self._config = config or ReaderConfig()
        self._logger = get_logger(logger_name)
        self._source_type = self._infer_source_type(source)
        self._source = self._normalize_source(source)

    def __iter__(self) -> Iterator[FrameTuple]:
        return self.read()

    def read(self) -> Iterable[FrameTuple]:
        capture = cv2.VideoCapture(self._source)
        self._apply_open_options(capture)
        if not capture.isOpened():
            raise StreamOpenError(f"无法打开视频源: {self._raw_source}")
        try:
            if self._source_type == "file":
                yield from self._read_file(capture)
            else:
                yield from self._read_stream(capture)
        finally:
            capture.release()

    def _read_file(self, capture: cv2.VideoCapture) -> Iterator[FrameTuple]:
        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_idx = 0
        last_ts: Optional[float] = None
        while True:
            success, frame = capture.read()
            if not success:
                self._logger.info("视频读取结束或读取失败，停止输出帧。")
                break
            ts_msec = capture.get(cv2.CAP_PROP_POS_MSEC)
            ts_sec = ts_msec / 1000.0 if ts_msec > 0 else 0.0
            if ts_sec <= 0 and fps > 0:
                ts_sec = frame_idx / fps
            if last_ts is not None and ts_sec <= last_ts:
                increment = 1.0 / fps if fps > 0 else 1e-3
                ts_sec = last_ts + increment
            last_ts = ts_sec
            frame_idx += 1
            yield frame, ts_sec

    def _read_stream(self, capture: cv2.VideoCapture) -> Iterator[FrameTuple]:
        start_time = time.time()
        last_ts: Optional[float] = None
        while True:
            success, frame = capture.read()
            if not success:
                self._logger.warning("流读取失败或断流，停止输出帧。")
                break
            ts_sec = time.time() - start_time
            if last_ts is not None and ts_sec <= last_ts:
                ts_sec = last_ts + 1e-3
            last_ts = ts_sec
            yield frame, ts_sec

    def _apply_open_options(self, capture: cv2.VideoCapture) -> None:
        if self._config.open_timeout is not None:
            prop = getattr(cv2, "CAP_PROP_OPEN_TIMEOUT_MSEC", None)
            if prop is not None:
                capture.set(prop, int(self._config.open_timeout * 1000))
        if self._config.reconnect:
            self._logger.info("reconnect 参数已配置，当前版本暂不实现复杂重连。")

    def _infer_source_type(self, source: str) -> str:
        if self._is_url(source):
            return "stream"
        return "file"

    def _is_url(self, source: str) -> bool:
        parsed = urlparse(source)
        if parsed.scheme and parsed.scheme != "file":
            if len(parsed.scheme) == 1 and os.path.exists(source):
                return False
            return True
        return False

    def _normalize_source(self, source: str) -> str:
        parsed = urlparse(source)
        if parsed.scheme == "file":
            path = parsed.path
            if os.name == "nt" and path.startswith("/"):
                path = path.lstrip("/")
            return path
        return source
