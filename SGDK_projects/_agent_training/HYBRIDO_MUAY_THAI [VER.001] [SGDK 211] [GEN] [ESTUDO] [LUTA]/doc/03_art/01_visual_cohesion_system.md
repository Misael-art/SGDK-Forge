# Visual Cohesion System - Hibrido Muay Thai

## Identidade visual obrigatoria

- Pele bronzeada/escura com rampas quentes.
- Braco direito de lava com pedra escura e rachaduras laranja/vermelhas.
- Calcao preto com detalhes dourados.
- Faixas brancas sujas em maos e pes.
- Outline escuro duro, sem anti-aliasing.
- Silhueta de Muay Thai: guarda alta, base baixa, peso nos pes, chutes/joelho com eixo claro.

## Paleta

PAL2 e PAL3 nao sao conveniencia tecnica; eles preservam semantica.

- PAL2: corpo, pele, cabelo, faixas, calcao, pedra escura.
- PAL3: magma, brilho interno, fogo, impacto.

Um material importante nao pode desaparecer por quantizacao global. Se pele,
calcao, pedra e lava virarem massas cinza parecidas, a traducao falhou mesmo
que o PNG esteja indexado.

## Acting

Idle, walk e golpe nao podem compartilhar a mesma face neutra.

- `idle`: olhar frio e focado, boca fechada.
- `walk_step`: foco no oponente, leve tensao.
- `teep`/`knee`/`punch`: maxilar tenso, dentes ou boca aberta de kiai, olhos estreitos.
- `hurt`: dor visivel e cabeca reagindo ao golpe.

## Escala

48x64 e uma escala de sintese. A fonte high-res deve ser reinterpretada em
clusters nativos: cabeca, olhos, torso, calcao, bandagens e braco de lava. Nao
ha espaco para preservar textura detalhada se isso destruir a leitura de forma.
