import cv2
import sys
import os

path = sys.argv[1] if len(sys.argv) > 1 else r".\test.mp4"
print("input path:", path)
print("abs path:", os.path.abspath(path))

cap = cv2.VideoCapture(path)

print("isOpened:", cap.isOpened())

try:
    backend = cap.getBackendName()
except Exception:
    backend = "unknown"

print("backend:", backend)
print("fps:", cap.get(cv2.CAP_PROP_FPS))
print("w,h:",
      cap.get(cv2.CAP_PROP_FRAME_WIDTH),
      cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

ok, frame = cap.read()
print("first read:", ok)
if ok and frame is not None:
    print("frame shape:", frame.shape)

cap.release()
