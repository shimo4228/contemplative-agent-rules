#!/bin/bash
# Install contemplative agent rules into Claude Code
# Usage: ./install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/rules/contemplative"
TARGET_DIR="${HOME}/.claude/rules/contemplative"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Error: Source directory not found: $SOURCE_DIR"
  exit 1
fi

mkdir -p "$TARGET_DIR"
cp -r "$SOURCE_DIR"/* "$TARGET_DIR"/

echo "Installed contemplative rules to $TARGET_DIR"
echo ""
echo "Files installed:"
ls -1 "$TARGET_DIR"
echo ""
echo "Restart Claude Code for the rules to take effect."
