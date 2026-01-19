from __future__ import annotations

import argparse
import pathlib
from typing import Any, Dict

import yaml

from src.pipeline import PipelineConfig, run_pipeline


def load_config(path: pathlib.Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data


def build_pipeline_config(config_data: Dict[str, Any]) -> PipelineConfig:
    pipeline = config_data.get("pipeline", {})
    return PipelineConfig(
        window_seconds=float(pipeline.get("window_seconds", 2.0)),
        sample_fps=int(pipeline.get("sample_fps", 5)),
        max_frames=int(pipeline.get("max_frames", 10)),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal video window sampler")
    parser.add_argument("--input", required=True, help="Path or URL to video/M3U8")
    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="Path to configuration YAML",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = pathlib.Path(args.config)
    config_data = load_config(config_path)
    pipeline_config = build_pipeline_config(config_data)

    result = run_pipeline(args.input, pipeline_config)
    print(result.to_json())


if __name__ == "__main__":
    main()
