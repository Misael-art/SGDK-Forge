# 08 - Biblia Artistica - Celestial Chase First Playable

## Referencia Visual Canonica

- Direcao congelada: `rascunho/processado/legacy_megadrive_dev/processed/celestial_chase_v001/elite_split_scene/locked_visual_direction_v005.json`
- Board de composicao: `rascunho/processado/legacy_megadrive_dev/processed/celestial_chase_v001/elite_split_scene/chase_elite_split_approval_board_v005.png`
- Candidata tecnica split: `rascunho/processado/legacy_megadrive_dev/processed/celestial_chase_v001/elite_split_scene/runtime_split_candidates_v007/chase_runtime_split_approval_board_v007.png`
- Animacao aprovada: `rascunho/processado/legacy_megadrive_dev/processed/celestial_chase_v001/source_baked_pixel_art_candidates_v001/animation_strip_candidates_v003/animation_strip_approval_board_v003.png`

Esses arquivos orientam composicao, paleta, escala e movimento. Nao autorizam promover assets sem ResComp, budget e BlastEm.

## Direcao

- `vibrant_16bit_pixel` como estilo principal;
- cel-anime analogico como influencia de staging e personagem;
- storybook celeste como influencia de ambiente;
- clusters source-baked, silhueta limpa e contraste forte em 320x224.

## Regras Visuais

- Contorno seletivo de um pixel; nunca linha preta pesada continua.
- Heroi: ivory, azul saturado e dourado; leitura clara sobre a pista.
- Perseguidor: massa metalica quente em frontal tres-quartos no eixo Z.
- Ambiente: indigo profundo, areia lunar e highlights celestes.
- Dithering apenas funcional em areas amplas; personagens sem ruido automatico.
- Perigo usa acento quente; coleta/Pulse usa ivory e ciano.
- Nenhum HUD final pode parecer telemetria ou debug.

## Composicao de Planos

- BG_B: atmosfera, horizonte e estrada distante.
- BG_A: trecho frontal da pista, marcas de faixa e telegrafos quando o budget permitir.
- Sprites: heroi, perseguidor, ameacas, pickups e FX.
- WINDOW: reservado para HUD fixo quando medido; nunca mascara de cenario.

## Regras Tecnicas de Producao

- PNG indexado, grid 8x8 e transparencia no indice 0 quando aplicavel.
- Paletas: PAL0 ambiente, PAL1 heroi, PAL2 perseguicao/FX, PAL3 HUD.
- Reducao de tiles deve traduzir a fonte aprovada por reuse/cluster simplification, nao substituir a composicao por fallback procedural.
- Asset critico exige laudo, budget, ResComp e evidencia da ROM vigente.

## Anti-Tom

- fundo plano de laboratorio;
- cyber-neon generico;
- gradiente suave;
- contorno pesado;
- ASCII dominante;
- arte copiada de IP existente;
- efeito sem consequencia de gameplay.
