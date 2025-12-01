#!/bin/bash
set -e

# Define the possible absolute path for Poetry (often used by official installer)
POETRY_BIN="$HOME/.local/bin/poetry"

# Check if the absolute path exists and is executable
if [ -x "$POETRY_BIN" ]; then
    POETRY_COMMAND="$POETRY_BIN run pytest --deselect=slow -q"
elif command -v poetry &> /dev/null; then
    # Fall back to the standard PATH
    POETRY_COMMAND="poetry run pytest --deselect=slow -q"
else
    echo "Error: 'poetry' command not found."
    echo "Please ensure Poetry is installed and available in your shell's PATH, or is located at $POETRY_BIN."
    exit 1
fi

echo "Running fast pytest tests via 'poetry run' (deselecting 'slow' tests)..."

$POETRY_COMMAND

TEST_EXIT_CODE=$?

# --- Provide Feedback ---
if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "Pre-commit hook failed: Some fast tests failed!"
    exit $TEST_EXIT_CODE
else
    echo "Fast tests passed. Proceeding with commit."
    exit 0
fi
