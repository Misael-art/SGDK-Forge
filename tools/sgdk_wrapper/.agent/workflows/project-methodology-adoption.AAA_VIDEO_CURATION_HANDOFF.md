# AAA Video Curation Handoff

Status: `candidate_applied_not_verified`

Use this handoff when adopting methodology for training, laboratory or curation projects that claim Mega Drive AAA techniques.

## New Required Route

When a project explicitly imports external video-derived techniques, run or schedule:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_aaa_video_curation.ps1
```

## Methodology Rules

- Keep direct sources, aggregate claims and backlog claims separated.
- Do not promote curation package status without local validation.
- Do not let curation validation replace project context, hygiene, methodology, freshness or learning audits.
- Game delivery still requires emulator evidence according to `AGENTS.md`.
