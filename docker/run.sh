#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="iterm-color-preview"
PRESETS_DIR="${1:-$REPO_DIR/themes}"
PREVIEWS_DIR="${2:-$REPO_DIR/previews}"

# Build if image doesn't exist
if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo "Building $IMAGE_NAME docker image..."
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
fi

echo "Presets:  $PRESETS_DIR"
echo "Output:   $PREVIEWS_DIR"
mkdir -p "$PREVIEWS_DIR"

docker run --rm \
    -v "$PRESETS_DIR:/data/presets:ro" \
    -v "$PREVIEWS_DIR:/data/previews" \
    "$IMAGE_NAME"
