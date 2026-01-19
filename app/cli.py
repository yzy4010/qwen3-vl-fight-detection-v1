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
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))

    reader = VideoStreamReader(args.input)
    sampler = FrameSampler(SamplingConfig(fps=config["video"]["sample_fps"]))
    windows = SlidingWindow(WindowConfig(size_seconds=config["video"]["window_seconds"]))

    model = QwenVLClient(
        QwenVLConfig(
            api_url=config["qwen"]["api_url"],
            model_name=config["qwen"]["model"],
            timeout_seconds=config["qwen"]["timeout_sec"],
            max_output_tokens=config["qwen"]["max_output_tokens"],
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

    sampled_frames = sampler.sample(reader.read())
    for result in pipeline.analyze(windows.iterate(sampled_frames)):
        print(format_result(result))


if __name__ == "__main__":
    main()
