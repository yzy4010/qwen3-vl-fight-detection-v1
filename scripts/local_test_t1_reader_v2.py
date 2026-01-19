import argparse
import time

from src.stream.reader import VideoFrameReader


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="mp4 file path or m3u8/rtsp url")
    parser.add_argument("--max_frames", type=int, default=30)
    args = parser.parse_args()

    print("Input:", args.input)

    reader = VideoFrameReader(args.input)

    last_ts = -1.0
    frame_count = 0
    t_start = time.time()

    try:
        for frame, ts in reader:
            print(f"[{frame_count:03d}] ts={ts:.3f}s shape={frame.shape}")

            # 1) timestamp 必须单调递增
            if ts < last_ts:
                raise AssertionError(
                    f"timestamp not monotonic: last={last_ts}, now={ts}"
                )
            last_ts = ts

            frame_count += 1
            if frame_count >= args.max_frames:
                print("Reached max_frames, stop iteration.")
                break

    except Exception as e:
        print("❌ Exception during reading:", repr(e))
        raise
    else:
        elapsed = time.time() - t_start
        print("✅ Reader finished normally.")
        print(f"Frames read: {frame_count}")
        print(f"Elapsed time: {elapsed:.3f}s")


if __name__ == "__main__":
    main()
