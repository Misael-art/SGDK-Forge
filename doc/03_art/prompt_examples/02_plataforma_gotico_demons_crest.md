# Prompt exemplo: personagem e mundo de plataforma gotico

Use este prompt quando quiser solicitar ao agente um conjunto completo e coerente de artes para um jogo de plataforma/acao gotico autoral. As referencias citadas abaixo devem ser tratadas como benchmark tecnico de leitura, atmosfera e composicao, nunca como autorizacao para copiar personagens, cenarios, sprites, nomes, paletas proprietarias ou silhuetas reconheciveis.

```text
[Contexto MD Carregado]

Atue como Art Director tecnico, Pixel Artist senior, Designer de mundo e Curador SGDK/Mega Drive.

Objetivo:
Criar um pacote completo de assets coerentes para um jogo autoral de plataforma gotica chamado provisoriamente "Coroa de Cinzas", com protagonista carismatico, mundo exploravel, inimigos, chefes, cenarios em multiplos planos, UI e FX. A direcao tecnica deve buscar a presenca visual, leitura de silhueta, dramaticidade e atmosfera de grandes jogos 16-bit de acao gotica, com Demon's Crest usado apenas como benchmark de qualidade: criatura protagonista expressiva, cenarios sombrios, transformacoes, leitura forte em baixa resolucao e animacoes com peso.

Regra de IP:
Nao copie Firebrand, Demon's Crest, nomes, mapas, sprites, chefes, paletas proprietarias ou composicoes reconheciveis. Use a referencia apenas para principios: silhueta clara, contraste, gotico fantastico, animacao economica e impacto visual.

Antes de propor arte, gere estes artefatos:
1. context_pack_manifest
   - Liste docs/projetos/fontes locais que devem ser consultados antes da geracao.
   - Incluir GDD/spec quando existir, budgets de cena, memoria operacional, source cases, perfis de engine e headers SGDK relevantes.
   - Se algum arquivo canonico nao existir, registrar fallback para doc/06_AI_MEMORY_BANK.md.
2. route_decision_record
   - Explicar em linguagem curta por que este trabalho deve passar por: art-creation-sourcing, visual-excellence-standards, multi-plane-composition, art-translation-to-vdp, art-conversion-pipeline e megadrive-vdp-budget-analyst.
3. master_style_manifest
   - Definir token de estilo unico: COROA_CINZAS_GOTHIC_PLATFORM_V1.
   - Declarar paletas hex candidatas, espessura de linha, densidade de detalhe, camera, escala, iluminacao e regras de sombra.
4. art_generation_brief
   - Descrever sujeito, gameplay, escala, animacoes, planos de fundo, restricoes SGDK e criterios de aceite.
5. qa_correction_loop
   - Descrever como rejeitar assets bonitos mas incoerentes, com drift cromatico, blur, excesso de cores, escala errada ou baixa legibilidade.

Restricoes tecnicas de True Pixel Art:
- Arte final deve ser pixel art real, sem blur, sem anti-aliasing subpixel, sem gradientes suaves de milhoes de cores e sem interpolacao linear.
- Trabalhar com resolucoes nativas como 32x32, 48x48, 64x64, 96x96, 128x128 ou tiles 8x8/16x16.
- Usar nearest neighbor em todo resize.
- Paleta indexada, com no maximo 15 cores visiveis por paleta Mega Drive mais cor transparente.
- Considerar 4 paletas simultaneas de 16 cores, 9-bit RGB Mega Drive e cor 0 transparente em sprites.
- Line art deve priorizar contorno de 1px com acentos de 2px apenas em sombra profunda.
- Shading deve usar no maximo 3 tons principais por material: luz, meio-tom e sombra.
- Dithering deve ser intencional, preferencialmente Bayer ou padroes manuais, apenas em pedra, nevoa, metal gasto e ceu.
- Todos os sprites devem preservar pivots consistentes e grid de alinhamento.
- Cenarios devem ser planejados para BG_B, BG_A, WINDOW/HUD e sprites, sem inventar terceiro plano de background.

Direcao visual:
- Tom: gotico fantastico, melancolico, heroico e misterioso.
- Mundo: ruinas suspensas, torres partidas, criptas com vitrais apagados, penhascos lunares, forjas de ossos minerais e jardins petrificados.
- Protagonista: "Nox, o Herdeiro da Cinza", uma pequena criatura alada autoral com carisma, postura nobre e expressao determinada.
- Silhueta: cabeca e ombros muito reconheciveis, asas compactas, chifres curtos assimetricos, capa curta rasgada e luva de pedra viva.
- Gameplay: plataforma precisa, salto, planagem curta, tiro arcano, agarrar parede, transformacoes por brasoes e chefes com leitura grande.
- Clima: alto contraste, luz lunar fria, fogo espectral controlado, sombras duras e pequenos highlights de metal antigo.

Pacote de assets esperado:
1. Hero sprite sheet
   - idle: 6 frames
   - run: 8 frames
   - jump rise/fall: 4 frames
   - glide: 4 frames
   - wall cling: 2 frames
   - arcane shot: 5 frames
   - claw slash: 6 frames
   - hurt: 3 frames
   - death/ash dissolve: 8 frames
   - transformation: 10 frames
   - Tamanho base recomendado: 48x48 ou 64x64 por frame.
2. Formas alternativas
   - Stone mantle: defesa e queda pesada.
   - Ember wing: planagem longa e tiro de fogo.
   - Hollow shade: atravessar grades magicas por curto tempo.
   - Para cada forma, entregar 1 pose ortografica frontal, 1 idle e 1 animacao de habilidade.
3. Inimigos comuns
   - Sentinela de sino quebrado.
   - Espirito de vitral.
   - Cavaleiro ferrugem.
   - Planta tumular cristalizada.
   - Para cada um: idle, walk/fly, attack, hurt/death.
4. Chefes
   - Guardiao do campanario lunar.
   - Rainha das cinzas frias.
   - Entregar concept ortografico, 3 ataques principais, telegraph visual e partes de sprite separaveis.
5. Cenarios
   - Fase 1: muralha sob eclipse.
   - Fase 2: cripta de vitrais mortos.
   - Fase 3: jardim petrificado com chuva de cinza.
   - Para cada fase: tileset solido, decoracao, props animados, plano distante BG_B, plano jogavel BG_A e sugestao de parallax.
6. UI e gameplay feedback
   - Medidor de vida em brasoes.
   - Icones de transformacao.
   - Orbes de energia.
   - Checkpoint, porta selada, pickup raro e indicador de chave.
7. FX
   - Tiro arcano, impacto em parede, poeira de pouso, rastro de planagem, brilho de pickup, quebra de pedra, chama espectral.

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
   - Prompt mestre de personagem.
   - Prompt de formas alternativas.
   - Prompt de inimigos.
   - Prompt de chefes.
   - Prompt de tilesets.
   - Prompt de backgrounds parallax.
   - Prompt de UI/FX.
7. negative_prompt_global
   Incluir: blur, anti-aliasing, painterly, copied IP, recognizable Firebrand silhouette, smooth gradient, high color count, inconsistent outline, 3D render, semi-transparent pixels, JPEG artifacts, variable pixel density.
8. qa_findings_template
   - Paleta respeitada?
   - Silhueta le em 1x?
   - Frame pivot consistente?
   - Cores cabem no budget Mega Drive?
   - Asset parece do mesmo mundo que o master_style_manifest?
   - Existe drift maior que 15% da paleta?
   - O asset e bonito mas incoerente? Se sim, rejeitar.
9. correction_request_template
   - Gerar pedidos de correcao objetivos, sem refazer tudo quando apenas paleta, linha, pivot ou contraste falharem.

Prompt mestre de imagem para o primeiro asset ancora:
"Original 16-bit gothic platform game protagonist, small noble winged ash creature named Nox, compact expressive silhouette, short asymmetric horns, tattered short cape, stone gauntlet, determined face, orthographic sprite sheet front side back and 3/4 gameplay pose, true pixel art, precise hand placed pixels, clean 1px outline, limited indexed palette, no anti-aliasing, no blur, high contrast moonlit shadows, flat cel shading, Mega Drive color discipline, transparent background #00FF00, 48x48 frame planning, charismatic but not cute-only, dramatic gothic fantasy mood, no copied characters, no recognizable Firebrand silhouette."

Entregue tudo como especificacao pronta para guiar geracao de imagem, revisao humana, conversao SGDK e validacao antes de qualquer promocao para res/.
```
