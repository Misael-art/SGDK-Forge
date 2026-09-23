# 17 - Concept Art Direction System

Status: `CANONICAL_WORKFLOW_GUIDE`

## Objetivo

Concept art nao e ilustracao bonita isolada. No workspace SGDK, concept art e
um contrato de direcao visual que deve melhorar leitura de gameplay, identidade
do jogo, viabilidade de producao e traducao honesta para o VDP.

Use este documento antes de prompt, sourcing, geracao, conversao ou promocao de
arte autoral.

## Artefato Obrigatorio: `concept_art_direction_brief`

O brief pode ser Markdown, YAML ou JSON, mas precisa declarar:

- `visual_purpose`: qual papel a arte cumpre no jogo.
- `gameplay_readability_goal`: o que o jogador deve perceber em 1 frame.
- `production_constraints`: tempo, equipe, volume de assets e risco de escopo.
- `hardware_constraints`: paletas, VRAM, sprites, tiles, planos e alvo 60 FPS.
- `tone_and_atmosphere`: emocao dominante e anti-tom proibido.
- `market_differentiation`: como evita parecer pixel art generico.
- `style_selection_method`: `production_driven`, `gameplay_driven`,
  `tone_driven`, `market_driven` ou combinacao explicita.
- `nine_style_axes`: os nove eixos visuais abaixo.
- `five_approval_gates`: os cinco gates abaixo.
- `references_used_as`: escala, densidade, timing, presenca ou qualidade; nunca
  fonte visual.
- `blocking_statuses`: vazio somente quando todos os pontos criticos foram
  resolvidos.

## Quatro Metodos de Escolha

| Metodo | Pergunta |
|---|---|
| `production_driven` | O estilo cabe no tempo, equipe e volume de assets? |
| `gameplay_driven` | O estilo aumenta leitura de hitbox, risco, rota e foco? |
| `tone_driven` | O estilo comunica genero, atmosfera e fantasia central? |
| `market_driven` | O estilo diferencia o jogo sem copiar IP ou benchmark? |

Regra: gosto pessoal nao e metodo. Se a escolha nao puder apontar pelo menos um
destes metodos, marque `style_chosen_by_taste_only`.

## Nove Eixos Visuais

Declare cada eixo com decisao curta, funcao e risco VDP:

1. `dimensionality`: 2D, pseudo-3D, 2.5D ou hibrido.
2. `fidelity_detail`: nivel de detalhe e o que sera simplificado.
3. `color_theory`: paleta dominante, suporte e acento funcional.
4. `lighting_shadow`: direcao de luz, sombra e limite de glow/fade.
5. `shape_language`: circulos, quadrados e triangulos como leitura mecanica.
6. `surface_material`: metal, pedra, pele, tecido, agua, fogo, vegetacao etc.
7. `ui_integration`: HUD diegetico, overlay ou janela, sem competir com jogo.
8. `motion_style`: peso, timing, smear, hitstop, idle e resposta ao controle.
9. `vfx_language`: efeitos que sinalizam impacto, risco, recompensa ou estado.

## Cinco Gates de Aprovacao

| Gate | Passa quando |
|---|---|
| `scope_style_constraints` | tamanho de sprite/tilemap, paleta, densidade e volume de assets cabem no projeto |
| `silhouette_shape_language` | asset critico funciona em silhueta e comunica papel mecanico |
| `value_hierarchy` | escala de cinza separa jogador, risco, rota, fundo e HUD |
| `palette_role_map` | cores seguem regra 60/30/10 ou justificativa equivalente de foco |
| `polish_vfx_gameplay_signal` | VFX, particulas, luz e juice reforcam gameplay, nao escondem leitura |

Qualquer gate falho bloqueia `elite_ready` para arte nova.

## Mapeamento Mega Drive

- Priorize leitura em 320x224 nativo antes de detalhe.
- Use estilo para reduzir custo, nao para prometer hardware inexistente.
- Paleta cirurgica vale mais que arco-iris decorativo.
- Dithering, shadow/highlight, palette cycling e raster FX precisam de funcao.
- UI deve pertencer ao mundo visual, mas nao roubar atencao de risco ou rota.
- VFX caro sem sinal mecanico vira `decorative_only_blocked`.

## Handoff

- Para `art-direction-selector`: entregar `concept_art_direction_brief`,
  matriz de candidatos e decisao de estilo.
- Para `art-creation-sourcing`: entregar brief antes de prompt ou busca.
- Para `art-translation-to-vdp`: entregar eixos de material, valor, paleta e
  silhueta que devem sobreviver a traducao.
- Para `visual-excellence-standards`: entregar gates preenchidos para julgamento.

## Anti-padroes

- escolher estilo porque "fica bonito";
- misturar linguagens visuais sem funcao de gameplay, tom ou mercado;
- concept art que so funciona ampliada;
- personagem e fundo com o mesmo peso de valor/saturacao;
- cor de acento usada em tudo;
- VFX como maquiagem para mecanica sem feedback claro;
- benchmark usado como fonte visual em vez de referencia tecnica.
