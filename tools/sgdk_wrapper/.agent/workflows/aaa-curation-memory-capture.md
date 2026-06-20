# AAA Curation Memory Capture

Status: `candidate_applied_not_verified`

Use this workflow when closing or resuming work on the Mega Drive AAA video curation package.

## Inputs

- `doc/05_technical/aaa_curation_memory_update.json`
- Current curation manifest.
- Current risk register.
- Primary workspace memory bank, when safe to inspect and edit.

## Steps

1. Read the memory update capsule.
2. Confirm whether the primary workspace memory bank can be safely inspected.
3. If safe, merge only the key decisions that remain current.
4. If not safe, keep the capsule as the candidate memory record and report that it is not merged.
5. Keep the curation package status unchanged unless validator and workspace audits pass.
6. Update the capsule whenever a new canonical decision, risk or recovery requirement is added.

## Output

- Memory merge status.
- Decisions captured.
- Decisions pending merge.
- Blockers.

## Hard Stop

Do not claim canonical memory-bank update when only the sidecar memory capsule was written.
