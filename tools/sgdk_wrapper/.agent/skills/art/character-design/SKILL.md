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
- `silhouette_test_result`
- `palette_role_map`
- `roster_distinction_notes`
- `face_readability_notes`
- `delivery_findings`

## Regras canonicas

- escala do sprite e decidida antes da producao da sheet
- heroi deve ser o elemento mais legivel e saturado da tela jogavel
- silhueta tem que funcionar em preto puro
- rosto pequeno comunica por contraste e postura, nao por microdetalhe
- palette swap troca roupas e sinais de identidade secundaria, nao estrutura
- roster compartilha base cromatica sem perder diferenciação funcional

## Gates de aprovacao

- `silhouette_recognition`
- `color_hierarchy`
- `readability_at_native`
- `palette_sharing_efficiency`
- `archetype_distinction`

## Anti-padroes

- rosto detalhado demais para a escala
- heroi que some no fundo
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

Regra:

- esta skill decide identidade, silhueta e hierarquia de cor
- se a cena pesada destruir essa leitura, a aprovacao deve ser retirada ate que a combinacao volte a funcionar

## Integracao

- combinar com `sprite-animation` quando o personagem tambem estiver em fase de sheet
- combinar com `art-translation-to-vdp` quando a origem vier de ilustração, mockup ou sheet editorial
- combinar com `visual-excellence-standards` quando a decisao for mais estetica do que estrutural
