# Template Registry

Status: operational registry created; no template files were moved.

The current canonical bootstrap template is:

`tools/sgdk_wrapper/modelo`

Reason: `tools/sgdk_wrapper/new_project.bat` and `tools/sgdk_wrapper/new_project.sh` resolve `tools/sgdk_wrapper/modelo` first. `sgdk_templates/base-elite` is a fallback/reference path, not the active primary bootstrap.

Machine-readable registry:

`doc/template_registry.json`

Validator:

`python tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`

## Registered Templates

| ID | Path | Status | Recommendation |
|---|---|---|---|
| `sgdk_modelo` | `tools/sgdk_wrapper/modelo` | `CANONICAL_BOOTSTRAP` | `KEEP`, `CLEAN_OUTPUTS` |
| `base_elite` | `sgdk_templates/base-elite` | `REFERENCE_TEMPLATE` | `KEEP`, `OWNER_REVIEW` |
| `simple_game_states_elite` | `sgdk_templates/SimpleGameStates_Elite` | `LOGIC_TEMPLATE` | `KEEP`, `OWNER_REVIEW` |
| `sgdk_templates_templates` | `sgdk_templates/templates` | `PARTIAL_TEMPLATE` | `KEEP`, `OWNER_REVIEW` |
| `wrapper_project_template_nested` | `tools/sgdk_wrapper/templates/project-template-nested` | `PARTIAL_TEMPLATE` | `KEEP`, `OWNER_REVIEW` |

## Rules

- Exactly one template may be `CANONICAL_BOOTSTRAP`.
- The canonical bootstrap remains `tools/sgdk_wrapper/modelo` unless a future registry update includes an explicit override justification and validates wrapper behavior.
- Templates containing `out/` are allowed for now but must be cleaned in a dedicated hygiene pass before being promoted as release-grade templates.
- Do not alter `sgdk_templates` or `tools/sgdk_wrapper/modelo` physically without a template-specific move plan, checksum manifest and rollback.

## Next Safe Step

Create a dedicated template hygiene branch that removes generated output from the canonical template and updates `doc/template_registry.json` after validation.

