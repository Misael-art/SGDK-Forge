---
name: character-design
description: Use quando a tarefa envolver concepcao, direcao, revisao ou traducao de personagens para Mega Drive. Cobre escala canonica, leitura facial, silhueta, color coding funcional, palette sharing, leitura sob FX pesados e coerencia de roster. Nao use para timing de animacao isolado ou para cenarios multi-plano.
---

# Character Design

Esta skill existe para proteger a identidade visual do personagem dentro das restricoes reais do Mega Drive.

## Ler antes de agir

1. `doc/03_art/08_character_design_standards.md`
2. `doc/03_art/00_visual_quality_bar.md`
3. `doc/03_art/01_visual_cohesion_system.md`
4. `doc/03_art/02_visual_feedback_bank.md`

## Quando usar

- definicao de escala do personagem
- revisao de silhueta e leitura facial
- organizacao de roster
- palette swap por variante ou jogador
- traducao de concept art para sprite jogavel
- comparacao com benchmarks de personagem Mega Drive

## Entregas obrigatorias

- `character_scale_choice`
- `visual_dna_manifest.scale_contract` com `scale_class`, `scale_lock_status`, FOV, hitbox, carga de animacao e politica de mudanca
- `arcade_sprite_style_contract` quando houver personagem grande, lutador, boss humanoide ou promessa arcade/hi-bit
- `lineart_blocking_1px` para personagem critico, heroi, lutador, boss, NPC expressivo ou asset autoral
- `silhouette_test_result`
- `material_color_ramp_plan`
- `palette_role_map`
- `art_gameplay_direction_gate` para personagem critico, heroi, lutador, boss,
  NPC expressivo ou asset autoral antes de model sheet, key poses, strips ou
  sheet final
- `roster_distinction_notes`
- `face_readability_notes`
- `delivery_findings`

## Regras canonicas

- escala do sprite e decidida antes da producao da sheet
- personagem critico nao comeca model sheet, key poses, strips ou sheet final
  sem `art_gameplay_direction_gate` com contexto de GDD/spec, camera,
  gameplay role, interacoes e revisao de art director
- escala aprovada para key poses precisa estar `locked`; se mudar depois, reseed e replanejar FOV, hitbox, pivot, tiles, residencia e animacao
- estilo arcade/hi-bit grande so e permitido com contrato de proporcao, budget e residencia; nao e default
- personagem critico nao inicia `color blocking` ou shading final sem `lineart_blocking_1px`
- `lineart_blocking_1px` usa linha principal de 1 px, hard-edge, sem AA/blur, em uma unica cor escura temporaria para focar forma, roupa, cabelo e anatomia antes da saturacao
- degraus desnecessarios, double corners, pixels orfaos e diagonais sujas bloqueiam a promocao da lineart
- a cor temporaria da lineart deve virar slot de outline/dark shadow no `palette_role_map`; ela nao pode entrar em palette swap por acidente
- heroi deve ser o elemento mais legivel e saturado da tela jogavel
- silhueta tem que funcionar em preto puro
- rosto pequeno comunica por contraste e postura, nao por microdetalhe
- material critico usa rampas curtas por funcao: highlight, base, shadow e dark shadow quando o budget permitir
- `material_color_ramp_plan` deve declarar hue shift por material critico: highlight tende ao quente/amarelo quando aplicavel; sombra tende a azul/roxo/frio; cinza/preto misturado por quantizacao nao conta como direcao de arte
- palette swap troca roupas e sinais de identidade secundaria, nao estrutura
- roster compartilha base cromatica sem perder diferenciação funcional
- cabelo, olhos, rosto, roupa, emblema, cicatriz, caracteristica fisica unica,
  arma, acessorio, material e assimetria sao marcadores de identidade; se um
  marcador muda entre poses sem oclusao ou acao justificavel, a entrega vira
  `cohesion_drift`
- sprite sheet reprovada, parcial ou sem gates humanos/runtime completos nunca
  corrige identidade por cima de si mesma. Quando houver drift de cabelo,
  olhos, roupa, emblemas, cicatrizes, feature assinatura, arma, acessorio,
  anatomia ou material, a rota volta ao model sheet aprovado/travado,
  `visual_dna_manifest`, brief de direcao, lineart 1 px e key poses; a sheet
  ruim vira `obsolete_for_generation_source` e apenas evidencia negativa.

### Proporcao de plataforma 2D

Origem: `curation_records/case_character_proportion_pixel_art_platformer.json`
(lote `curation_batch_2026_06_16`, evidencia `E1_text`, expansao candidata).
Estas regras refinam o `character_scale_contract` existente; nao criam contrato
ou schema novo e nao prometem AAA/runtime.

- personagem jogavel de plataforma deve declarar `character_scale_contract`
  (parte do `visual_dna_manifest.scale_contract`) antes de key poses
- proporcao recomendada para plataforma 16-bit: caixa visual `16x32` ou multiplo
  equivalente quando o gameplay usar grade `16x16`
- escala de `3 a 4 cabecas` para sprites pequenos/medios, salvo justificativa
  explicita por genero declarada no contrato
- rosto/olhos so contam como leitura quando legiveis na resolucao nativa
  `320x224`; detalhe facial invisivel nao justifica escala
- o sprite visual pode exceder a hitbox, mas a hitbox deve ser fixa, menor que o
  visual e documentada no contrato; margem visual nao e hitbox
