#!/usr/bin/env bash
# 既存VLA (pi0.5, LeRobot公開チェックポイント) を LIBERO シミュレーション上で推論実行する。
# 学習は行わない (推論のみ)。
set -euo pipefail

export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl

POLICY=${POLICY:-lerobot/pi05_libero_finetuned}
OUT=${OUT:-./eval_logs}
# 実行するスイートとタスク番号。環境変数で上書き可能。
SUITE=${SUITE:-libero_object}
TASK_IDS=${TASK_IDS:-[0,1,2]}
EPISODES=${EPISODES:-1}

lerobot-eval \
  --output_dir="$OUT/$SUITE" \
  --policy.path="$POLICY" \
  --policy.n_action_steps=10 \
  --env.type=libero \
  --env.task="$SUITE" \
  --env.task_ids="$TASK_IDS" \
  --eval.batch_size=1 \
  --eval.n_episodes="$EPISODES" \
  --env.max_parallel_tasks=1
