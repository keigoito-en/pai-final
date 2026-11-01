# PAI最終課題: 既存VLA(SmolVLA)による言語指示ロボット操作

LeRobot で公開されている SmolVLA の LIBERO 向けチェックポイント(`HuggingFaceVLA/smolvla_libero`)を、
追加学習なしで LIBERO シミュレーション上で推論実行し、言語指示に従ったロボットアーム操作を動画にする。

- `run_vla.sh` : `lerobot-eval` による推論実行 (スイート/タスク/エピソード数は環境変数で指定)
- `make_video.py` : 評価動画の連結、タスク名の字幕付与、倍速化
- `run_colab.ipynb` : Colab (GPU) 上で上記を順に実行するノートブック

## 実行方法
Colab で `run_colab.ipynb` を開き、GPUランタイムを選んで上から順に実行する。

## 出典
- LeRobot: https://github.com/huggingface/lerobot
- SmolVLA (Hugging Face) / `HuggingFaceVLA/smolvla_libero`
- LIBERO ベンチマーク
