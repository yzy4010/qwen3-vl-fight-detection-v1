import argparse

from src.stream.reader import VideoFrameReader
from src.stream.sampler import FrameSampler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--read_frames", type=int, default=60, help="最多读取多少原始帧用于测试")
    parser.add_argument("--sample_fps", type=float, default=2.0)
    args = parser.parse_args()

    reader = VideoFrameReader(args.input)

    # 先读一段原始帧（避免视频太长）
    raw = []
    for i, (frame, ts) in enumerate(reader):
        raw.append((frame, ts))
        if i + 1 >= args.read_frames:
            break

    print(f"Raw frames: {len(raw)}")
    if len(raw) >= 2:
        duration = raw[-1][1] - raw[0][1]
        print(f"Raw time range: {raw[0][1]:.3f}s -> {raw[-1][1]:.3f}s (duration {duration:.3f}s)")

    sampler = FrameSampler(sample_fps=args.sample_fps)
    sampled = list(sampler.sample(iter(raw)))

    print(f"Sample fps target: {args.sample_fps}")
    print(f"Sampled frames: {len(sampled)}")

    # 校验：时间戳单调 + 相邻间隔 >= 1/sample_fps（允许一点浮动）
    if args.sample_fps > 0:
        min_dt = 1.0 / args.sample_fps
        eps = 1e-3
        for i in range(1, len(sampled)):
            dt = sampled[i][1] - sampled[i - 1][1]
            if dt + eps < min_dt:
                raise AssertionError(f"Sampled dt too small at {i}: dt={dt:.6f}, min_dt={min_dt:.6f}")

    for i, (_, ts) in enumerate(sampled[:10]):
        print(f"[sampled {i:02d}] ts={ts:.3f}s")

    print("✅ sampler basic checks passed.")


if __name__ == "__main__":
    main()
