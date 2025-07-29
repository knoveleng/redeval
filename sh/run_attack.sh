#!/bin/bash

# Run attack evaluation using the refactored RedEval CLI
# This script uses environment variables for configuration

set -e  # Exit on any error

# Load environment setup
source "$(dirname "$0")/setup_env.sh"

# Configuration
OPEN_CONFIG_PATH="${REDEVAL_RECIPES_DIR}/attack/base-open.yml"
CLOSE_CONFIG_PATH="${REDEVAL_RECIPES_DIR}/attack/base-close.yml"

# Model configurations (can be overridden by environment variables)
OPEN_SOURCE_MODELS=${REDEVAL_OPEN_SOURCE_MODELS:-"Qwen/Qwen2.5-7B-Instruct"}
CLOSED_SOURCE_MODELS=${REDEVAL_CLOSED_SOURCE_MODELS:-"gpt-4o-mini gpt-4.1-nano"}

echo "Running attack evaluation..."

# Process open-source models
echo "Processing open-source models: $OPEN_SOURCE_MODELS"
for MODEL_NAME in $OPEN_SOURCE_MODELS; do
    echo "Running attack on open-source model: $MODEL_NAME"
    python -m redeval.cli run-attack \
        --config "$OPEN_CONFIG_PATH" \
        --model "$MODEL_NAME"
    
    echo "Completed attack on $MODEL_NAME"
done

# Process closed-source models
echo "Processing closed-source models: $CLOSED_SOURCE_MODELS"
for MODEL_NAME in $CLOSED_SOURCE_MODELS; do
    echo "Running attack on closed-source model: $MODEL_NAME"
    python -m redeval.cli run-attack \
        --config "$CLOSE_CONFIG_PATH" \
        --model "$MODEL_NAME"
    
    echo "Completed attack on $MODEL_NAME"
done

echo "Attack evaluation completed!"