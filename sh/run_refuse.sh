#!/bin/bash

# Run refuse evaluation using the refactored RedEval CLI
# This script uses environment variables for configuration

set -e  # Exit on any error

# Load environment setup
source "$(dirname "$0")/setup_env.sh"

# Configuration
OPEN_CONFIG_PATH="${REDEVAL_RECIPES_DIR}/refuse/base-open.yml"
CLOSE_CONFIG_PATH="${REDEVAL_RECIPES_DIR}/refuse/base-close.yml"

# Parameters
NUM_SAMPLES=${REDEVAL_REFUSE_SAMPLES:-10}
SEED=${REDEVAL_SEED:-0}
SPLIT=${REDEVAL_SPLIT:-"train"}

# Model configurations
OPEN_SOURCE_MODELS=${REDEVAL_OPEN_SOURCE_MODELS:-"Qwen/Qwen2.5-7B-Instruct"}
CLOSED_SOURCE_MODELS=${REDEVAL_CLOSED_SOURCE_MODELS:-"gpt-4o-mini gpt-4.1-nano"}

echo "Running refuse evaluation..."
echo "Samples: $NUM_SAMPLES"
echo "Seed: $SEED"
echo "Split: $SPLIT"

# Process open-source models
echo "Processing open-source models: $OPEN_SOURCE_MODELS"
for MODEL_NAME in $OPEN_SOURCE_MODELS; do
    echo "Running refuse test on open-source model: $MODEL_NAME"
    python -m redeval.cli run-refuse \
        --config "$OPEN_CONFIG_PATH" \
        --model "$MODEL_NAME" \
        --num-samples $NUM_SAMPLES \
        --seed $SEED \
        --split "$SPLIT"
    
    echo "Completed refuse test on $MODEL_NAME"
done

# Process closed-source models
echo "Processing closed-source models: $CLOSED_SOURCE_MODELS"
for MODEL_NAME in $CLOSED_SOURCE_MODELS; do
    echo "Running refuse test on closed-source model: $MODEL_NAME"
    python -m redeval.cli run-refuse \
        --config "$CLOSE_CONFIG_PATH" \
        --model "$MODEL_NAME" \
        --num-samples $NUM_SAMPLES \
        --seed $SEED \
        --split "$SPLIT"
    
    echo "Completed refuse test on $MODEL_NAME"
done

echo "Refuse evaluation completed!"