# AAA Curation Package Inventory Audit

Status: `candidate_applied_not_verified`

Use this workflow when adding, removing or promoting any artifact in the Mega Drive AAA video curation package.

## Inputs

- `doc/05_technical/aaa_curation_package_inventory.json`
- Changed skill, schema, workflow, document or validator file.

## Steps

1. Identify which inventory category the change affects.
2. Update the inventory count and list when a category changes.
3. Update `validate_aaa_video_curation.py` to enforce the new artifact when it is mandatory.
4. Update manifest, registry, README, changelog, checklist, operational summary and audit report when the artifact is correlated.
5. Keep package status as `candidate_applied_not_verified` until validator output proves otherwise.

## Output

- Inventory category changed.
- Files updated.
- Validator coverage updated or reason for no validator change.
- Status retained or promotion evidence.

## Hard Stop

Do not add a new canonical artifact without either adding it to the inventory or explicitly marking it as experimental/backlog.
