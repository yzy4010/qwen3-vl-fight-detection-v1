from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple


@dataclass
class FightEventResult:
    video_id: Optional[str]
    video_time: Tuple[float, float]
    event: Literal["fight", "normal", "uncertain"]
    confidence: float
    scene_description: str
    evidence: List[str] = field(default_factory=list)
    debug: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "video_id": self.video_id,
            "video_time": [self.video_time[0], self.video_time[1]],
            "event": self.event,
            "confidence": self.confidence,
            "scene_description": self.scene_description,
            "evidence": list(self.evidence),
            "debug": dict(self.debug),
        }
