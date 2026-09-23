# AAA Video Curation Handoff

Status: `candidate_applied_not_verified`

Use this handoff when `sgdk-build-wrapper-operator` prepares, validates or closes workspace/project automation.

## New Required Routes

- Expose `validate_aaa_video_curation.ps1` as the package validator for the video-curation guardrails.
- Keep curation validation separate from ROM/runtime validation.
- Route release or AAA claims to `aaa-pipeline-guardian` and `emulator-vdp-evidence-curator`.

## Wrapper Rules

- Do not treat curation validation as game delivery.
- Do not claim commit/push or validator pass unless command output exists.
- Record runner blockers explicitly when process execution fails.
