# archives

Arquivos antigos de limpeza (`cleanup_*`, etc.) ficam só no disco, fora do git.

## 2026-09-23 — harmonização (versionado)

Projetos movidos de `SGDK_projects/` para `archives/2026-09-23/SGDK_projects/` com `git mv`
(renomeações 100% idênticas; histórico preservado com `git log --follow`). Nada foi apagado,
exceto uma pasta vazia com nome inválido (colchete não fechado).

| Projeto | Motivo |
| --- | --- |
| `KIRBY_FAN GAME GROK AX ALPHA [...]` | Experimento Kirby (sem uso por ferramentas) |
| `KIRBY_FAN GAME GROK BUILD [...]` | Experimento Kirby (sem uso por ferramentas) |
| `KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GAME] [ACTION_PLATFORMER]` | Pasta paralela (sem `[GEN]`) com 23 docs que divergem da linha canônica `[GEN]`; guardada para consulta, não fundida |
| `BLUE_CIRCUIT [...]` | Jogo parado desde 2026-09-05 |
| `MARE_BRAVA [...]` | Jogo parado desde 2026-09-05 (exemplos de ferramentas passaram a apontar para HAMOOPIG) |
| `GOTHAM_OVERDRIVE [...]` | Tech demo parada; o gerador `build_gotham_overdrive_assets.py` foi junto para `archives/2026-09-23/tools/` |

Para restaurar um projeto: `git mv "archives/2026-09-23/SGDK_projects/<nome>" "SGDK_projects/<nome>"`.
Saídas de build (`out/`) e arquivos ignorados foram movidos no disco, mas continuam fora do git.

## 2026-09-23 — arquivos soltos da raiz (`root_loose/`, só no disco)

Curadoria pela `doc/ROOT_LOOSE_FILES_POLICY.md`: build/depuração soltos e relatórios de agentes sem projeto
dono saíram de `out/` para `archives/2026-09-23/root_loose/out/` (ignorado pelo git; binários e reports).
A evidência do Mugenesis foi para o próprio projeto (`Mugenesis_Demo/out/evidence/`). Origem, destino,
hashes e rollback: `doc/curation/2026-09-23-root-loose-manifest.json`.

`_agent_training` foi devolvido a `SGDK_projects/`: o `AGENTS.md` define esse local como canônico para treino.
