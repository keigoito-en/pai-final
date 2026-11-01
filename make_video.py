"""eval_logs 以下の評価動画を連結し、各クリップの前に指示文の説明カードを入れて 1 本の MP4 にする。

使い方: python make_video.py eval_logs final.mp4 [speed] [instructions.json] [card_sec]
  instructions.json : {"libero_10_0": "put both ...", ...} (動画フォルダ名 -> 指示文)。無ければフォルダ名を表示。
  speed             : 1.0 = 等倍。倍速にした場合は動画内の字幕に表示する。
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])
speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
instr_path = Path(sys.argv[4]) if len(sys.argv) > 4 else Path("instructions.json")
card_sec = float(sys.argv[5]) if len(sys.argv) > 5 else 2.0
instr = json.loads(instr_path.read_text()) if instr_path.exists() else {}

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FPS = 20


def run(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


def esc(text):
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def size_of(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "csv=s=x:p=0", str(path)],
                       capture_output=True, text=True, check=True)
    w, h = r.stdout.strip().split("x")
    return int(w), int(h)


clips = sorted(root.rglob("*.mp4"), key=lambda p: (p.parent.name.rsplit("_", 1)[0],
                                                    int(p.parent.name.rsplit("_", 1)[1]), p.name))
if not clips:
    sys.exit(f"no mp4 found under {root}")

w, h = size_of(clips[0])
tmp = Path(tempfile.mkdtemp())
parts = []
for i, clip in enumerate(clips):
    key = clip.parent.name                      # e.g. libero_10_0
    text = instr.get(key, key.replace("_", " "))
    suite = key.rsplit("_", 1)[0]
    head = f"[{i + 1}/{len(clips)}] {suite}"

    card = tmp / f"c{i}.mp4"
    vf = (f"drawtext=fontfile={FONT}:text='{esc(head)}':x=(w-tw)/2:y=h/2-40:fontsize=22:fontcolor=white,"
          f"drawtext=fontfile={FONT}:text='{esc(text)}':x=(w-tw)/2:y=h/2:fontsize=16:fontcolor=white")
    run("-f", "lavfi", "-i", f"color=c=black:s={w}x{h}:r={FPS}:d={card_sec}", "-vf", vf,
        "-pix_fmt", "yuv420p", card)

    part = tmp / f"p{i}.mp4"
    cap = esc(text + (f"  (x{speed:g} speed)" if speed != 1.0 else ""))
    vf = (f"setpts=PTS/{speed},fps={FPS},"
          f"drawtext=fontfile={FONT}:text='{cap}':x=8:y=h-th-8:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.6")
    run("-i", clip, "-vf", vf, "-an", "-pix_fmt", "yuv420p", part)
    parts += [card, part]

lst = tmp / "list.txt"
lst.write_text("".join(f"file '{p}'\n" for p in parts))
run("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out)
print("wrote", out, "from", len(clips), "clips, speed x", speed)
