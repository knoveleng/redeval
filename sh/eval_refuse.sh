#!/bin/bash

# Evaluate refuse results using the refactored RedEval CLI
# This script uses environment variables for configuration

set -e  # Exit on any error

# Load environment setup
source "$(dirname "$0")/setup_env.sh"

# Configuration
BASE_LOG_DIR="${REDEVAL_LOG_DIR}/refuse"
CONFIG_PATH="${REDEVAL_RECIPES_DIR}/refuse/eval.yml"

# Dataset and method configurations
SUBDATASETS=${REDEVAL_REFUSE_DATASETS:-"CoCoNot SGXSTest XSTest ORBench"}
MODEL_NAMES=${REDEVAL_MODELS:-"Qwen/Qwen2.5-7B-Instruct gpt-4o-mini"}
METHOD_NAMES=${REDEVAL_REFUSE_METHODS:-"base"}

echo "Evaluating refuse results..."
echo "Base log directory: $BASE_LOG_DIR"
echo "Config: $CONFIG_PATH"
echo "Subdatasets: $SUBDATASETS"
echo "Models: $MODEL_NAMES"
echo "Methods: $METHOD_NAMES"

# Process all combinations
for SUBDATASET in $SUBDATASETS; do
    for METHOD_NAME in $METHOD_NAMES; do
        for MODEL_NAME in $MODEL_NAMES; do
            LOG_DIR="$BASE_LOG_DIR/$SUBDATASET/$METHOD_NAME/$MODEL_NAME"
            
            if [ -d "$LOG_DIR" ]; then
                echo "Evaluating: $SUBDATASET/$METHOD_NAME/$MODEL_NAME"
                python -m redeval.cli eval-refuse \
                    --config "$CONFIG_PATH" \
                    --log-dir "$LOG_DIR"
                echo "Completed evaluation for $MODEL_NAME"
            else
                echo "Warning: Log directory not found: $LOG_DIR"
            fi
        done
    done
done

echo "Refuse evaluation completed!"
