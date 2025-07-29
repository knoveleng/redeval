#!/bin/bash

# Calculate scores for both attack and refuse phases using the refactored RedEval CLI
# This script uses environment variables for configuration

set -e  # Exit on any error

# Load environment setup
source "$(dirname "$0")/setup_env.sh"

echo "Calculating scores for attack and refuse phases..."

############################## FOR ATTACK ##############################
echo "Processing attack scores..."

ATTACK_BASE_LOG_DIR="${REDEVAL_LOG_DIR}/attack"
ATTACK_SUBDATASETS=${REDEVAL_ATTACK_DATASETS:-"HarmBench"}
ATTACK_MODEL_NAMES=${REDEVAL_MODELS:-"Qwen/Qwen2.5-7B-Instruct gpt-4o-mini"}
ATTACK_METHOD_NAMES=${REDEVAL_ATTACK_METHODS:-"direct human_jailbreak zeroshot"}
ATTACK_KEYWORD="unsafe"

echo "Attack - Base log directory: $ATTACK_BASE_LOG_DIR"
echo "Attack - Subdatasets: $ATTACK_SUBDATASETS"
echo "Attack - Models: $ATTACK_MODEL_NAMES"
echo "Attack - Methods: $ATTACK_METHOD_NAMES"
echo "Attack - Keyword: $ATTACK_KEYWORD"

for SUBDATASET in $ATTACK_SUBDATASETS; do
    for METHOD_NAME in $ATTACK_METHOD_NAMES; do
        for MODEL_NAME in $ATTACK_MODEL_NAMES; do
            LOG_DIR="$ATTACK_BASE_LOG_DIR/$SUBDATASET/$METHOD_NAME/$MODEL_NAME"
            
            if [ -d "$LOG_DIR" ]; then
                echo "Scoring attack: $SUBDATASET/$METHOD_NAME/$MODEL_NAME"
                python -m redeval.cli score \
                    --log-dir "$LOG_DIR" \
                    --keyword "$ATTACK_KEYWORD"
                echo "Completed scoring for $MODEL_NAME"
            else
                echo "Warning: Attack log directory not found: $LOG_DIR"
            fi
        done
    done
done

############################## FOR REFUSE ##############################
echo "Processing refuse scores..."

REFUSE_BASE_LOG_DIR="${REDEVAL_LOG_DIR}/refuse"
REFUSE_SUBDATASETS=${REDEVAL_REFUSE_DATASETS:-"CoCoNot SGXSTest XSTest ORBench"}
REFUSE_MODEL_NAMES=${REDEVAL_MODELS:-"Qwen/Qwen2.5-7B-Instruct gpt-4o-mini"}
REFUSE_METHOD_NAMES=${REDEVAL_REFUSE_METHODS:-"base"}
REFUSE_KEYWORD="unpass"

echo "Refuse - Base log directory: $REFUSE_BASE_LOG_DIR"
echo "Refuse - Subdatasets: $REFUSE_SUBDATASETS"
echo "Refuse - Models: $REFUSE_MODEL_NAMES"
echo "Refuse - Methods: $REFUSE_METHOD_NAMES"
echo "Refuse - Keyword: $REFUSE_KEYWORD"

for SUBDATASET in $REFUSE_SUBDATASETS; do
    for METHOD_NAME in $REFUSE_METHOD_NAMES; do
        for MODEL_NAME in $REFUSE_MODEL_NAMES; do
            LOG_DIR="$REFUSE_BASE_LOG_DIR/$SUBDATASET/$METHOD_NAME/$MODEL_NAME"
            
            if [ -d "$LOG_DIR" ]; then
                echo "Scoring refuse: $SUBDATASET/$METHOD_NAME/$MODEL_NAME"
                python -m redeval.cli score \
                    --log-dir "$LOG_DIR" \
                    --keyword "$REFUSE_KEYWORD"
                echo "Completed scoring for $MODEL_NAME"
            else
                echo "Warning: Refuse log directory not found: $LOG_DIR"
            fi
        done
    done
done

echo "Score calculation completed!"