---
status: historical_art_audit
report_date: 2026-07-28
scope: MARE_BRAVA VER.001, registros locais ate 2026-07-09
asset_mutation: false
---

# 21 - Relatorio de Direcao de Arte — MARE BRAVA VER.001

## Leitura executiva

MARE BRAVA ainda esta na **pre-producao visual com provas tecnicas pontuais**,
nao na fase de arte final. A VER.001 ja tem uma linguagem de arte bem definida,
um conjunto consideravel de fontes conceituais e um plano de composicao para o
CAIS_01 que dialoga diretamente com o hardware. O projeto tambem teve a
disciplina rara e correta de reprovar traducoes tecnicamente validas quando
elas nao preservavam a identidade da heroina.

O saldo mais forte ate aqui e a transformacao de uma ideia visual ampla em um
processo rastreavel: concept source -> prova de leitura em 320x224 -> model
sheet pixel -> lineart nativo -> key poses -> strip -> conversao para `res/`.
O processo ainda esta entre as tres primeiras etapas. Nenhum concept, painel
do cais ou lineart da TAINA deve ser chamado de arte final, e nenhum deles foi
promovido para a ROM como asset de gameplay.

> **Escopo temporal.** Este parecer cobre os registros locais entre 2026-07-03
> e 2026-07-09. Dias sem entrada sao ausencia de registro nesta trilha, e nao
> prova de ausencia de trabalho. As entradas de 2026-06-03 no changelog sao
> heredadas do template e nao pertencem a producao de MARE BRAVA.

## Linha do tempo e historico de criacao

| Periodo | Fase e producao observada | Leitura historica |
|---|---|---|
| 2026-06-03 | Snapshots de branding, ROM e probes XGM2 registrados antes do nascimento do projeto. | Material de template. O proprio changelog o reclassifica explicitamente como heranca; ele prova apenas que a base tecnica existia. |
| 2026-07-03, inicio | Nascimento do projeto, GDD, contratos de brawler, escala de personagens e direcao `angular_cps2_fighter`. | Primeiro veio a fundacao de linguagem e gameplay, nao um sprite isolado. A escolha fixa uma heroina de 48 px, inimigos de 44/56 px e o cais como palco de combate. |
| 2026-07-03, pico de concepts | Recebidos 15 concepts: TAINA, inimigos, HUD/FX, logo e cais. Criada a prancha `vdp_survival_contact_sheet_v01.png` em 320x224, 15 cores e snap de cor MD. | Pico de produtividade conceitual. A prova visual separou imediatamente o que sobrevive a reducao do que exige redesenho nativo. |
| 2026-07-03, correcao de rota | CAIS_01 deixa de ser tratado como panorama pronto e passa a ser um `scene_kit` modular, guiado por blueprint, streaming, camera, ring-out e parallax. | Gargalo convertido em decisao de autoria: uma imagem pode sugerir materia e atmosfera, mas nao deve decidir sozinha o layout jogavel nem a residencia de tiles. |
| 2026-07-04 | Prompt pack revisado; contrato de traco autoral; lote de pranchas candidatas e um descarte auditavel por texto indevido. | A producao fica mais seletiva: o objetivo nao e gerar mais imagens, e gerar fontes com linhagem, papel e criterio de aceite. |
| 2026-07-08 | Rodadas de lineart TAINA v03–v07, relatorios de fidelidade, contratos de escala/pivot/animacao e build tecnico v001. | Pico de refinamento, mas tambem o maior gargalo artistico: PNG valido e grid correto nao recuperaram por si sos rosto, cabelo, guarda e peso corporal. A ROM/BlastEm observou apenas boot/menu. |
| 2026-07-09 | Rota nativa de imagem retomada; quatro turnarounds da TAINA gerados, dois aceitos como `source_candidate` e dois descartados. | Recuperacao da etapa de fonte: melhora a base para um futuro model sheet pixel, mas nao equivale a sprite, animacao ou integracao em `res/`. |

Os picos registrados se concentram em 3 de julho (fundacao, concepts e
arquitetura de cena) e 8 de julho (critica e traducao da personagem). O
intervalo de 5–7 de julho nao possui entrada de producao no changelog; este
relatorio nao o interpreta como queda de produtividade.

## O fluxo artistico e a maturidade dos assets

O `premium_source_manifest.json` atual contabiliza 23 itens: **19
`source_candidate`**, dois `mood_reference_only` e dois
`landmark_reference_only`. Essa classificacao e o principal sinal de maturidade
do pipeline: a fonte e preservada, mas nao recebe um status que ela ainda nao
conquistou.

