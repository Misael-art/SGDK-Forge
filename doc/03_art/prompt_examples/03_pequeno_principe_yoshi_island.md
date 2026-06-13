# Prompt exemplo: mundo poetico de plataforma com grafico desenhado

Use este prompt quando quiser solicitar ao agente um conjunto completo e coerente de artes para um jogo de plataforma poetico, infantil e contemplativo. A referencia ao universo do pequeno viajante estelar e ao acabamento visual desenhado de jogos 16-bit deve servir como direcao de tom e tecnica, sem copiar texto, personagens, planeta, rosa, ilustracoes, sprites, nomes ou composicoes proprietarias.

```text
[Contexto MD Carregado]

Atue como Art Director tecnico, Pixel Artist senior, Designer narrativo e Curador SGDK/Mega Drive.

Objetivo:
Criar um pacote completo de assets coerentes para um jogo autoral de plataforma poetica chamado provisoriamente "O Menino das Estrelas de Papel". O jogo deve transmitir inocencia, descoberta, amizade, pequenas tristezas e maravilhamento cosmico, com graficos que parecam desenhados a lapis de cor, giz e aquarela, mas convertidos para pixel art real e viavel no Mega Drive. Use Yoshi's Island apenas como benchmark tecnico de encanto visual: contorno expressivo, textura desenhada, cores alegres, cenarios em camadas, animacao viva e legibilidade. Use a obra do pequeno viajante estelar apenas como inspiracao tematica ampla, sem reproduzir personagens, frases, planeta, rosa, raposa, aviador ou iconografia reconhecivel.

Regra de IP:
Nao copie O Pequeno Principe, Yoshi's Island, personagens, frases, sprites, fases, paletas proprietarias ou silhuetas reconheciveis. Criar um universo original com linguagem propria.

Antes de propor arte, gere estes artefatos:
1. context_pack_manifest
   - Listar GDD/spec, memoria operacional, budgets, feedback bank, source cases, engine profiles e headers SGDK consultados.
   - Quando doc/10-memory-bank.md nao existir no projeto, registrar fallback em doc/06_AI_MEMORY_BANK.md.
2. route_decision_record
   - Justificar o fluxo por: art-creation-sourcing, visual-excellence-standards, multi-plane-composition, art-translation-to-vdp, art-conversion-pipeline e megadrive-vdp-budget-analyst.
3. master_style_manifest
   - Token de estilo: MENINO_ESTRELAS_PAPEL_V1.
   - Definir paletas pastel indexadas, contorno irregular controlado, textura de papel simulada por dithering, camera lateral e regras de animacao.
4. art_generation_brief
   - Especificar personagem, mundo, assets, escala, gameplay, planos de fundo e restricoes SGDK.
5. qa_correction_loop
   - Rejeitar arte borrada, pintada demais, com excesso de cores, sem grid, com visual de filtro automatico ou incoerente com o manifesto.

Restricoes tecnicas de True Pixel Art:
- Pixel art real, com bordas nitidas em nearest neighbor.
- Sem anti-aliasing, sem blur, sem textura high-res disfarcada e sem filtros que criem subpixels.
- Paleta indexada com no maximo 15 cores visiveis por paleta Mega Drive mais transparente.
- Cores devem respeitar aproximacao 9-bit RGB do Mega Drive.
- Dithering deve simular lapis, giz e papel, mas com padroes controlados e repetiveis.
- Contorno pode parecer organico, mas deve continuar legivel em 1x.
- Tiles e sprites devem respeitar grade 8x8/16x16.
- Evitar semitransparencia; efeitos suaves devem ser feitos por troca de paleta, dithering ou sprites alternados.
- Backgrounds devem ser planejados em BG_B distante, BG_A jogavel/decorativo e sprites/foreground, sem terceiro plano BG.

Direcao visual:
- Tom: lirico, luminoso, delicado, curioso e levemente melancolico.
- Mundo: pequenos astros de papel, jardins suspensos, campos de estrelas dobradas, casinhas em luas, pontes de cometa, livros abertos que viram ilhas.
- Protagonista: "Lio", um pequeno viajante autoral com capa curta, cabelo em forma simples, cachecol-estandarte e mochila de cartas.
- Companheira: uma criatura estelar autoral chamada "Nina-Luz", feita de papel dobrado e brilho pontilhado, sem copiar a raposa classica.
- Silhueta: cabeca grande, corpo pequeno, cachecol legivel e mochila como marca visual.
- Gameplay: pulo suave, planar com cachecol, carregar pequenas sementes luminosas, conversar com habitantes, resolver plataformas com vento, estrelas e gravidade leve.
- Visual: pastel com acentos vivos, sombras coloridas, ceu profundo com poucos tons, textura de papel feita por dithering seletivo.

Pacote de assets esperado:
1. Hero sprite sheet
   - idle contemplativo: 8 frames
   - walk/run leve: 8 frames
   - jump: 4 frames
   - fall: 2 frames
   - scarf glide: 6 frames
   - water seed/flor: 6 frames
   - talk/listen: 4 frames
   - surprise: 3 frames
   - hurt: 3 frames
   - sleep/checkpoint: 6 frames
   - Tamanho base recomendado: 32x48 ou 48x48 por frame.
2. Companion sprite sheet
   - hover idle, follow, sparkle, point, hide, celebrate.
   - Tamanho base: 24x24 ou 32x32.
3. Habitantes e NPCs
   - Cartografo de nuvens.
   - Flor-cantora original.
   - Guardiao de lanternas.
   - Crianca de constelacao.
   - Cada NPC deve ter idle, talk e reaction.
4. Cenarios
   - Astro jardim: plataformas curvas, grama desenhada, pequenas flores e ceu em parallax.
   - Biblioteca celeste: paginas como terreno, letras abstratas decorativas, poeira de estrela.
   - Deserto de vidro doce: dunas pastel, sombras frias, vento visivel por linhas de pixel.
   - Cidade-lanterna lunar: casinhas pequenas, pontes, luzes animadas.
5. Tilesets
   - Solo principal, bordas, plataformas moveis, nuvens solidas, pontes, molas poeticas, blocos quebraveis, portas pequenas, signos de checkpoint.
6. UI e colecionaveis
   - Medidor de coragem.
   - Sementes-estrelas.
   - Cartas perdidas.
   - Pequeno mapa de constelacao.
   - Icones de amizade, vento e luz.
7. FX
   - Poeira de papel no pouso, brilho de estrela, vento desenhado, flor abrindo, estrela coletada, dobra de papel, transicao de planeta.

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
   - risco tecnico
   - criterio de aceite
6. prompts de geracao por lote
   - Prompt mestre do protagonista.
   - Prompt da companheira.
   - Prompt de NPCs.
   - Prompt de tilesets.
   - Prompt de backgrounds em parallax.
   - Prompt de UI/colecionaveis.
   - Prompt de FX.
7. negative_prompt_global
   Incluir: blur, anti-aliasing, copied IP, recognizable Little Prince design, recognizable Yoshi sprites, watercolor high-res texture, smooth gradients, semi-transparent pixels, soft edges, noisy AI artifacts, JPEG compression, inconsistent palette, inconsistent outline, too many colors.
8. qa_findings_template
   - O asset continua pixel-perfect em 1x?
   - A textura desenhada e feita por pixels controlados?
   - A paleta cabe no Mega Drive?
   - A silhueta do protagonista continua reconhecivel?
   - O mundo parece autoral?
   - O asset herda MENINO_ESTRELAS_PAPEL_V1?
   - Existe drift cromatico maior que 15%?
9. correction_request_template
   - Corrigir com instrucoes objetivas: reduzir cores, endurecer bordas, simplificar textura, alinhar grid, recuperar paleta, melhorar contraste ou refazer silhueta.

Prompt mestre de imagem para o primeiro asset ancora:
"Original poetic 16-bit platform game protagonist, small star traveler named Lio, short cape scarf, letter backpack, gentle curious expression, hand drawn crayon-like pixel art translated into true pixel art, clean readable silhouette, hard pixel edges, no anti-aliasing, limited indexed pastel palette, controlled paper dithering, side-view orthographic sprite sheet with front side back and gameplay pose, 32x48 frame planning, Mega Drive color discipline, transparent background #00FF00, whimsical cosmic garden mood, charming and melancholic, no copied Little Prince design, no copied Yoshi style sprites."

Entregue tudo como especificacao pronta para guiar geracao de imagem, revisao humana, conversao SGDK e validacao antes de qualquer promocao para res/.
```
