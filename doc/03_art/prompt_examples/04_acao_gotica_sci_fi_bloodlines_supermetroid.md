# Prompt exemplo: acao gotica sci-fi com exploracao

Use este prompt quando quiser solicitar ao agente um conjunto completo e coerente de artes para um jogo de acao lateral com exploracao, tensao gotica e tecnologia alienigena. Castlevania: Bloodlines e Super Metroid devem ser usados apenas como benchmarks tecnicos de atmosfera, contraste, leitura, composicao e design de progressao, nunca como autorizacao para copiar sprites, personagens, armas, mapas, inimigos, HUDs ou paletas proprietarias.

```text
[Contexto MD Carregado]

Atue como Art Director tecnico, Pixel Artist senior, Designer de gameplay lateral e Curador SGDK/Mega Drive.

Objetivo:
Criar um pacote completo de assets coerentes para um jogo autoral de acao/exploracao chamado provisoriamente "Catacumba Orbital". O jogo combina arquitetura gotica, ruinas biomecanicas, combate rapido, portas por habilidades e cenarios com profundidade. Use Castlevania: Bloodlines como benchmark de dramaticidade gotica, parallax, leitura de arma e ritmo de acao. Use Super Metroid como benchmark de exploracao, linguagem de portas, biomas, leitura de mapa e atmosfera alienigena. Nao copiar IP.

Regra de IP:
Nao copiar Belmont, Morris, Samus, Metroids, Mother Brain, armas iconicas, mapas, inimigos, HUDs, tiles ou silhuetas reconheciveis. Criar universo, personagem, armas, monstros e arquitetura originais.

Antes de propor arte, gere estes artefatos:
1. context_pack_manifest
   - Listar docs consultados, GDD/spec, budget de cena, memoria, feedback bank, source cases, perfis de engine e headers SGDK relevantes.
   - Registrar hashes/timestamps quando possivel.
   - Se doc/10-memory-bank.md nao existir, usar doc/06_AI_MEMORY_BANK.md como fallback.
2. route_decision_record
   - Roteie por: game-design-planning, multi-plane-composition, art-creation-sourcing, art-translation-to-vdp, art-conversion-pipeline, visual-excellence-standards e megadrive-vdp-budget-analyst.
3. master_style_manifest
   - Token de estilo: CATACUMBA_ORBITAL_GOTHIC_SF_V1.
   - Declarar paletas, contraste, materialidade, linha, camera, densidade por plano e regras para tecnologia alienigena.
4. art_generation_brief
   - Definir personagem, habilidades, armas, portas, inimigos, cenarios, UI e restricoes SGDK.
5. qa_correction_loop
   - Rejeitar qualquer asset bonito mas incoerente com gotico sci-fi, excesso de cores, blur, escala errada, copia reconhecivel ou leitura ruim.

Restricoes tecnicas de True Pixel Art:
- Pixel art real, sem blur, sem anti-aliasing, sem smear e sem gradientes suaves.
- Usar nearest neighbor em todos os redimensionamentos.
- Paleta indexada com ate 15 cores visiveis por paleta Mega Drive mais transparente.
- Planejar 4 paletas de 16 cores: BG gotico, BG alienigena/energia, protagonista/armas, inimigos/UI.
- Respeitar grid 8x8/16x16, metatiles e colisao clara.
- Sprites devem ter pivots consistentes, caixas de colisao sugeridas e leitura em 1x.
- Backgrounds devem usar BG_B para atmosfera/distancia, BG_A para area jogavel e WINDOW/HUD quando necessario.
- Sem alpha blending; brilho deve usar palette cycling, shadow/highlight do VDP quando aplicavel, sprites alternados ou dithering.
- Planejar cenarios para VRAM/DMA realista; nao promover assets para res/ sem budget validado.

Direcao visual:
- Tom: elegante, sombrio, alienigena, letal e grandioso.
- Mundo: uma catedral espacial presa a um asteroide, onde reliquias goticas foram tomadas por tecnologia organica.
- Protagonista: "Iria Voss", cacadora de reliquias orbitais com armadura leve, manto curto e arma original chamada "lanca-corrente de plasma".
- Silhueta: postura atletica, ombro assimetrico, lanca-corrente dobravel nas costas, visor estreito e capa curta que ajuda a leitura em movimento.
- Gameplay: correr, pular, deslizar, atacar com corrente, disparo curto, mirar diagonal, abrir portas por runas de energia, explorar shafts verticais.
- Visual: pedra escura, vitrais rachados, cabos organicos, luzes magenta/ciano controladas, sombras duras, highlights metalicos.

Pacote de assets esperado:
1. Protagonista sprite sheet
   - idle combat: 6 frames
   - run: 8 frames
   - jump rise/fall: 5 frames
   - crouch/aim: 4 frames
   - slide: 5 frames
   - chain slash horizontal: 7 frames
   - chain slash diagonal: 7 frames
   - plasma shot: 5 frames
   - climb/ledge: 6 frames
   - hurt/death: 8 frames
   - Tamanho base recomendado: 48x64 ou 64x64 por frame.
2. Armas e habilidades
   - Lanca-corrente de plasma.
   - Selo de fase para atravessar grades organicas.
   - Bota de impulso curto.
   - Nucleo de abertura para portas codificadas por cor.
3. Inimigos
   - Monge-circuito.
   - Carcaca biomecanica rastejante.
   - Vitrais sentinelas.
   - Parasita de organo eletrico.
   - Para cada um: idle, patrol, attack, hurt/death.
4. Chefes
   - Arconte da Nave-Sino.
   - Coracao Liturgico.
   - Entregar partes separaveis, telegraphs, ataques e estado de dano.
5. Cenarios/tilesets
   - Nave-catedral exterior com parallax orbital.
   - Capela de plasma e vitrais.
   - Dutos organicos verticais.
   - Laboratorio de ossos metalicos.
   - Cada area deve ter tiles solidos, plataformas, portas, slopes quando necessario, decoracoes animadas e marcadores de progressao.
6. UI
   - Barra de vida.
   - Energia de plasma.
   - Icones de habilidade.
   - Mini mapa simplificado por salas.
   - Portas codificadas por simbolos alem de cor.
7. FX
   - Rastro de corrente, impacto metalico, plasma charge, porta abrindo, sparks, poeira de pedra, dano organico, save terminal, teleport curto.

Formato obrigatorio da resposta:
1. context_pack_manifest
2. route_decision_record
3. master_style_manifest
4. art_generation_brief
5. asset_catalog
   Para cada asset, incluir:
   - asset_id
   - descricao
   - dimensoes
   - frames
   - paleta alvo
   - plano VDP sugerido
   - pivot
   - hitbox sugerida
   - risco tecnico
   - criterio de aceite
6. prompts de geracao por lote
   - Prompt mestre da protagonista.
   - Prompt de arma/habilidades.
   - Prompt de inimigos.
   - Prompt de chefes.
   - Prompt de tilesets.
   - Prompt de backgrounds parallax.
   - Prompt de UI/mapa.
   - Prompt de FX.
7. negative_prompt_global
   Incluir: blur, anti-aliasing, copied IP, recognizable Belmont, recognizable Samus, Metroid-like creature copying, smooth gradients, semi-transparent pixels, painterly texture, 3D render artifacts, inconsistent outline, too many colors, unreadable silhouette.
8. qa_findings_template
   - O asset herda CATACUMBA_ORBITAL_GOTHIC_SF_V1?
   - A leitura funciona em 1x?
   - A arma e original e legivel?
   - O cenario comunica area jogavel claramente?
   - A paleta cabe no budget?
   - O asset tem copia reconhecivel?
   - Ha drift cromatico maior que 15%?
9. correction_request_template
   - Gerar pedidos especificos: reduzir brilho, separar foreground/background, endurecer pixels, ajustar silhueta, trocar simbolo proprietario, reduzir cores, corrigir pivot ou redesenhar animacao.

Prompt mestre de imagem para o primeiro asset ancora:
"Original 16-bit gothic sci-fi action exploration heroine named Iria Voss, light relic hunter armor, short mantle, folded plasma chain-lance on back, narrow visor, athletic readable silhouette, side-view orthographic sprite sheet front side back and combat gameplay pose, true pixel art, precise hand placed pixels, clean 1px outline, indexed limited Mega Drive palette, hard shadows, gothic cathedral and alien technology material language, no anti-aliasing, no blur, transparent background #00FF00, 48x64 frame planning, no copied Castlevania or Metroid characters."

Entregue tudo como especificacao pronta para guiar geracao de imagem, revisao humana, conversao SGDK e validacao antes de qualquer promocao para res/.
```
