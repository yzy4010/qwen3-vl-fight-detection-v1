# Qwen3-VL Fight Detection v1

本项目为视频打架/斗殴识别的 **v1 工程（非 demo）**，聚焦“视频语义理解 + 可解释判断”的端到端流程，
为后续多模型扩展与工程化落地预留接口。

## 当前阶段（T0）

T0 仅完成架构与规范落地：

- 统一配置、日志与结果 schema
- 模块边界与数据流定义
- CLI 与基础目录结构

**不包含具体视频分析策略或模型推理优化。**

## 功能概览

- 支持 `mp4` 文件、`m3u8`、`rtsp` 视频流输入
- 使用滑动时间窗口进行分析（参数可配置）
- 调用 Qwen3-VL（OpenAI-compatible API）输出严格 JSON
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

- `video.window_seconds / video.stride_seconds`：时间窗口大小与步长
- `video.sample_fps`：采样帧率
- `video.resize`：采样帧缩放尺寸
- `video.max_frames_per_window`：每个窗口最大帧数
- `qwen`：模型 API 与推理参数
- `runtime`：日志与输出策略

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
- window/
- model/
- prompt/
- pipeline/
- utils/
- schemas/
app/cli.py
config/default.yaml
docs/architecture.md
```

## 任务路线（T1–T7）

- **T1**：完善预处理与窗口策略（步长、重采样、异常帧处理）
- **T2**：补齐统一结果 schema 与 JSONL 存储
- **T3**：加入轻量级动作检测/前置过滤器
- **T4**：引入多模型协同与融合策略
- **T5**：性能优化（异步、并行、缓存）
- **T6**：GPU 推理与批处理支持
- **T7**：服务化部署（REST/gRPC）与监控

## 说明

- v1 以 Qwen3-VL 为主，但架构允许扩展多模型
- 后续版本将逐步补齐检测策略、性能与服务化能力
