# Visual Cohesion System - Hibrido Muay Thai

## Identidade visual obrigatoria

- Pele bronzeada/escura com rampas quentes.
- Braco direito de lava com pedra escura e rachaduras laranja/vermelhas.
- Calcao preto com detalhes dourados.
- Faixas brancas sujas em maos e pes.
- Outline escuro duro, sem anti-aliasing.
- Silhueta de Muay Thai: guarda alta, base baixa, peso nos pes, chutes/joelho com eixo claro.

## Marcadores de coesao

Os marcadores abaixo precisam ser comparados entre model sheet, key poses,
strips, sprite sheet final e runtime:

- cabelo: silhueta e volume nao mudam entre poses sem decisao de acao/camera;
- olhos/rosto: foco agressivo, linha de sobrancelha e expressao por estado;
- roupa: shorts pretos, ornamentos dourados, faixa vermelha e bandagens;
- corpo: anatomia atlética, torso, ombros, quadris e proporcao constantes;
- assimetria: braco de lava sempre no lado correto e com endpoint legivel;
- materiais: pele bronzeada, pedra, rachadura de lava, tecido e bandagem nao
  podem colapsar em uma mesma massa cromatica.

Se uma pose aceita contradiz outra, como cabelo diferente entre frente/costas ou
entre a primeira pose e as demais, a producao deve parar para decidir:
`intentional_variation`, `occlusion_by_pose`, `camera_angle_change` ou
`redraw_required`. Sem essa decisao, qualquer sheet derivada fica
`cohesion_drift`.

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

## Contexto de producao

Sprite sheet nao pode ser gerado como prancha isolada. Antes de produzir, o
agente deve registrar em `art_gameplay_direction_gate`:

- papel do estado no jogo;
- perspectiva de camera e leitura em 320x224;
- oponente, contato, alcance, hitbox e interacao com cenario;
- marcadores visuais que precisam sobreviver;
- movimento secundario de cabelo, faixas, shorts, maos e expressao.
