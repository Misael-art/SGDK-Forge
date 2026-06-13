# Visual Quality Bar - Hibrido Muay Thai

Este estudo separa sintaxe tecnica de semantica visual.

Um PNG pode ser correto para SGDK e ainda ser arte reprovada. Build limpo,
PLTE <= 16, grid 9-bit e ROM no BlastEm provam apenas que o pipeline roda.
Eles nao provam anatomia, acting, contraste, identidade cromatica ou fidelidade
ao concept art.

## Regras absolutas

- Model sheet e frame individual devem ter exatamente 2 bracos, 2 pernas, 1 cabeca e 1 tronco, salvo design explicitamente documentado.
- Cada membro deve se conectar a uma articulacao plausivel: ombros para bracos, quadris para pernas.
- Mao, pe e dedos precisam ter silhueta limpa. Extremidade amorfa reprova.
- Model sheet candidato canonico precisa de escala coerente entre poses. A pose pode ocupar bbox diferente por acao, mas cabeca, torso, ombros, quadris e proporcao base nao podem mudar arbitrariamente.
- Fonte canonica de personagem deve incluir pose de costas/turnaround quando houver intencao de producao longa.
- Marcadores de figurino/material precisam ser consistentes entre poses. Faixa, cinta, detalhe de cor ou assimetria nao podem sumir sem motivo de ocultacao claro.
- Membros assimetricos precisam de contrato de adereco por lado. No Hibrido, a mao/braco lava fica sempre rocha exposta sem faixa/luva; a faixa branca pertence apenas a mao humana e aos pes.
- Fonte candidata a producao longa precisa de mapa de paleta/material antes do redraw 48x64.
- Membro especial precisa terminar em extremidade legivel. No Hibrido, o braco lava precisa ter mao/punho de rocha claro em todas as poses.
- Sombreamento deve usar clusters limpos com 2-3 tons bem espacados por material. Spray, ruido de detalhe e microtextura que vira tile-noise reprovam.
- Silhueta e contraste vencem textura. O personagem deve ser reconhecivel em um frame parado.
- Sempre que possivel, construa poses, guias e recortes pensando em multiplos de 8 px para reduzir cortes feios e tile churn.
- Assets runtime devem ser PNG indexed com paleta controlada; cor 0 fica reservada para transparencia.
- Paleta do personagem deve mirar 1 paleta de 16 cores: 15 uteis + transparencia. FX destacado pode usar paleta separada apenas quando for strip/camada separada.
- Rosto deve atuar junto com o corpo: idle focado, golpe com mandibula tensionada/dentes/kiai, dano com dor ou choque.
- Olhos devem mirar a linha horizontal de ataque/oponente.
- Sprite 48x64 precisa preservar leitura de olhos, braco de lava, calcao e bandagens.
- PAL2 cobre corpo: pele, cabelo, faixa, calcao, pedra escura.
- PAL3 cobre glow/lava/fire: amarelo, laranja e vermelho vivos.
- Se o runtime parecer cinza, azulado ou lavado, a paleta/mapeamento falhou.

## Bloqueios

- Downscale bilinear, bicubic, lanczos ou quantizacao global direta de concept high-res para 48x64.
- Foto digitalizada de baixa qualidade disfarçada de pixel art.
- Ruido de dithering automatico ou pixels isolados sem funcao.
- Promover source IA ou builder procedural como final art.
- Declarar progresso visual por build, screenshot ou validacao de formato.

## Perguntas obrigatorias antes de aceitar runtime

1. Os olhos, o braco de lava e o calcao sao identificaveis no BlastEm?
2. A paleta reflete terra/fogo quente do concept, com contraste material claro?
3. O sprite parece pixel art 16-bit nativa, nao uma imagem encolhida?

Se 1 ou 2 for "nao", ou 3 indicar foto digitalizada/borrada, o asset fica
`placeholder` e `visual_aprovado=false`.
