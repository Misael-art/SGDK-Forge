# Changelog de Curadoria Canonica - 2026-06-09

## Curadoria MUGEN Showdown + HYBRIDO Muay Thai

Escopo: assimilar licoes qualificadas dos estudos:

- `_agent_training/[ESTUDO]_mugen_sff_showdown_v1`
- `_agent_training/HYBRIDO_MUAY_THAI [VER.001] [SGDK 211] [GEN] [ESTUDO] [LUTA]`

## Canonizado

- `scene_tilemap_conversion_report.schema.json` agora suporta
  `world_tilemap_with_camera_window_streaming`.
- Streaming por janela exige `world_dimensions`, `viewport_dimensions` e
  `runtime_streaming`.
- `BIN_CUSTOM_TILE_GRAPHICS_AND_TILEMAP_WINDOW_STREAMING` foi aceito como
  estrategia de empacotamento, sem virar prova de residencia VDP.
- `tilemap_flag_report.schema.json` aceita `frame_index` opcional por entrada.
- `mugen_sff_fixture_contract.json` passou a exigir reports de conversao,
  flags, conflito de paleta, `res_graph`, BlastEm e evidencia VDP/VRAM.
- `megadrive-vdp-budget-analyst` foi endurecido contra promocao de budget por
  estimativa ou por BIN customizado sem medicao de runtime.
- `visual-excellence-standards` reforcou que model sheet de personagem critico
  so vira fonte de producao quando escala, turnaround, marcadores e mapa de
  material/paleta estiverem travados.
- `learning_owner_catalog.json` ganhou rota conservadora para recorrencias de
  MUGEN/window streaming.

## Nao Promovido

- `tools/mugen2sgdk` permanece `legacy_gui_tool_without_cli` ate tool-first
  audit, fixture e evidencia.
- Parser/export MUGEN nao foi promovido para `MESTRE`.
- HYBRIDO nao gerou skill nova: as licoes foram absorvidas nas skills visuais
  existentes.
- Nenhum projeto, ROM, asset ou tecnica recebeu status de entrega.

## Validacao

- `py tools/sgdk_wrapper/ci/test_schema_contract_gates.py`: `73/73`.
- `py tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`: passed.
- `py tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`: ok.
- JSON parse: schemas alterados, fixture MUGEN, learning owner catalog e
  framework manifest validos.

Regra factual: esta curadoria e de framework operacional. Ela melhora futuros
trabalhos de conversao MUGEN/tilemap largo e julgamento visual de lutadores,
mas nao substitui ROM rodando, BlastEm, budget medido e aprovacao humana.
