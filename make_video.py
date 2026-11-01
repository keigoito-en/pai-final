"""eval_logs 以下の評価動画を連結し、各クリップの前に指示文の説明カードを入れて 1 本の MP4 にする。

使い方: python make_video.py eval_logs final.mp4 [speed] [instructions.json] [card_sec]
  instructions.json : {"libero_10_0": "put both ...", ...} (動画フォルダ名 -> 指示文)。無ければフォルダ名を表示。
  speed             : 1.0 = 等倍。倍速にした場合は動画内の字幕に表示する。
"""
import json
import subprocess
import sys
import tempfile
import textwrap
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


clips = sorted(root.rglob("*.mp4"), key=lambda p: (p.parent.name.rsplit("_", 1)[0],
                                                    int(p.parent.name.rsplit("_", 1)[1]), p.name))
if not clips:
    sys.exit(f"no mp4 found under {root}")

W, H, V = 1280, 720, 720          # 出力サイズ / ロボット映像の一辺 (左に配置し、右の余白に指示文を出す)
tmp = Path(tempfile.mkdtemp())


def lines_filter(lines, x, y0, size, step):
    """行ごとに drawtext を並べる (折り返しは呼び出し側で行う)。x は式も可。"""
    return ",".join(
        f"drawtext=fontfile={FONT}:text='{esc(l)}':x={x}:y={y0 + k * step}:fontsize={size}:fontcolor=white"
        for k, l in enumerate(lines))


parts = []
for i, clip in enumerate(clips):
    key = clip.parent.name                      # e.g. libero_10_0
    text = instr.get(key, key.replace("_", " "))
    suite = key.rsplit("_", 1)[0]
    head = f"[{i + 1}/{len(clips)}] {suite}"
    body = textwrap.wrap(text, 40)

    card = tmp / f"c{i}.mp4"
    vf = lines_filter([head], "(w-tw)/2", 250, 36, 0) + "," + lines_filter(body, "(w-tw)/2", 310, 30, 44)
    run("-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={card_sec}", "-vf", vf,
        "-pix_fmt", "yuv420p", card)

    part = tmp / f"p{i}.mp4"
    side = [head] + [""] + textwrap.wrap(text, 24) + ([""] + [f"(x{speed:g} speed)"] if speed != 1.0 else [])
    vf = (f"setpts=PTS/{speed},fps={FPS},scale={V}:{V}:flags=lanczos,pad={W}:{H}:0:0:black,"
          + lines_filter(side, V + 30, 60, 30, 42))
    run("-i", clip, "-vf", vf, "-an", "-pix_fmt", "yuv420p", part)
    parts += [card, part]

lst = tmp / "list.txt"
lst.write_text("".join(f"file '{p}'\n" for p in parts))
run("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out)
print("wrote", out, "from", len(clips), "clips, speed x", speed)
