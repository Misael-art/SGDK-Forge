# Valis 01 [VER.001] [SGDK 211] [GEN] [TEMPLATE] [PLATAFORMA]

Este projeto foi organizado como um **template pedagogico minimo** para quem
quer estudar um fluxo simples de jogo de plataforma no Mega Drive com SGDK.
Ele reaproveita um pequeno conjunto de assets ja existentes e os transforma em
um exemplo funcional de fundo + sprites.

## O que voce encontra aqui

- `src/main.c`: exemplo didatico que desenha o fundo e tres sprites
- `res/gfx.res`: fundo principal
- `res/sprites.res`: protagonista, inimigo e item
- `doc/`: guias de onboarding e desenvolvimento

## Fluxo recomendado

1. Rode `build.bat`.
2. Rode `run.bat`.
3. Abra `src/main.c`.
4. Troque os assets em `res/` e observe o comportamento da ROM.

## Controles do exemplo

- `Esquerda` e `Direita`: muda o sprite destacado
- `A`: seleciona a heroina
- `B`: seleciona o inimigo
- `C`: seleciona o item

## Objetivo pedagogico

O foco aqui nao e entregar um jogo pronto. A ideia e oferecer um ponto de
partida organizado para iniciantes entenderem:

- como declarar recursos no ResComp
- como carregar paletas e imagens
- como instanciar sprites e atualizar a tela em loop
