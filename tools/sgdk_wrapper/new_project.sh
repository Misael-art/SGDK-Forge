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
HOST_PATH="$PATH"
source "$SCRIPT_DIR/env.sh"
# env.sh exposes SGDK variables, but its Wine toolchain PATH must not shadow
# native coreutils during Linux project bootstrap (for example cp.exe vs cp).
PATH="$HOST_PATH"
export PATH

if ! command -v pwsh >/dev/null 2>&1; then
    echo "[ERROR] pwsh is required to validate naming and bootstrap the canonical .agent."
    exit 1
fi

if ! pwsh -NoProfile -File "$SCRIPT_DIR/validate_project_name.ps1" -Name "$NEW_PROJ_NAME" >/dev/null; then
    echo "[ERROR] Invalid canonical project name '$NEW_PROJ_NAME'."
    echo "[ERROR] Expected: NOME [VER.XXX] [SGDK YYY] [PLATAFORMA] [TIPO] [GENERO]"
    exit 1
fi

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
shopt -s dotglob nullglob
for template_entry in "$TEMPLATE_DIR"/*; do
    entry_name="$(basename "$template_entry")"
    if [ "$entry_name" = ".agent" ] || [ "$entry_name" = "out" ]; then
        continue
    fi
    cp -a "$template_entry" "$TARGET_DIR/"
done
shopt -u dotglob nullglob
PROJECT_CREATED=1

if [ -d "$TARGET_DIR/.agent" ]; then
    rm -rf "$TARGET_DIR/.agent"
fi

# Vibe Playable template seeds are structural only. Runtime evidence must never be born from the template.
if [ -d "$TARGET_DIR/out" ]; then
    rm -rf "$TARGET_DIR/out"
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
    done < <(find "$TARGET_DIR/doc" -type f \( -name '*.md' -o -name '*.json' \) | sort)
fi

pwsh -NoProfile -File "$SCRIPT_DIR/reset_new_project_state.ps1" \
    -ProjectRoot "$TARGET_DIR" \
    -ConfirmNewProjectSeed >/dev/null

pwsh -NoProfile -File "$SCRIPT_DIR/adopt_project_methodology.ps1" -ProjectRoot "$TARGET_DIR" -Lifecycle new >/dev/null

pwsh -NoProfile -File "$SCRIPT_DIR/ensure_project_agent.ps1" -SourceDir "$AGENT_SOURCE_DIR" -TargetDir "$TARGET_DIR" >/dev/null

if ! pwsh -NoProfile -File "$SCRIPT_DIR/scene_contract_compiler.ps1" \
    -ProjectRoot "$TARGET_DIR" \
    -WarnOnly >/dev/null; then
    echo "[WARN] scene_contract_compiler.ps1 could not generate the initial doc/scene-contracts.json." >&2
    echo "[WARN] Review doc/13-spec-cenas.md and doc/scene-regression.json before the first validation pass." >&2
fi

# Final safety pass: bootstrap helpers may create out/ for diagnostics, but new projects must not be born with runtime evidence.
if [ -d "$TARGET_DIR/out" ]; then
    rm -rf "$TARGET_DIR/out"
fi

echo "[OK] Project created: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. cd SGDK_projects/$NEW_PROJ_NAME"
echo "  2. code ."
echo "  3. Classifique doc/project_context_manifest.json antes de arte/runtime."
echo "  4. Valide o contexto com ../../tools/sgdk_wrapper/validate_project_context.ps1."
echo "  5. Classifique doc/project_methodology_manifest.json e doc/technique_usage_manifest.json antes de arte/runtime."
echo "  6. Valide com ../../tools/sgdk_wrapper/validate_project_methodology.ps1; review_required bloqueia closeout."
echo "  7. Atualize .mddev/project.json, doc/00-project-brief.md, doc/11-gdd.md, doc/15-tdd.md e doc/13-spec-cenas.md conforme o contexto."
echo "  8. Declare a identidade de front-end e o papel formal de menu/title antes do runtime."
echo "  9. Put raw art in res/data/ when needed."
echo "  10. Run ../../tools/sgdk_wrapper/build.sh \"\$PWD\" (or build.bat on Windows) to verify the canonical wrapper pipeline."
echo "  11. Vibe Playable seed installed: blocked_no_premium_source."
echo "  12. No approval, ROM, screenshot, SRAM, VDP dump or runtime panel was created by this bootstrap."
echo "  13. Next visual gates: premium source -> human asset approval -> VDP conversion -> build -> BlastEm evidence."
echo ""
echo "DIRETRIZ DE BLOQUEIO ESTETICO (ja em doc/00-diretrizes-agente.md):"
echo "  - nenhum pixel de personagem, inimigo, boss ou cenario pode nascer de codigo;"
echo "  - primitiva/ImageDraw serve apenas para telemetria, debug visual e UI transitoria;"
echo "  - todo simbolo visual do .res exige registro em doc/asset_provenance_manifest.json;"
echo "  - auditor: python3 ../../tools/sgdk_wrapper/audit_procedural_asset_provenance.py --project-root \"\$PWD\" --shared-builder-root ../../tools/image-tools"
echo ""
echo "REGRA DE OURO: sempre atualize a documentacao quando a verdade do projeto mudar."
