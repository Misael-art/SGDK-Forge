# Processo de Traducao Visual — Armored Sentinel

## Objetivo

Traduzir uma referencia autoral high-res para uma leitura convincente em Mega Drive sem tratar o PNG como ilustração solta. O alvo foi uma cena comparativa `BASIC vs ELITE` com o mesmo personagem, preservando massa, material e separação de planos.

## Referencia autoral

- Arquivo-base: `doc/03_art/reference/armored_sentinel_reference.png`
- Intencao visual:
  - armadura com brilho controlado
  - tecido escuro para separar volume
  - fundo atmosferico com hierarquia clara entre profundidade e plano jogavel

## Como a paleta foi reduzida

- O personagem foi comprimido para a logica de `15 cores + transparencia`.
- O lane `basic` deliberadamente desperdiça rampa tonal e usa transicoes mais chapadas.
- O lane `elite` concentra a rampa em:
  - brilho especular do metal
  - meio-tom estrutural
  - sombra principal
  - sombra de recorte
- A cor mais clara foi reservada para leitura de material, nao para "embelezar" borda aleatoria.

## Onde o dithering entrou

- No lane `basic`, o dithering foi minimizado ou deixado sem funcao dramatica.
- No lane `elite`, o dithering entrou em dois pontos:
  - transicao atmosferica do fundo
  - materiais que precisavam simular degradê sem gastar cores demais
- Regra aplicada:
  - dithering so entra quando descreve volume, material ou distancia
  - dithering sem funcao narrativa ou estrutural conta como ruido

## Como o personagem foi protegido do fundo

- O contraste entre `BG_B` e `BG_A` foi tratado antes da escolha de matiz.
- `BG_B` ficou menos agressivo em contraste e densidade.
- `BG_A` manteve estrutura, mas sem roubar leitura do personagem.
- O lane `elite` recebeu silhueta mais clara e leitura interna mais organizada.
- A priorizacao foi:
  1. separar o pico de leitura do personagem
  2. conter a energia visual do fundo
  3. usar textura como suporte, nao como protagonista

## O que foi sacrificado

- Microdetalhes high-res que nao sobrevivem em 320x224
- gradientes limpos demais
- volumes sutis que dependiam de anti-alias moderno

## O que foi preservado

- massa principal do sentinela
- leitura de metal vs tecido
- hierarquia de planos da cena
- contraste entre interpretacao `basic` e `elite`

## Heuristica consolidada

- Se o fundo parecer mais "afiado" do que o personagem, o problema nao e falta de detalhe no personagem: e excesso de agressividade no plano errado.
- Se o metal perde leitura apos reduzir paleta, a cor clara esta mal alocada ou o meio-tom nao sustenta a forma.
- Se a silhueta depende de ampliar a imagem para funcionar, ela ainda nao foi resolvida para Mega Drive.
