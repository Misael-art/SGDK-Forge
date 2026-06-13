# Lib Case — SGDK Runtime

Esta biblioteca guarda casos minimos de codigo e runtime SGDK 2.11.

Ela existe para preservar aprendizado real de:

- API correta
- ordem do loop
- reset de cena
- decisao entre `IMAGE` e `MAP`
- palette swap
- H-Int, line scroll e priority split
- HUD e fonte custom

## Regra

Isto nao e codigo produtivo.
Sao casos didaticos para few-shot operacional.

## Ponto de entrada

- `tools/sgdk_wrapper/.agent/lib_case/sgdk-runtime/index.json`

Cada caso contem:

- `README.md`
- `minimal_example.c`
- `why_it_exists.md`
- `engine_sources.json`
