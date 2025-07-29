#!/bin/bash

# Generate attack prompts using the refactored RedEval CLI
# This script uses environment variables for configuration

set -e  # Exit on any error

# Load environment setup
source "$(dirname "$0")/setup_env.sh"

# Configuration
CONFIG_PATH="${REDEVAL_RECIPES_DIR}/attack/base-close.yml"
NUM_SAMPLES=${REDEVAL_NUM_SAMPLES:--1}
SEED=${REDEVAL_SEED:-0}
SPLIT=${REDEVAL_SPLIT:-"train"}

echo "Generating attack prompts..."
echo "Config: $CONFIG_PATH"
echo "Samples: $NUM_SAMPLES"
echo "Seed: $SEED"
echo "Split: $SPLIT"

# Use the new CLI interface
python -m redeval.cli generate-attack \
    --config "$CONFIG_PATH" \
    --num-samples $NUM_SAMPLES \
    --seed $SEED \
    --split "$SPLIT"

echo "Attack prompt generation completed!"