# Architecture (v1 Phase 1)

## Goal
Establish a minimal, runnable pipeline that can open a video or M3U8 input on Windows CPU, sample a small window of frames, and report basic frame statistics.

## Components
- **CLI (`app/cli.py`)**: Parses inputs, loads configuration, and orchestrates the pipeline.
- **Pipeline (`src/pipeline.py`)**: Opens the media source, samples a short frame window, and computes simple statistics for validation.
- **Config (`config/default.yaml`)**: Provides defaults for sampling window and logging.

## Data Flow
1. CLI loads `config/default.yaml` (optional override with `--config`).
2. Pipeline opens the input via OpenCV (`cv2.VideoCapture`).
3. Pipeline samples frames at a configured rate and computes basic stats.
4. Results are printed to stdout as a JSON-like summary.

## Future Expansion
- Replace basic statistics with fight-detection model inference.
- Add streaming reconnection and buffer handling for M3U8.
- Add structured logging and output persistence.
