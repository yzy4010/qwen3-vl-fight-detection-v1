from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from model.qwen_vl_client import QwenVLClient, QwenVLConfig
from pipeline.analyzer import PipelineConfig, ResizeConfig, VideoAnalyzerPipeline, format_result
from stream.reader import VideoStreamReader
from stream.sampler import FrameSampler, SamplingConfig
from window.sliding_window import SlidingWindow, WindowConfig


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fight detection v1 pipeline")
    parser.add_argument("--input", required=True, help="Video file, m3u8, or rtsp stream URL")
    parser.add_argument("--config", default="config/default.yaml", help="Path to config yaml")
    parser.add_argument(
        "--enable_llm",
        action="store_true",
        help="Enable Qwen3-VL inference; otherwise run statistics-only mode",
    )
    return parser


def build_pipeline(config: dict) -> tuple[VideoStreamReader, FrameSampler, SlidingWindow, VideoAnalyzerPipeline]:
    reader = VideoStreamReader(config["input"])
    sampler = FrameSampler(SamplingConfig(fps=config["video"]["sample_fps"]))
    window = SlidingWindow(
        WindowConfig(
            window_seconds=config["video"]["window_seconds"],
            stride_seconds=config["video"]["stride_seconds"],
        )
    )
    model = QwenVLClient(
        QwenVLConfig(
            api_url=config["qwen"]["api_url"],
            model_name=config["qwen"]["model"],
            timeout_seconds=config["qwen"]["timeout_sec"],
            max_output_tokens=config["qwen"]["max_output_tokens"],
            temperature=config["qwen"]["temperature"],
        )
    )
    pipeline = VideoAnalyzerPipeline(
        model=model,
        resize_config=ResizeConfig(
            width=config["video"]["resize"]["width"],
            height=config["video"]["resize"]["height"],
        ),
        pipeline_config=PipelineConfig(
            max_frames_per_window=config["video"]["max_frames_per_window"]
        ),
    )
    return reader, sampler, window, pipeline


def run_stats(reader: VideoStreamReader, sampler: FrameSampler, window: SlidingWindow) -> None:
    sampled_frames = sampler.sample(reader.read())
    window_count = 0
    first_start = None
    last_end = None
    total_window_frames = 0
    for batch in window.iterate(sampled_frames):
        window_count += 1
        total_window_frames += len(batch.frames)
        if first_start is None:
            first_start = batch.start
        last_end = batch.end
    duration = 0.0 if first_start is None or last_end is None else last_end - first_start
    print(f"[Stats] windows={window_count}, window_frames={total_window_frames}, duration={duration:.2f}s")


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    config["input"] = args.input

    reader, sampler, window, pipeline = build_pipeline(config)

    if not args.enable_llm:
        run_stats(reader, sampler, window)
        return

    for result in pipeline.analyze_stream(reader, sampler, window):
        print(format_result(result))


if __name__ == "__main__":
    main()