| Familia | Evidencia | Estagio correto | Leitura de direcao de arte |
|---|---|---|---|
| Concepts de TAINA, CRIA, ESTIVADOR, HUD/FX, logo e cais | `data/source_art/` e `premium_source_manifest.json` | `source_candidate` | Estabelecem identidade, roupa, materiais, clima e composicao; sao fontes RGB/RGBA de alta resolucao, nao PNGs prontos para ResComp. |
| Paineis do cais e loop mar/ceu | `data/source_art/cais_world/` | `mood_reference_only` ou `landmark_reference_only` | Valem por atmosfera, paleta e landmarks; nao autorizam tilemap final, layout pronto ou promocao a `res/`. |
| Prancha de sobrevivencia VDP | `data/processed/contact_sheets/vdp_survival_contact_sheet_v01.png` | prova visual offline | Em 320x224, o cais, o horizonte e o logo continuam claros; os personagens reduzidos perdem anatomia e identidade. Ela prova uma decisao de rota, nao um asset de runtime. |
| Lineart TAINA v03–v07 | `data/processed/characters/taina/lineart/` e relatorios de fidelidade | controle tecnico e evidencia negativa/iterativa | Sao PNGs indexados, 192x64, com quatro celulas de 48x64, dois indices e index 0 magenta. Passam sintaxe, mas nao a fidelidade visual. |
| Branding em `res/branding/` | `res/resources.res` | baseline herdado do template | As cinco `IMAGE` declaradas estao integradas ao recurso de branding, nao constituem identidade final de MARE BRAVA nem arte de gameplay do brawler. |
| Board do mundo | `doc/art/world_layout_board_1344x224.png` | documento de montagem | Mostra fases, locks de camera, ring-out, landmarks e costuras de streaming. E um excelente mapa de decisao, mas nao e background final. |

### O que a prancha em 320x224 revelou

Esta foi a decisao estetica mais produtiva da VER.001. O cais de entardecer
mantem uma leitura forte porque as massas maiores sobreviveram: ceu e mar se
separam, o tablado tem perspectiva simples, os landmarks recortam o horizonte e
as rampas quente/fria ainda organizam a profundidade. O logo tambem conserva
silhueta e contraste em miniatura.

O resultado oposto nos personagens e igualmente valioso. A reducao direta
produz massas corporais difusas: rosto, massa de cabelo, guarda de muay thai e
roupa deixam de comunicar caracter. Isso encerrou cedo uma armadilha comum de
arte 16-bit — confundir downscale com pixel art — e deslocou o processo para
redesenho em grid nativo.

### A TAINA como estudo de rigor

Os candidatos v03/v04 foram corretamente reprovados por serem simbolicos e
genericos. O v05 recuperou parte do cabelo cacheado, face wedge, guarda alta,
luvas, faixa e calca larga, mas se afastou da escala e caiu em proporcao chibi.
O v07 corrigiu parte da altura visivel e o contato dos pes com o pivot, porem
perdeu novamente a irregularidade do cabelo, a atitude de sobrancelha/maxilar e
a mecanica dos antebracos. O veredito atual e `scale_probe_not_promoted`.

Essa sequencia e um aprendizado, nao desperdicio: o projeto mediu que escala,
silhueta e identidade precisam ser resolvidas juntas. A proxima tentativa deve
nascer do model sheet aprovado e dos contratos de escala/animacao, preservando
os ganhos de identidade do v05 sem reutilizar v06/v07 como fonte final.

## Restricao como oportunidade de linguagem

O projeto nao esta usando o Mega Drive apenas como um teto de cores; esta
desenhando uma gramatica visual que faz a restricao trabalhar a favor do
brawler.

- **Paleta como elenco de papeis.** Os quatro dominios previstos separam
  cenario, heroina/FX, inimigos e HUD/espuma. A luz quente de fim de tarde e a
  sombra fria com hue shift permitem que pele, tecido, madeira e mar tenham
  funcao cromatica sem competir pela mesma leitura.
- **Silhueta antes de acabamento.** Em lutadores de 44–56 px, o que sobrevive
  e a massa de cabelo, guarda, ombros, calca e postura. Esse limite favorece
  uma direcao agressiva e grafica, em vez de detalhes ilustrativos que so
  existem ampliados.
- **Animacao com intencao, nao volume bruto.** O catalogo planeja estados de
  4–8 frames, antecipacao curta, impacto travado e hitstop; sem smear no slice.
  Isso abre espaco para timing e pose venderem impacto, preservando VRAM para a
  cena e para os inimigos.
- **Profundidade com funcao de gameplay.** BG_A e o cais jogavel streamado; o
  BG_B e um loop de 512 px com quatro bandas a 0.125, 0.25, 0.375 e 0.5. Em vez
  de um panorama caro, a parallax cria velocidade e distancia. A espuma nunca
  cortada funciona como aviso de beirada/ring-out, portanto e sinal jogavel,
  nao decoracao.
