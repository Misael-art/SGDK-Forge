# Biblioteca de Retencao de Conhecimento

Esta base existe para reduzir perda de contexto em tarefas complexas de arte e runtime.

Ela nao e codigo produtivo.
Ela e few-shot pedagogico e memoria reproduzivel.

## Pontos de entrada canonicos

- `tools/sgdk_wrapper/.agent/lib_case/art-translation/index.json`
- `tools/sgdk_wrapper/.agent/lib_case/sgdk-runtime/index.json`
- `tools/sgdk_wrapper/.agent/lib_case/video-curation-2026-06-16/index.json`
- `tools/sgdk_wrapper/.agent/lib_case/project-learning/index.json`
- `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md`
- `doc/05_technical/92_sgdk_engine_pattern_registry.json`

## Lote curation_batch_2026_06_16

- `video-curation-2026-06-16/` contem 16 case studies de referencia
  (`phase6_case_studies_materialized_candidate`, `evidence_grade: E1_text`).
- Sao referencia/few-shot, nao skills, nao schemas e nao prova de runtime.
- Divergencia registrada: `declared_case_count_mismatch: declared_14_listed_16`.

## Regras

- `index.json` resolve taxonomia e casos
- `registry` resolve ids e promocao de padrao
- `lib_case` resolve few-shot executavel
- nada daqui promove canon automaticamente

## Casos de aprendizado de projeto

- `project-learning/celestial-chase-revive-2026-06-16/`
  registra licoes locais de um `aaa_game` com specs, runtime seed e evidencia
  limitada ao seed. O caso ensina reconciliacao de status, pre-runtime
  contract closure, input/transition ownership e limites de placeholder.
  Evidencia: `E1_project_artifact`; nao e prova de gameplay, budget ou AAA.

## Casos de falha que devem ser lembrados

- `palette_inflated_png`
- `vram_overflow_budget`
- `image_map_streaming_decision`

Esses casos existem para impedir que a IA repita os mesmos erros caros em diagnostico e promocao de cena.

## Casos de exploracao controlada

Nem todo caso forte da biblioteca e uma falha.
Alguns existem para ensinar ao agente como abrir alternativas sem perder coerencia.

Exemplo atual:

- `case_scene_route_variants_city_crop`
  - mesma cena
  - mesmo crop
  - multiplas rotas validas de atmosfera
  - escolha humana congelada antes de budget final e runtime
