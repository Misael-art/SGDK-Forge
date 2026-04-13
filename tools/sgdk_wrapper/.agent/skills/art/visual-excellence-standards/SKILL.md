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
