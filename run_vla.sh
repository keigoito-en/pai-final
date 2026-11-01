#!/usr/bin/env bash
# 既存VLA (SmolVLA, LeRobot公開チェックポイント) を LIBERO シミュレーション上で推論実行する。
# 学習は行わない (推論のみ)。
# メモリ節約のため、タスクごとに別プロセスで実行する (Colab無料枠のRAM不足対策)。
set -uo pipefail

export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl

POLICY=${POLICY:-HuggingFaceVLA/smolvla_libero}
OUT=${OUT:-./eval_logs}
SUITE=${SUITE:-libero_object}
TASKS=${TASKS:-"0 1 2"}      # 空白区切りのタスク番号
EPISODES=${EPISODES:-1}

for T in $TASKS; do
  echo "=== $SUITE task $T ==="
  lerobot-eval \
    --output_dir="$OUT/${SUITE}_task${T}" \
    --policy.path="$POLICY" \
    --eval.use_async_envs=false \
    --env.type=libero \
    --env.task="$SUITE" \
    --env.task_ids="[$T]" \
    --eval.batch_size=1 \
    --eval.n_episodes="$EPISODES" \
    --env.max_parallel_tasks=1 || echo "task $T failed (see log above)"
  sleep 2
done
