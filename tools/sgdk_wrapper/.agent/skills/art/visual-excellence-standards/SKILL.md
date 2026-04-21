---
name: visual-excellence-standards
description: Use quando a tarefa pedir julgamento estetico, legibilidade, contraste entre planos, dithering funcional, leitura CRT-aware, eficiencia perceptiva de paleta ou canonizacao de feedback visual para assets Mega Drive. Esta skill trata arte como recurso de VDP com barra AAA e memoria acumulada. Nao use para diagnosticar qual cenario de arte o projeto possui, converter tecnicamente assets ja aprovados para o pipeline, buscar assets externos ou validar restricoes pixel-rigidas sem contexto estetico.
---

# Visual Excellence Standards

Esta skill e o cerebro estetico do workspace MegaDrive_DEV.

Quando a entrada principal for uma imagem-fonte high-res, concept art ou arte de IA que precise ser reinterpretada para o VDP, use esta skill em conjunto com `art-translation-to-vdp`.

Se o `source` vier como prancha editorial, spritesheet com residuos, tile/object sheet ou board misto, a primeira pergunta nao e "qual paleta usar?".
A primeira pergunta e "o que dessa prancha e cena util e o que e ruido semantico?".

Todo asset deve ser tratado como recurso de hardware:
- paleta compartilhada
- tiles 8x8
- custo de VRAM
- legibilidade em 320x224
- contraste entre planos
- potencial de reuso via flip e duplicata

Nao existe "imagem bonita" isolada do hardware. Existe composicao visual que sobrevive ao VDP do Mega Drive.

## Contrato Operacional

### Entrada minima

- fonte visual (ou assets traduzidos por layer) e seu papel na cena
- `doc/03_art/02_visual_feedback_bank.md` e barra de qualidade quando existirem
- contexto de composicao (`layer_plan` / `shared_canvas_contract`) quando houver multi-plano
- `ui_decision_card` quando a surface formal for HUD/UI/overlay/menu
- `scene_transition_card` quando houver transicao formal de cena, zona, ato, menu, cutscene ou estado visual

### Saida minima

- julgamento estetico com criterio observavel (nao apenas subjetivo)
- metricas canonicas aplicadas (ex.: `palette_efficiency`, `layer_separation`)
- leitura de `attention_profile` e `hud_density` quando houver UI formal
- leitura de `transition_role`, `continuity_model` e clareza visual quando houver transicao formal
- leitura de `typography_role` e contraste tipografico quando houver anexo tipografico
- bloqueios visuais registrados quando aplicavel (ex.: `visual_gate_blocked`)
- recomendacao objetiva de proxima etapa (budget/runtime)

### Passa quando

- a leitura em 320x224 nativo foi considerada
- os sintomas foram traduzidos em diagnostico tecnico e heuristica preventiva quando necessario
- a decisao resultante nao contradiz o hardware sem declarar tradeoff
- quando houver UI formal, `attention_profile`, `hud_density` e clareza da arquitetura ficam registrados
- quando houver transicao formal, a tecnica comunica causa, geografia, tom, risco ou ritmo; se for so bonita, reprovar
- quando houver tipografia relevante, fonte-display, fonte-body, acentos e separacao contra o fundo ficam julgados

### Handoff para proxima etapa

- se a rota visual estiver congelada: entregar para `hardware/megadrive-vdp-budget-analyst`
- se ainda faltar traducao: entregar para `art/art-translation-to-vdp` com lista objetiva de ajustes

## Regra de Ouro

Nenhum feedback humano corrige PNG diretamente.

Fluxo obrigatorio:
1. Capturar o sintoma em linguagem observavel.
2. Traduzir o sintoma em diagnostico tecnico.
3. Escrever uma heuristica preventiva em [doc/03_art/02_visual_feedback_bank.md](F:\Projects\MegaDrive_DEV\doc\03_art\02_visual_feedback_bank.md).
4. Atualizar esta skill se a heuristica passar a valer como regra geral.
5. So entao corrigir o asset.

Se o agente pular esse fluxo, a melhoria nao foi canonizada. Foi improvisada.

## Leitura obrigatoria

