# Canonical Claim Enforcement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reproducible claim-to-evidence enforcement that blocks the ten Celestial Chase false-green scenarios.

**Architecture:** A standalone promotion audit reconciles ROM identity, evidence scope, warnings, integration reachability, asset provenance, executed gates, metric provenance, review state, and phase blockers. The scene closeout workflow invokes it as a required step.

**Tech Stack:** PowerShell 7/Windows PowerShell-compatible scripts, JSON Schema draft-07, existing SGDK wrapper CI fixtures.

---

### Task 1: Pressure fixtures

**Files:**
- Create: `tools/sgdk_wrapper/ci/test_promotion_claim_enforcement.ps1`

- [ ] Write ten fixtures with expected blocker codes.
- [ ] Run the suite and verify RED because the canonical auditor is absent.

### Task 2: Claim contracts

**Files:**
- Create: `tools/sgdk_wrapper/schemas/promotion_claim_manifest.schema.json`
- Create: `tools/sgdk_wrapper/schemas/promotion_claim_audit_report.schema.json`

- [ ] Define explicit claims, scopes, ROM hashes, evidence, owner, integration,
  metric provenance, visual state, review state, and phase state.
- [ ] Validate minimal passing and failing fixture shapes.

### Task 3: Canonical auditor

**Files:**
- Create: `tools/sgdk_wrapper/audit_promotion_claims.ps1`

- [ ] Read the current ROM and canonical artifacts.
- [ ] Emit deterministic blocker codes for all ten pressure cases.
- [ ] Reconcile conflicts to the least optimistic status.
- [ ] Write `out/logs/promotion_claim_audit_report.json`.
- [ ] Run the pressure suite and verify GREEN.

### Task 4: Closeout integration

**Files:**
- Modify: `tools/sgdk_wrapper/scene_closeout_gate.ps1`
- Modify: `tools/sgdk_wrapper/ci/test_scene_closeout_gate.ps1`

- [ ] Add `promotion_claim_audit` as a required closeout step.
- [ ] Preserve plan-only and legacy project behavior.
- [ ] Verify closeout tests.

### Task 5: Canonical documentation

**Files:**
- Modify: `tools/sgdk_wrapper/.agent/ARCHITECTURE.md`
- Modify: `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
- Modify: `tools/sgdk_wrapper/.agent/workflows/production-loop.md`
- Modify: `tools/sgdk_wrapper/.agent/skills/governance/aaa-pipeline-guardian/SKILL.md`
- Modify: `tools/sgdk_wrapper/.agent/skills/operation/sgdk-build-wrapper-operator/SKILL.md`

- [ ] Document the claim ceiling and MTR/MDRT distinction.
- [ ] Require integration ownership and phase blocking.

### Task 6: Regression and closeout report

**Files:**
- Create: `doc/curation/celestial_claim_enforcement_2026-06-18.md`
- Modify: `doc/06_AI_MEMORY_BANK.md`
- Modify: `doc/agent_learning/changelog_2026-06-18.md`

- [ ] Run pressure, closeout, evidence, placeholder, freshness, and schema tests.
- [ ] Record root causes, enforcement mapping, compatibility, residual risks,
  and promotion candidates as `not_applied`.
