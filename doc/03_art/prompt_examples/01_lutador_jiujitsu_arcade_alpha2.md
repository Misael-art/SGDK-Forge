# Prompt Exemplo - Lutador de Jiu-Jitsu Brasileiro em Luta Arcade

Use este prompt para pedir ao agente um conjunto completo e coerente de assets para um personagem original de luta, usando jogos arcade 2D de meados dos anos 90 como benchmark tecnico. Nao copie personagens, roupas, poses registradas, nomes, logos ou paletas exatas de jogos comerciais.

```text
[Contexto MD Carregado]

Atue como Art Director tecnico, Pixel Artist senior e curador SGDK/Mega Drive.

Objetivo:
Criar o pacote completo de artes para um personagem original de jogo de luta 2D: um lutador carismatico de jiu-jitsu brasileiro, com presenca de arcade premium, leitura forte em 320x224 e animacao fluida. Use Street Fighter Alpha 2 apenas como benchmark tecnico de qualidade: escala heroica, poses claras, color blocking, timing de golpes, expressividade, impacto e acabamento de sprite. Nao copie nenhum personagem, roupa, golpe, nome, pose iconica, UI, cenario ou paleta proprietaria.

Antes de propor arte:
1. Gere ou declare um context_pack_manifest.v1 com as fontes canonicas consultadas.
2. Gere um master_style_manifest.v1 com style_anchor_id = "bjj_arcade_fighter_md_v1".
3. Gere um art_generation_brief.
4. Nao exponha Chain of Thought. Use route_decision_record, qa_findings e correction_request quando precisar justificar decisao.

Restricoes Mega Drive / SGDK:
- Tela alvo: 320x224.
- Pixel art verdadeiro, sem anti-aliasing, sem blur, sem alpha parcial, sem gradientes suaves.
- Grid 8x8, dimensoes multiplas de 8.
- Paleta indexada: maximo 15 cores visiveis por paleta, index 0 transparente.
- Cores devem respeitar o grid 9-bit do VDP.
- O personagem pode ser metasprite; declare envelope por frame, numero estimado de tiles e risco de sprites por scanline.
- Flip horizontal por hardware para lado esquerdo/direito; nao duplique a direcao em PNG.
- Priorize leitura, pivot estavel, massa consistente e silhouette em preto puro.

Identidade do personagem:
- Nome provisoriamente original: "Caio Aranha".
- Origem visual: atleta brasileiro de jiu-jitsu com postura calma, olhar confiante, carisma solar e disciplina de ringue.
- Arquetipo: grappler tecnico, rapido no chao, contra-ataque e quedas limpas.
- Roupa: rashguard curta ou gi estilizado recortado para leitura arcade, faixas de cor funcionais, sem marcas reais.
- Linguagem visual: mistura de elegancia marcial, energia urbana brasileira e clareza competitiva.
- Personalidade visual: simpatico antes da luta, implacavel no timing, expressivo sem caricatura.

Master Style Manifest esperado:
- style_anchor_id: bjj_arcade_fighter_md_v1
- line_weight_px: 1 px principal, outline reforcado apenas onde o fundo competir.
- iluminacao: top-left constante, cel shading com 3 tons por material.
- paleta base sugerida: pele quente, azul profundo, branco quebrado, amarelo/dourado pequeno para destaque, sombra roxa ou azul escura.
- limite de drift: qualquer asset com variancia cromatica/valor acima de 15% deve entrar como revisar.
- benchmarks tecnicos:
  - Street Fighter Alpha 2: leitura de pose, carisma e animacao fluida.
  - Mortal Kombat Plus e HAMOOPIG internos: PAL2/PAL3, mirrored fighters e stage layering.
  - BLAZE_ENGINE interno: depth, HUD e impacto de golpes como referencia tecnica, nao estetica literal.

Entregue o conjunto completo de assets, nao uma imagem isolada:

1. Character design package
- Orthographic sheet: frente, lado, costas, postura neutra, canvas limpo.
- Gameplay scale test: sprite em escala de luta contra fundo medio e fundo escuro.
- Silhouette test: 1 frame em preto puro.
- Palette role map: pele, tecido, sombra, brilho, outline, detalhes.

2. Sprite sheet principal
- Idle: 6 frames, respiracao e guard stance.
- Walk forward/back: 6 frames.
- Crouch / stand transition: 3 frames.
- Jump neutral: 5 frames.
- Dash in / dash back: 4 frames cada.
- Light punch, medium punch, heavy palm strike: 3-5 frames cada.
- Low kick e knee strike: 4 frames cada.
- Grapple entry / clinch: 5 frames.
- Takedown: 6-8 frames, com linha de acao clara.
- Armbar / choke special: 8-10 frames, se for viavel como animacao curta.
- Guard block high/low: 2-3 frames.
- Hurt high/low, knockdown, getup, KO: minimo funcional.
- Intro pose, win pose e taunt curto.

3. FX e feedback
- Hit sparks pequenos, dust burst de queda, impacto no chao, speed lines discretas.
- Todos os FX com paleta compartilhavel e custo de sprite/scanline declarado.
- Impactos devem ter efeito colateral fisico: poeira, shake visual sugerido ou deformacao temporal simples.

4. UI e front-end
- Portrait 48x48 ou 64x64 em paleta limitada.
- Icone pequeno 16x16.
- Nameplate original.
- P1/P2 palette swap: manter identidade, trocar funcao competitiva.

5. Stage de teste
- Arena brasileira original, sem marcas reais: tatame urbano aberto ou academia estilizada.
- BG_B: profundidade distante e atmosfera.
- BG_A: estrutura jogavel e leitura do piso.
- Foreground opcional apenas se couber como sprite graft ou prioridade declarada.
- Declarar parallax e layer_plan.

Para cada asset, entregue:
- asset_id
- asset_role
- dimensoes em pixels e tiles
- numero de frames
- paleta prevista
- lineage: prompt/source, style_anchor_id, status aceito/revisar/rejeitado
- riscos: VRAM, scanline, legibilidade, pivot, drift de estilo
- linha .res sugerida quando aplicavel

Formato de saida:
1. context_pack_manifest resumido
2. master_style_manifest
3. art_generation_brief
4. asset_catalog completo
5. prompts por asset para modelo de imagem
6. negative prompt global
7. qa_checklist com pixel strict, style cohesion, conversion pipeline e budget VDP
8. correction_request se algum asset proposto nao cumprir a barra
```