Antes de qualquer iteracao visual relevante:
1. Ler [doc/03_art/02_visual_feedback_bank.md](F:\Projects\MegaDrive_DEV\doc\03_art\02_visual_feedback_bank.md)
2. Ler [doc/03_art/00_visual_quality_bar.md](F:\Projects\MegaDrive_DEV\doc\03_art\00_visual_quality_bar.md)
3. Ler [doc/03_art/01_visual_cohesion_system.md](F:\Projects\MegaDrive_DEV\doc\03_art\01_visual_cohesion_system.md)
4. Conferir o budget da cena e a funcao do asset no gameplay
5. Se a fonte for complexa, exigir `semantic_parse_report` antes de julgar a traducao

## Metricas canonicas

Estas metricas devem ser usadas pelo agente, pelo `analyze_aesthetic.py` e pelo discurso tecnico sobre arte:

### `palette_efficiency`
- Mede se a paleta esta trabalhando a favor do asset ou desperdicando slots.
- Penaliza cores redundantes, pouca distancia tonal util e cores quase indistinguiveis.
- Pergunta base: "Cada cor ganhou o direito de existir?"

### `tile_efficiency`
- Mede aproveitamento real dos tiles 8x8.
- Penaliza bordas vazias, bounding box frouxo e excesso de tile morto.
- Pergunta base: "Quanto desse sprite consome VRAM sem entregar leitura?"

### `detail_density_8x8`
- Mede riqueza de detalhe por tile sem confundir ruido com acabamento.
- O alvo e densidade legivel, nao sujeira.
- Pergunta base: "O tile conta materia e volume ou so empilha pixel?"

### `dithering_density`
- Mede se o dithering foi usado como ferramenta de gradiente e material, nao como muleta aleatoria.
- Bom dithering cria transicao e textura controlada.
- Mau dithering parece ruido ou xadrez sem funcao.

### `silhouette_readability`
- Mede se a massa principal do sprite e clara em 1 frame.
- Outline, massa, pose e contraste interno devem colaborar.
- Pergunta base: "O jogador reconhece a forma antes de ler detalhes?"

### `layer_separation`
- Mede separacao tonal e luminosa entre sprite e fundo, ou entre BG_A e BG_B.
- O plano importante deve vencer a disputa de leitura.
- Pergunta base: "O gameplay salta do fundo ou afunda nele?"

### `reuse_opportunity`
- Estima quanto do asset poderia ser reorganizado para maior reuso em VRAM.
- Considera duplicatas, espelhamentos e oportunidades de consolidacao de tiles.
- Pergunta base: "Estamos pagando VRAM por informacao nova ou por repeticao desorganizada?"

## Traducao de estetica para hardware

## Exploracao controlada de rotas visuais

Quando o usuario pedir alternativas, ou quando uma cena critica admitir duas leituras fortes sem quebrar o hardware, esta skill deve julgar as rotas como uma familia controlada, nao como experimentos soltos.

Entregas esperadas:

- `route_exploration_board`
- `route_comparison_matrix`
- `route_preferred_by_judge`
- `locked_visual_direction` apos escolha humana

Regras:

- todas as rotas devem compartilhar o mesmo `shared_canvas_contract`
- todas as rotas devem respeitar o mesmo teto de paleta e a mesma historia espacial
- cada rota deve declarar qual eixo esta variando
- rotas nao podem competir por geometrias ou enquadramentos incompatíveis

Eixos aceitaveis de variacao:

- ceu e atmosfera
- temperatura global
- contraste e densidade de sombra
- peso do `BG_B` versus `BG_A`
- limpeza versus aspereza do material

Eixos proibidos sem nova rodada de composicao:

- perspectiva
- distribuicao de massas principais
- posicao do ponto focal
- papel estrutural dos planos

Protocolo de julgamento:

1. eliminar rotas que so parecem fortes ampliadas
2. eliminar rotas que sacrificam gameplay para ganhar ilustracao
3. ranquear as sobreviventes por leitura, atmosfera, coerencia de projeto e risco de budget
4. recomendar uma rota, mas preservar a escolha do usuario quando mais de uma ainda for valida

## Regra de incumbencia

