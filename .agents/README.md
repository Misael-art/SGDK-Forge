# `.agents/` no root canônico

Esta pasta existe como **ponte de compatibilidade** entre a superfície `.agents/skills` (formato consumido nativamente por ferramentas como Codex) e a fonte canônica real do framework `.agent` que vive em `tools/sgdk_wrapper/.agent/`.

## Layout

```
.agents/
  README.md          ← este arquivo
  skills/            ← symlink relativo -> ../tools/sgdk_wrapper/.agent/skills
```

## Política

- **A fonte canônica é `tools/sgdk_wrapper/.agent/skills`** — nunca duplique skills em uma segunda árvore paralela.
- No primeiro uso de uma sessão, qualquer agente deve rodar:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/assert_agent_environment.ps1
  ```
- Graphify é consultivo e deve ser usado apenas via `pwsh -File tools/sgdk_wrapper/graphify_forge.ps1`; nunca use `graphify query` direto.
- **Esta ponte é um symlink relativo** — não um diretório real. Se ferramentas de migração quebrarem o link, recrie com:
  ```powershell
  New-Item -ItemType SymbolicLink -Path ".agents\skills" -Target "..\tools\sgdk_wrapper\.agent\skills"
  ```
- Se o ambiente bloquear symlink, uma junction local pode ser usada como fallback, mas o alvo preferido permanece relativo para facilitar portabilidade.
- O link aponta **apenas para o root canônico atual**. Se o workspace for renomeado ou movido, valide a ponte.
- Modos de sessão, menu e troca de perspectiva são workflows em `tools/sgdk_wrapper/.agent/workflows/`, não uma segunda árvore de skills.
- O menu de sessão usa `tools/sgdk_wrapper/.agent/workflows/agent-session-bootstrap.md` e `doc/agent_session_state.json`.

## Por que não copiar `skills/` para cá?

- Skills ocupam ~0.5 MB mas o conteúdo evolui frequentemente junto com `tools/sgdk_wrapper/.agent/`. Manter como ponte evita drift entre as duas árvores.
- Cópia real levaria a cenários onde uma skill é atualizada em um lugar e esquecida no outro, quebrando o framework.
