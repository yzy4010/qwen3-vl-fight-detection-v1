from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Sequence

import requests
from PIL import Image

from model.base import ModelResult, VideoAnalyzerModel
from prompt.fight_prompt import build_fight_prompt


@dataclass
class QwenVLConfig:
    api_url: str
    model_name: str
    timeout_seconds: int
    max_output_tokens: int


class QwenVLClient(VideoAnalyzerModel):
    def __init__(self, config: QwenVLConfig) -> None:
        self._config = config

    def analyze_window(
        self,
        frames: Sequence[Image.Image],
        video_time: tuple[float, float],
    ) -> ModelResult:
        prompt = build_fight_prompt(video_time)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    *[
                        {
                            "type": "image_url",
                            "image_url": {"url": _image_to_data_url(frame)},
                        }
                        for frame in frames
                    ],
                ],
            }
        ]
        payload = {
            "model": self._config.model_name,
            "messages": messages,
            "max_tokens": self._config.max_output_tokens,
        }
        response = requests.post(
            self._config.api_url,
            json=payload,
            timeout=self._config.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        parsed = _safe_json_parse(content)
        return ModelResult(
            video_time=(parsed["video_time"][0], parsed["video_time"][1]),
            event=parsed["event"],
            confidence=float(parsed["confidence"]),
            scene_description=parsed["scene_description"],
            evidence=list(parsed.get("evidence", [])),
        )


def _image_to_data_url(image: Image.Image) -> str:
    from io import BytesIO

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def _safe_json_parse(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise
        return json.loads(text[start : end + 1])
