# 01 - Visao Geral

## Intencao

`Pequeno Principe Cronicas das Estrelas` foi desenhado como um jogo-estudo:

- emocional na superficie
- rigoroso no hardware por baixo
- util para aprendizado de SGDK 211 em codigo real

## Escopo atual

O slice entregue nesta versao contem:

- `B-612`
- `Planeta do Rei`
- `Planeta do Lampiao`
- `Deserto das Estrelas`

Cada planeta tem:

- um micro-objetivo
- um encontro narrativo curto em `window plane`
- um conjunto de tecnicas visuais dominantes
- uma entrada destravavel no codex tecnico

## Loop de jogo

1. explorar um planeta curto
2. interagir com o elemento narrativo central
3. absorver o encontro curto daquele capitulo
4. ler o efeito visual em contexto
5. viajar para o proximo mundo

## Pilares

- `Pedagogia integrada`: o jogo nao vira slideshow de tecnica
- `Hardware real`: sem `float`, sem bibliotecas externas, sem excesso de DMA
- `Arquitetura clara`: state machine, cenas por planeta, H-Int centralizado
- `Assets disciplinados`: placeholders em codigo agora, `rescomp` depois
