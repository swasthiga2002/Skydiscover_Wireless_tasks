#!/usr/bin/env bash
set -euo pipefail

cd /mnt/shared-scratch/Narayanan_K/swasthiga2002/skydiscover_reference

CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
ALGORITHM_NAME=EvoX \
DISABLE_BLER_PLOTS=1 \
SKYDISCOVER_OUTPUT_DIR=outputs/evox_from_nve11_best \
python3 -m skydiscover.cli \
  outputs/evox/channel_estimation_0617_1726/best/best_program.py \
  benchmarks/channel_estimation/evaluator.py \
  -c benchmarks/channel_estimation/config.yaml \
  --search evox \
  --iterations 10 \
  --model gpt-5.4 \
  --output outputs/evox_from_nve11_best
