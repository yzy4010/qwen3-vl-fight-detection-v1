from __future__ import annotations

import json
from typing import Any

REQUIRED_FIELDS = {"video_time", "event", "confidence", "scene_description", "evidence"}


def extract_first_json(text: str) -> dict[str, Any] | None:
    for start_idx, char in enumerate(text):
        if char != "{":
            continue
        for end_idx in range(len(text) - 1, start_idx, -1):
            if text[end_idx] != "}":
                continue
            snippet = text[start_idx : end_idx + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                continue
    return None


def validate_or_fallback(parsed: dict[str, Any] | None, video_time: tuple[float, float]) -> dict[str, Any]:
    if not isinstance(parsed, dict):
        return _fallback(video_time, "模型返回无法解析为 JSON")
    missing = REQUIRED_FIELDS - set(parsed.keys())
    if missing:
        return _fallback(video_time, f"缺少字段: {', '.join(sorted(missing))}")
    parsed["video_time"] = [video_time[0], video_time[1]]
    return parsed


def parse_model_output(text: str, video_time: tuple[float, float]) -> dict[str, Any]:
    parsed = extract_first_json(text)
    return validate_or_fallback(parsed, video_time)


def _fallback(video_time: tuple[float, float], error_message: str) -> dict[str, Any]:
    return {
        "video_time": [video_time[0], video_time[1]],
        "event": "uncertain",
        "confidence": 0.0,
        "scene_description": "模型输出不完整，已降级为 uncertain。",
        "evidence": [error_message],
    }
