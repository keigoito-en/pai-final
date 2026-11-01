"""eval_logs 以下の評価動画を連結し、タスク名の字幕と倍速をつけて 1 本の MP4 にする。

使い方: python make_video.py eval_logs final.mp4 [speed]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])
speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

clips = sorted(root.rglob("*.mp4"))
if not clips:
    sys.exit(f"no mp4 found under {root}")

tmp = Path(tempfile.mkdtemp())
parts = []
for i, clip in enumerate(clips):
    label = clip.parent.name.replace("_", " ")
    part = tmp / f"p{i}.mp4"
    vf = f"setpts=PTS/{speed},drawtext=text='{label}':x=10:y=h-th-10:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-vf", vf,
                    "-an", "-pix_fmt", "yuv420p", str(part)], check=True)
    parts.append(part)

lst = tmp / "list.txt"
lst.write_text("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                "-i", str(lst), "-c", "copy", str(out)], check=True)
print("wrote", out, "from", len(clips), "clips, speed x", speed)