- **Composicao modular como autoria.** O kit do cais deve combinar piso,
  borda, props, landmarks, oclusao e ecologia. Reuso de tiles, flip, palettes e
  scroll passam a ser ferramentas de ritmo espacial, nao reducoes de ambicao.

As tecnicas de `palette_cycling` e Shadow/Highlight aparecem como ambicao
adiada/de laboratorio. Elas sao oportunidades futuras, nao efeitos ja usados
na VER.001; o relato mantem essa diferenca para nao antecipar entrega.

## Aprendizados e desafios superados

1. **Fonte premium e asset VDP sao categorias diferentes.** Concepts de alta
   resolucao sao valiosos para decisao de design, mas precisam de traducao
   semantica, paleta indexada, grid, tiles e budget antes de chegar a `res/`.
2. **O panorama foi substituido por uma cena jogavel.** A correcao do CAIS_01
   evita que uma imagem bonita determine camera, ring-out, colisoes, costuras e
   streaming. O `world_layout_board` devolve essas decisoes ao level design.
3. **Conformidade tecnica nao aprova personagem.** TAINA v05/v07 passam
   dimensao, indexacao e cores, mas ainda falham em `visual_pass`. Esse e o
   comportamento correto de um gate de arte: a sintaxe do VDP nao substitui
   anatomia, materiais, acting ou fidelidade ao model sheet.
4. **Paleta compartilhada precisa nascer cedo.** A separacao de dominios e o
   index 0 predefinido evitam que cenario, heroina, inimigos e HUD disputem os
   mesmos tons tarde demais. O custo visual vira planejamento, nao correcao de
   ultima hora.
5. **A evidencia observada ainda e estreita.** A ROM v001 e a janela BlastEm
   confirmam boot/menu, mas nao validam o CAIS_01, a TAINA, animacao, gameplay,
   performance, audio ou budget VDP. A build prova a base tecnica, nao a arte
   do jogo.

## Estagio atual da construcao artistica

### Consolidado como direcao e processo

- Fantasia visual de cais brasileiro ao entardecer, gramática de linha,
  materiais e paleta documentadas.
- Escala do elenco, estados de animacao, criterio de hitstop e contratos de
  pivot/scale definidos.
- Sources organizados por status, hash e uso permitido; descartes mantidos como
  evidencias auditaveis.
- Rota do CAIS_01 orientada por camera, parallax, ring-out, foreground e
  streaming, em vez de por um unico background ilustrado.
- Prova offline de leitura em 320x224 capaz de orientar a proxima conversao.

### Ainda provisiorio, bloqueado ou ausente

- Model sheet pixel definitivo e lineart 1 px aprovado da TAINA; color
  blocking, key poses, strip, frame delta, pivot overlay e prova de movimento.
- Sources de producao para CRIA e ESTIVADOR; seus telegraphs e poses de hit/down.
- Decomposicao do `dock_scene_kit` em familias A–G e sua traducao para tiles,
  mapas, paletas e recursos SGDK.
- Conversao do tilemap do CAIS_01, conflito por paleta/tile e medicao de VRAM,
  DMA, residencia e pior scanline.
- Logo, HUD e FX autorais finalizados; o branding em `res/` permanece baseline
  herdado.
- Evidencia visual de gameplay no BlastEm. A captura existente e apenas de
  boot/menu e nao pode promover a qualidade da arte de combate.

O status mais honesto, portanto, e: **direcao visual consistente e fontes
promissoras, com traducao nativa de personagem e de cenario ainda incompleta**.
O proximo ganho real nao e outro build; e um model sheet pixel da TAINA que
passe em leitura, identidade e escala, seguido da decomposicao modular do cais.

## Evidencias consultadas

Para comparacao cronologica das imagens e das mudancas de decisao, ver tambem
`doc/22-linha-do-tempo-visual-ver-001.md`.

- `doc/changelog/changelog.md`
- `doc/10-memory-bank.md`
- `data/source_art/premium_source_manifest.json`
- `doc/art/asset_acceptance_report.json`
- `doc/art/art_asset_diagnostic.json`
- `doc/art/art_direction_decision_record.json`
- `doc/art/master_style_manifest.json`
- `doc/contracts/level_art_assembly_contract.json`
- `doc/contracts/parallax_layer_contract.json`
- `doc/art/characters/taina/native_grid_translation_report_v01.json`
- `doc/art/characters/taina/lineart_blocking_report_v01.json`
- `doc/art/characters/taina/model_sheet_to_sprite_fidelity_report_v05.json`
- `doc/art/characters/taina/model_sheet_to_sprite_fidelity_report_v07.json`
- `data/processed/contact_sheets/vdp_survival_contact_sheet_v01.png`
- `doc/art/characters/taina/review/taina_lineart_v05_v06_v07_compare_6x_v01.png`
- `doc/art/world_layout_board_1344x224.png`
- `res/resources.res`