Quando ja existir uma rota padrao aprovada no projeto, ela passa a ser o `incumbent visual method`.

As rotas alternativas podem ser apresentadas ao usuario, mas nao substituem o incumbente por default.

Para um desafiante substituir o incumbente, ele precisa vencer em dois niveis ao mesmo tempo:

1. `perceptual win`
   - leitura igual ou melhor
   - identidade da cena igual ou melhor
   - coerencia com a linguagem do projeto igual ou melhor
2. `system win`
   - budget igual ou melhor
   - risco estrutural igual ou menor
   - promocao para ROM igual ou mais honesta

Regra:

- se o desafiante so vencer em "imagem bonita isolada", ele nao toma o lugar do incumbente
- se o incumbente for multi-plano, o julgamento precisa acontecer em contexto composto, nao apenas na layer isolada
- na ausencia de vitoria clara do desafiante, o default continua sendo o metodo padrao ja consolidado

Aplicacao pratica:

- `visual_excellence_score` isolado nao pode derrubar sozinho um metodo incumbente multi-plano
- a decisao final de rota deve considerar tambem reuse, pressao de tiles e aderencia ao `source` como cena

Regra de ouro:

- o foco AAA nao significa impor uma unica resposta
- significa oferecer poucas rotas excelentes, cada uma honesta com o hardware, e depois congelar a direcao escolhida para manter coerencia visual

### Dithering
- Nao e enfeite.
- E mecanismo para simular gradiente, materiais e atmosfera com poucas cores.
- Em metal, ceu, pedra e fumaca, a ausencia de dithering so e aceitavel se houver outra solucao de volume igualmente forte.

### Outline
- Outline serve para separar massa, fixar silhueta e impedir que o sprite suma no fundo.
- Outline nao precisa ser preto absoluto em todos os casos, mas precisa produzir leitura.

### Volume
- Todo material principal precisa de pelo menos tres estados legiveis: luz, base e sombra.
- Volume sem direcao de luz nao existe. E borrado.

### Materiais
- Metal: highlights agressivos, contraste alto, transicoes controladas
- Pedra: massa opaca, textura rustica, quebra de superficie
- Pele: rampas mais suaves, leitura de plano, contraste localizado
- Tecido: sombra mais larga, menos brilho especular

### Contraste de planos
- BG_B deve competir menos que BG_A.
- Sprite principal deve competir menos consigo mesmo do que com o fundo.
- Se tudo brilha igual, nada conduz gameplay.

### Economia de paleta
- Compartilhar paleta nao e sacrificio. E planejamento.
- Paleta boa serve a mais de um sistema da cena sem destruir hierarquia visual.
- Em traducao elite, quantizacao cega so pode servir de controle.
- O resultado canônico vem de curadoria manual semantica: escolher quais rampas ficam, quais tons fundem e qual highlight realmente merece sobreviver.

### Review de tileset
- `palette_strip`, `tileset_sheet` e auditoria de `H-Flip` ajudam a revelar disciplina estrutural real.
- Isso e criterio de review e planejamento de VRAM, nao objetivo estetico isolado.
- Se a imagem fica mais "organizada" mas menos legivel, o review esta certo e a transformacao visual esta errada.

### Leitura em 320x224
- Avalie sempre em escala nativa.
- Se um detalhe so funciona ampliado, ele ainda nao existe no jogo.

## Menus e Title Screens

Menu forte no Mega Drive nao e tela parada com lista de opcoes. E uma cena de apresentacao.
Referencia longa: `doc/03_art/12_menu_visual_language.md`.
Doutrina complementar obrigatoria: `doc/03_art/13_hud_ui_fx_decision_system.md`.

Checklist canonico:
- o menu precisa compor a proposta do jogo, nao uma estetica generica solta
- o fundo deve permanecer vivo em idle, via parallax, cycling, wobble, timeline curta ou equivalente tematico
- o olhar deve ser conduzido por uma geometria forte, como piso em perspectiva ou outra estrutura espacial coerente com o tema
- a tipografia deve vencer o fundo com outline, sombra dura ou separacao de valor igualmente forte
- a opcao selecionada deve ter feedback ativo visivel, nao apenas troca de cor
- a paleta deve ter contraste alto e hierarquia perceptiva clara

