# scripts/local_test_t1_reader.py
import argparse
import time

from src.stream.reader import VideoFrameReader


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="mp4 file path or m3u8/rtsp url")
    parser.add_argument("--max_frames", type=int, default=20)
    args = parser.parse_args()

    reader = VideoFrameReader(args.input)

    last_ts = -1.0
    t0 = time.time()

    for i, (frame, ts) in enumerate(reader):
        print(f"[{i:03d}] ts={ts:.3f}s shape={frame.shape}")
        if ts < last_ts:
            raise RuntimeError(f"timestamp not monotonic: last={last_ts}, now={ts}")
        last_ts = ts

        if i + 1 >= args.max_frames:
            break

    print("OK. elapsed(s)=", time.time() - t0)


if __name__ == "__main__":
    main()
