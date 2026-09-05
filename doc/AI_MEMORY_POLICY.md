# SGDK Forge managed ai-memory policy.

# AI Memory Policy

Status: `consultive_optional_layer`

## Role

`ai-memory` may be used as a project-local, cross-agent memory aid for handoff,
search and operational recall.

It is not a source of truth for SGDK Forge.

## Authority

Authoritative state remains, in order:

- `doc/10-memory-bank.md` inside a project, or `doc/06_AI_MEMORY_BANK.md` for workspace scope;
- GDD/TDD/spec/manifests/changelog;
- validators and reports in `out/logs/`;
- BlastEm evidence tied to the same ROM hash;
- SGDK headers and wrapper contracts.

`ai-memory` retrieval can suggest where to look, but every decision must be
validated by opening the canonical files or evidence it references.

## Controlled Integration

- `.ai-memory.toml` markers are allowed as routing hints.
- Root marker scope is `workspace`; project markers should be created inside
  each project by `adopt_project_methodology.ps1` or
  `prepare_ai_memory_integration.ps1 -ProjectRoot`.
- The wrapper never runs `install-hooks --apply`, `install-mcp --apply`,
  `bootstrap`, `auto-improve`, `pending-writes approve` or any global client
  mutation automatically.
- Auto-improvement must remain pending for human review. For ai-memory configs,
  use `[auto_improve] require_approval = true` and prefer disabling the
  scheduler until the pilot is approved.
- No ai-memory page can promote `documentado` to `implementado`, `buildado`,
  `testado_em_emulador`, `validado_budget`, `MESTRE_*`, `stable`, `release` or
  `ready_for_aaa`.

## First Host Startup

`assert_agent_environment.ps1` calls `prepare_agent_environment.ps1`, which
calls `prepare_ai_memory_integration.ps1`. This prepares local markers and this
policy with minimal output. Missing ai-memory CLI/server is reported as optional
and does not block the SGDK framework.

## Human Setup Boundary

Installing ai-memory itself, wiring MCP/hook clients, configuring bearer tokens
or selecting an LLM provider is a host/user action. Do it from the same
environment that launches the agent, then verify the agent can call
`memory_status` or equivalent.
