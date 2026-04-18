---
name: visual-excellence-standards
description: Converte direcao de arte de Mega Drive em metricas e gates de hardware AAA. Use quando o agente precisar julgar, criar, revisar, converter, otimizar ou corrigir assets visuais como recursos de VDP em vez de tratar PNGs como imagens genericas. Obriga referencias reais de jogos MD, heuristicas preventivas, leitura do banco vivo em doc/03_art/02_visual_feedback_bank.md e canonizacao de feedback humano antes de qualquer ajuste pontual em arte.
---

# Visual Excellence Standards

Esta skill e o cerebro estetico do workspace MegaDrive_DEV.

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

### Leitura em 320x224
- Avalie sempre em escala nativa.
- Se um detalhe so funciona ampliado, ele ainda nao existe no jogo.

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
