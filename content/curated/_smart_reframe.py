"""
Subject-tracked smart reframe: 16:9 landscape -> 9:16 vertical (1080x1920).

Strategy:
  1. Sample face positions every N frames using OpenCV Haar cascade.
  2. Smooth the trajectory (EMA + clamp velocity) to avoid jitter.
  3. Scale source so height = 1920, then crop a 1080-wide window
     whose x-center follows the smoothed face trajectory.
  4. Pipe frames to ffmpeg, mux original audio back in.

Usage:
  python _smart_reframe.py <source.mp4> <out.mp4>
"""
import sys
import os
import subprocess
import cv2
import numpy as np

SRC = sys.argv[1]
OUT = sys.argv[2]

TARGET_W, TARGET_H = 1080, 1920
DETECT_EVERY = 5         # detect every N frames (5 = ~6 detections/sec at 30fps)
SMOOTH_ALPHA = 0.08      # EMA factor (lower = smoother, slower to react)
MAX_PAN_PER_FRAME = 4.0  # px per frame max camera move (in target coords) -> ~120 px/sec at 30fps

cap = cv2.VideoCapture(SRC)
src_w  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
src_h  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = cap.get(cv2.CAP_PROP_FPS)
nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Scaled dimensions: scale src so height matches TARGET_H, keep AR
scaled_h = TARGET_H
scaled_w = int(round(src_w * (TARGET_H / src_h)))
crop_x_max = scaled_w - TARGET_W
print(f"src {src_w}x{src_h} @ {fps:.2f}fps, {nframes}f")
print(f"scaled {scaled_w}x{scaled_h}, crop_x_max={crop_x_max}")

cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Pass 1: detect faces, store center x in *scaled* coords (or None)
print("pass 1: face detection...")
face_centers = []  # list of (frame_idx, x_in_scaled_coords) where face found
fidx = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    if fidx % DETECT_EVERY == 0:
        # downscale for detection speed
        small = cv2.resize(frame, (src_w // 2, src_h // 2))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.2, 5, minSize=(40, 40))
        if len(faces) > 0:
            # pick the largest face
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            x, y, w, h = faces[0]
            cx_src = (x + w / 2) * 2  # back to source coords
            cx_scaled = cx_src * (scaled_w / src_w)
            face_centers.append((fidx, cx_scaled))
    fidx += 1
    if fidx % 200 == 0:
        print(f"  {fidx}/{nframes}")
cap.release()
print(f"  found faces in {len(face_centers)} samples")

if not face_centers:
    print("ERROR: no faces detected; falling back to center crop")
    smoothed = [scaled_w / 2] * nframes
else:
    # Build per-frame trajectory by linear interpolation between samples
    sample_idxs = np.array([s[0] for s in face_centers])
    sample_xs   = np.array([s[1] for s in face_centers])
    raw = np.interp(np.arange(nframes), sample_idxs, sample_xs)

    # EMA smoothing
    ema = np.zeros_like(raw)
    ema[0] = raw[0]
    for i in range(1, len(raw)):
        ema[i] = SMOOTH_ALPHA * raw[i] + (1 - SMOOTH_ALPHA) * ema[i - 1]

    # Velocity clamp: limit pan speed
    smoothed = ema.copy()
    for i in range(1, len(smoothed)):
        delta = smoothed[i] - smoothed[i - 1]
        if delta > MAX_PAN_PER_FRAME:
            smoothed[i] = smoothed[i - 1] + MAX_PAN_PER_FRAME
        elif delta < -MAX_PAN_PER_FRAME:
            smoothed[i] = smoothed[i - 1] - MAX_PAN_PER_FRAME

# Convert face center -> crop x (top-left of crop window), clamp to bounds
crop_xs = np.clip(np.array(smoothed) - TARGET_W / 2, 0, crop_x_max).astype(int)

# Pass 2: write frames piped to ffmpeg
print("pass 2: encoding...")
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-pix_fmt", "bgr24",
    "-s", f"{TARGET_W}x{TARGET_H}",
    "-r", f"{fps}",
    "-i", "-",
    "-i", SRC,                # for audio
    "-map", "0:v:0",
    "-map", "1:a:0?",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart",
    "-shortest",
    OUT,
]
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

cap = cv2.VideoCapture(SRC)
fidx = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    scaled = cv2.resize(frame, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
    cx = crop_xs[fidx] if fidx < len(crop_xs) else crop_xs[-1]
    cropped = scaled[:, cx:cx + TARGET_W]
    if cropped.shape[1] != TARGET_W:
        # safety pad if rounding makes it short
        pad = np.zeros((TARGET_H, TARGET_W - cropped.shape[1], 3), dtype=np.uint8)
        cropped = np.hstack([cropped, pad])
    proc.stdin.write(cropped.tobytes())
    fidx += 1
    if fidx % 200 == 0:
        print(f"  {fidx}/{nframes}")
cap.release()
proc.stdin.close()
proc.wait()
print(f"done -> {OUT}")
