# context_pack_manifest

project: NOVO ARARA GI FIGHTER V2
date: 2026-05-13
context_type: projeto_novo
rag_model: local_auditable_files_v1

## Canonical Files Read

- F:/Projects/MegaDrive_DEV/AGENTS.md instructions supplied in chat
- tools/sgdk_wrapper/.agent/ARCHITECTURE.md
- tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md
- tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json
- tools/sgdk_wrapper/.agent/workflows/production-loop.md
- tools/sgdk_wrapper/.agent/workflows/route-decision-gate.md
- tools/sgdk_wrapper/.agent/workflows/build-validate.md
- tools/sgdk_wrapper/.agent/skills/art/art-asset-diagnostic/SKILL.md
- tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/SKILL.md
- tools/sgdk_wrapper/.agent/skills/art/sprite-animation/SKILL.md
- tools/sgdk_wrapper/.agent/skills/art/character-design/SKILL.md
- tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md
- tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md
- tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md
- tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/references/source_to_rom_visual_gate.md
- tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md
- tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/SKILL.md
- tools/sgdk_wrapper/.agent/skills/operation/sgdk-build-wrapper-operator/SKILL.md
- tools/sgdk_wrapper/.agent/skills/architecture/scene-state-architect/SKILL.md
- sdk/sgdk-2.11/inc/ will be consulted before any API-sensitive runtime addition.

## Project Truth Sources

- doc/10-memory-bank.md: exists from template, to be rewritten for this project.
- doc/11-gdd.md: exists from template, to be rewritten for this project.
- doc/13-spec-cenas.md: exists from template, to be rewritten for this project.
- doc/00-diretrizes-agente.md: exists from template.
- .mddev/project.json: exists and declares flat SGDK 2.11 layout.

## Source Cases And Builders

- Existing ARARA GI FIGHTER assets and builder were inspected only for pipeline structure.
- No HAMOOPIG image, palette, pose, timing, tile, or stage is authorized as source.
- tools/image-tools/build_arara_gi_fighter_assets.py is allowed only as a conversion/promotion reference if adapted to consume this project source_art.

## Image Tooling

- Built-in image_gen is callable and persists files under C:/Users/misae/.codex/generated_images/019e2330-db4e-7561-822e-0df5d44c9d65.
- First test image was generated before animation contracts and is excluded from this project's premium source manifest.
- Production image generation begins only after animation_state_plan, pose_roster, frame_budget_table and pivot_and_scale_contract exist.

## Memory Fallback

Project doc/10-memory-bank.md exists and is primary. Workspace doc/06_AI_MEMORY_BANK.md is not used as fallback for this project.