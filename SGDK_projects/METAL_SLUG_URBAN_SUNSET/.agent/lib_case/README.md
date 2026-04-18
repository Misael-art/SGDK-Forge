# Biblioteca de Retencao de Conhecimento

Esta base existe para reduzir perda de contexto em tarefas complexas de arte e runtime.

Ela nao e codigo produtivo.
Ela e few-shot pedagogico e memoria reproduzivel.

## Pontos de entrada canonicos

- `tools/sgdk_wrapper/.agent/lib_case/art-translation/index.json`
- `tools/sgdk_wrapper/.agent/lib_case/sgdk-runtime/index.json`
- `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md`
- `doc/05_technical/92_sgdk_engine_pattern_registry.json`

## Regras

- `index.json` resolve taxonomia e casos
- `registry` resolve ids e promocao de padrao
- `lib_case` resolve few-shot executavel
- nada daqui promove canon automaticamente

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
