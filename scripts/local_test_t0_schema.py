# local_test_t0_schema.py
from src.schemas.result import FightEventResult

# 构造一个最小对象
r = FightEventResult(
    video_id="test123",
    video_time=(0.0, 1.234),
    event="uncertain",
    confidence=0.5,
    scene_description="架构测试",
    evidence=["无"],
    debug={"stage": "t0_schema_check"}
)

print("Schema OK:", r)
