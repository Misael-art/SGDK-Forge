# HAMOOPIG main — Nota de Compilacao

Este projeto e um **codigo de referencia** da engine HAMOOPIG.
Ele contem apenas o `main.c` (324KB) com toda a logica da engine de luta
documentada, mas **nao inclui os recursos graficos e sonoros** (sprites,
backgrounds, sons) necessarios para compilar.

## Por que nao compila?

O `main.c` inclui `sprite.h`, `gfx.h` e `sound.h` — estes headers sao
gerados automaticamente pelo ResComp a partir de arquivos `.res` que
definem os sprites, imagens e sons do jogo. Como este projeto nao tem
a pasta `res/` com esses recursos, a compilacao falha.

## Para que serve?

- **Estudo**: Leia o `main.c` para entender a arquitetura da engine
- **Referencia**: Use como base para seus projetos de luta
- **Documentacao**: Consulte o `README.md` para a lista completa de funcoes

## Projetos compilaveis da engine HAMOOPIG

Se voce quer compilar e testar, use uma das versoes completas:

- `HAMOOPIG [VER.001] [SGDK 211]` — Versao basica funcional
- `HAMOOPIG [VER.1.0] [SGDK 211]` — Versao completa
- `HAMOOPIG [VER.1.0 CPU6.2] [SGDK 211]` — Versao com otimizacoes de CPU
- `KOF94 HAMOOPIG MINIMALIST [VER.001] [SGDK 211]` — Versao minimalista