Defaults fortes:
- 2 a 3 camadas de profundidade
- um eixo visual dominante no fundo
- item selecionado com pulso, seta viva, brilho corrido ou cycling controlado

Regra de versatilidade:
- `grade infinita` e referencia historica, nao obrigacao universal
- o equivalente correto depende do projeto: energia, ruina, arquitetura, magia, industria, horizonte urbano ou outro motivo espacial forte

Anti-padroes:
- fundo sem vida
- excesso de detalhe atras do texto
- menu que parece overlay de debug
- identidade visual desconectada do jogo

## HUD, interface e overlay

- quando houver surface formal de UI, ler o `ui_decision_card` antes de julgar a imagem
- `attention_profile` define quanta disputa visual a interface pode criar por segundo
- `hud_density` nao pode subir alem do que a mecanica consegue sustentar
- `typography_role` decide a rota:
  - `hud_critical` tende a `fixed_custom_hud_font`
  - `narrative_text` tende a `variable_width_tidytext`
  - `front_end_premium` pode pedir `display_font_plus_body_font`
- `window_plane_static_hud` continua sendo o default seguro para leitura constante
- `fixed_custom_hud_font` e o default forte para timer, score, ammo, labels e leitura rapida
- `variable_width_tidytext` sobe para dialogo, credito, lore e corpo de texto premium em PT-BR
- reprovar fonte ornamental pesada ou compositor proporcional em HUD de combate
- `window_plane_lifebar` e `sonic_hud_physics_family` sao referencias de pattern, nao defaults universais
- `raster_enhanced_ui` e `procedural_raster_glitch_suite` so passam quando houver ganho perceptivo real, `fx_ownership_map` e fallback honesto

## Transicoes contextualizadas

- quando houver transicao formal, ler o `scene_transition_card` antes de julgar a imagem
- `transition_role` precisa explicar por que a troca existe: geografia, causa narrativa, ritmo, risco, humor, maquina, sonho ou palco
- `continuity_model` decide o julgamento visual:
  - `spatial_scroll_bridge` precisa preservar leitura de camera e esconder o seam
  - `scripted_avatar_bridge` precisa fazer o avatar parecer agente da passagem, nao passageiro de cutscene vazia
  - `lighting_state_transition` precisa manter silhueta, paleta e prioridade de gameplay legiveis
  - `raster_distortion_bridge` precisa servir agua, impacto, sonho, corrupcao ou choque fisico, nao enfeite solto
  - `pseudo3d_perspective_bridge` precisa justificar o custo como setpiece e declarar fallback
- se a transicao tocar HUD, menu, title, overlay ou texto, consumir tambem o `ui_decision_card`
- `palette_fade_bridge` e fallback honesto, mas nao deve substituir uma passagem espacial clara quando o mundo poderia conectar as cenas
- reprovar efeito que esconda estado do jogador, confunda direcao de movimento ou quebre o ritmo sem payoff dramatico

## Extrapolacao legitima do VDP

### Repartir budget e melhor que fingir que o limite nao existe

- O caminho elite nao e forcar uma cena impossivel.
- O caminho elite e reorganizar budget com intencao.
- A primeira resposta estrutural deve ser a menos fragil.
- Em cenas de cenario grande, `VDP_setPlaneSize(..)` vem antes de alias de tabela.
- Se o foreground realmente precisa de uma paleta propria, mover o background para `3+1` pode ser decisao superior.
- Se a profundidade pede um elemento intermediario, `sprite graft` pode ser legitimo.
- Se a prova em ROM nao comporta dois planos completos, `compare_flat` pode ser a forma honesta de provar leitura sem mentir sobre o hardware.

### Taxonomia de montagem avancada

- `canonica_segura`
  - `plane size tuning`
  - reorganizacao de paleta
  - `SPR_initEx(u16 vramSize)` quando a medicao pedir
  - `compare_flat`
- `avancada_com_tradeoff`
  - `window alias`
  - `hscroll slack reuse`
  - `sprite graft`
