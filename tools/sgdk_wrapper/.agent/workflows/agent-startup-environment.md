# Agent Startup Environment

Use este workflow no inicio de uma sessao em qualquer superficie de agente/IDE deste workspace.

## Objetivo

Garantir que o agente entre com o contexto SGDK carregado, pontes de skills validas e Graphify consultivo preparado sem criar uma segunda fonte de verdade.

## Passos obrigatorios

1. Carregue `AGENTS.md` e diga `[Contexto MD Carregado]`.
2. Rode o preparo de ambiente:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/assert_agent_environment.ps1
   ```

3. Se a tarefa for direta e clara, prossiga sem abrir menu.
4. Se o usuario pedir `menu`, `modo`, `iniciar`, `abrir sessao` ou a intencao estiver ambigua, siga `tools/sgdk_wrapper/.agent/workflows/agent-session-bootstrap.md`.

## Uso do Graphify

- Use Graphify apenas via `pwsh` e pelo wrapper `tools/sgdk_wrapper/graphify_forge.ps1`.
- Nunca use `graphify query` direto.
- `graph_status=stale` bloqueia uso do grafo para decisao.
- Depois de consultar, abra os arquivos canonicos citados antes de decidir ou editar.
- Obsidian e apenas cockpit humano opcional; nao fecha gate.

## Primeiro uso

`assert_agent_environment.ps1` chama `prepare_agent_environment.ps1 -InstallMissing` automaticamente, grava `graphify-out/AGENT_ENVIRONMENT_REPORT.json`, serializa chamadas concorrentes por lock global e pode instalar:

- PowerShell 7 (`pwsh`) via `winget`;
- `uv` via `winget`;
- Graphify via `uv tool install graphifyy`.

Se o host bloquear instalacao automatica, o agente deve reportar o blocker e nao improvisar outro indice.
