# Graphify + Obsidian (Cockpit Consultivo)

## Papel de cada ferramenta

- **Fonte de verdade (inalterada):** os arquivos canônicos do workspace e dos projetos (hierarquia em `AGENTS.md`, rules/workflows/skills em `tools/sgdk_wrapper/.agent/`, registries/schemas/validators, GDD/TDD, manifests e evidência BlastEm).
- **Graphify:** índice consultivo para localizar arquivos, símbolos e relações. Não é autoridade e não “promove” técnica, status ou decisão.
- **Obsidian:** cockpit humano para navegação/consulta. Não é dependência de build, não é requisito de validação e não fecha gate.

## Escopo do índice

O grafo deve cobrir somente:

- `tools/sgdk_wrapper/.agent/`
- `doc/05_technical/`
- `doc/07_game_design/`
- `doc/06_AI_MEMORY_BANK.md`
- `doc/AI_MEMORY_POLICY.md`

Controle de escopo: `.graphifyignore` na raiz do workspace.

## Artefatos gerados (não canônicos)

- `graphify-out/` (grafo, relatórios e memória do Graphify) é **gerado/cache** e deve permanecer fora do Git.

## Fluxo query-first (sem alucinação)

0. No primeiro uso da sessão, preparar o ambiente:
   - `powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/assert_agent_environment.ps1`
1. Verificar se o grafo está fresh:
   - `pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action status`
2. Se stale:
   - `pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action update`
3. Consultar:
   - `pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action query -Question "..."`
4. Para qualquer decisão/edição:
   - abrir os arquivos canônicos citados e validar pela hierarquia de verdade.

## Regra de freshness

- O wrapper `tools/sgdk_wrapper/graphify_forge.ps1` bloqueia `query` quando o grafo está stale.
- O wrapper deve ser chamado por `pwsh`/PowerShell 7; `powershell.exe` legado não é a superfície suportada para consultas Graphify.
- Operacoes externas do Graphify rodam com timeout controlado pelo wrapper. Se o executavel for bloqueado pelo host, o status deve ser `graphify_start_failed`, nao stack trace solto nem espera indefinida.
- O preparo de ambiente grava `graphify-out/AGENT_ENVIRONMENT_REPORT.json` e serializa updates concorrentes para evitar disputa de cache quando multiplos agentes iniciam juntos.
- Sempre que editar `tools/sgdk_wrapper/.agent/`, `doc/05_technical/`, `doc/07_game_design/` ou `doc/06_AI_MEMORY_BANK.md`, trate o grafo como stale e rode `update` antes de usar resultados do grafo em decisões.
- Um grafo com violação de escopo é inválido mesmo que timestamps e snapshot indiquem frescor: `graph_status` deve virar `stale` com `reason=graph_scope_violation` e a correção exigida é `-Action build`.

## Limites e riscos

- Um grafo fresh ainda pode estar incompleto: ele não substitui leitura direta, headers do SGDK nem validações.
- O grafo não prova runtime, budget ou qualidade AAA. Gates continuam sendo build/validators + BlastEm + evidência rastreável.

## Uso recomendado no Obsidian (opcional)

- Abra um vault apontando para a raiz do workspace.
- Não versione `.obsidian/` (config local).
- Use Obsidian para navegar e anotar, mas trate qualquer anotação como auxiliar; a decisão canônica continua nos arquivos canônicos do repo.

## Integração com IDEs/agentes (opcional)

- O Graphify expõe `graphify install --platform <...>` para instalar integrações em diretórios de configuração do usuário (fora do repo).
- Não trate isso como instalação project-scoped e não permita que substitua ou duplique regras canônicas do workspace.