- `opt_in_de_cena_especial`
  - `SAT reuse`
  - quirks de mascaramento ou comportamento off-screen
  - `borrowed_fx_ramp`

Regra:

- tecnica de layout nao e virtude estetica por si so
- ela so sobe de categoria quando preserva leitura e reduz fragilidade do layout

### Auditoria de slot em Shadow/Highlight

- Em cenas que usam Shadow/Highlight para afetar fundo e sprite juntos, o ultimo slot visivel da paleta do sprite deve ser tratado como auditado.
- Nao colocar ali:
  - highlight principal de pele
  - highlight principal de metal
  - volume critico que deve reagir normalmente a sombra
- Esse slot pode ser sacrificado de forma defensiva ou usado de forma intencional para ponto emissivo.
- Sem `palette_slot_audit`, a cena com Shadow/Highlight nao esta madura.

### Waterline e palette split

- Separacao de agua, atmosfera ou gradiente dramatico por split mid-frame deve preservar coerencia cromatica entre os dois hemisferios da tela.
- A parte abaixo da linha nao pode parecer "outra fase" sem causa.
- Se a linha oscilar, a leitura precisa continuar estavel quadro a quadro.

### Leitura sob interlace

- `interlaced_448` nunca deve ser julgado apenas por "caber mais coisa".
- O criterio visual minimo e: shimmer toleravel, tipografia legivel e ganho real de layout em relacao ao modo normal.
- Se a cena treme mais do que informa, o modo foi mal aplicado.

### Ilusoes modernas honestas

- `masked_shadow_highlight_lighting`
  - deve ser julgado como spotlight, lanterna ou weak spot de boss, nunca como luz suave de engine moderna
- `procedural_raster_glitch_suite`
  - so funciona quando o ruído e dirigido e o jogador continua lendo risco, hitbox e objetivo
- `mutable_tile_decal_mutation`
  - o valor visual esta na persistencia localizada e na narrativa do impacto, nao em prometer destruicao universal
- `cellular_microbuffer_sim`
  - so e elite quando uma ilha pequena parece organica sem trair o budget; aumentar a area sem necessidade e erro de direcao

### Fundo enorme nao e virtude por si so

- Conversao direta de ilustracao inteira costuma gerar muitos tiles unicos e pouca inteligencia estrutural.
- O agente deve desconfiar de toda cena bonita que "so cabe" porque ninguem mediu o VDP ainda.

## Quirks e exploits opt-in

- Bugs e comportamentos de mascaramento do VDP sao ferramentas avancadas, nao defaults.
- O agente nao deve explorar quirk de sprite off-screen por padrao.
- So liberar exploit quando existir:
  - intencao declarada
  - benchmark dedicado
  - evidencia em BlastEm
  - memoria operacional descrevendo riscos e motivacao

## Protocolo de referencias

Nenhum asset critico pode ser iniciado sem:
1. Tres jogos reais de Mega Drive.
2. Heranca explicita por jogo.
3. Justificativa do que esta sendo herdado.

Formato obrigatorio:
- `referencia_1`: jogo + heranca tecnica
- `referencia_2`: jogo + heranca tecnica
- `referencia_3`: jogo + heranca tecnica

Exemplo de heranca aceitavel:
- `Streets of Rage 3`: contraste de silhueta e musculatura sombreada
- `Monster World IV`: delicadeza de textura e clareza cromatica
- `Shinobi III`: leitura de sprite contra fundos movimentados

Exemplo de heranca invalida:
- "quero algo bonito tipo Sega"

## Protocolo de feedback

Todo feedback corretivo deve sair desta estrutura:

```markdown
sintoma: "o rosto esta borrado"
diagnostico_tecnico: "faltou separacao entre plano do maxilar e sombra de bochecha em 16x16"
heuristica_preventiva: "rostos abaixo de 24x24 precisam de contorno mandibular explicito e highlight de testa isolado"
metricas_afetadas:
- silhouette_readability
- detail_density_8x8
benchmark_referencia:
- Monster World IV
check_em_rom: "validar no BENCHMARK_VISUAL_LAB em BlastEm com fundo claro e escuro"
```

## Senior Competencies

Esta skill deve tratar como competencias seniores explicitas:

