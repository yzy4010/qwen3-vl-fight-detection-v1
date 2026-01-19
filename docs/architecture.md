# v1 架构说明

## v1 总体目标与边界

v1 聚焦“可运行的工程骨架”，用于把视频流输入、时间窗口、模型调用与结果输出统一起来：

- 目标：建立稳定的模块边界、统一配置与结果 schema，保证后续模型与 pipeline 可快速接入。
- 边界：不实现更复杂的视频分析策略、不引入多模型融合、不实现服务化部署。
- 模型策略：v1 以 Qwen3-VL 为主，但架构允许在后续版本扩展多模型与不同推理引擎。

## 模块划分

```
src/
- stream/       # Stream：统一视频文件/流读取与按时间戳抽帧
- window/       # Window：时间窗口切分与管理
- preprocess/   # Preprocess：图像预处理（缩放等）
- model/        # Model：模型接口与具体实现（Qwen3-VL）
- pipeline/     # Pipeline：端到端串联调度
- utils/        # 通用工具（日志、配置、schema 等）
app/cli.py      # CLI：命令行入口
```

说明：`preprocess` 目前包含缩放等基础处理逻辑（T0 仅定义规范与入口）。

## 数据流说明

1. **Stream**：读取视频文件或流，并按时间戳进行抽帧，输出连续帧数据。
   - **Reader/Sampler 边界**：
     - Reader 只负责读取帧与生成单调递增时间戳。
     - Sampler 只负责按时间差抽帧，不基于 frame index 采样。
   - **时间戳策略**：
     - 本地 mp4：优先使用 `CAP_PROP_POS_MSEC` 获取帧时间戳；若不可用则回退为 `fps + frame_idx` 计算，并保证单调递增。
     - 流（m3u8/rtsp）：fps 不可靠，使用 `time.time()` 计算相对时间戳，保证单调递增。
   - **最小示例**：

```python
from stream.reader import VideoFrameReader

reader = VideoFrameReader("demo.mp4")
for frame_bgr, ts_sec in reader:
    print(frame_bgr.shape, ts_sec)
```
2. **Preprocess**：执行缩放等图像预处理。
3. **Window**：按时间窗口与步长组织帧序列。
4. **Model**：对单窗口帧序列进行分析，返回统一结果 schema。
5. **Pipeline**：串联上述步骤，负责调度与结果输出。
6. **CLI**：加载配置、触发流水线运行。

## v2/v3 扩展方向

- **多模型协同**：引入检测模型 + 多模态理解模型的组合，支持投票/融合策略。
- **GPU 加速**：将预处理与推理迁移到 GPU，提升吞吐与延迟表现。
- **服务化**：提供 REST/gRPC 服务，支持多租户与监控；进一步拆分异步队列与任务调度。
