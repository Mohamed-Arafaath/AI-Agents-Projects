#!/bin/bash

# Freepik Image Generator Skill for Claude Code
# Usage: freepik-image-generator.sh "prompt" [aspect_ratio] [safety_tolerance]

if [ $# -lt 1 ]; then
  echo "Usage: freepik-image-generator.sh \"prompt\" [aspect_ratio] [safety_tolerance]"
  echo "Example: freepik-image-generator.sh \"A beautiful landscape\" square_1_1 2"
  exit 1
fi

PROMPT="$1"
ASPECT_RATIO="${2:-square_1_1}"
SAFETY_TOLERANCE="${3:-2}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/../projects/agents/freepik-image-generator/freepik_image_generator.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
  echo "Python script not found: $PYTHON_SCRIPT"
  exit 1
fi

# Execute the Python script with the provided arguments
python3 "$PYTHON_SCRIPT" "$PROMPT" "$ASPECT_RATIO" "$SAFETY_TOLERANCE"