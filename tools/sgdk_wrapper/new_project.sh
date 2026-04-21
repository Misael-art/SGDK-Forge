#!/bin/bash
set -euo pipefail

NEW_PROJ_NAME="${1:-}"
if [ -z "$NEW_PROJ_NAME" ]; then
    echo "Usage: new_project.sh <project-name>"
    exit 1
fi

case "$NEW_PROJ_NAME" in
    *"/"*|*"\\"*|*".."*)
        echo "[ERROR] Invalid project name '$NEW_PROJ_NAME'. Use only a single directory name."
        exit 1
        ;;
esac

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/env.sh"

TARGET_DIR="$MD_ROOT/SGDK_projects/$NEW_PROJ_NAME"
TEMPLATE_DIR="$SCRIPT_DIR/modelo"
AGENT_SOURCE_DIR="$SCRIPT_DIR/.agent"
PROJECT_CREATED=0
CURRENT_TMP_FILE=""
if [ ! -d "$TEMPLATE_DIR" ]; then
    TEMPLATE_DIR="$MD_ROOT/SGDK_templates/base-elite"
fi

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "[ERROR] Canonical template not found at '$TEMPLATE_DIR'."
    exit 1
fi

if [ ! -f "$AGENT_SOURCE_DIR/ARCHITECTURE.md" ] || [ ! -f "$AGENT_SOURCE_DIR/framework_manifest.json" ]; then
    echo "[ERROR] Canonical .agent not found at '$AGENT_SOURCE_DIR'."
    exit 1
fi

if [ -d "$TARGET_DIR" ]; then
    echo "[ERROR] Project '$NEW_PROJ_NAME' already exists."
    exit 1
fi

cleanup_on_exit() {
    local exit_code=$?
    if [ -n "${CURRENT_TMP_FILE:-}" ] && [ -f "${CURRENT_TMP_FILE:-}" ]; then
        rm -f "$CURRENT_TMP_FILE"
    fi

    if [ $exit_code -ne 0 ] && [ "${PROJECT_CREATED:-0}" = "1" ] && [ -d "${TARGET_DIR:-}" ]; then
        rm -rf "$TARGET_DIR"
        echo "[CLEANUP] Removed partial project at '$TARGET_DIR'." >&2
    fi
}

trap cleanup_on_exit EXIT

escape_sed_replacement() {
    printf '%s' "$1" | sed 's/[\/&]/\\&/g'
}

replace_placeholder_in_file() {
    local file_path="$1"
    CURRENT_TMP_FILE="$(mktemp)"
    sed "s/__PROJECT_NAME__/$ESCAPED_PROJECT_NAME/g" "$file_path" > "$CURRENT_TMP_FILE"
    mv "$CURRENT_TMP_FILE" "$file_path"
    CURRENT_TMP_FILE=""
}

mkdir -p "$TARGET_DIR"
cp -a "$TEMPLATE_DIR/." "$TARGET_DIR/"
PROJECT_CREATED=1

if [ -d "$TARGET_DIR/.agent" ]; then
    rm -rf "$TARGET_DIR/.agent"
fi

ESCAPED_PROJECT_NAME="$(escape_sed_replacement "$NEW_PROJ_NAME")"

for file in "$TARGET_DIR/README.md" "$TARGET_DIR/.mddev/project.json"; do
    if [ -f "$file" ]; then
        replace_placeholder_in_file "$file"
    fi
done

if [ -d "$TARGET_DIR/doc" ]; then
    while IFS= read -r file; do
        replace_placeholder_in_file "$file"
    done < <(find "$TARGET_DIR/doc" -type f -name '*.md' | sort)
fi

if ! command -v pwsh >/dev/null 2>&1; then
    echo "[ERROR] pwsh is required to bootstrap the canonical .agent for new projects."
    exit 1
fi

pwsh -NoProfile -File "$SCRIPT_DIR/ensure_project_agent.ps1" -SourceDir "$AGENT_SOURCE_DIR" -TargetDir "$TARGET_DIR" >/dev/null

echo "[OK] Project created: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. cd SGDK_projects/$NEW_PROJ_NAME"
echo "  2. code ."
echo "  3. Atualize .mddev/project.json, doc/11-gdd.md e doc/13-spec-cenas.md"
echo "  4. Declare a identidade de front-end e o papel formal de menu/title antes do runtime."
echo "  5. Put raw art in res/data/ when needed."
echo "  6. Run ../../tools/sgdk_wrapper/build.sh \"\$PWD\" (or build.bat on Windows) to verify the canonical wrapper pipeline."
echo ""
echo "REGRA DE OURO: sempre atualize a documentacao quando a verdade do projeto mudar."
