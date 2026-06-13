# Prompt exemplo: RPG 16-bit com aventura, magia e mundo vivo

Use este prompt quando quiser solicitar ao agente um conjunto completo e coerente de artes para um RPG autoral 16-bit com mapas ricos, personagens expressivos, combate e magia. Chrono Trigger e Secret of Mana devem ser usados apenas como benchmarks tecnicos de clareza, carisma, composicao de tiles, leitura de batalha e riqueza de mundo, nunca como autorizacao para copiar personagens, mapas, monstros, sprites, menus, nomes, paletas ou cenas.

```text
[Contexto MD Carregado]

Atue como Art Director tecnico, Pixel Artist senior, Designer de RPG 16-bit e Curador SGDK/Mega Drive.

Objetivo:
Criar um pacote completo de assets coerentes para um RPG autoral chamado provisoriamente "Lume dos Ecos". O jogo deve ter personagens memoraveis, vilas vivas, florestas magicas, ruinas antigas, combate visualmente expressivo e uma identidade propria. Use Chrono Trigger como benchmark de expressividade, proporcao chibi funcional, poses de combate e leitura cinematica. Use Secret of Mana como benchmark de natureza exuberante, tiles organicos, magia colorida e atmosfera de aventura. Nao copiar IP.

Regra de IP:
Nao copiar Crono, Marle, Frog, Robo, Mana Tree, Randi, Popoi, mapas, monstros, HUDs, menus, paletas proprietarias, poses reconheciveis ou cenas iconicas. Criar mundo, personagens e linguagem visual originais.

Antes de propor arte, gere estes artefatos:
1. context_pack_manifest
   - Listar docs consultados, GDD, spec de cenas, budget, memoria operacional, feedback bank, source cases, engine profiles e headers SGDK.
   - Registrar hashes/timestamps quando possivel.
   - Se doc/10-memory-bank.md nao existir, usar doc/06_AI_MEMORY_BANK.md como fallback.
2. route_decision_record
   - Roteie por: game-design-planning, scene-state-architect, art-creation-sourcing, multi-plane-composition, art-translation-to-vdp, art-conversion-pipeline, visual-excellence-standards e megadrive-vdp-budget-analyst.
3. master_style_manifest
   - Token de estilo: LUME_DOS_ECOS_RPG_V1.
   - Declarar proporcoes de personagem, paletas, densidade de tiles, camera top-down 3/4, leitura de batalha, contorno e regras de magia.
4. art_generation_brief
   - Definir party, mundo, areas, inimigos, NPCs, UI, FX, tilesets e restricoes SGDK.
5. qa_correction_loop
   - Rejeitar assets bonitos mas fora do manifesto, com perspectiva errada, excesso de cores, UI ilegivel, copia reconhecivel ou tiles que nao conectam.

Restricoes tecnicas de True Pixel Art:
- Pixel art real com bordas nitidas e nearest neighbor.
- Sem anti-aliasing, blur, textura high-res, gradientes suaves ou semitransparencia.
- Paleta indexada, ate 15 cores visiveis por paleta Mega Drive mais transparente.
- Planejar 4 paletas: ambiente principal, ambiente detalhe/magia, party/NPCs, inimigos/UI.
- Tiles devem encaixar em grid 8x8/16x16 e formar metatiles consistentes.
- Personagens devem ter pivots consistentes nas quatro direcoes.
- Combate e mapa devem compartilhar DNA visual, mas podem ter sprites de batalha maiores.
- Magias devem usar palette cycling, sprites alternados, dithering e shapes claros; nao usar alpha blending inventado.
- Cenarios devem planejar BG_A/B com prioridade, colisao, decoracao e legibilidade de caminho.

Direcao visual:
- Tom: aventura calorosa, misterio antigo, natureza viva, magia luminosa e drama heroico.
- Mundo: continentes formados por ecos de eras antigas, arvores de cristal, vilas construidas em raizes, ruinas de relogios solares e rios de luz.
- Party inicial:
  - "Taro", aprendiz de cartografo com espada curta e bussola de luz.
  - "Mira", guardia de sementes, cajado dobravel e magia de vinhas luminosas.
  - "Oren", jovem ferreiro de sinos, martelo leve e defesa ritmica.
- Silhuetas: cada heroi deve ser reconhecivel em 24x32 por cabelo/chapeu/equipamento/postura, sem depender de cor.
- Gameplay: exploracao top-down, conversa com NPCs, puzzles ambientais, combate em arena/cena, magias elementais e bosses com fases.
- Visual: vegetacao densa mas legivel, sombras coloridas, highlights quentes, pedras antigas com runas discretas, agua com ciclos de paleta.

Pacote de assets esperado:
1. Party overworld sprites
   - 3 herois.
   - 4 direcoes: down, up, left, right.
   - walk: 3 frames por direcao.
   - idle: 1 frame por direcao.
   - interact/talk: 2 frames.
   - Tamanho base recomendado: 24x32 ou 32x32 por frame.
2. Party battle sprites
   - idle battle: 4 frames
   - attack: 6 frames
   - cast: 6 frames
   - hurt: 3 frames
   - victory: 5 frames
   - Tamanho base recomendado: 48x48 por frame.
3. NPCs
   - Mercadora de raizes.
   - Anciao relogio.
   - Crianca mensageira.
   - Guarda de ponte.
   - Musico de praca.
   - Cada NPC: 4 direcoes basicas, talk e reaction.
4. Monstros
   - Lesma de cristal.
   - Armadura de musgo.
   - Esporo-lanterna.
   - Totem quebrado.
   - Para cada um: idle, attack, hurt, defeat.
5. Chefes
   - Colosso do Relogio Solar.
   - Raiz-Coroa Luminar.
   - Entregar partes separaveis, telegraphs, animacoes de fase e paleta de dano.
6. Tilesets
   - Vila das Raizes: casas, pontes, barracas, pocos, placas, cercas e interiores.
   - Floresta de Cristal: grama, troncos, raizes, flores, agua, pedras e clareiras.
   - Ruina do Relogio: pisos, paredes, engrenagens, portas, interruptores, sombras.
   - Overworld: costa, montanha, floresta, estrada, rios, ponte, icones de cidade.
7. UI
   - Janela de dialogo.
   - Menu principal.
   - Icones de itens.
   - Retratos pequenos da party.
   - Barra de vida/magia.
   - Cursor e indicador de alvo.
8. FX
   - Corte de espada, golpe de martelo, vinhas luminosas, cura, agua, fogo ritual, vento, sparkle de item, transicao de batalha.

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
   - metatile/collision quando aplicavel
   - risco tecnico
   - criterio de aceite
6. prompts de geracao por lote
   - Prompt mestre da party.
   - Prompt de overworld sprites.
   - Prompt de battle sprites.
   - Prompt de NPCs.
   - Prompt de monstros.
   - Prompt de chefes.
   - Prompt de tilesets.
   - Prompt de UI.
   - Prompt de FX.
7. negative_prompt_global
   Incluir: blur, anti-aliasing, copied IP, recognizable Chrono Trigger character, recognizable Secret of Mana character, smooth gradient, too many colors, inconsistent perspective, non-tiling tiles, painterly texture, semi-transparent pixels, 3D render artifacts, unreadable chibi silhouette.
8. qa_findings_template
   - A perspectiva top-down 3/4 esta consistente?
   - Os tiles conectam sem seams visiveis?
   - Cada heroi e reconhecivel em 1x?
   - A paleta cabe no budget?
   - O asset herda LUME_DOS_ECOS_RPG_V1?
   - O menu e legivel em 320x224?
   - Existe copia reconhecivel ou drift cromatico maior que 15%?
9. correction_request_template
   - Corrigir com pedidos objetivos: alinhar perspectiva, reduzir cores, simplificar textura, reforcar silhueta, ajustar tileability, trocar simbolo proprietario, separar paleta de magia ou corrigir pivots.

Prompt mestre de imagem para o primeiro asset ancora:
"Original 16-bit JRPG party orthographic sprite design, three charismatic heroes named Taro Mira Oren, warm adventurous fantasy world, top-down 3/4 RPG proportions, overworld and battle pose planning, true pixel art, precise hand placed pixels, clean readable outlines, limited indexed Mega Drive palette, lush magical forest material language, expressive chibi silhouettes, no anti-aliasing, no blur, transparent background #00FF00, 24x32 overworld frames and 48x48 battle frames, no copied Chrono Trigger or Secret of Mana characters."

Entregue tudo como especificacao pronta para guiar geracao de imagem, revisao humana, conversao SGDK e validacao antes de qualquer promocao para res/.
```
