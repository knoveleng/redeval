#!/bin/bash

# Environment setup script for RedEval
# This script sets up the required environment variables and authentication

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up RedEval environment...${NC}"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"

# Load environment variables from .env file if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Loading environment variables from .env file..."
    # Use a safer method to load .env that handles special characters
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^#.*$ ]] && continue
        [[ -z $key ]] && continue
        # Remove quotes from value if present
        value=$(echo "$value" | sed 's/^"\(.*\)"$/\1/')
        export "$key"="$value"
    done < "$PROJECT_ROOT/.env"
else
    echo -e "${YELLOW}No .env file found. Please ensure environment variables are set.${NC}"
fi

# Validate required environment variables
missing_vars=()

if [ -z "$OPENAI_API_KEY" ]; then
    missing_vars+=("OPENAI_API_KEY")
fi

if [ -z "$HUGGINGFACE_TOKEN" ]; then
    missing_vars+=("HUGGINGFACE_TOKEN")
fi

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${RED}Error: Missing required environment variables:${NC}"
    for var in "${missing_vars[@]}"; do
        echo -e "${RED}  - $var${NC}"
    done
    echo -e "${YELLOW}Please set these variables in your environment or create a .env file.${NC}"
    echo -e "${YELLOW}Example .env file:${NC}"
    echo "OPENAI_API_KEY=your_openai_key_here"
    echo "HUGGINGFACE_TOKEN=your_huggingface_token_here"
    exit 1
fi

# Login to HuggingFace if token is available
if [ -n "$HUGGINGFACE_TOKEN" ]; then
    echo -e "${GREEN}Logging in to HuggingFace...${NC}"
    echo "$HUGGINGFACE_TOKEN" | huggingface-cli login --token "$HUGGINGFACE_TOKEN" --add-to-git-credential
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}HuggingFace login successful${NC}"
    else
        echo -e "${YELLOW}Warning: HuggingFace login failed, but continuing...${NC}"
    fi
fi

# Set default values for optional environment variables
export REDEVAL_LOG_LEVEL=${REDEVAL_LOG_LEVEL:-"INFO"}
export REDEVAL_PROJECT_ROOT=${REDEVAL_PROJECT_ROOT:-$(pwd)}
export REDEVAL_LOG_DIR=${REDEVAL_LOG_DIR:-"$REDEVAL_PROJECT_ROOT/logs"}
export REDEVAL_RECIPES_DIR=${REDEVAL_RECIPES_DIR:-"$REDEVAL_PROJECT_ROOT/recipes"}

echo -e "${GREEN}Environment setup complete!${NC}"
echo -e "${GREEN}Project root: $REDEVAL_PROJECT_ROOT${NC}"
echo -e "${GREEN}Log directory: $REDEVAL_LOG_DIR${NC}"
echo -e "${GREEN}Recipes directory: $REDEVAL_RECIPES_DIR${NC}"
