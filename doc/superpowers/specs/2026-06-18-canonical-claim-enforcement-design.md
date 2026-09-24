# Canonical Claim Enforcement Design

## Goal

Prevent SGDK Forge agents from promoting delivery status from file inventory,
isolated builds, technically valid assets, screenshots from another ROM, or
reports that do not observe the claimed behavior.

## Architecture

Add one conservative `audit_promotion_claims.ps1` gate. It reads a small claim
manifest plus the canonical project artifacts, computes the strongest status
supported by the weakest consistent evidence, and emits a machine-readable
report. Existing specialized auditors remain authoritative in their domains;
this gate reconciles their outputs and blocks cross-domain extrapolation.

`scene_closeout_gate.ps1` invokes the gate before freshness and final
validation. A manual `scene_closeout_report.json` is evidence input only and
never substitutes the executed gate report.

## Claim model

Each requested promotion declares:

- claim identifier;
- scope;
- ROM SHA-256;
- evidence references;
- integration owner when parallel work exists.

The gate recognizes the delivery-sensitive claims `first_playable`,
`gameplay_rom_aprovada`, `performance_estavel`, `assets_premium`,
`scene_closeout`, `validado_budget`, `ready_for_aaa`, and
`advance_next_phase`.

## Conservative rules

- Evidence ROM hash must match `out/rom.bin`.
- Screenshot-only or `boot_title_only` evidence proves boot/title only.
- Gameplay, audio, and performance require dedicated observed scopes.
- Compiler warnings for impossible comparisons or unreachable logic block
  promotion.
- Modules progress through `module_present`, `integrated`, `reachable`, and
  `runtime_proven`; inventory cannot skip stages.
- Procedural assets stay quarantined regardless of automatic technical score.
- Artistic approval is distinct from technical validation.
- MTR statistics are not MDRT performance evidence.
- Crash, visual corruption, blocked review, or inconsistent reports lower the
  ceiling and block phase advancement.
- Parallel runtime/visual work requires one integration owner.
- Conflicting reports resolve to the least optimistic consistent status.

## Compatibility

Projects without promotion intent may continue to build and validate. Strong
delivery claims require the new manifest or equivalent explicit fields in
canonical reports. Legacy artifacts are accepted as inputs but cannot silently
grant new claims.

## Testing

One fixture suite reproduces all ten false-green pressure scenarios from
Celestial Chase Revive. Each scenario must produce its expected blocker code.
Existing closeout, evidence, placeholder, freshness, and schema tests remain
green.
