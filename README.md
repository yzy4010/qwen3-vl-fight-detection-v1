# Qwen3-VL Fight Detection v1

Minimal runnable pipeline for v1 phase 1. The goal is to open a video or M3U8 stream on Windows + CPU, sample a short window, and report basic frame statistics.

## Quick Start

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.cli --input path/to/video.mp4
```

## CLI Usage

```bash
python -m app.cli --input <video_or_m3u8> --config config/default.yaml
```

## Output
The CLI prints a summary of frame sampling (frame count, average brightness, size) to stdout.

## Structure

```
app/                # CLI entrypoint
src/                # Pipeline implementation
config/             # Default configuration
docs/               # Architecture notes
```

