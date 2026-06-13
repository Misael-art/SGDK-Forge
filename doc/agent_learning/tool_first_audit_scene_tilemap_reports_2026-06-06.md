# Tool-first audit: scene/tilemap conversion reports (2026-06-06)

Status: `tool_first_audit_completed`

## Goal

Decidir, antes de qualquer nova automacao, se o workspace ja possui ferramentas suficientes (ou extensoes de baixo risco) para produzir os reports canonicos:

- `scene_tilemap_conversion_report.json`
- `tilemap_flag_report.json`
- `per_tile_palette_conflict_report.json`

## Scope (tools audited)

- `tools/image-tools/analyze_aesthetic.py`
- `tools/image-tools/analyze_translation_case.py`
- `tools/image-tools/analyze_source_semantics.py`
- `tools/sgdk_wrapper/res_graph_audit.ps1`
- `tools/sgdk_wrapper/lib/res_graph.psm1`
- `tools/mugen2sgdk/`

## Findings

### analyze_aesthetic.py

File: [analyze_aesthetic.py](file:///f:/Projects/Sgdk%20Forge/tools/image-tools/analyze_aesthetic.py)

- Existe dedup com H/V/HV flip por tile 8x8 (flip-aware) em `reuse_opportunity`.
- O output e um report estetico; nao entrega um tilemap flag report nem um contrato de conversao de cena.

### analyze_translation_case.py

File: [analyze_translation_case.py](file:///f:/Projects/Sgdk%20Forge/tools/image-tools/analyze_translation_case.py)

- Existe `tile_budget_stats` com `unique_ratio` (dedup exato, sem flip-aware).
- O output e orientado a "translation case" (manifest) e nao emite os 3 reports canonicos com nomes/campos exigidos.

### analyze_source_semantics.py

File: [analyze_source_semantics.py](file:///f:/Projects/Sgdk%20Forge/tools/image-tools/analyze_source_semantics.py)

- Existe pipeline de `semantic_parse_report` e tipificacao (tile_cluster/overlay_cluster etc).
- Nao emite dedup/flag/palette-conflict reports por si so; pode ser insumo do fluxo.

### res_graph_audit.ps1

File: [res_graph_audit.ps1](file:///f:/Projects/Sgdk%20Forge/tools/sgdk_wrapper/res_graph_audit.ps1)

- Gera `out/logs/res_graph_report.json` e estrutura budget de VRAM por ranges.
- Nao gera nem valida os 3 reports novos; mas e um gate relevante para entregar junto.

### lib/res_graph.psm1

File: [res_graph.psm1](file:///f:/Projects/Sgdk%20Forge/tools/sgdk_wrapper/lib/res_graph.psm1)

- Existe `Get-SgdkPngTileStats` (dedup exato, sem flip-aware) para estimativas de tiles.
- Nao ha suporte a tilemap flags nem a per-tile palette conflicts.

### tools/mugen2sgdk

Dir: [tools/mugen2sgdk](file:///f:/Projects/Sgdk%20Forge/tools/mugen2sgdk/)

- Conteudo e um bundle binario GUI (Tkinter) sem codigo-fonte, sem CLI e sem testes no repo.
- Presenca de `_tkinter.pyd`, `tcl86t.dll`, `tk86t.dll` e `mugen2sgdk.exe` indica app GUI empacotado.
- Recomendacao: classificar como `legacy_gui_tool_without_cli`.

## Decision

Decision: `extend + create_minimal_new_tool`

## Chosen path

### 1) Extender de baixo risco (recomendado)

- Estender `tools/image-tools/analyze_translation_case.py` para expor, no bloco `tile_budget_stats`, estatisticas flip-aware adicionais (dedup com H/V/HV) reutilizando a mesma logica existente em `analyze_aesthetic.py`.
- Motivo: reduz divergencia de metricas entre "unique_ratio" (case analyzer) e "flip reuse" (aesthetic analyzer).

### 2) Criar ferramenta nova (justificada, minima)

- Criar `tools/image-tools/analyze_tilemap_dedup_flags.py` para gerar os 3 reports canonicos com nomes/campos exigidos.
- Justificativa: nenhuma ferramenta existente emite `tilemap_flag_report` nem `per_tile_palette_conflict_report` em formato consumivel por `validate_resources.ps1` e `megadrive-vdp-budget-analyst`. Forcar isso dentro de `validate_resources.ps1` violaria a regra (validator nao gera).

## Explicit non-goals (enforcement rule)

- `validate_resources.ps1` nao deve gerar reports automaticamente. Ele valida presenca, schema e coerencia.

## Risk notes

- Paths Windows com espacos e colchetes: qualquer acesso em PowerShell deve usar `-LiteralPath`.
- Saida CLI deve ser ASCII-safe (CP1252). Sem Unicode decorativo.
- Report schema: JSON invalido ou sem schema valido deve ser tratado como ausente.
- Report scope: nenhum report pode apontar para path absoluto fora do projeto/workspace.

