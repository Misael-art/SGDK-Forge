# Como Integrar

Para reaproveitar este modulo em um projeto compilavel:

1. Copie `snapshot/source/cenarios.c` para `src/`.
2. Copie `snapshot/source/include/cenarios.h` e `commun.h` para `inc/`.
3. Crie um arquivo `.res` que gere `cenarios_res.h` com as imagens esperadas.
4. Ajuste os nomes `gfx_bgb1` ate `gfx_bgb7` para casar com seus recursos.
5. Chame `CEN_init(...)` na inicializacao do fundo.
6. Chame `CEN_Anima(...)` no loop principal quando quiser trocar frames.

## Melhor uso pedagogico

Integre primeiro em um projeto pequeno de teste antes de levar para uma engine
grande. Isso facilita entender o que e codigo generico e o que e dependencia do
projeto original.
