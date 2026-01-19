# v1 架构设计说明（Phase 2）

## 设计目标

- 面向真实工程场景：输入视频/流，输出可解释的打架检测 JSON
- 以 Qwen3-VL 为唯一模型依赖，确保 v1 可跑通
- 模型与业务流程解耦，支持后续模型替换或多模型协同

## 模块划分

```
src/
- stream/
  - reader.py          # 视频 / m3u8 / rtsp 抽帧
  - sampler.py         # 帧率与采样控制
- window/
  - sliding_window.py  # 时间窗口管理（Video Time + stride）
- model/
  - base.py            # 模型接口定义（抽象层）
  - qwen_vl_client.py  # Qwen3-VL v1 实现
- prompt/
  - fight_prompt.py    # 严格 JSON 输出的 Prompt
- pipeline/
  - analyzer.py        # 端到端分析流水线（与具体模型解耦）
- utils/
  - json_utils.py      # JSON 容错与字段校验
```

### 数据流程

1. `stream.reader` 统一读取视频文件/流
2. `stream.sampler` 根据配置控制采样帧率
3. `window.sliding_window` 形成固定窗口 + stride 滑动
4. `pipeline.analyzer` 负责帧预处理并调用模型
5. `model.qwen_vl_client` 通过 OpenAI-compatible API 调用 Qwen3-VL
6. `utils.json_utils` 对模型输出做 JSON 提取与字段校验

## Phase 2 关键能力

- 窗口级别输出严格 JSON（`fight|normal|uncertain`）
- 兼容模型输出夹带说明时的 JSON 提取与降级策略
- CLI 支持 `--enable_llm`（推理模式）与统计模式

## 模型选型理由

- Qwen3-VL 具备多模态理解与场景描述能力
- 能同时完成“检测 + 解释”，输出可读证据
- 适合在 v1 中验证端到端链路与 JSON 输出格式

## 可扩展设计

- `model.base.VideoAnalyzerModel` 为统一接口，可替换为其他模型实现
- `pipeline.analyzer` 与模型解耦，支持并行模型、融合策略等扩展
- `stream` 与 `window` 模块可替换为更高效的解码/时序抽样方案

## 后续演进方向

- 引入轻量级动作检测或目标检测模型，作为前置过滤器
- 加入时序模型做连续性判断（如打斗持续性/升级程度）
- GPU 加速与服务化部署（REST/gRPC）
