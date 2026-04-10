# 08 - Bible Artistica

## Referencia visual canonica

A **arte conceito** do jogo e a referencia visual obrigatoria para todos os assets e boards. Ela define paleta, contornos, ornamentacao e escala.

- **Arquivo:** `doc/Concept art.jpg`
- **Uso:** Agentes de IA de arte, arte manual e revisao de lote devem seguir este arquivo como biblia visual, nao apenas como inspiracao vaga. O prompt em `tmp/imagegen/PROMPT_AGENTE_ASSETS_PEQUENO_PRINCIPE.md` mapeia cada asset a um elemento do concept.
- **Boards de referencia:** As cenas em `res/gfx/boards/` (board_title_scene, board_b612, board_king, board_lamp, board_desert, board_travel) sao arte conceito promovida e servem como documentacao e guia para conversao futura em tilemap.

## Direcao

Mistura entre:

- delicadeza narrativa de `O Pequeno Principe`
- sensacao manual de giz, cera e tinta
- leitura limpa para TV CRT e pixel art de Mega Drive

## Regras visuais

- contornos vivos e levemente irregulares
- massas de cor planas
- dithering como linguagem, nao como acidente
- tons pastois quentes, sem gradientes complexos

## Identidade do heroi

- corpo pequeno
- cabelo dourado
- casaco verde
- cachecol amarelo como assinatura de movimento

## Leitmotivs por planeta

- `B-612`: intimidade e por do sol
- `Rei`: escala vertical e peso cenografico
- `Lampiao`: calor, luz, rotina e contraste
- `Deserto`: silencio, vento e vastidao

## Regras tecnicas de producao

Para especificacoes tecnicas completas (paleta indexada, grid 8x8, limites de cor, checklist de validacao e regras anti-alucinacao para IAs de imagem), consultar `doc/15-diretrizes-producao-assets.md`.
