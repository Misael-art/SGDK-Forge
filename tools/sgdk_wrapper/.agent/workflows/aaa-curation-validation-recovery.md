# AAA Curation Validation Recovery

Status: `candidate_applied_not_verified`

Use this workflow when the Mega Drive AAA video curation package exists in the workspace but local command execution, validation, commit or push was previously blocked.

## Inputs

- Current runner status.
- `doc/05_technical/aaa_curation_validation_recovery_plan.json`.
- Current curation manifest and audit report.

## Steps

1. Confirm local process execution works with a simple command.
2. Run the curation validator exactly as declared in the recovery plan.
3. Run the workspace audits required by `AGENTS.md` for the active curation scope.
4. If validation passes, update only curation-package status fields to `validated_curation`.
5. Do not promote ROM, asset, runtime, VDP or AAA release claims.
6. Review git status, stage only intended files, commit, then push if the remote is available.
7. Record any blocker truthfully in the audit report.

## Output

- Validator result.
- Workspace audit result.
- Status changes applied or blocked.
- Commit hash, push result or exact blocker.

## Hard Stop

Do not claim validation, commit or push without command output from the recovered environment.
