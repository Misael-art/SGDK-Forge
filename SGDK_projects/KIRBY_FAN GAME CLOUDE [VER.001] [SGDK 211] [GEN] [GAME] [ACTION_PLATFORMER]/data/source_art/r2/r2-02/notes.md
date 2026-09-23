# R2-02 — escurecimento isolado da camada 5

- Assinatura: Codex
- Parent: `data/source_art/r1/r1-02/layers.png` (sha256 `2624b9cfba697ea83f05c384b40693b5fccd0d480d4181473e1df4b127fe9e52`).
- Escopo: somente `y=730..895` foi alterado; `y=0..729` cobre camadas 1-4 e o separador superior.
- Metodo: escurecimento multiplicativo com snap para a grade RGB333 do projeto; a descontinuidade discreta da paleta foi fechada com 4454 pixels de micro-dither deterministico no backing neutro.
- Aceite medido: luminancia sRGB ponderada da camada 5 = 0.269899; diff de pixel nas camadas 1-4 = 0; 47 cores; 0 pixels ilegais na grade do projeto.
- Limitacao: estudo de composicao, sem promocao para `res/`; a separacao semantica em planos reais e a validacao VDP continuam obrigatorias.
