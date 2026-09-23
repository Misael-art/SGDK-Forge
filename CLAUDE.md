# SGDK Forge - Claude Entry Point

Leia `AGENTS.md` primeiro e diga `[Contexto MD Carregado]` antes de propor acao.

No primeiro uso da sessao, prepare o ambiente:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/assert_agent_environment.ps1
```

Use Graphify apenas como indice consultivo:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/graphify_forge.ps1 -Action status
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/graphify_forge.ps1 -Action query -Question "..."
```

Nunca use `graphify query` direto. Antes de decidir ou editar, abra os arquivos canonicos citados pelo grafo.
