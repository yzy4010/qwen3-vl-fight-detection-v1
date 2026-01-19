from __future__ import annotations

from typing import Iterable, Iterator, Optional

from src.utils.logging_utils import get_logger
from stream.reader import FrameTuple


class FrameSampler:
    """基于时间戳的抽帧器，只负责丢帧，不修改帧内容。"""

    def __init__(
        self,
        sample_fps: float,
        max_frames_per_window: Optional[int] = None,
        logger_name: str = "stream.sampler",
    ) -> None:
        self._sample_fps = sample_fps
        self._max_frames_per_window = max_frames_per_window
        self._logger = get_logger(logger_name)

    def sample(self, iter_frames: Iterable[FrameTuple]) -> Iterator[FrameTuple]:
        """按时间差抽帧，确保相邻输出帧时间差 >= 1 / sample_fps。"""
        min_interval = 1.0 / self._sample_fps if self._sample_fps > 0 else 0.0
        last_time: Optional[float] = None
        first_out_ts: Optional[float] = None
        last_out_ts: Optional[float] = None
        input_count = 0
        output_count = 0

        for frame, timestamp in iter_frames:
            input_count += 1
            if self._sample_fps <= 0:
                should_output = True
            else:
                should_output = last_time is None or timestamp - last_time >= min_interval

            if not should_output:
                continue

            last_time = timestamp
            output_count += 1
            if first_out_ts is None:
                first_out_ts = timestamp
            last_out_ts = timestamp
            yield frame, timestamp

            if (
                self._max_frames_per_window is not None
                and output_count >= self._max_frames_per_window
            ):
                break

        actual_fps = 0.0
        if (
            output_count >= 2
            and first_out_ts is not None
            and last_out_ts is not None
            and last_out_ts > first_out_ts
        ):
            actual_fps = output_count / (last_out_ts - first_out_ts)

        self._logger.info(
            "采样完成：输入帧=%d，输出帧=%d，实际输出fps≈%.2f",
            input_count,
            output_count,
            actual_fps,
        )
