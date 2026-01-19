# Qwen3-VL Fight Detection v1

本项目为视频打架/斗殴识别的 v1 工程实现，聚焦“视频语义理解 + 可解释判断”的端到端流程，
并为后续多模型扩展预留接口。

## 功能概览

- 支持 `mp4` 文件、`m3u8`、`rtsp` 视频流输入
- 使用滑动时间窗口（默认 2.5 秒）进行分析
- 每个时间窗口采样多帧，调用 Qwen3-VL（OpenAI-compatible API）输出严格 JSON
- 模型与流水线解耦，方便未来替换或新增模型

## 环境要求

- Windows 优先，CPU 可运行
- Python 3.10+ 推荐

## 安装

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## 配置

`config/default.yaml` 包含全部运行参数：

- `window.size_seconds`：时间窗口大小（秒）
- `sampling.fps`：采样帧率
- `resize.width / resize.height`：采样帧缩放尺寸
- `model.api_url / model.name`：模型 API 地址与名称
- `model.timeout_seconds / model.max_output_tokens`：模型调用参数

## 运行

```bash
python -m app.cli --input <video_or_m3u8_or_rtsp>
```

输出为严格 JSON：

```json
{
  "video_time": [start, end],
  "event": "fight | normal | uncertain",
  "confidence": number,
  "scene_description": string,
  "evidence": [string]
}
```

## 目录结构

```text
src/
- stream/
  - reader.py
  - sampler.py
- window/
  - sliding_window.py
- model/
  - base.py
  - qwen_vl_client.py
- prompt/
  - fight_prompt.py
- pipeline/
  - analyzer.py
- utils/
app/cli.py
config/default.yaml
```

## 说明

- v1 仅依赖 Qwen3-VL 即可运行
- 后续可扩展更高效检测模型或多模型协同机制