- toda escala de heroi, inimigo ou boss deve declarar papel, budget e leitura em
  `320x224`
- a expansao continua candidata: exige fixture visual ou contrato de baseline
  antes de promover para producao

## Gates de aprovacao

- `silhouette_recognition`
- `lineart_cleanliness`
- `scale_lock_integrity`
- `scale_gameplay_fit`
- `hue_shift_ramp_quality`
- `color_hierarchy`
- `readability_at_native`
- `palette_sharing_efficiency`
- `archetype_distinction`

## Anti-padroes

- rosto detalhado demais para a escala
- escala escolhida por beleza isolada sem FOV, hitbox e custo de animacao
- key poses ou strips iniciados com escala em `draft`
- heroi que some no fundo
- lutador arcade grande sem budget de metasprite, scanline e residencia
- lineart suja tentando ser corrigida com cor, sombra ou zoom
- color blocking iniciado antes de lineart 1px limpa em personagem critico
- color ramp sem papel de material, gerando arte lavada ou barrenta
- straight shading que escurece/clareia a mesma matiz e gera sprite morto
- roster com mesma forma e mesma cor dominante
- silhouette boa so em zoom
- outline entrando no palette swap

## Senior Competencies

Esta skill deve dominar explicitamente:

- `palette sharing under pressure`
  - roster compartilhando base cromatica sem colapsar leitura
- `silhouette under FX-heavy scenes`
  - personagem continua reconhecivel sob chuva, glow, wobble, split e parallax forte
- `readability under shadow/highlight`
  - volumes criticos e rosto nao podem depender do slot operador
- `readability under palette cycling`
  - personagem nao pode perder prioridade quando o fundo pulsa ou gira cor
- `boss-scale identity`
  - escalar personagem ou boss sem perder massa, hierarquia e funcao
- `arcade_hi_bit_sprite_contract`
  - proporcao 6-7 cabecas, 80-110 px, anatomia blocada e fundo subordinado sem prometer o que o VDP nao suporta
- `lineart_blocking_1px`
  - linha estrutural de 1 px, cor escura temporaria, limpeza de degraus e separacao entre desenho, saturacao e shading
- `character_scale_contract`
  - escala como decisao de gameplay: FOV, hitbox, workload, pivot, tile budget e integer-pixel render
- `hue_shift_material_ramps`
  - rampas por material com temperatura, funcao e economia real de slots

Regra:

- esta skill decide identidade, silhueta e hierarquia de cor
- se a cena pesada destruir essa leitura, a aprovacao deve ser retirada ate que a combinacao volte a funcionar

## Integracao

- combinar com `sprite-animation` quando o personagem tambem estiver em fase de sheet
- combinar com `art-translation-to-vdp` quando a origem vier de ilustração, mockup ou sheet editorial
- combinar com `visual-excellence-standards` quando a decisao for mais estetica do que estrutural

## Contrato Operacional

### Entrada minima

- papel do personagem no gameplay e na fantasia do projeto
- `master_style_manifest` quando o personagem for gerado ou expandido por IA/sourcing
- escala desejada ou faixa de pixels/tile budget preliminar
- `visual_dna_manifest` quando existir ou novo `scale_contract` a emitir antes de key poses
- contexto de cena, roster ou inimigos que competem pela leitura
- restricoes de paleta, efeitos e prioridade visual conhecidas

### Saida minima

- `character_scale_choice`
- `visual_dna_manifest.scale_contract` quando houver personagem novo ou alteracao de escala
- `arcade_sprite_style_contract` quando aplicavel
- `lineart_blocking_1px` quando aplicavel
- `silhouette_test_result`
- `material_color_ramp_plan`
- `palette_role_map`
- `style_anchor_inheritance` quando houver `master_style_manifest`
- `art_gameplay_direction_gate` quando o personagem for critico ou autoral
- `roster_distinction_notes`
- `face_readability_notes`
- `delivery_findings`

### Passa quando

- silhueta funciona em preto puro e em 320x224 nativo
- `visual_dna_manifest.scale_contract` tem bbox em multiplos de 8, FOV, hitbox, workload, integer-pixel motion e `scale_lock_status=locked` antes de aprovar key poses
- se `arcade_sprite_style_contract` se aplica, altura, proporcao, metasprite, budget e fundo subordinado estao declarados
- se `lineart_blocking_1px` se aplica, a linha 1px em cor escura temporaria foi limpa antes de color blocking e mapeada para outline/dark shadow no `palette_role_map`
- paleta diferencia funcao, faccao ou estado sem quebrar compartilhamento
- material critico possui hue shift curado ou justificativa explicita para rampa neutra
- personagem herda paleta, line weight, iluminacao e densidade do `master_style_manifest` quando existir
- `art_gameplay_direction_gate` foi aprovado antes de key poses, strips ou sheet
  final, e todos os marcadores `must_preserve` de identidade foram preservados
  ou declarados como oclusao/acao justificada
- rosto, postura e massa continuam legiveis sob FX previstos
- personagem nao depende de detalhe subpixel, alpha, AA ou gradiente inexistente

### Handoff para proxima etapa

- entregar escala, silhueta e paleta para `sprite-animation`
- entregar concept/mockup aprovado para `art-translation-to-vdp` quando houver fonte high-res
- entregar riscos de leitura para `visual-excellence-standards` e `megadrive-vdp-budget-analyst`