- `waterline readability`
  - leitura acima e abaixo da linha de split sem ruptura cromatica acidental
- `palette split coherence`
  - transicao cromatica dramática sem perder pertencimento de cena
- `interlace tolerance`
  - shimmer aceitavel e hierarquia visual ainda legivel em 448
- `shadow/highlight slot audit`
  - operador nao pode destruir volume critico por descuido
- `CRT-aware evaluation`
  - dithering e material precisam sobreviver ao julgamento LCD + CRT-aware

## Gatilhos de reprovacao

Reprovar imediatamente quando houver:
- sprite flat sem volume convincente
- paleta desperdicada com cores quase iguais
- fundo engolindo sprite critico
- material sem leitura do que e
- tile vazio em excesso
- ruido confundido com detalhe
- dithering aleatorio sem funcao
- asset cuja leitura so existe ampliada

## Integracao com agentes

### `art-director`
- Usa esta skill como barreira de veto.
- Nenhum asset critico pode ser aprovado sem passar pelas metricas canonicas.

### `mega-drive-pixel-engineer`
- Traduz diretriz visual em custo de hardware.
- Deve sempre reportar leitura visual junto com custo de VRAM.

### `art-creator`
- Usa esta skill para formular prompts, buscar referencias e filtrar assets externos.
- Nao pode descrever arte apenas em termos subjetivos.

### `art-pipeline-operator`
- Usa esta skill para transformar diagnostico visual em gate operacional.
- Deve chamar o juiz estetico e refletir a leitura no `validation_report.json`.

## Governanca operacional

- A validacao visual AAA nao substitui a validacao tecnica. Ela a complementa.
- Asset tecnicamente valido ainda pode ser reprovado por legibilidade ruim.
- Asset bonito mas inviavel para VDP continua reprovado.

## O Segredo da Profundidade

- `BG_B` deve carregar atmosfera e massa distante com contraste menor e densidade de detalhe menor.
- `BG_A` deve carregar estrutura de cena, mas continuar subordinado ao plano jogavel.
- O sprite ou elemento heroico deve ser o pico de leitura da composicao.
- Separacao tonal vem antes de separacao por matiz.
- Quando o fundo parece mais agressivo que o personagem, a cena esta visualmente errada mesmo que esteja "bonita".
- Densidade precisa obedecer hierarquia:
  - `BG_B`: respiracao
  - `BG_A`: estrutura
  - `sprite`: decisao
- Regra de reprovação:
  - se `BG_A` ou `BG_B` exigem mais atencao do olho que o elemento jogavel, falhou o criterio de profundidade canônica.

## Benchmark Lab

Novas heuristicas so viram doutrina canonizada quando:
1. entram em [doc/03_art/02_visual_feedback_bank.md](F:\Projects\MegaDrive_DEV\doc\03_art\02_visual_feedback_bank.md)
2. atualizam esta skill
3. sao provadas em `BENCHMARK_VISUAL_LAB` com ROM observada no BlastEm

## Nunca faca

- Tratar PNG como fim em si mesmo
- Aceitar feedback humano como remendo local sem generalizar
- Confundir ruido com riqueza
- Confundir mais cores com melhor paleta
- Corrigir legibilidade com detalhe extra quando o problema e silhueta
- Declarar excelencia visual sem prova em ROM

## Senior Competencies

Esta skill deve assumir pericia explicita em:

- `dithering funcional`
  - gradiente, material e atmosfera; nunca xadrez aleatorio
- `CRT-aware reading`
  - distinguir leitura de LCD ampliado de leitura perceptual em tela nativa
- `shadow/highlight slot audit`
  - proteger slots criticos de volume e brilho do sprite
- `material readability under VDP limits`
  - metal, pedra, pele, tecido e fogo sob 15 cores por paleta
- `palette cycling hierarchy`
  - cor em movimento sem destruir prioridade dos planos
- `FX-heavy readability`
  - personagem continua vencendo fundo mesmo sob wobble, split, glow ou chuva

Regra:

- esta skill pode reprovar arte tecnicamente valida se a leitura falhar
- ela tambem pode aprovar recuo visual honesto quando isso preserva a cena no hardware
