# Agent Startup Environment

Use este workflow no inicio de uma sessao em qualquer superficie de agente/IDE deste workspace.

## Objetivo

Garantir que o agente entre com o contexto SGDK carregado, pontes de skills validas, Graphify consultivo e ai-memory opcional preparados sem criar uma segunda fonte de verdade.

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
- `graphify_start_failed` ou `graphify_timeout` devem ser reportados como blocker de ferramenta externa, sem diagnostico longo nem retry infinito.
- Depois de consultar, abra os arquivos canonicos citados antes de decidir ou editar.
- Obsidian e apenas cockpit humano opcional; nao fecha gate.

## Uso do ai-memory

- `ai-memory` e opcional e consultivo.
- O wrapper prepara apenas `.ai-memory.toml`, `doc/AI_MEMORY_POLICY.md` e report local.
- Nao instale hooks/MCP globais automaticamente a partir deste workflow.
- Nao rode `bootstrap`, `auto-improve` ou aprovacao de pending writes sem pedido humano explicito.
- Qualquer memoria recuperada deve apontar para arquivo canonico, report ou evidencia antes de influenciar decisao.

## Primeiro uso

`assert_agent_environment.ps1` chama `prepare_agent_environment.ps1 -InstallMissing` automaticamente, grava `graphify-out/AGENT_ENVIRONMENT_REPORT.json`, prepara `out/logs/ai_memory_integration_report.json`, serializa chamadas concorrentes por lock global e pode instalar:

- PowerShell 7 (`pwsh`) via `winget`;
- `uv` via `winget`;
- Graphify via `uv tool install graphifyy`.

O ai-memory CLI/servidor nao e instalado automaticamente; quando ausente, a camada fica preparada como rota opcional. Se o host bloquear instalacao automatica de dependencias obrigatorias, o agente deve reportar o blocker e nao improvisar outro indice.
