from __future__ import annotations


def build_fight_prompt(video_time: tuple[float, float]) -> str:
    start, end = video_time
    return (
        "你是专业的视频安全分析助手，请根据提供的多个视频帧判断是否出现打架/斗殴等暴力场景。\n"
        "必须严格按照 JSON 输出，不要包含其他文字。\n"
        "输出格式如下：\n"
        "{\n"
        '  "video_time": [start, end],\n'
        '  "event": "fight | normal | uncertain",\n'
        '  "confidence": number,\n'
        '  "scene_description": string,\n'
        '  "evidence": [string]\n'
        "}\n"
        f"当前分析窗口时间为 {start:.2f} - {end:.2f} 秒，请保持该时间段一致。\n"
        "请根据画面动作、肢体接触、攻击性动作等线索给出判断，并提供证据要点列表。"
    )
