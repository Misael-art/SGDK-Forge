#!/bin/bash
NEW_PROJ_NAME="$1"
if [ -z "$NEW_PROJ_NAME" ]; then
    echo "Usage: new_project.sh <project-name>"
    exit 1
fi

source "$(dirname "$0")/env.sh"

TARGET_DIR="$MD_ROOT/projects/$NEW_PROJ_NAME"
TEMPLATE_DIR="$(cd "$(dirname "$0")" && pwd)/modelo"
if [ ! -d "$TEMPLATE_DIR" ]; then
    TEMPLATE_DIR="$MD_ROOT/templates/project-template"
fi

if [ -d "$TARGET_DIR" ]; then
    echo "[ERROR] Project '$NEW_PROJ_NAME' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -r "$TEMPLATE_DIR/." "$TARGET_DIR/"

echo "[OK] Project created: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. cd projects/$NEW_PROJ_NAME"
echo "  2. review .mddev/project.json and doc/01-visao-geral.md"
echo "  3. put raw assets in res/data/"
echo "  4. run build.sh or build.bat"
