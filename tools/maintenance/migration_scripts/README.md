# migration_scripts

Scripts one-off de migração e debug, movidos de `SGDK_templates/` em 2026-03-19.

## Conteúdo

| Script | Propósito | Status |
|--------|-----------|--------|
| `debug_build.py` | Executa build do SimpleGameStates_Elite para debug | Referência histórica |
| `rename_fix.py` | Renomeou `SimpleGameStates [VER.1.0]...` → `SimpleGameStates_Elite` | Já executado; obsoleto |
| `run_build_v2.py` | Build com short path e log em `build_log_p.txt` | Referência histórica |
| `verify_elite_fix.py` | Verifica se ROM foi gerada após build | Referência histórica |

## Uso

Estes scripts contêm caminhos hardcoded para `SGDK_templates/`. Para reutilizar, ajuste as variáveis `base_dir` conforme o ambiente local.

Não fazem parte do fluxo canônico de build. O build oficial usa `tools/sgdk_wrapper/`.
