# Baseline de proveniencia de asset — diretriz de bloqueio estetico

Data: 2026-08-17
Politica retroativa aprovada: **retroativo com auditoria**
Excecao de fixture aprovada: **excecao nomeada por manifesto** (`validator_fixture`)
Machine-readable: `doc/curation/asset_provenance_baseline_2026-08-17.json`
Enforcement: `tools/sgdk_wrapper/audit_procedural_asset_provenance.py`

Status: `documentado_bloqueio_sem_promocao`.

## O que mudou

A diretriz "nenhum grafico desenhado por codigo representa personagem, inimigo, boss ou
cenario na compilacao final" **ja estava escrita** em `SGDK_GLOBAL.md` (8.2, 17, 22),
`visual-excellence-standards`, `art-creation-sourcing`, `art-conversion-pipeline`,
`image-generation-routing` e no pipeline `aaa_scene_v1.json`.

Ela nao era medida. O unico detector estatico era `VDP_drawText >= 8 && SPR_addSprite == 0`
em `validate_resources.ps1`, e `audit_placeholder_quarantine.ps1` decidia por
**nome de arquivo e tag declarada** — um PNG desenhado por `ImageDraw` e salvo com nome
limpo passava intacto.

Essa curadoria fecha o furo com proveniencia declarada por simbolo do `.res`, auditada
contra os builders que realmente escrevem cada arquivo.

## Baseline medida

| Projeto | Simbolos visuais | Rastreados a builder de primitivas | Veredito |
|---|---|---|---|
| BLUE_CIRCUIT | 9 | 0 | BLOCKED — proveniencia ausente |
| Celestial Chase Revive | 11 | 0 | BLOCKED — proveniencia ausente |
| Celestial Chase visual benchmark | 21 | **20** | BLOCKED — promocao procedural |
| FORGE_REFERENCE | 0 | 0 | OK — `validator_fixture` |
| GOTHAM_OVERDRIVE | 16 | 5 | BLOCKED — promocao procedural |
| KIRBY_FAN GAME CLOUDE | 22 | **21** | BLOCKED — promocao procedural |
| KIRBY_FAN GAME GROK BUILD | 26 | 5 | BLOCKED — promocao procedural |
| MARE_BRAVA | 15 | **11** | BLOCKED — promocao procedural |
| SMOKE_TEST | 16 | 16 | BLOCKED — promocao procedural |

Total: 9 projetos auditados, 8 bloqueados, 136 simbolos visuais, **78 rastreados a
builders que desenham por primitiva**.

Nenhum projeto sustentava `ready_for_aaa=true` antes desta auditoria, portanto nao houve
selo AAA a revogar. O efeito retroativo real e sobre os **tetos de claim**: cinco projetos
declaram `vertical_slice` e dois `technical_demo` com arte cuja proveniencia agora esta
formalmente bloqueada. Esses tetos ficam sem sustentacao ate re-autoria ou declaracao
honesta de `placeholder`.

## Leitura por caso

- **MARE_BRAVA** — 7 dos 8 builders em `tools/art/` importam `ImageDraw`;
  `build_taina_p0_locomotion_v01.py` tem 13 chamadas de primitiva. A heroina TAINA e os
  backgrounds de CAIS_01 entram no `.res` como `final` sem marca de placeholder. Pela
  Regra 17 esses assets deveriam estar em quarentena desde o commit `9c21683d`.
- **SMOKE_TEST** — 16/16 simbolos procedurais. Coerente com a funcao de smoke, mas precisa
  declarar `acceptance_status: placeholder` para ficar honesto em vez de silencioso.
- **FORGE_REFERENCE** — unico OK. Passou a declarar `validator_fixture: true` e teve
  `delivery_claim_ceiling` corrigido de `technical_demo` para `lab`: fixture nao pode
  compilar sem asset externo **e** manter teto de entrega visual.

## Rota de saida por projeto

1. Criar `doc/asset_provenance_manifest.json` declarando cada simbolo do `.res`.
2. Para asset desenhado por primitiva: `source_kind: procedural_primitive` +
   `acceptance_status: placeholder`. Isso desbloqueia o gate e mantem o teto honesto.
3. Para promover a `final`: re-autorar a arte por canal externo, ou persistir a fonte
   autoral em `data/source_art/` e declarar `procedural_composed_from_authored` com hash —
   codigo pode montar, recortar e paletizar arte autoral, nunca desenha-la.
4. Rodar o auditor e anexar o report ao closeout.

## Falsos positivos calibrados durante a curadoria

O detector de runtime foi corrigido duas vezes antes de entrar; a primeira versao reprovava
9/9 projetos por engano:

- `TILE_USER_INDEX`, `VDP_setTileMapXY` e `VDP_fillTileMapRect` sao endereçamento de VRAM e
  composicao de mapa de asset **importado** — nao contam como arte por codigo;
- paleta autoral em C (`const u16 pal_x[16]` com literais de 4 digitos) e trabalho legitimo
  de paleta — nao conta como tile art.

O sinal aceito e estreito de proposito: `const u32` com >=16 literais de 8 digitos, que e a
forma de pixel de tile no SGDK. Gate que grita em projeto saudavel e gate que sera ignorado.

## Limites deste registro

Nao promove projeto, asset, ROM, release ou status AAA. Nao altera skills de arte, pipeline
`aaa_scene_v1.json` nem os validadores PowerShell existentes. Nao renomeia projeto legado.

## Fase 2 — diretriz residente por projeto

A diretriz deixou de depender de um agente lembrar de ler o workspace. Ela agora mora
dentro de cada projeto, em `doc/00-diretrizes-agente.md` (autoridade #4 da hierarquia de
verdade), entre os marcadores `diretriz-bloqueio-estetico v1`, e carrega o **estado medido
daquele projeto**: contagem de simbolos, quantos vem de builder de primitivas, blockers
ativos e a lista nominal dos simbolos com o builder que escreve cada um.

- Injetado em 12 projetos (9 de topo + 3 subprojetos de treino/laboratorio).
- Injetado no template `tools/sgdk_wrapper/modelo/doc/00-diretrizes-agente.md` sem bloco de
  medicao, portanto **todo projeto novo nasce com a diretriz**.
- `new_project.sh` e `new_project.bat` imprimem a diretriz e o comando do auditor no
  bootstrap.
- Ferramenta idempotente: `tools/sgdk_wrapper/apply_aesthetic_directive.py`. Com `--check`
  retorna exit 1 quando um projeto esta sem diretriz ou com medicao velha — serve de gate
  de CI local.
- Insercao verificada como aditiva: 82 linhas adicionadas e 0 removidas em MARE_BRAVA,
  nenhum conteudo pre-existente alterado.

### Achado sistemico: o branding compartilhado e procedural

`tools/image-tools/build_branding_intro_assets.py` desenha por primitiva os 5 simbolos de
branding (`img_brand_fx_tiles`, `img_brand_engine_logo`, `img_brand_author_logo`,
`img_brand_project_logo`, `img_brand_presents_text`) e **8 projetos consomem esses
simbolos como finais**. Isso significa que qualquer projeto que use a intro de branding
herda 5 violacoes por default, sem ter escrito uma linha de builder.

Corrigir na fonte resolve os 8 de uma vez: re-autorar o logo da engine, o logo do autor e
o texto de apresentacao como arte externa, ou declarar os 5 como `placeholder` no manifesto
de cada projeto enquanto a arte definitiva nao existir. Esta decisao e de curadoria humana
e nao foi tomada aqui.

### Achado: fixture sem manifesto de contexto

`SGDK_projects/_agent_laboratory/SCENE_TILEMAP_CURATION_FIXTURE [...]` se chama fixture,
tem 6 simbolos visuais (5 procedurais de branding) e **nao possui
`doc/project_context_manifest.json`** — portanto nao pode declarar `validator_fixture`,
nem `context_type`, nem teto de claim. Nao inventei o manifesto: ele exige classificacao
humana. Enquanto nao existir, o projeto fica bloqueado como qualquer outro.

## Fase 3 — causa raiz encontrada e abertura v2 fundamentada

### A causa raiz nao era o agente, era o prompt

`doc/15-prompt-telas-assinatura.md`, o prompt mestre das telas de assinatura, instruia
literalmente: *"voce nao pode encerrar dizendo 'falta gerar assets' se ainda pode entregar a
estrutura procedural placeholder que compila"*, alem de *"mantenha o fallback procedural"*.

Os 78 simbolos procedurais nao vieram de preguica de agente. Vieram de obediencia a uma
instrucao canonica. O documento existia em **10 projetos**, contradizendo diretamente a
diretriz instalada na fase 2 nos mesmos projetos.

- Prompt do template reescrito como v2, com a politica invertida: encerrar com o blocker de
  arte nomeado passou a ser entrega honesta, e renderer procedural deixou de ser rota de
  saida.
- Banner de revogacao inserido nas 10 copias existentes (20 linhas adicionadas, 0 removidas
  por copia; as 2 copias com conteudo divergente foram preservadas intactas).

### Abertura de assinatura v2: `branding_sequence_v2`

O contrato v1 ja se autodenunciava com o blocker
`visual_aesthetic_report_has_rework_for_existing_author_logo_until_art_pass`. A medicao
confirma que nao era so a arte:

| Eixo | v1 medido | Leitura |
|---|---|---|
| Sprites | `sprite_engine_peak: 0` de 80 | hardware de sprite 100% ocioso |
| Scanline | `max_scanline_sprites: 0` de 20 | idem |
| Paletas | PAL2 e PAL3 ociosas | 32 de 64 entradas de CRAM paradas |
| H-Int | nenhum | sem gradiente alem de 61 cores |
| Shadow/Highlight | nunca ligado | unico operador de luz do MD sem uso |
| Line scroll | amplitude 2 por 36 quadros | assinatura do MD usada e desligada |
| CPU | `over_budget_frames: 1`, `cpu_load_max: 401` | estouro com zero sprites |

O spike de CPU com hardware ocioso aponta o upload da tabela de HScroll por CPU e os
`VDP_drawImageEx` no caminho de troca de fase. Como o v2 e uma tomada continua sem trocas de
fase e envia a tabela por DMA no VBlank, corrigir isso e o passo 1 da implementacao.

Conceito: **"A FORJA"** — tomada unica, tres atos, zero cortes a preto. Uma brasa cai, o
martelo bate, o impacto forja a marca em metal incandescente. A metafora existe para dar
funcao mecanica aos pontos fortes do VDP: emissividade por Shadow/Highlight, metal liquido
por rotacao de CRAM, ar quente por line scroll, estilhaços por multiplexacao de sprites.

- 28 tecnicas declaradas, **todas com `registry_id` conferido contra
  `doc/05_technical/93_16bit_hardware_mastery_registry.json`** — zero ID inventado.
- 4 tecnicas rejeitadas com motivo declarado (`interlaced_448_display_mode`,
  `procedural_raster_glitch_suite`, `pseudo3d_road_stack`, `software_affine_pseudo3d`).
- As 4 paletas ocupadas, com folga de highlight reservada em PAL1[13..14] por
  `shadow_highlight_slot_rule` — sem essa folga a varredura especular do ato 2 nao existe.
- Truque de orcamento: o enxame de 32 estilhaços usa 1 sprite de 4 quadros com flip H/V
  (`tile_flipping` + `tile_dedup_hvflip_hashing`), gerando 16 orientacoes com **zero DMA de
  tile de sprite por quadro**.
- Todo numero de orcamento marcado `measurement_level: estimated`, exigindo
  `res_graph_report`, `vdp_scanline_simulator.py` e `visual_vdp_dump.bin`. O workspace se
  recusa a fixar teto de DMA por decreto e o contrato respeita isso.

Fundamento entregue no template: contrato v2, `inc/scenes/branding_v2.h` com a linha do
tempo e o mapa de posse do H-Int, bloco de 8 declaracoes `.res` comentadas com dimensoes e
paleta por asset, e o prompt de handoff com portao de aprovacao humana apos o model sheet.

**Status: `documentado`.** A arte v2 nao existe, o runtime v2 nao esta implementado, nada foi
buildado nem observado em emulador.

## Fase 4 — direcao de arte da abertura v2

`doc/branding_v2_art_direction.md` e `doc/art_direction_decision_record.json` autorados no
template. A direcao esta FECHADA: o agente de arte executa e preenche apenas campos
`execution_*`, sem inventar direcao.

- As 6 travas da Visual Quality Bar preenchidas antecipadamente.
- Estilo primario `gothic_16bit_dark_fantasy` (lighting_model "torchlit hard highlights" e
  palette_signature com "gold highlights, cool shadows" descrevem literalmente uma forja;
  `mega_drive_compatibility=native`, `vram_pressure_hint=medium`); secundario
  `vibrant_16bit_pixel` restrito a rampa emissiva. Rejeitados
  `baroque_32bit_gothic_pixel` e `digicel_16bit_animation` por `vram_pressure_hint=high`.
  Os 4 IDs conferidos contra `art_style_catalog.json` — nenhum inventado.
- Decisao central de direcao: **a forja ilumina de baixo**. Plano superior em sombra, face
  inferior iluminada, sombra subindo pela parede, contato com o piso como ponto mais quente
  da imagem. Asset legivel como iluminado de cima reprova por definicao.
- Papel de indice de paleta travado como contrato (o runtime depende dele), hex como seed
  ajustavel. Duas travas criticas: `PAL0[9..12]` precisa fechar em ciclo porque o runtime
  rotaciona em CRAM, e `PAL1[13..14]` precisa ficar abaixo do branco maximo senao a
  varredura especular do ato 2 nao existe.
- Model sheet especificado em 5 paineis (512x384), cada um provando uma decisao herdavel.
  Painel E exige brasa e estilhaco a 16x16 real, nao ampliados.

### Pendencia que exige decisao humana

`trava_5_art_gameplay_direction_gate` esta com `needs_human_ruling`. A cena nao tem gameplay:
nao existe rota, risco, timing de inimigo ou decisao do jogador para a arte alterar, e o eixo
de consequencia jogavel nao pode ser preenchido com invencao. A proposta e substituir por
`brand_comprehension_consequence`. Sem decisao do curador, o blocker
`art_gameplay_direction_gate_axis_undeclared` fica aberto no closeout.

## Fase 5 — trava_5 aplicada: `brand_comprehension_consequence`

Eixo aprovado pela curadoria humana em 2026-08-17 e aplicado. Escopo estrito: cena de marca
sem gameplay (branding, title card, selo de autor). **Cena jogavel continua obrigada ao eixo
canonico de consequencia jogavel** — a substituicao nao e rota de fuga.

Definicao: cada decisao de arte precisa mudar o que o espectador entende sobre quem fez o jogo.

### Por que ela pode reprovar

Um eixo aprovado que nao reprova nada e decoracao — exatamente o padrao que esta curadoria
passou a sessao fechando. A substituicao so e legitima porque e falsificavel:

- toda tecnica carrega `brand_comprehension_claim` + `brand_comprehension_negative_test` +
  `brand_comprehension_strength`; ou
- e classificada `enabling_discipline` (previne artefato, nao ensina nada ao espectador,
  isenta mas obrigatoria);
- tecnica que nao e nem um nem outro e espetaculo sem consequencia e reprova.

Enforcement: `tools/sgdk_wrapper/validate_brand_comprehension_gate.py`. Blockers:
`brand_comprehension_missing`, `brand_comprehension_not_falsifiable`,
`brand_comprehension_strength_undeclared`, `brand_comprehension_unjustified_technique`.

### O gate encontrou um problema na primeira execucao

`xgm2_audio_architecture` estava declarado como tecnica do ato 2 com funcao "cauda de reverb e
acento metalico" e ficou sem justificativa. Julgamento: o registry_id descreve **arquitetura de
driver**, nao uma afirmacao ao espectador; a funcao declarada confundia encanamento com
conteudo. Reclassificado como `enabling_discipline`, com o claim espacial da cauda de reverb
realocado para `audio_contract.new_cue_map`.

Resultado final: 24 tecnicas auditadas, 15 comprehension_bearing, 9 enabling_discipline,
veredito OK.

### Dois claims marcados como fracos, nao escondidos

- `column_scrolling` — a cortina por coluna carrega continuidade, mas um fade tambem
  preservaria continuidade; o ganho e de carater, nao estrutural;
- `expressive_text_presentation_system` — timing de respiracao dos wordmarks nao quebra nada
  visivelmente se for arbitrario, o que expoe o risco de virar decoracao.

Ambos exigem prova perceptiva no runtime e **nao podem ser apresentados como fortes no
closeout**.

### Limite declarado da automacao

O validador prova que nenhuma tecnica passou sem justificativa. Ele nao julga se o claim e
verdadeiro: isso permanece decisao humana no gate visual, contra screenshot e
`visual_vdp_dump` reais. Automatizar julgamento subjetivo seria recriar o falso verde.

## Fase 6 — diretriz e gate aplicados nos projetos existentes

### Dois falsos verdes fechados antes de aplicar

**1. O gate passava contratos vazios.** O validador procurava tecnicas em `acts` (formato v2).
Os projetos existentes usam `screens` (v1) e um usa um v3 divergente — nenhum declara tecnica
com `registry_id`. Aplicado como estava, o gate reportaria OK em 10 projetos sem julgar nada.
Corrigido: a coleta virou varredura recursiva, agnostica de formato, e contrato de cena de
marca **ativo sem nenhuma tecnica declarada** agora e blocker
`brand_comprehension_techniques_undeclared`. Ausencia de declaracao nao e aprovacao.

**2. Um subprojeto ficava fora da varredura.** `apply_aesthetic_directive.py` descia um nivel
em containers, entao o viewer SGDK aninhado em
`_agent_training/[ESTUDO]_mugen_sff_showdown_v1/sgdk_viewer/showdown_viewer` — que tem `doc/`,
`res/` e `src/` proprios — nunca recebia a diretriz. Descoberta trocada por profundidade
arbitraria. Cobertura foi de 12 para **13 projetos**.

### Estado apos aplicar

Gate de compreensao de marca, 11 contratos:

| Projeto | Contrato | Estado | Veredito |
|---|---|---|---|
| BLUE_CIRCUIT | `branding_sequence_legacy_template_inactive` | inactive | **OK — isento declarado** |
| Celestial Chase Revive | `credits_contract.json` (sem `contract_id`) | active | BLOCKED |
| Celestial Chase visual benchmark | `branding_sequence_v1` | active | BLOCKED |
| FORGE_REFERENCE | `branding_sequence_v1` | active | BLOCKED |
| GOTHAM_OVERDRIVE | `branding_sequence_v1` | active | BLOCKED |
| KIRBY_FAN CLOUDE | `branding_sequence_v1` | active | BLOCKED |
| KIRBY_FAN GROK BUILD | `branding_sequence_v1` | active | BLOCKED |
| MARE_BRAVA | `branding_sequence_v1` | active | BLOCKED |
| SMOKE_TEST | `branding_sequence_v3` | active | BLOCKED |
| SCENE_TILEMAP_CURATION_FIXTURE | `branding_sequence_v1` | active | BLOCKED |
| showdown_viewer (aninhado) | `branding_sequence_v1` | active | BLOCKED |

**10 de 11 bloqueados, 1 isento.** O unico OK e o BLUE_CIRCUIT, que declarou seu contrato de
branding inativo porque foi substituido pela title screen propria — isencao registrada como
`exempt_inactive_contract`, com a nota de que a cena de marca ativa dele precisa ser gateada
onde ela realmente vive.

Diretriz estetica: bloco elevado para `diretriz-bloqueio-estetico v2` nos 13 projetos e no
template, substituindo o v1 em vez de duplicar. O bloco agora carrega tambem o eixo
`brand_comprehension_consequence`, com o escopo estrito e o comando do gate.

### O que NAO foi propagado, de proposito

A direcao criativa "A FORJA" ficou **so no template**. Impor o conceito de forja a 10 projetos
existentes seria overreach de curadoria: BLUE_CIRCUIT ja substituiu o branding pela title
screen propria e o SMOKE_TEST tem um `branding_sequence_v3` com conceito autoral. O que foi
propagado e a **exigencia estrutural** — declarar claim com teste negativo para a marca que
cada projeto ja tem — nao o conceito.

### Achado de higiene

`Celestial Chase Revive/doc/credits_contract.json` nao tem campo `contract_id`. Passou pelo
gate como `None`. Nao inventei um id: quem conhece o projeto declara.

## Fase 7 — gate do model sheet construido antes da arte

`tools/sgdk_wrapper/validate_model_sheet_contract.py`. O criterio de aceitacao da fase 1 passou
a ser medido **antes** do agente de arte comecar, em vez de discutido depois da entrega.

Seis checks, deliberadamente sem duplicar `art_diagnostic.py` (formato tecnico geral) nem
`art_quality_gate.py` (qualidade artistica):

1. canvas exatamente 512x384;
2. os 5 paineis carregam conteudo;
3. painel B e silhueta de tinta unica (se tem shading, nao esta provando os `silhouette_hooks`);
4. `PAL1[13..14]` com canal maximo `<= 0xCC` — sem folga, o operador de Shadow/Highlight nao tem
   para onde clarear e a varredura especular do ato 2 nao existe;
5. `PAL0[9..12]` fecha como anel uniforme — o runtime rotaciona em CRAM, e passo desigual vira
   tranco na brasa;
6. painel E em escala real, detectando ampliacao por blocos 4x4 uniformes.

Convencao que faltava e foi adicionada a direcao: o model sheet e um PNG indexado com a paleta
ordenada em `PAL0=0-15, PAL1=16-31, PAL2=32-47, PAL3=48-63`. Sem essa ordem o gate nao consegue
ler a folga de highlight nem o ciclo de brasa, e paleta fora de ordem reprova por nao ser
verificavel.

### Dois erros meus que a construcao do gate expos

**Seeds de paleta invalidos.** `0x0630` e `0x0CDD` na direcao de arte usam nibbles `3` e `D`,
que nao existem no CRAM de 9 bits. Corrigidos para `0x0620` e `0x0CCC`. O agente de arte teria
herdado cor impossivel de representar.

**Definicao errada de "ciclo fechado".** A primeira versao comparava o passo de fechamento
contra o maior passo interno. Uma rampa com um salto interno gigante fazia qualquer fechamento
passar — o fixture deliberadamente aberto passou no primeiro teste. Trocado por uniformidade do
anel: os 4 passos, incluindo o wrap, precisam ser comparaveis (razao `<= 3.0`), com deteccao
separada de passo morto por cores duplicadas.

Verificado nas duas direcoes com fixtures sinteticas: folha conforme passa com exit 0, folha
violando dispara os 5 blockers com exit 1, e passo morto no anel dispara isolado. As fixtures
sao PNGs desenhados por codigo no scratchpad — uso de debug permitido pela propria diretriz,
nunca em `res/`.

## Fase 8 — primeira entrega do agente de arte revisada

O agente de arte executou a fase 1 e entregou `model_sheet_forge_v01.png` com 14 fontes
brutas em `raw/`, `assemble_model_sheet.py` e `model_sheet_lineage.json`.

**A rota de proveniencia funcionou.** O assemblador tem zero chamadas de primitiva — apenas
crop, resize nearest, paste, chroma key e remap de paleta. Fontes autorais persistidas com
sha256 por painel, canal declarado `native_chat_image_generation_callable`,
`procedural_generation_used_as_asset_source: false`. Codigo montou, nao desenhou: exatamente
o `procedural_composed_from_authored` que a diretriz permite. O gate de contrato passou com
exit 0.

**O agente nao vendeu a folha como pronta.** Declarou `visual_quality_bar_1994: no_not_yet`
por conta propria e nomeou a parede modular, o martelo e a perda dos rotulos do painel C.
A politica de parada honesta, que substituiu o mandato de fallback procedural, produziu o
comportamento pretendido logo na primeira entrega.

**Revisao: `rework`.** Registro em `doc/model_sheet_review_v01.md`. Quatro blockers:

1. wordmark do painel D iluminado por cima — a calota clara esta na aresta superior e o
   painel vira `img_logo_engine_v2`, entao o erro contamina o ato 2 inteiro;
2. wordmark na familia de paleta errada, azul-ardosia em vez da rampa de ferro de PAL1, o
   que esvazia a varredura especular;
3. wordmark sem a marca de ferramenta assimetrica, caindo no `generic_blocker` de simetria;
4. martelo do painel A iluminado por cima, contradizendo a lei dentro do painel que existe
   para prova-la, e pequeno demais para servir de `silhouette_hook`;
5. os 4 quadros de brasa nao formam rotacao, e os 4 de estilhaco ja sao espelhos entre si,
   o que colapsa as 16 orientacoes esperadas do flip H/V.

**O que a folha acertou:** a lei da luz de baixo funciona no painel A. Fornalha no piso,
barriga da bigorna e parede lavando em laranja, plano superior escuro, pedra distante em
azul-violeta. Temperatura fazendo trabalho estrutural e bico da bigorna legivel em silhueta.
O nucleo da direcao esta de pe.

### Correcao na direcao, nao no trabalho

Eu havia especificado o painel B como "preto puro sobre transparente". O agente entregou
preto sobre branco, que e convencao de estudio padrao e le igual ou melhor. A especificacao
estava apertada demais sem ganho; foi relaxada. O gate ja tolerava dois indices e ficou como
esta.

Vale registrar que os checks de folga de highlight e de ciclo de brasa passaram porque o gate
le a **tabela de paleta do PNG**, nao o painel C. A perda dos rotulos do painel C custa
revisao humana, nao verificacao mecanica.

### Rework despachado

`doc/model_sheet_rework_v02_brief.md`. Passada de correcao, nao recomeco: a v01 acertou a lei
da luz do painel A, o hook da bigorna, o painel B e a rota de proveniencia, e tudo isso fica
preservado.

**Causa tecnica encontrada na revisao do rework:** as 14 fontes brutas sao JPG.
`wordmark_forja_v02.jpg` tem 66.030 cores unicas e o painel D final tem 13 — o ringing e o
blocking do JPEG sobrevivem a quantizacao e viram o salpico dentro das letras e da pedra. Nao
e dither com funcao de material, e artefato de compressao, que a direcao proibe. Duas saidas
oferecidas: fontes em PNG lossless, ou posterizacao/denoise antes do remap de paleta. Sem
isso, qualquer correcao de luz chega suja no PNG final.

## Fase 9 — v02 do model sheet revisada

`doc/model_sheet_review_v02.md`. Os dois blockers duros da v01 estao resolvidos: o wordmark
inverteu a luz (frio no topo, ouro na aresta inferior, mossa so no J, 100% em PAL1) e o
martelo ganhou cunha legivel com o contato na bigorna como ponto mais quente. O median 3x3
mais snap 9-bit antes do remap limpou o ruido de JPEG.

### Furo no meu proprio gate, encontrado ao revisar

Medindo a autocritica do agente, o wordmark usa `PAL1[13..14]` em **0,0%** — os slots de folga
nao sao pintados. Meu gate conferia a folga exatamente neles: media a declaracao, nao a
realidade. `PAL1[12]=(238,204,34)` esta no teto `0xEE` e em uso, e passava.

O operador de Shadow/Highlight clareia a cor de saida do pixel, nao o slot reservado pelo
contrato. Corrigido com `model_sheet_specular_headroom_unusable`, medindo cores pintadas.
Calibrado por proporcao: acima de 15% dos pixels no teto reprova, abaixo fica warning, porque
reprovar um glint de 1% seria gate gritando em asset saudavel. Mesma classe de erro que esta
curadoria vinha fechando nos outros — verificar declaracao em vez de realidade.

### Duas vezes em que a medicao corrigiu minha leitura visual

- achei que a parede regrediu para salpico branco: pixels claros isolados no painel A caem de
  17 na v01 para 4 na v02. E cluster, que e a hachura que a direcao pede. Ampliacao de 3x me
  enganou.
- achei que o fundo competia com o foco: pico de luminancia da parede 80 contra 226 do foco,
  separacao +146, mediana da parede em 3. Hierarquia de valor forte.

### Recomendacao

Aprovar como direcao provada, com um item obrigatorio de arrasto: o wordmark nao tem passo de
luz nenhum, e `img_logo_engine_v2` e justamente o asset sobre o qual a varredura especular do
ato 2 corre. O degrau em `PAL1[13..14]` com canal `<= 0xCC` na aresta inferior de cada haste
precisa entrar na producao do asset final. Isso nao e refinamento, e a existencia do efeito.

Parede modular, rotulos apertados do painel C e entalhe do estilhaco viram arrasto de
producao dos assets, nao uma terceira folha. Aprovacao final e do curador humano.

## Fase 10 — concepcao de cena, e o que ela quebrou no contrato de assets

O curador barrou a liberacao dos 8 assets com a observacao certa: **asset nao e cena**. O
fundamento dizia quais tecnicas e quais arquivos, mas nao dizia o que se move, para onde, em
quanto tempo e com que peso — e a spec dos assets depende disso.

Autorado em `doc/branding_v2_scene_conception.md` (leitura humana) e
`doc/branding_v2_cinematic_storyboard.json`, instancia conforme
`cinematic_storyboard_contract.schema.json`, `status_ceiling: planning_only`. Todos os campos
obrigatorios do schema conferidos.

### A coreografia invalidou o contrato de assets

Escrever o movimento expos que a lista de 8 estava errada:

- **`spr_forge_hammer` e asset NOVO.** O contrato punha o martelo dentro de
  `img_forge_bg_a_props`, uma imagem estatica. Mas o martelo sobe em F96-120 e bate em F120.
  Imagem estatica nao bate. Strip de 6 quadros, 48x48.
- **`img_forge_bg_a_props` perde o martelo**, que virou sprite.
- **`spr_forge_ember` vai de 4 para 6 quadros.** A brasa pousa na bigorna em F96; sem quadro
  de esmagamento e assentamento ela para no ar.
- **`img_forge_bg_b` ganha restricao de composicao.** As 48 scanlines inferiores sofrem
  cisalhamento por linha no ato 2, entao detalhe fino ou aresta que dependa de alinhamento
  horizontal quebra ali.
- **`img_logo_engine_v2` formaliza o degrau de luz** em `PAL1[13..14]` como nao negociavel: e
  sobre ele que a varredura especular corre.

Contagem de 8 para 9.

### Pendencia de orcamento que precede a arte

`spr_forge_hammer` a 6 quadros de 48x48 pesa 216 tiles residentes. Reduzir quadros, reduzir
para 40x40 ou fazer streaming sao decisoes que **mudam o que o artista desenha**, e nenhuma
delas e decisao de arte. Precisa de `res_graph_report` real antes de liberar a producao.

### O que faz isto ser cena

Tres regras estruturais verificaveis: tomada continua sem `VDP_clearPlane`; escalada de camada
de hardware por ato; consequencia fisica em todo efeito. Momento de assinatura em F120, quando
o impacto lanca 32 estilhacos que voltam e se montam no logo — a marca e forjada, nao exibida.

## Fase 11 — streaming decidido, e a coreografia medida quebrando o hardware

Decisao do curador: **streaming** para `spr_forge_hammer`, porque a premissa e maxima qualidade
visual e o golpe e o momento de assinatura. Contrato em
`doc/branding_v2_dma_queue_contract.json`, conforme `dma_queue_contract.schema.json`.

- 216 tiles residentes viram **72** em janela dupla: economia de 144 tiles preservando os 6
  quadros a 48x48;
- custo: 1152 B por troca de quadro, a cada 5,7 quadros, media de 203 B/quadro;
- pior coincidencia teorica 1600 B num VBlank; `vblank_budget_bytes` declarado como envelope
  teorico de 224p NTSC com nota explicita de que **nao e medicao deste projeto**;
- ordem de recuo declarada: alargar o intervalo de troca primeiro, encurtar a janela de ar
  quente depois, e cortar quadro de arte **por ultimo**, porque contraria a premissa.

### A coreografia que eu escrevi quebrava o hardware

Modelei o ato 2 e rodei no `vdp_scanline_simulator.py` canonico antes de existir arte ou
runtime. Resultado: **36 sprites numa scanline** contra o limite de 20, `status: error`. A
estimativa que estava no contrato dizia 12.

Duas causas: todos os 32 estilhacos nasciam no mesmo ponto no mesmo quadro, e a convergencia
terminava com todos empacotados na faixa de 64px do logo (24 em F179).

Tres correcoes, medidas ate passar com folga:

1. spawn escalonado, 2 por quadro ao longo de 16 quadros;
2. **pouso progressivo** — cada estilhaco que chega vira tile e sai do SAT, entao a populacao
   cai durante a montagem em vez de picar no fim;
3. recuo do martelo em 10 quadros. Foi a correcao de maior efeito: ele tem 4 sprites de
   hardware e coexistia com a nuvem.

Medicao final pela ferramenta canonica: **15 sprites por scanline, margem de 25%**. O campo do
storyboard passou de `estimated` para `measured_by_simulator`.

A correcao 2 comecou como orcamento e virou a melhor decisao narrativa do ato: o logo se
constroi peca por peca em vez de trocar de uma vez. O ultimo estilhaco pousa em F194, entao a
linha do tempo do ato 2 foi corrigida de F180 para F194.

**Se eu tivesse liberado a arte antes de medir**, o agente teria desenhado 32 estilhacos para
uma coreografia impossivel, e a descoberta viria na implementacao do runtime com a arte pronta.

## Fase 12 — 9 assets liberados para producao

Curador aprovou o model sheet v02 e a concepcao de cena em 2026-08-17. Estados atualizados:
`trava_3=approved`, storyboard `status_ceiling=production_candidate`, asset_contract
`released_for_production`. Brief em `doc/asset_production_brief_v2.md`.

O brief carrega tres coisas que o contrato sozinho nao carregava:

**1. O requisito nao negociavel do degrau de luz.** `img_logo_engine_v2` precisa de degrau em
`PAL1[13..14]` com canal `<= 0xCC` na aresta inferior. O model sheet v02 nao tem passo de luz
nenhum — 0,0% de uso desses slots — e a varredura especular do ato 2 corre sobre esse asset.

**2. Registro de posicao derivado da coreografia.** Face da bigorna em (128,104), caixa do
logo em x 48-272 / y 80-144, faixa de cisalhamento nas 48 scanlines inferiores. Sem essas
ancoras os assets nao compoem cena: a brasa pousa no ar e o martelo bate no vazio.

**3. Carga de correcao da v02 distribuida nos assets certos.** A parede modular vai para
`img_forge_bg_b`, o entalhe do estilhaco para `spr_forge_shard`, em vez de uma terceira folha
que nao provaria nada novo.

Ordem de producao comeca por `img_forge_bg_a_props`, porque ele fixa o registro de (128,104)
do qual os outros dependem.

O teto de 1994 passa a ser cobrado nos assets. O model sheet era prova de direcao.

## Fase 13 — densidade do enxame: 32 -> 56 sem flicker

Provocacao do curador: tecnicas avancadas de romhack (multiplexacao com flicker, aglutinacao
de sprites, render nos planos) poderiam elevar a cena. Avaliadas uma a uma contra medicao.

### Correcao de numero de hardware

O limite do Mega Drive em H40 e **20 sprites por linha E 320 pixels de sprite por linha**, dois
limites simultaneos. A figura de "32 vagas de slot" nao corresponde ao MD.

Consequencia medida: para sprites de 16x16, `20 x 16 = 320`. Os dois limites **fecham no mesmo
ponto**. Por isso aglutinar estilhacos em sprites maiores nao compraria nada aqui — trocaria
contagem por pixel na razao de 1:1. Aglutinacao paga quando ha muitos sprites de 8x8 adjacentes,
onde se economiza slot sem somar pixel. Os estilhacos sao espalhados de proposito.

### Furo encontrado na minha propria verificacao

`vdp_scanline_simulator.py` reporta apenas `max_sprites_per_scanline`. **Ele nao mede o
orcamento de 320 px por linha.** Toda a validacao anterior desta cena cobria so um dos dois
limites. O segundo foi medido a parte: 288 de 320 no pior quadro.

Isso e uma limitacao da ferramenta canonica, nao deste projeto — outros projetos que dependem
dela estao igualmente descobertos.

### Flicker: excluido pelo canon, nao por opiniao

O skill de budget do workspace ja decide: *"So e canonico se passar em sprites por scanline,
total de sprites na tela, custo de VRAM e ausencia de flicker"* e *"multiplexing/flicker e
tradeoff declarado, nao mascara de overflow"*. Alem disso, numa abertura de marca o flicker e
autodestrutivo: e a primeira impressao de acabamento, e a persistencia retiniana que sustentava
a tecnica em CRT de 1994 e muito mais fraca em painel moderno e em screenshot de emulador, que
e o meio de evidencia do workspace.

### Render nos planos: ja esta em uso, e era a melhor das tres ideias

O pouso progressivo **e** essa tecnica: cada estilhaco que chega vira tile e sai do SAT,
liberando slot. O que nao serve e render por plano de objeto pequeno e rapido — apagar e
redesenhar 56 objetos por quadro custaria varios KB de DMA por VBlank. Plane takeover
(`bg_b_bypassing` no registry) e para objeto grande e lento, tipo boss gigante.

### O que de fato elevou: medir a folga que sobrava

| Estilhacos | Grade | Sprites/linha | Pixels/linha | Margem |
|---|---|---|---|---|
| 32 (antes) | 8x4 | 15/20 | 240/320 | 25% |
| 40 | 10x4 | 20/20 | 320/320 | 0% |
| 48 | 8x6 | 19/20 | 304/320 | 5% |
| **56 (novo)** | **8x7** | **18/20** | **288/320** | **10%** |
| 64 | 8x8 | 20/20 | 320/320 | 0% |

**56 estilhacos, +75% de densidade, sem tecnica nova e sem flicker.** Confirmado pelo simulador
canonico nos quatro piores quadros: 18/20, `status: ok`. Ultimo pouso vai de F194 para F203.

A intuicao do curador de que a cena podia ser mais densa estava certa. A rota era medicao, nao
flicker. Nao muda nenhum asset: mesmo `spr_forge_shard` de 4 quadros, so mais instancias.

## Fase 14 — simulador com os dois limites, e a doutrina de audacia

### `vdp_scanline_simulator.py` v1.0.0 -> v1.1.0

A v1.0.0 media apenas contagem de sprites por linha. Toda cena validada por ela ficou
descoberta no orcamento de pixel — nao so esta abertura, mas qualquer projeto do workspace que
tenha usado a ferramenta.

Adicionado, mantendo retrocompatibilidade (todos os campos antigos preservados):

- `max_sprite_pixels_per_scanline` e `over_pixel_limit_lines`;
- blocker `sprite_pixels_per_scanline_over_<limite>`;
- suporte a `display_mode` h40 (20 sprites / 320 px) e h32 (16 / 256);
- bloco `headroom` com utilizacao dos dois limites, qual deles amarra e a justificativa
  declarada;
- warning `unexploited_headroom` abaixo de 60% de utilizacao de pico.

`--self-check` passou de 2 para 5 assercoes, incluindo o caso que a v1.0.0 nao enxergava: 16
sprites de 32px numa linha passam na contagem (16 de 20) e estouram o pixel (512 de 320).

Cena real dos 56 estilhacos medida na v1.1.0: 18/20 sprites (90%) e 288/320 px (90%), limite
que amarra e a contagem.

### Doutrina de audacia, `SGDK_GLOBAL.md` secao 30

Pedido do curador: o agente deve ser audacioso e buscar o maximo dos limites, sem conter, mas
respeitando direcao de arte, level design e premissas.

O risco de encodar isso e obvio — "seja audacioso" vira licenca para overclaim, que e o
oposto de tudo que esta curadoria construiu. A formulacao que resolve:

> **Audacia e sobre a ambicao, nunca sobre o claim.** Empurre o que voce tenta; meca o que
> voce afirma. Quanto mais ousado o alvo, mais rigorosa precisa ser a medicao.

Isso separa os dois eixos em vez de troca-los. Ambicao alta com claim medido e o padrao;
ambicao baixa desperdica hardware; claim alto sem medicao e falso verde, ja bloqueado.

Regras operacionais:

- **antes de fechar um orcamento, meca o degrau seguinte.** Se 32 cabem, meca 48 e 64. Pare
  quando MEDIR o estouro, nao quando sentir receio. O numero entregue tem que ser resultado de
  busca, nao o primeiro que funcionou;
- **`unexploited_headroom` e aviso, nunca blocker**, limpo por `headroom_justification`. Forca
  decisao consciente sem proibir cena leve;
- **direcao de arte, level design e premissas vencem a densidade, mas por declaracao**, nunca
  por omissao;
- **falsa audacia** — flicker para mascarar overflow, efeito sem consequencia, densidade que
  destroi leitura — continua bloqueada, e nao vira permitida em nome de ser ousado.

Dois casos canonicos registrados na propria secao: o 32 -> 56 como audacia correta, e a
proposta de flicker como falsa audacia.

Propagacao: `AGENTS.md` (secao propria no ponto de entrada + restricao nao negociavel +
referencia rapida), `SGDK_GLOBAL.md` secao 30, e o bloco de diretriz por projeto elevado a
`diretriz-bloqueio-estetico v3` nos 13 projetos e no template, substituindo o v2 sem duplicar.

## Fase 15 — varredura de folga nas cenas contratadas

Pedido: rodar o simulador nas cenas ja contratadas.

**Nao foi possivel, e a impossibilidade e o primeiro achado.** O
`vdp_scanline_simulator.py` exige layout de sprites (x/y/w/h por sprite). **Nenhuma cena
contratada do workspace declara layout** — todas declaram pressao como prosa ou como um numero
solto. Nao existe nada para apontar a ferramenta.

O que deu para fazer: `tools/sgdk_wrapper/audit_scene_headroom.py` varre as declaracoes,
classifica em tres estados e aplica a doutrina da secao 30 onde ha numero. Report em
`doc/curation/scene_headroom_sweep_2026-08-17.json`.

### 41 declaracoes em 10 projetos

| Estado | Qtd | Significado |
|---|---|---|
| `declared_zero` | **21** | a cena declara zero sprites |
| `unmeasured` | **17** | `nao_medido` ou prosa; nada computavel |
| `measured` | **3** | existe numero real |

### Os tres numeros reais valem 45%

`Celestial Chase Revive` declara `max_scanline_sprites: 9` e o `Celestial Chase visual
benchmark` registra "runtime v012 observado 9/20". Nove de vinte e **45% de utilizacao**,
abaixo do limiar de 60%: `unexploited_headroom` nos tres.

Isso nao e reprovacao — e a pergunta que a doutrina obriga: nove foi o teto medido ou foi o
primeiro numero que funcionou? Se a direcao de arte ou o level design pedem uma cena esparsa,
a razao entra em `headroom_justification` e o aviso some. Se ninguem mediu o degrau seguinte,
ha hardware na mesa.

### Vinte e uma declaracoes de zero sprites

Sao as cenas de branding v1 e seus contratos de cena. Ja diagnosticadas nesta curadoria como
hardware ocioso — 0 de 80 sprites, 2 de 4 paletas, nenhum H-Int. A varredura agora quantifica:
`hardware_idle_undeclared` em 21 pontos.

O codigo separa `hardware_idle_undeclared` de `unexploited_headroom` de proposito: zero sprites
pode ser decisao legitima de cena estatica, mas precisa estar declarado como decisao. Nenhuma
das 21 declara.

### Dezessete cenas sem medicao nenhuma

Incluindo uma de MARE_BRAVA que diz `nao_medido (risco declarado: 4 inimigos na mesma...)` — o
projeto **sabe** que tem risco de pressao de scanline e nunca mediu. Essa e a que mais merece
atencao, porque tem risco nomeado sem numero.

### O gap estrutural que isto expoe

A doutrina de audacia so consegue morder onde ha numero, e o workspace tem numero em 3 de 41
declaracoes. Enquanto os contratos de cena nao carregarem layout de sprite do pior quadro, o
simulador continua sem poder ser apontado para nada, e `scanline_sprite_pressure` segue sendo
um campo de prosa.

O caminho seria o `scene_contract` passar a aceitar um `worst_frame_sprite_layout` — mas isso
e mudanca de schema canonico que afeta todos os projetos, e nao foi feita aqui.

## Fase 16 — schema, registro nos projetos, e a abertura como vitrine

### `worst_frame_sprite_layout` no schema canonico

`scene_contract.schema.json` ganhou o campo, **opcional e aditivo**: o schema era frouxo
(`additionalProperties: true`, `scenes.items` sem constraints), entao nenhum contrato existente
quebra. Os 11 contratos de cena do workspace seguem validos.

O campo carrega `frame`, `sprites[]` no formato do simulador, `display_mode` (h40/h32),
`how_determined` e `headroom_justification`. Com ele, `scanline_sprite_pressure` deixa de ser
prosa e vira medicao.

### Registro nos outros projetos, sem mexer neles

Bloco de diretriz elevado a `v4`. Alem da diretriz estetica, do gate de marca e da doutrina de
audacia, cada projeto agora carrega o **seu** registro de folga: quantas declaracoes tem, quais
acusam `unexploited_headroom`, `hardware_idle_undeclared` ou `sprite_pressure_unmeasured`, e o
que fazer quando um agente for atuar ali.

12 de 13 projetos com registro. O 13o, HYBRIDO_MUAY_THAI, nao tem contrato de cena nenhum —
nao ha o que registrar. Projeto com contrato de cena mas **zero** declaracoes recebe um
registro proprio dizendo que ausencia de medicao e pior que estar fora do teto, porque nem a
pergunta foi feita.

Nada foi corrigido nos outros projetos, conforme instrucao.

### A abertura como vitrine: 23 -> 31 tecnicas, zero sprites novos

O registry tem 114 tecnicas e a abertura usava 23. A revisao mediu o que estava ocioso e
avaliou cada candidata pelo gate de compreensao, nao por vontade de acumular.

**Entraram como comprehension_bearing:**

- `mutable_tile_decal_mutation` — o golpe grava cicatriz incandescente permanente na bigorna.
  Claim: o mundo guarda memoria do que aconteceu nele; isto e um lugar, nao um fundo. Teste
  negativo: sem ela o martelo bate e a bigorna fica intacta, entao o impacto nao teve
  consequencia. **E o sinal mais AAA disponivel: estado persistente de mundo.**
- `smear_frame_animation` — quadro de contato em smear. Claim: o golpe tem velocidade que uma
  pose parada nao mostra. Teste negativo: a 60fps pose limpa le como teletransporte.
- `window_plane_static_hud` — o `presents` vive no plano WINDOW, imovel enquanto a cortina
  move os planos por baixo. Claim: existe uma terceira superficie independente do scroll. O
  WINDOW estava **100% ocioso** no v1 e no v2.

**Entraram como enabling_discipline** (ja decididas, faltava declarar): `sprite_frame_vram_slot_streaming`,
`animation_lookahead_dma_queue`, `large_metasprite_vblank_fit_audit`, `tile_dedup_hvflip_hashing`.

**Rejeitadas com motivo escrito**, de 4 para 9: `cellular_microbuffer_sim` (CPU num projeto que
ja mediu spike), `bg_b_bypassing` (nao ha boss gigante), `forward_kinematics` (nao ha cadeia
articulada), `prerendered_sprite_scaling` (nao ha eixo de profundidade), `tile_cache_streaming_refcount`
(nao ha mapa maior que a VRAM).

Custo total: **zero sprites novos**, 1 quadro de arte a mais no martelo (6 -> 7), absorvido
pelo streaming — 252 tiles residentes viram 72, economia sobe de 144 para 180.

Gate de compreensao: 31 tecnicas, 18 bearing, 13 enabling, `verdict=OK`.

A vitrine nao e a contagem de tecnicas. E o fato de cada uma ter que dizer o que o espectador
entende e o que se perderia sem ela — e de cinco terem sido cortadas justamente por nao
conseguirem responder.

## Fase 17 — 9 assets entregues, ROM compilada, e o blocker que nenhum gate pegou

### O que a validacao confirmou

- **proveniencia limpa**: 14 simbolos, 14 declarados, `blocking=[]`;
- **dimensoes exatas** nos 9 assets, todos em modo indexado;
- **degrau de luz do logo confirmado**: `PAL1[13]` a 4,5% dos pixels visiveis, `[14]` vazio,
  pico de canal exatamente `0xCC` — no teto, nao acima. Requisito nao negociavel cumprido;
- **face da bigorna limpa como declarado**: `4` puro de y=80 a y=103. Minha primeira leitura
  acusou textura porque centrei a janela errado; a medicao corrigiu a mim, nao ao artista;
- **ROM compilada**: 262144 B pelo wine bridge, os 9 simbolos em `resources.h`.

### Autocritica do agente conferida por medicao

O agente disse que o FORGE ficou "azul-ardosia demais". Medido: **51% de pixels frios contra
29% quentes**. Confirmado, e no asset sobre o qual a varredura especular corre.

### BLOCKER: o orcamento de VRAM esta estourado

Nenhum gate desta curadoria pegou isto, porque todos mediam sprites, proveniencia e paleta —
nenhum media **residencia de tiles**.

| | Bruto | Unico (dedup H/V) | Reducao |
|---|---|---|---|
| `forge_bg_b` | 1120 | **1093** | **2%** |
| `forge_bg_a_props` | 1120 | 304 | 73% |
| demais 7 | 804 | 599 | 26% |
| **total** | 3044 | **1996** | 34% |

Residencia por ato contra o teto util de ~1700 tiles:

| Ato | Residentes | Margem |
|---|---|---|
| 1 ignition | 1493 | 12% |
| **2 strike** | **1667** | **2%** |
| 3 signature | 1316 | 23% |

Contra as linhas do proprio contrato: `bg_forge_set` orcado em 640 e real em **1397 (+118%)**.

### A causa e a mesma de sempre, em forma nova

`forge_bg_b` deduplica **2%**. Um fundo de alvenaria deveria deduplicar muito. Dois por cento
significa que quase todo tile e unico — o que acontece quando a imagem e fotografica e foi
quantizada, e nao autorada como tiles.

E o mesmo vicio do ringing de JPEG, agora em outra camada: **a arte foi composta como imagem,
nao como conjunto de tiles.**

A ironia esta na leitura: o agente escreveu que a parede "continua lendo como fiada", ou seja
modular demais aos olhos. A medicao diz o oposto na VRAM — 98% de tiles unicos. Ela consegue
parecer repetitiva e custar como arte unica ao mesmo tempo, que e o pior dos dois mundos.

`forge_bg_a_props`, autorado com formas mais limpas, deduplica 73%. Prova que o problema e de
metodo de composicao e nao de estilo.

### A ROM compilou, mas nao mostra a abertura v2

Os 9 assets estao em `resources.h` e ocupam ROM, e **nenhuma linha de runtime os referencia**:
`scene_branding.c` continua sendo a implementacao v1 com os 5 placeholders `img_brand_*`.

O build prova que o ResComp aceita os 9 assets e que a ROM fecha em 256KB. **Nao prova nada
sobre a abertura v2**, que nao existe em runtime. Apresentar essa ROM como validacao da cena
seria o falso verde que esta curadoria passou a sessao inteira fechando.

### Gap de gate exposto

Esta curadoria construiu gate de proveniencia, de compreensao de marca, de model sheet e de
pressao de scanline. **Nenhum mede residencia de tiles em VRAM.** O `res_graph_report` cobre
isso no framework, mas nunca foi rodado sobre esta cena porque o runtime nao existe.

Dedup de tile deveria ser medido no **asset**, antes do runtime — e da para fazer com o mesmo
metodo usado aqui.

## Fase 18 — gate de residencia de tiles, e a correcao que ele fez em mim

`tools/sgdk_wrapper/audit_tile_residency.py`. Le `res/*.res`, abre cada asset e conta tiles
unicos de 8x8 com dedup por flip H/V — **sem precisar de runtime**. Fecha a janela em que a
arte esta pronta, o orcamento ja quebrou e ninguem consegue dizer, porque `res_graph_audit.ps1`
so responde depois que a cena existe.

Teto util derivado e publicado no relatorio: 2048 tiles, menos nametables de BG_A/BG_B a 64x32
(256), menos SAT (20), menos tabela de scroll por linha (32) = **1740**.

### O gate corrigiu a minha propria medicao

Na primeira execucao ele acusou **1749 tiles no ato 2 contra 1740, estouro**. Estava cobrando o
`spr_forge_hammer` inteiro (154 tiles unicos) sem saber que a decisao de streaming ja tinha sido
tomada e documentada: a janela residente e de 72.

Corrigido: o gate agora le `vram_slots` do `dma_queue_contract` do projeto. Com o streaming
contabilizado, o ato 2 fica em **1667 de 1740 — 4% de margem, nao estouro**.

**Isso corrige o que reportei na fase 17.** Eu havia dito que o orcamento estava estourado; o
numero estava inflado pelo mesmo motivo. O orcamento **cabe**, com 4% de margem — o que continua
sendo apertadissimo, mas e legal.

O que **nao** muda da fase 17: `img_forge_bg_b` deduplica 2%, e a linha `bg_forge_set` do
contrato foi orcada em 640 e esta em 1397.

### Residencia medida por ato

| Ato | Residentes | Margem |
|---|---|---|
| 1 ignition | 1493 | 14% |
| **2 strike** | **1667** | **4%** |
| 3 signature | 1316 | 24% |

Utilizacao de pico: **96%**.

### Verificado nas duas direcoes

Fixture sintetica com dois fundos de ruido puro: 2402 tiles, 138% do teto, `verdict=BLOCKED`,
exit 1. O tileset limpo da mesma fixture deduplica 99% e o de ruido 0% — a metrica discrimina
exatamente o que deveria. Projeto real: exit 0.

### Sinais

- `tile_residency_over_ceiling` **bloqueia** — excesso de VRAM e fato de hardware;
- `low_tile_dedup_ratio` **avisa** — fundo grande abaixo de 30% de dedup foi composto como
  imagem e quantizado. Sintoma, nao violacao: nomeia o suspeito sem reprovar o estilo;
- `unexploited_vram_headroom` abaixo de 40%, por simetria com a doutrina de audacia.

Canonizado em `SGDK_GLOBAL.md` secao 31, na referencia rapida do `AGENTS.md` e no bloco de
diretriz dos 13 projetos.

## Fase 19 — runtime v2 escrito, ROM buildada, BlastEm rodou, CPU crashou

### O que funcionou

- `src/scenes/scene_branding_v2.c` escrito contra a coreografia medida, com os parametros de
  spawn, stagger e recuo do martelo comentados como **nao alteraveis sem re-medir**;
- ligado em `app.c` no lugar da v1;
- **build passou** pelo wine bridge. `scene_branding_v2.o` com 10964 B, simbolos
  `SCENE_brandingV2Enter/Update` e `brandHIntHandler` no `symbol.txt`, ROM nova
  (`873cd957...` contra `f45d77e6...` da v1);
- **BlastEm rodou de verdade** pelo `capture_blastem_evidence_linux.sh`, com screenshot, GIF,
  SRAM e 5 quadros de animacao;
- **o ato 1 renderiza**: a parede da forja aparece, e as bandas de calor do H-Int funcionam —
  frio no topo, quente embaixo. A tecnica `hint_palette_blending` esta de pe em hardware
  emulado.

### O que quebrou

**`M68K attempted to execute code at unmapped or I/O address 23080000`.** Nao e congelamento:
e a CPU pulando para o vazio. Os 5 quadros capturados tem **0,0% de pixels diferentes entre
si** — a cena trava no primeiro quadro do ato 1.

Causa medida: o pool de VRAM do sprite engine.

| | Tiles |
|---|---|
| brasa (4 x 6 quadros) | 24 |
| fantasmas (4 x 6 x 5) | 120 |
| martelo (36 x 7) | 252 |
| **estilhacos (4 x 4 x 56)** | **896** |
| **total exigido** | **1292** |
| reserva do contrato | 320 |

**304% acima da reserva.** `SPR_addSprite` devolve NULL quando o pool acaba, e as chamadas
seguintes de `SPR_setVisibility`/`SPR_setPosition` sobre ponteiro nulo derrubam a CPU.

### O erro e meu, e tem nome

O `dma_queue_contract` decidiu **streaming em janela dupla de 72 tiles** para o martelo. Eu
escrevi o runtime usando `SPR_addSprite` com auto-alocacao e **nao implementei streaming
nenhum**. O contrato existia, foi aprovado pelo curador, e o runtime o ignorou.

Pior: os 56 estilhacos sozinhos pedem 896 tiles porque cada instancia aloca os 4 quadros. O
correto e **um unico conjunto de tiles compartilhado** entre as 56 instancias, com
`SPR_setVRAMTileIndex` apontando todas para a mesma base — que e justamente o que
`tile_flipping` e a decisao de 4 quadros com flip H/V pressupunham.

### Status honesto

`implementado` e `buildado`. **Nao** `testado_em_emulador`: a ROM boota e crasha. O bundle de
captura foi rejeitado pelo proprio gate com `vlab_block_missing`,
`artifact_missing:vdp_dump` e `artifact_missing:runtime_metrics`, porque o runtime nao chega a
emitir telemetria.

Nenhum status de entrega e reivindicavel. A regra de ferro do workspace continua valendo e
desta vez ela reprovou o meu proprio codigo.

## Fase 20 — runtime corrigido: crash resolvido, cena anima, margem zero

### O crash: bisecao encontrou, hipotese inicial estava errada

Minha primeira hipotese foi esgotamento do pool de sprites (1292 tiles exigidos contra 320).
Corrigi para tiles compartilhados e streaming do martelo — **e o crash continuou identico**,
mesmo endereco `0x23080000`.

Bisecao desligando `brandAcquireHInt()`: **sem crash, e a cena passou a animar**. A causa era o
H-Int, nao o pool.

Tentei corrigir trocando `PAL_setColor` por escrita direta no CRAM, que e o padrao canonico
para mudar paleta em interrupcao. **O crash voltou.** Entao nao e o metodo de escrita: e o
proprio callback de H-Int nesta configuracao, e a causa ainda nao foi encontrada.

`hint_palette_blending` esta **desligado no codigo, com blocker escrito no proprio arquivo**. O
gradiente de bandas do ato 1 nao existe nesta ROM.

### Segundo bug: offsets de VRAM hardcoded

Eu havia escrito `TILE_USER_INDEX + 1093` para o BG_A usando **a minha** contagem de dedup. O
ResComp gera **1097** para o `bg_b` e **309** para o `bg_a`, nao os 1093 e 304 que calculei.
Cinco tiles de diferenca sobrepuseram o logo e encheram a tela de lixo.

Corrigido: todos os offsets agora sao **derivados de `tileset->numTile`**, nunca escritos a mao.

### O que a ROM faz agora

Sem crash de CPU. Quadros capturados no BlastEm mudando **26,3%, 3,5%, 18,6%, 3,9% e 1,3%** —
a cena roda. A bigorna renderiza, o enxame de estilhacos aparece, e o fundo magenta das bordas
sumiu depois de mover o `PAL_setColor(0, 0x0000)` para **depois** do carregamento das paletas.

### O que continua quebrado, e a raiz e sempre a mesma

| | Tiles |
|---|---|
| TILE_USER_INDEX | 16 |
| **bg_b** | **1097** |
| bg_a | 309 |
| logo_engine | 187 |
| shard + ember | 40 |
| janela do martelo | 72 |
| pool SPR | 16 |
| **total** | **1737** |
| teto util | 1740 |

**Tres tiles de margem.** Por isso so carreguei o quadro 0 dos tilesets de brasa e estilhaco:
nao ha espaco para os 6 e 4 quadros. Visualmente eles nao animam, e ainda ha lixo na metade
inferior da tela.

Com o `bg_b` re-autorado ao alvo de 644 tiles do brief, a margem saltaria para **456 tiles** —
espaco de sobra para carregar todos os quadros de sprite e parar de brigar por tile.

### Status

`implementado` e `buildado`. **Nao** `testado_em_emulador`: a cena roda mas com lixo visual,
sem H-Int e sem animacao de quadro nos FX. O bundle segue rejeitado por falta de `vdp_dump` e
`runtime_metrics`.

Dois blockers nomeados para a proxima sessao: **causa do crash de H-Int** e **re-autoria do
`bg_b`**. O segundo destrava o primeiro tipo de problema por folga.

## Fase 21 — outro agente destravou; contrato reconciliado com a ROM

### O que o outro agente resolveu

**A causa do crash de H-Int, que eu nao achei.** O handler era `void` e o GCC emitia `RTS`.
H-Int e excecao de nivel 4: a pilha tem SR+PC, e `RTS` desempilha so o PC, entao o SR (0x2308)
virou a word alta do endereco seguinte — **0x23080000**, exatamente o endereco do crash. A
correcao e `HINTERRUPT_CALLBACK`, que emite `RTE`. Minhas duas tentativas atacaram o metodo de
escrita no CRAM, que era um risco secundario e nao o vetor.

**O `bg_b` re-autorado**: 1093 -> **642 tiles unicos, 43% de dedup**, contra o alvo de 644 do
brief. A margem do ato 2 saltou de **3 tiles para 30%**.

**Resultado**: sem crash, cena animando por todos os atos, e o bundle de evidencia
`sealed` com `blockers: []` — a primeira vez que o gate de captura aceita esta cena.

### O que eu corrigi nesta rodada

Contrato e storyboard declaravam **56 estilhacos com 18/20 sprites medidos**. A ROM roda
**32**, com stagger 4 e logo em y=64. Contrato descrevendo coreografia que nao foi
implementada e exatamente o falso verde que esta curadoria combate.

Re-medi com os parametros lidos do codigo: **16/20 sprites e 256/320 px, status ok**. O runtime
no BlastEm registrou pico de 11 na amostra. Contrato e storyboard atualizados, com a divergencia
registrada em vez de apagada.

Detalhe que importa: a reducao para 32 **nao foi por VRAM**. Estilhacos compartilham um unico
tileset de 16 tiles e nao pesam em VRAM; a causa foi pressao de CPU (`over_budget=12`). Com o
`bg_b` corrigido, restaurar 56 depende so de CPU — e a doutrina de audacia pede medir antes de
aceitar 32 como final.

### Blockers abertos

- `over_budget=12` quadros acima do orcamento de CPU;
- `performance_claim: unproven` no proprio bundle;
- captura terminou em `vlab.scene_id: 2`, ou seja depois da cena, entao o dump de VDP nao
  cobre o pior quadro do ato 2;
- 32 estilhacos sem justificativa medida contra os 56 que cabem por scanline.

## Fase 22 — over_budget zerado, e a densidade reprovada por medicao

### A causa era divisao de 32 bits no loop quente

Por estilhaco e por quadro o update fazia: um modulo por 5, uma divisao `(t*t)/dur` e **duas
divisoes de 32 bits** no lerp, mais duas chamadas recomputando posicao de explosao e alvo que
sao **constantes**. Com 32 estilhacos isso da ~128 divisoes por quadro; no 68000 um `DIVS`
custa cerca de 150 ciclos, entao so as divisoes comiam perto de 15% do orcamento do quadro.

Correcao: tudo precomputado em `brandEnterStrike` — `born`, `convStart`, `dur`, posicao de
explosao, alvo e um reciproco `65536/(dur*dur)`. O ease-in virou
`(delta * t^2 * recip) >> 16`: dois multiplicadores e um shift, **zero divisao**.

| | antes | depois |
|---|---|---|
| `over_budget_frames` | **12** | **0** |
| `max_cpu_load` | 401 (v1) | **45** |

Medido com `scene_id: 0` e `frame_counter: 151`, ou seja **dentro do ato 2**, nao no fim da
cena como as capturas anteriores.

### O teste de audacia rodou — e a medicao disse nao

Com CPU folgada, testei restaurar os 56 estilhacos. A ROM rodou sem crash e com
`over_budget_frames: 0`, e a telemetria reportou `max_scanline_sprites: 6`. **Parecia
aprovado.**

A varredura do simulador reprovou: **23/20 sprites e 368/320 px, `status: error`**. A
telemetria amostrou F151; o pico real esta em F144 e F185.

Matriz completa na geometria atual (`LOGO_Y0=64`):

| Config | Sprites | Pixels | |
|---|---|---|---|
| **32, stagger 4** | **16/20** | **256/320** | **adotado** |
| 40, stagger 5 | 19/20 | 304/320 | ok, 5% de margem |
| 48, stagger 5 | 20/20 | 320/320 | ok, margem zero |
| 56, stagger 4 | 23/20 | 368/320 | ERROR |
| 56, stagger 5 | 22/20 | 352/320 | ERROR |
| 56, stagger 6 | 22/20 | 352/320 | ERROR |

**Minha medicao anterior de 18/20 com 56 estilhacos nao vale mais.** Ela foi feita com
`LOGO_Y0=80`; o runtime entregue usa 64, e aproximar a banda de pouso da origem da explosao em
y=104 elevou a sobreposicao por linha. Numero medido em uma geometria nao transfere para outra.

`headroom_justification` registrado: 32 e escolha medida e nao timidez. 40 e 48 cabem mas
ficam a 1 e 0 sprites do limite fisico, dentro da faixa em que o proprio simulador ja emite
`scanline_pressure_near_limit`.

### Licao para o canon

Amostra unica de telemetria de runtime **nao substitui** varredura de todos os quadros. Neste
episodio ela deu falso verde para uma configuracao que viola o limite de hardware em dois
quadros — e o sintoma no console seria dropout de sprite, exatamente o flicker que o workspace
proibe.

## Fase 23 — a probe reescrita, um bug de corrupcao de memoria, e 16 sprites invisiveis

### A probe media 4 linhas de 224

`measure_max_scanline_sprites` amostrava **4 scanlines por quadro** com um cursor rotativo. Um
pico transitorio numa linha especifica tinha chance de ~2% de coincidir com a amostra. Foi por
isso que ela reportou 6 numa configuracao em que a varredura do simulador media 23 — **falso
verde para algo que causaria dropout de sprite no console**.

Reescrita para contar **todas as 224 linhas** por quadro: ~700 incrementos mais 224
comparacoes, muito abaixo do que custava uma unica divisao de 32 bits no loop de gameplay.

### Um bug de corrupcao de memoria na minha propria reescrita

A primeira versao clampava `start < 0` mas nao tratava `end` negativo. Sprite estacionado
acima da tela (martelo em y=-48, fantasmas em -32) produz `end` negativo; o cast para `u16`
virava ~65000 e o loop escrevia **fora do array**, corrompendo memoria. O sintoma foi o VLAB
parar de exportar e todos os bundles falharem com `vlab_block_missing`.

Guarda adicionada. Vale registrar que o proprio bundle de evidencia detectou o dano — a
ferramenta de medicao pegou o defeito da ferramenta de medicao.

### O achado que explica a divergencia

Com 32 estilhacos, o codigo calcula `sector = index * 16 / SHARD_COUNT` e
`born = 122 + index / SHARD_SPAWN_PER_FRAME`. Para `SHARD_COUNT=32` e `SPAWN_PER_FRAME=2` isso
da, para todo par `2k` e `2k+1`, **o mesmo setor e o mesmo quadro de nascimento**.

Resultado medido: **16 pares perfeitamente sobrepostos**. Os 32 sprites do SAT rendem
**16 posicoes visiveis distintas**. Metade do orcamento de sprite e gasta em duplicatas que o
espectador nunca ve, e que ainda assim consomem slot de SAT e pressao de scanline.

Isso explica por que a probe corrigida reporta 6: a densidade visual real e metade da nominal.
E explica por que os 56 estouravam — com `SHARD_COUNT=56` a divisao `index*16/56` deixa de
duplicar e a densidade real dobra de fato.

### Estado

`over_budget_frames: 0`, `max_cpu_load: 52`, bundle `sealed`, probe medindo as 224 linhas.

Blocker novo e nomeado: **`shard_sector_aliasing`** — a formula de setor precisa desacoplar do
`SHARD_COUNT`, senao densidade nominal e densidade visual divergem por construcao. Enquanto
existir, qualquer claim de "32 estilhacos" e nominal e nao visual.

## Fase 24 — aliasing corrigido destrava a densidade; ato 3 quebrado

### A correcao do aliasing REDUZ a pressao

`sector = (index * 16) / SHARD_COUNT` trocado por `sector = (index * 5) & 15`. Stride 5 e
coprimo de 16, entao visita os 16 setores antes de repetir; pares consecutivos ficam a 5
setores de distancia e pares que repetem setor tem `born` separado por 8 quadros.

Matriz re-medida, com e sem aliasing:

| Config | Com alias | Sem alias |
|---|---|---|
| 32, stagger 4 | 16/20 | **13/20** |
| 40, stagger 5 | 19/20 | 14/20 |
| 48, stagger 5 | 20/20 | 15/20 |
| **56, stagger 6** | 22/20 **error** | **16/20 ok** |

Remover as duplicatas **baixou** a pressao porque os estilhacos se espalham em vez de empilhar.
Os 56 agora cabem com a mesma pressao que os 32 antigos tinham — e os 32 antigos rendiam
apenas 16 posicoes visiveis. **Adotado: 56 estilhacos, stagger 6, 16/20 e 256/320.** Densidade
visual real 3,5x maior pelo mesmo custo de scanline.

### Duas correcoes na probe

1. **Conta as 224 linhas** por quadro, em vez de amostrar 4 com cursor rotativo.
2. **Re-exporta a cada 60 quadros** enquanto a cena roda. A condicao antiga exigia mudanca na
   contagem de amostras, que satura em 32: a probe exportava **uma unica vez**, no quadro 151,
   e o maximo acumulado cobria so F90-F151. Qualquer pico posterior nunca chegava a SRAM.
   Agora as capturas alcancam F331, F451 e F511.

Com a cena inteira coberta: `over_budget_frames: 0`, `max_cpu_load` subindo ate 96 no ato 3.

### Divergencia entre modelo e hardware, registrada e nao resolvida

Meu modelo em Python preve pico de 16 sprites por scanline; a probe on-hardware, cobrindo
F90-F511 e contando todas as linhas, mede **6**. Os dois discordam de forma consistente.

A probe e a autoridade: ela mede o codigo real no hardware emulado. O modelo ja errou uma vez
nesta sessao (o "56 cabe" que nao transferiu entre geometrias). A divergencia significa que a
matriz de densidade e **conservadora**, nao perigosa — mas ela nao esta explicada.

### Blockers visuais abertos

Captura do ato 3 (F331) mostra a parede com o piso de brasa, e:

- **o magenta voltou nas bordas** — `PAL_setColor(0, 0x0000)` nao sobrevive as trocas de
  paleta dos atos seguintes;
- **nenhum wordmark aparece** — a cortina por coluna nao revela autor nem projeto;
- **a bigorna sumiu** sem o logo ter entrado no lugar.

O ato 1 e o ato 2 renderizam; **o ato 3 nao entrega**.

### Risco nao medido que permanece

`brandEnsureShard` retorna em silencio quando `SPR_addSpriteEx` devolve NULL: sem contador,
sem blocker. A cena pode estar renderizando uma fracao dos estilhacos e nada reporta. Enquanto
esse caminho for silencioso, o claim de "56 estilhacos" e nominal.

## Fase 25 — o magenta nunca esteve na ROM

O outro agente fechou as tres pontas do ato 3 medindo antes de corrigir:
`VDP_setWindowVPos(FALSE, 22)` punha a WINDOW nas fileiras 0-21 enquanto o draw estava em
y=23; os wordmarks saiam sombreados por prioridade baixa com Shadow/Highlight ligado; e o
contador novo em `brandEnsureShard` provou `spawned=56, failed=0`, ou seja `SPR_addSpriteEx`
**nunca** falhava em silencio.

Sobrou um item que a bisseccao de seis pontos nao explicou: o magenta das bordas no ato 3.

### A medicao que resolveu

`PAL0[0]` lido direto do `visual_vdp_dump.bin` em quatro sessoes: **`0x0000`, preto**, incluindo
os quadros do ato 3. O backdrop nunca foi magenta no hardware.

Comparando os dois caminhos de captura da mesma sessao:

| Sessao | `screenshot.png` | `frame_1` | `frame_3` |
|---|---|---|---|
| v5 | preto | preto | preto |
| dealias | preto | **MAGENTA** | preto |
| re4 | preto | **MAGENTA** | preto |
| act2_v2 | preto | **MAGENTA** | preto |
| act3_master | preto | **MAGENTA** | preto |
| act3_pres_fix | preto | **MAGENTA** | preto |

O magenta aparece **apenas no primeiro quadro do burst**, nunca no screenshot e nunca no
terceiro quadro. E aparece tambem em `act2_v2`, uma sessao que eu havia declarado limpa —
porque ali eu olhei o `frame_3` e no ato 3 olhei o `frame_1`.

### O que era

Artefato de captura. Com `--burst-delay 0` o primeiro quadro e capturado antes da janela do
emulador terminar de compor, e a superficie nao inicializada e gravada como magenta puro.

Corrigido no `capture_blastem_evidence_linux.sh` com uma guarda de 0,35s antes do primeiro
quadro do burst. Verificado: os tres quadros e o screenshot agora saem pretos.

### O custo do erro

**Eu reportei "magenta do backdrop" como bug da ROM durante varias fases**, e o handoff que
escrevi mandou bissectar seis pontos do codigo atras de uma causa que nao existia ali. O outro
agente gastou a bisseccao inteira e concluiu, corretamente, que nenhum dos seis explicava.

A leitura que faltou era de um clique: o `visual_vdp_dump.bin` ja continha `PAL0[0]` desde a
primeira captura selada. Eu julguei um PNG em vez de ler o dump que o proprio gate exige.

Licao registrada: **evidencia visual tem hierarquia.** Dump de VDP > screenshot > quadro de
burst. Julgar backdrop, paleta ou prioridade por PNG de animacao e julgar pelo artefato mais
fraco da pilha.

## Fase 26 — ato 3 corrigido conforme o storyboard

Implementacao das saidas declaradas em `doc/act3_storyboard.md`.

### O que mudou

Zonas de tela no codigo (`STAGE_TX/TY/TW/TH`) e a regra do PALCO: **um wordmark por vez**.
Cada elemento ganhou saida:

| Elemento | Saida implementada |
|---|---|
| FORGE | varredura de 1 fileira de tiles por quadro, F318-330, sob a cortina |
| MISAEL | entra no palco vazio em F330; sai por varredura F428-440 |
| MASTER | entra no palco vazio em F440 |

Resultado medido: **um unico elemento no palco**. A captura em F451 mostra so o MASTER, sem o
FORGE azul por tras, com a bigorna intacta na zona FORJA.

### A primeira tentativa regrediu o orcamento

Implementei as saidas com `PAL_fadeOutPalette` e `PAL_fadeInPalette`, como a concepcao pedia.
Medicao: `over_budget_frames` de **0 para 8** e `cpu_load` de 96 para 105, com jitter em 91.

Tentei separar limpeza e desenho em quadros distintos: **nao resolveu**, o que ja eliminou a
hipotese de custo concentrado num quadro.

Bisseccao desligando apenas os tres fades: `over_budget` voltou a **0** e cpu a 97. Eram os
fades.

### A substituicao ficou melhor que o original

Troquei fade de paleta por **varredura de tilemap**: uma fileira de 28 tiles apagada por
quadro. Custa praticamente nada e **le melhor** — o wordmark e varrido de cima para baixo em
vez de simplesmente escurecer, o que combina com a cortina que sobe no mesmo momento.

Medicao final: `over_budget_frames: 0`, `max_cpu_load: 96`, os tres gates em exit 0.

### O que isto confirma do workflow

O passo 2 do `scene-direction-first` — planta baixa com saida declarada por elemento — era o
que faltava, e nenhum gate podia ter pego. A correcao nao exigiu asset novo: foi runtime e
contrato, exatamente como o storyboard previu.

E a regra de bissectar antes de teorizar pagou de novo: a hipotese plausivel era custo
concentrado no quadro de troca, e separar os quadros nao mudou nada. So o desligamento
apontou o culpado.

## Fase 27 — pico 6 vs 16 resolvido: o instrumento estava quebrado, e o modelo concentra

### O instrumento nao media nada

A probe exportava dois campos para responder "quantos sprites estao vivos":

```c
g_mdRuntimeProbe[16] = SPR_getNumActiveSprite();   /* valor do quadro do export */
g_mdRuntimeProbe[17] = 1;                          /* CONSTANTE */
```

`[17]` era literalmente `1` e saia rotulado como `active_sprite_count`. `[16]` guardava o valor
do quadro em que o export acontece — no ato 3, zero. **Os dois campos que existiam para essa
pergunta nunca a responderam.**

Corrigido: `[16]` continua instantaneo, `[17]` acumula o **maximo da cena**, e os nomes no
`seal_fresh_evidence_bundle.py` passaram a descrever o que os campos medem
(`active_sprite_count_at_export` e `max_active_sprites`).

### A medicao decisiva

`max_active_sprites = 63`.

São 56 estilhacos + 1 brasa + 5 fantasmas + 1 martelo. **Todos vivos ao mesmo tempo.**
Visibilidade, pouso antecipado e esgotamento de pool ficam descartados: o modelo acerta a
contagem de vivos.

### A divergencia e geometrica, e agora esta explicada

O leque espalha por `y = 104 + FAN_SIN[setor] * r / 64`, com `r` ate 70: **y de 34 a 174, ou
140 linhas**. Com 56 estilhacos de 16px, sao 896 coberturas de linha distribuidas por 140
linhas — media de **6,4 por linha**.

A probe mede pico **6**. O runtime bate com a distribuicao real.

Meu modelo em Python previa 16 porque **concentra onde o hardware espalha**: ele nao reproduz
a mesma aritmetica inteira de posicao, e superestima o empilhamento. O detalhe que sobrevive:
os setores 0 e 8 tem `FAN_SIN = 0`, entao os 7 estilhacos que caem neles ficam com `y = 104`
fixo independentemente do raio — e essa e a unica concentracao real do leque.

### O que isso muda

- **A matriz de densidade e conservadora por um fator de ~2,7x.** Ela reprovou 56/stagger 4 com
  23/20 previstos; o hardware provavelmente comportaria. Nao vou reabrir a decisao com base no
  modelo — qualquer aumento agora exige medicao on-hardware, que finalmente e confiavel.
- **A probe virou a autoridade de densidade.** Com contagem de todas as 224 linhas, re-export
  periodico e maximo de sprites ativos acumulado, ela mede o que o modelo so estima.
- **Ha folga real:** 63 sprites vivos e pico de 6 por linha, contra um limite de 20.

### A licao

Tres ferramentas de medicao apresentaram defeito nesta curadoria: o simulador que ignorava o
limite de pixel, a probe que amostrava 4 de 224 linhas, e agora dois campos que exportavam uma
constante. **Verificar o instrumento antes de acreditar na leitura** deixou de ser prudencia e
virou etapa obrigatoria.

## Fase 28 — meta-gate nos projetos: ferramenta obsoleta com self-check verde

Rodar o meta-gate na arvore inteira expos um ponto cego dele proprio.

### As 6 ferramentas canonicas passam

`6/6 com self-check passando`.

### E 5 copias locais estao em v1.0.0

| Copia | Estado |
|---|---|
| FORGE_REFERENCE `/.agent/scripts/` | **em uso** |
| GOTHAM_OVERDRIVE `/.agent/scripts/` | **em uso** |
| KIRBY_FAN CLOUDE `/.agent/scripts/` | **em uso** |
| KIRBY_FAN GROK BUILD `/.agent/scripts/` | **em uso** |
| HYBRIDO_MUAY_THAI `/rascunho/...backup/` | arquivada |

Todas em `v1.0.0` contra a canonica `v1.1.0` — ou seja, **sem o limite de 320 px por linha**.

### O ponto cego, medido

A copia defasada:

- roda `--self-check` e **passa com exit 0**;
- recebe uma cena com 16 sprites de 32px numa linha, 512 px contra teto de 320;
- responde **`status: ok, blockers: []`**.

O self-check dela passa porque **ele so testa o que aquela versao faz**. A v1.0.0 nao tem o
conceito de limite de pixel, entao nao ha o que falhar.

**Ferramenta obsoleta com self-check verde e pior que ferramenta sem self-check, porque parece
verificada.**

### Correcao no meta-gate

Nova deteccao por hash: copia local de ferramenta de medicao precisa ser identica a canonica.
Blocker `measurement_tool_stale_copy`. Copia sob `out/`, `rascunho/` ou `__pycache__` e backup
morto e sai como aviso, nao como bloqueio.

O self-check do proprio meta-gate ganhou a fixture correspondente: ferramenta sadia, quebrada,
sem check, ausente **e copia defasada**.

Veredito atual da arvore: **BLOCKED**, com 4 copias em uso defasadas e 1 arquivada.

### Nao sincronizei as copias

Sincronizar `.agent/` de projeto e materializacao do framework e tem politica propria — o
`AGENTS.md` diz que `.agent` local existente **nao e sobrescrita**. O blocker fica levantado e
nomeado; a decisao de propagar e do curador.

## Fase 29 — sincronizacao das 4 copias em uso

Autorizada pelo curador, sobrepondo a politica do `AGENTS.md` de nao sobrescrever `.agent` local.

### Verificacao antes de sobrescrever

As 5 copias eram **byte-identicas entre si** (sha `be8ba38f6292`, 4125 bytes). Nenhuma tinha
customizacao local, entao sobrescrever nao descartou trabalho de ninguem. Essa checagem vem
antes de qualquer copia: cinco arquivos com o mesmo nome nao sao cinco copias da mesma coisa
ate que o hash diga que sao.

As 4 em uso sao **ignoradas por politica** (`.gitignore:51` — `SGDK_projects/**/.agent/`): sao
materializacao do framework, nao conteudo versionado. A sincronizacao foi operacao de
filesystem e nao entra em commit.

### Prova antes e depois, na mesma cena

Cena de controle: 16 sprites de 32 px na mesma linha = 512 px, contra o teto de 320 do H40.

| | status | blockers | px/linha |
|---|---|---|---|
| v1.0.0 (backup em `rascunho`, nao sincronizado) | `ok` | `[]` | campo inexistente |
| FORGE_REFERENCE | `error` | `sprite_pixels_per_scanline_over_320` | 512 |
| GOTHAM_OVERDRIVE | `error` | `sprite_pixels_per_scanline_over_320` | 512 |
| KIRBY_FAN CLOUDE | `error` | `sprite_pixels_per_scanline_over_320` | 512 |
| KIRBY_FAN GROK BUILD | `error` | `sprite_pixels_per_scanline_over_320` | 512 |

O controle continua aprovando a cena estourada — e por isso que ele serve de controle.

### Backup nao foi sincronizado

`HYBRIDO_MUAY_THAI/rascunho/local_agent_physical_backup_v002/` continua em v1.0.0 de proposito.
Backup que e atualizado deixa de ser backup. O meta-gate ja o classifica como `archived` e ele
sai como aviso, nunca como blocker.

### Veredito

`validate_measurement_tools.py`: **8/8 com self-check passando, verdict=OK**. Primeira vez que a
arvore inteira sai limpa desde que a deteccao de copia defasada existe.

Consequencia para os 4 projetos: qualquer numero de pressao por scanline medido antes desta data
saiu de instrumento cego para metade do orcamento. Os numeros nao estao necessariamente errados
— estao **nao medidos** naquele eixo, e precisam ser refeitos antes de sustentar claim.

## Fase 30 — re-medicao de scanline nos 4 projetos

O simulador defasado nunca foi a trava aqui. A trava e outra e e maior.

### O que os 4 declaram, contra o que o codigo faz

| projeto | declaracao | `SPR_addSprite` no codigo | veredito |
|---|---|---|---|
| FORGE_REFERENCE | `0 sprites neste baseline` | **nenhum** (so `SPR_init`) | declaracao **verdadeira** |
| GOTHAM_OVERDRIVE | `0 sprites neste baseline` | player, 4 drones, boss de 5 pecas | declaracao **falsa** |
| KIRBY_FAN CLOUDE | `0 sprites neste baseline` | 33 objetos de sprite | declaracao **falsa** |
| KIRBY_FAN GROK BUILD | `0 sprites neste baseline` | 33 objetos de sprite | declaracao **falsa** |

Tres de quatro declaram hardware ocioso enquanto o codigo popula a SAT. Isso nao e erro de
instrumento: e declaracao que nunca foi ligada ao codigo. O simulador cego para pixel escondia
metade do orcamento, mas aqui nao havia nem numero para esconder.

### Sprite de hardware nao e sprite do SGDK

O VDP conta **sprites de hardware**, e nenhum passa de 4x4 tiles. O SGDK quebra o resto. O chassi
do boss de GOTHAM tem 8x6 tiles e vira **4 sprites**, nao 1. Medir sem decompor subconta o limite
de 20 por linha pela metade — e teria dado um verde falso.

### GOTHAM_OVERDRIVE, quadro pos-init

Todas as posicoes lidas do codigo (`BOSS_START_X/Y = 128/40`, `PLAYER_START = 136/176`). Os
drones nascem em `-32,-32` com `SPR_setVisibility(HIDDEN)`: estao fora da tela.

| | |
|---|---|
| sprites de hardware em tela | 10 |
| pico por scanline | **5 de 20** |
| pico de pixels por scanline | **160 de 320** |
| limite que amarra | `sprite_pixels` |
| utilizacao | **50%** |

`status=ok`, sem blockers. Abaixo do limiar de 60% da secao 30: folga nao explorada, sem
justificativa declarada.

Um cenario com os 4 drones ativos na faixa do player nao move o pico (continua 5/20 e 160/320) —
o boss e o player e que dominam a linha. **Esse cenario e modelado por mim, nao lido do codigo**,
e por isso nao entra como medicao.

### KIRBY CLOUDE e GROK BUILD: inventario medido, scanline NAO

Contagens lidas do codigo (`BOSS_BRANCH_COUNT 4`, `BOSS_SEGMENTS_PER_BRANCH 5`,
`BOSS_APPLE_POOL 8`, `BOSS_LIGHT_SPRITES 3`):

| elemento | qtd | tiles | sprites de hardware |
|---|---|---|---|
| segmentos de galho | 20 | 2x2 | 20 |
| macas | 8 | 2x2 | 8 |
| luzes | 3 | 4x4 | 3 |
| face do boss | 1 | 6x4 | 2 |
| kirby | 1 | 4x4 | 1 |
| **total** | | | **34** |

34 de 80 slots da SAT. **O pico por scanline nao pode ser medido**: as posicoes saem de
`seg->x/seg->y` calculados em runtime pela simulacao dos galhos, e nao derivam de constante
nenhuma. Se mais de 20 coincidirem numa linha, ha dropout — e com 20 segmentos de galho numa
cena de boss, coincidir e plausivel.

Para virar medicao, cada um precisa de **`worst_frame_sprite_layout` preenchido** no
`scene_contract` ou de uma probe de runtime. Nao chutei o layout.

### O que fica aberto

- 3 declaracoes de `0 sprites` precisam ser corrigidas para o que o codigo faz.
- GOTHAM tem 50% de folga sem justificativa declarada.
- Os dois KIRBY precisam de layout declarado ou probe antes de qualquer claim de scanline.

## Fase 31 — RETRATACAO da Fase 30: as declaracoes estavam certas

A Fase 30 afirmou que tres projetos declaravam `0 sprites` com a SAT populada. **Isso esta
errado e a tabela daquela fase nao vale.**

### O erro

As declaracoes de `0 sprites` sao **escopadas na cena de branding**:

- `branding_sequence_contract.json` -> `scene_id: APP_SCENE_BRANDING`
- `scene-contracts.json` -> `scenes[0].scene_id: branding_sequence`

Eu rodei `grep SPR_addSprite` no projeto inteiro e comparei contra uma declaracao de UMA cena.
Os `SPR_addSprite` que encontrei estao todos em `src/gameplay/` (GOTHAM) e em
`scene_boss.c`/`scene_stage.c` (KIRBY) — que pertencem a `first_playable_slice`, e essa cena ja
declara `nao_medido`.

### Medido agora, no arquivo certo

`src/scenes/scene_branding.c`, chamadas de sprite (`SPR_addSprite`, `SPR_setPosition`,
`SPR_setVisibility`):

| projeto | chamadas na cena de branding | declaracao |
|---|---|---|
| GOTHAM_OVERDRIVE | **0** | `0 sprites` — **verdadeira** |
| KIRBY_FAN CLOUDE | **0** | `0 sprites` — **verdadeira** |
| KIRBY_FAN GROK BUILD | **0** | `0 sprites` — **verdadeira** |
| FORGE_REFERENCE | **0** (nenhum no projeto) | `0 sprites` — **verdadeira** |

**As quatro declaracoes de zero estao corretas. Nenhuma foi alterada.**

### O que sobrevive da Fase 30

- **Sprite de hardware nao e sprite do SGDK.** O split em 4x4 tiles continua valendo, e continua
  sendo obrigatorio decompor antes de medir.
- **A medicao de GOTHAM** (10 sprites de hardware, 5/20 por linha, 160/320 px) e valida, mas
  pertence a `first_playable_slice`, nao ao branding. Ela **preenche** um `nao_medido`, nao
  contradiz um zero.
- **O inventario dos KIRBY** (34 sprites de hardware) idem.

### O que nao foi feito, de proposito

A medicao de GOTHAM e do **quadro pos-init**, com o boss e o player nas posicoes de spawn. Nao e
o pior quadro da cena. Escrever 5/20 em `first_playable_slice.scanline_sprite_pressure` faria um
numero de escopo estreito parecer o pico da cena — trocaria um `nao_medido` honesto por um verde
com escopo escondido. `nao_medido` continua sendo a declaracao correta ate existir
`worst_frame_sprite_layout` ou probe.

### A licao

Declaracao tem escopo, e o escopo faz parte da leitura. Medicao de projeto inteiro contra
declaracao de cena nao mede nada — produz acusacao. Essa e a terceira vez nesta curadoria em que
o instrumento estava errado e nao o alvo, e a primeira em que o instrumento era um `grep` meu.

## Fase 32 — worst frame do GOTHAM: o VDP estoura na morte do boss

`first_playable_slice` saiu de `nao_medido`. O pior quadro nao foi procurado em captura: ele
esta escrito no codigo.

### O gerador

`gotham_boss.c:216-219`, estado `BOSS_STATE_DEFEATED`:

```c
if ((sBoss.defeatTimer & 7) == 0) {            /* a cada 8 quadros */
    s16 rx = bx + (sBoss.defeatTimer % 50);
    s16 ry = by + (sBoss.defeatTimer % 30);
    GOTHAM_PARTICLES_spawnExplosion(rx, ry, 6);
}
```

E `gotham_particles.c:142-152` emite **3 particulas por iteracao, na mesma coordenada**. Entao
`count 6` = **18 particulas coincidentes** no quadro do spawn. A cada 8 quadros, por 180 quadros,
com vida de 14 a 22 quadros: o pool de 24 satura e tudo fica dentro de 50x30 px do boss.

### Medido

Boss em `BOSS_COMBAT_Y=72` com as 5 pecas nos offsets de `gotham_boss.c:31-35`. Sprites do SGDK
decompostos em sprites de hardware de no maximo 4x4 tiles.

| | sprites de hw | sprites/linha | px/linha | status |
|---|---|---|---|---|
| **A** boss + 1 explosao (**so codigo**) | 26 | **22 / 20** | **408 / 320** | `error` |
| **B** pool saturado (+6 residuais modeladas) | 32 | **23 / 20** | **424 / 320** | `error` |

**Estoura os dois limites do VDP em 16 scanlines seguidas, da linha 80 a 95.**

A variante A ja estoura sem nenhuma suposicao minha: boss nas posicoes do codigo mais uma
chamada que o codigo faz. As 6 residuais da B estao marcadas como `modeled_not_derived` no
contrato.

**Nao incluidos** no layout: os 24 projeteis do pool, o player e os 4 drones. Qualquer um deles
so piora.

### Consequencia

Sprite alem do vigesimo numa scanline nao e desenhado. Na sequencia de morte do boss — o climax
da fatia jogavel — vao sumir sprites, e o candidato mais provavel a sumir e o proprio boss, que
esta atras das particulas na ordem da SAT.

### Um falso verde encontrado no caminho

`audit_scene_headroom.py` reportava **`ok` para 115% de utilizacao**. A regra dele so olhava para
baixo, procurando folga; nao havia ramo para estouro. Corrigido com o blocker
`scanline_limit_exceeded` e uma fixture no self-check. Quarta ferramenta de medicao com defeito
nesta curadoria, e a segunda que eu mesmo escrevi.

## Fase 33 — o conserto que eu sugeri estava errado, e a medicao mostrou

Na Fase 32 eu fechei sugerindo "espalhar o spawn por 2-3 quadros resolve sem tirar nada da
tela". **Medido, piora.**

### Varredura dos 181 quadros da derrota

| alteracao | sprites/linha | px/linha | veredito |
|---|---|---|---|
| atual | 23/20 | 448/320 | estoura |
| **espalhar o spawn em 3 quadros** | **24/20** | **464/320** | **pior que o original** |
| count 6 -> 4 | 20/20 | 376/320 | estoura |
| count 6 -> 3 | 18/20 | 368/320 | estoura |
| pool 24 -> 16 | 20/20 | 376/320 | estoura |
| velocidade x2 | 23/20 | 448/320 | estoura |
| vidas 14/18/22 -> 8/10/12 | 23/20 | 448/320 | estoura |
| explosao a cada 16 quadros | 22/20 | 408/320 | estoura |

Espalhar no tempo nao muda nada porque **o pool de 24 satura de qualquer jeito**. A explosao a
cada 8 quadros com vidas de 14 a 22 mantem 24 particulas vivas o tempo todo; mudar o instante do
nascimento so muda o arranjo.

### O limite que amarra e pixel, nao contagem

Varias opcoes levam a contagem a 20 ou menos e continuam estourando px. O boss sozinho ocupa
~120 px nas linhas dele (chassi 2 sprites de 32 px, torre 32, casulo 24), sobrando ~200 px, isto
e **12 particulas de 16 px**. Cortar particula ate caber destruiria a explosao.

### O que resolve: espalhar no ESPACO

| raio de nascimento | sprites/linha | px/linha | folga |
|---|---|---|---|
| r=2 | 21/20 | 416/320 | -96 |
| r=4 | 15/20 | 320/320 | 0 |
| **r=6** | **13/20** | **288/320** | **+32** |
| r=8 + count 5 | 11/20 | 256/320 | +64 |

`EXPLOSION_BIRTH_SPREAD 6`: a particula nasce deslocada na direcao da propria velocidade, como se
a explosao ja tivesse 6 quadros de idade no primeiro quadro. **Nada foi removido da tela** — pool
24, count 6 e periodo de 8 quadros continuam identicos.

Escolhi r=6 e nao r=8: a secao 30 diz que o teto e o alvo. Com 288/320 a cena usa 90% do
orcamento de pixel e 65% do de sprite, com folga medida. r=8 entregaria margem que ninguem pediu
ao custo de uma explosao mais rala.

### Pior quadro depois

`defeatTimer=24`, os mesmos 32 sprites de hardware em tela, **13/20 e 288/320, `status=ok`**.

### A licao

Sugeri um conserto por plausibilidade no fim da Fase 32 e o usuario pediu exatamente ele. Se eu
tivesse implementado sem medir, teria entregue uma regressao com cara de correcao — e o
`status=error` continuaria, so que agora com a justificativa de "ja foi tratado".

**Conserto sugerido sem medicao e chute com sotaque de engenharia.** A varredura custou um
script de 40 linhas e derrubou a minha hipotese junto com mais cinco.

## Fase 34 — build e captura do GOTHAM: nao foi possivel, e o motivo importa

Pedido: compilar a ROM e capturar no BlastEm para pagar a analise das Fases 32 e 33 com
evidencia de hardware, conforme a secao 33.

### O build reprova, e nao pelo que eu mexi

```
src/gameplay/gotham_boss.c:33: error: 'spr_boss_tread' undeclared;
                               did you mean 'spr_boss_turret'?
wine_bridge_status=blocked reason=sgdk_make_failed exit_code=2
```

`res/gotham.res` declara `spr_boss_tread_left` e `spr_boss_tread_right`; o codigo chama
`spr_boss_tread`. **O projeto nao compila.**

### E o codigo do boss e trabalho em andamento do usuario

| arquivo | git |
|---|---|
| `src/gameplay/gotham_boss.c` | **untracked** |
| `src/gameplay/gotham_enemies.c` | **untracked** |
| `src/gameplay/gotham_particles.c` | untracked |

Nao corrigi o erro de compilacao. Codigo nao commitado de terceiro nao se conserta por
iniciativa propria, mesmo quando o conserto parece obvio — o autor pode estar no meio de uma
refatoracao em que `spr_boss_tread` e o nome que vai existir.

### Consequencia para as Fases 32 e 33

**A analise do pior quadro e sobre codigo que nunca compilou.** Ela continua sendo leitura
correta do que o codigo diz, e o mecanismo (18 particulas num pixel) e real. Mas os numeros
23/20 e 448/320 **nunca rodaram em hardware nenhum**, e o conserto de 13/20 e 288/320 tambem
nao. Os dois sao simulacao, e a secao 33 poe simulacao abaixo de dump de VDP.

Existe `out/rom.bin` de 15/08, mas ela e anterior a este codigo — capturar aquela ROM produziria
evidencia de outro programa, o que e pior que nenhuma evidencia.

### E a probe esta defasada tambem

`src/system/runtime_probe.c` do GOTHAM tem 262 linhas contra 367 do modelo, e mantem os dois
defeitos que a curadoria ja corrigiu la:

- `g_mdRuntimeProbe[17] = 1;` — constante exportada sob o nome `active_sprite_count`;
- sem `s_linePressure[224]`, ou seja amostragem por grupos em vez de varredura das 224 linhas.

Mesmo com o build passando, a captura leria um instrumento quebrado. Pela secao 34, essa leitura
nao sustentaria claim nenhum.

### Erro meu, corrigido

O commit `a7e0c067` adicionou `gotham_particles.c` ao git. O arquivo era **untracked**: trabalho
nao commitado do usuario, fora do escopo desta curadoria. Desfeito com `git rm --cached`; a
edicao pedida continua no disco, apenas nao versionada.

### O caminho para fechar de verdade

1. O autor resolve `spr_boss_tread` (fora do meu escopo);
2. portar a `runtime_probe.c` corrigida do modelo para o GOTHAM;
3. build pelo wine bridge, captura por `capture_blastem_evidence_linux.sh` na sequencia de
   derrota, e comparar o pico medido contra os 13/20 e 288/320 da simulacao.

Ate os tres, o estado honesto de `first_playable_slice` e **medido por simulacao, nao por
hardware**, e o contrato ja diz isso em `how_determined`.

## Fase 35 — probe corrigida portada para o GOTHAM

Autorizada pelo curador.

### Verificacao antes de sobrescrever

Diff ignorando fim de linha: **19 linhas so no GOTHAM, 124 so no modelo**. As 19 exclusivas do
GOTHAM sao exatamente o codigo defeituoso:

- `sampleLines[4]` / `pressure[4]` / cursor rotativo — amostragem de 4 de 224 scanlines;
- `g_mdRuntimeProbe[17] = 1;` — constante exportada sob o nome `active_sprite_count`.

**Nenhuma customizacao propria do GOTHAM foi perdida.** As unicas dependencias externas da
versao do modelo sao `gApp`, `game_vars.h` e `system/runtime_probe.h`, e as tres existem no
GOTHAM.

### O que entrou junto

O header do modelo tem duas linhas a mais: `MDRuntimeProbe_noteSpriteAlloc(u16 spawned, u16
failed)`. Nao e bagagem — `GOTHAM_PARTICLES_spawnParticle` retorna `FALSE` em silencio quando o
pool de 24 enche, e ninguem checa. E o mesmo defeito que a licao
`silent_failure_path_invalidates_claims` descreve, e agora o GOTHAM tem onde contar.

E o bloco `PROBE_VLAB_*`, que o GOTHAM **nao tinha**. Sem ele
`capture_blastem_evidence_linux.sh` rejeita com `vlab_block_missing`: a probe antiga nunca
poderia sustentar captura, mesmo com o build passando.

### Verificacao depois

Fim de linha convertido para CRLF, que e a convencao do GOTHAM (a do modelo e LF).

Compilacao da unidade isolada pelo wrapper do wine bridge, ja que o build completo para antes de
chegar nela:

```
gcc -m68000 -Wall -Wextra ... -c src/system/runtime_probe.c
-> out/probecheck/runtime_probe.o, 7808 bytes, zero warning
```

| defeito | antes | depois |
|---|---|---|
| `g_mdRuntimeProbe[17] = 1;` | presente | **0 ocorrencias** |
| varredura das 224 linhas | ausente | **presente** |
| bloco VLAB | ausente | **presente** |

### Nao commitado, de proposito

`src/system/runtime_probe.c` e `inc/system/runtime_probe.h` sao **untracked** no GOTHAM, como
quase todo o `src/` dele. Estao no disco e nao no git, pelo mesmo motivo da Fase 34: o escopo
desta curadoria nao versiona arquivo nao commitado do usuario.

### Ainda bloqueado

A captura continua impossivel enquanto `gotham_boss.c:33` chamar `spr_boss_tread`. O passo 2 dos
tres da Fase 34 esta feito; o 1 e do autor e o 3 depende dele.

## Fase 36 — GOTHAM compila e roda; a probe portada se prova e acha outra coisa

### O conserto

`gotham_boss.c:33-34`: `spr_boss_tread` -> `spr_boss_tread_left` e `spr_boss_tread_right`, que sao
os nomes declarados em `res/resources.res:23-24`. Era erro de digitacao, nao refatoracao em
andamento como eu suspeitei na Fase 34. Duas linhas.

`wine_bridge_status=buildado`. Unico warning e pre-existente e alheio:
`gotham_enemies.c:79: unused variable 'dx'`.

A `runtime_probe.c` portada compilou **dentro do build completo**, nao so isolada, o que fecha a
verificacao da Fase 35.

### A captura

`linux_blastem_capture_status=sealed`, `blockers: []`. Cena capturada:
`APP_SCENE_TECHDEMO = 4`, 151 quadros.

### A prova de que o port valeu

| campo | probe antiga | probe portada, medida |
|---|---|---|
| `active_sprite_count` | **`1`** (constante) | **`58`** |
| `max_active_sprites` | inexistente | **`58`** |
| `max_scanline_sprites` | 4 de 224 linhas amostradas | **`7`**, varredura completa |
| bloco VLAB | ausente | presente e lido |

O campo que exportava a constante `1` agora exporta 58. **A leitura da probe antiga era ficcao**,
e agora ha numero.

### O que a captura achou, e nao era o que eu procurava

| | |
|---|---|
| `max_cpu_load` | **185** |
| `over_budget_frames` | **61** de 151 |
| `max_cpu_jitter` | 13 |
| `max_scanline_sprites` | 7 de 20 |
| `max_active_sprites` | 58 |

**A techdemo roda a 185% do orcamento de quadro, com 61 dos 151 quadros estourados.** O HUD da
propria ROM concorda: `CPU:170` na captura. Isso e problema de CPU, nao de VDP — com 58 sprites
ativos o pico por scanline e so 7 de 20, ou seja eles estao espalhados.

Nao investiguei nem corrigi: e codigo untracked do usuario e esta fora do que foi pedido.

### O que continua sem contraprova

A captura **nao alcanca `BOSS_STATE_DEFEATED`** — chegar la exige jogar ate matar o boss. Os
`13/20` e `288/320` das Fases 32 e 33 continuam sendo simulacao. O que mudou e que agora existe
instrumentacao capaz de medi-los: ROM que compila, probe que le de verdade e bundle que sela.

Bundle: `out/remediation/P0-005/fresh_bundle/blastem-linux-20260818T154746Z-2690057`
(`out/` e ignorado, entao o bundle nao entra no git; o caminho fica registrado aqui).

## Fase 37 — nao ha atalho de debug, e a rota por input nao alcancou o boss

### Procura

`scene_techdemo.c` tem exatamente dois atalhos: `START` pausa e `MODE`/`X` alterna o overlay de
telemetria. **Nao existe caminho de debug para `BOSS_STATE_DEFEATED`** — o boss so morre por dano
em `GOTHAM_BOSS_damage`.

### A rota que a matematica do codigo sugeria

- boss com 200 de vida (`gotham_boss.c:18`);
- vulcan com 2 projeteis de 2 de dano e cooldown de 6 quadros = **40 de dano/s**;
- player nasce em x=136, canhoes em 146 e 168, dentro da caixa do boss (`bx..bx+64` = 128..192);
- `g_mdRuntimeProbe[14]` e `[17]` sao **maximos acumulados**, entao nao era preciso acertar o
  quadro da explosao.

No BlastEm, `a` = `gamepads.1.a`. Captura rodada com `xdotool keydown a` por 34 s.

### Resultado: nao funcionou

| | sem input | com fogo |
|---|---|---|
| `frame_counter` | 151 | 1111 |
| `max_cpu_load` | 185 | **212** |
| `over_budget_frames` | 61 | **1021 de 1111** |
| `max_scanline_sprites` | 7 | **21** |
| `max_active_sprites` | 58 | 58 |

HUD ao fim da sessao: `P:[......]` **vazio** e `BOSS:[###############.]` **cheio**.

**O player morreu e o boss ficou com a vida intacta.** Segurar o tiro sem desviar mata o player
antes de o boss cair. A rota por input roteirizado precisa de desvio, nao so de tiro.

### O que a captura provou mesmo assim

**Estouro de scanline existe neste ROM, medido em hardware: 21 contra o teto de 20.** Isso e
dropout real, e e a primeira vez nesta curadoria que o estouro sai de dump e nao de simulacao.

Mas **nao e o quadro de derrota do boss**, e nao da para atribui-lo: a probe exporta o maximo sem
o quadro em que ele ocorreu. Os candidatos sao a barragem de vulcan e a explosao de morte do
player (`gotham_player.c:77`, que usa o mesmo `spawnExplosion` de count 6).

E ele foi medido **com o meu conserto ja compilado**. O `EXPLOSION_BIRTH_SPREAD 6` nao impediu o
21, o que significa que ou o pico vem de outra fonte, ou o conserto e insuficiente fora do
cenario do boss que eu simulei.

### O achado dominante nao e o meu

**1021 de 1111 quadros estourados, 92%, com `max_cpu_load` de 212.** O ROM esta em sobrecarga
permanente, nao em pico. Isso e problema de CPU e ofusca em ordem de grandeza o eixo de scanline
que eu vinha perseguindo. Nao investiguei: e codigo untracked do usuario.

### Estado honesto

Os `13/20` e `288/320` da Fase 33 **continuam sem contraprova**. O que existe agora e uma medicao
de hardware que diz que o teto e violado em algum momento, sem dizer qual.

Para fechar faltam duas coisas: um campo de quadro-do-pico na probe (hoje o maximo e anonimo) e
um caminho ate `BOSS_STATE_DEFEATED` — atalho de debug no `scene_techdemo.c`, que e edicao de
codigo untracked e depende de autorizacao.

## Fase 38 — quadro do pico na probe, e o furo de integracao que ele revelou

### O que foi adicionado

`probe_note_peak_frame(slot)` grava `gApp.totalFrames` como par hi/lo **no mesmo instante em que
o maximo sobe**, para tres picos: scanline (`[24..25]`), cpu (`[26..27]`) e sprites ativos
(`[28..29]`). Zeram junto com os picos no reset de cena.

Anexados em `words[26..31]`, no FIM do bloco, subindo `PROBE_VLAB_METRIC_WORDS` de 26 para 32 —
sem deslocar `words[0..25]`, que o sealer ja consome por indice fixo.

### O furo

Primeira captura com a probe nova: os tres campos vieram **`None`** num bundle cuja SRAM tinha o
dado. `extract_vlab` cortava o bloco em `words[:24]`, com **24 escrito na mao**, enquanto a probe
ja emitia **26**. As seis palavras novas cairam no balde da paleta.

E isso nao era regressao minha: os dois campos que ja sobravam — `spawned` e `failed` do contador
de alocacao de sprite — **nunca chegaram ao report desde que foram criados**. O contador que a
licao `silent_failure_path_invalidates_claims` mandou construir existia na ROM e morria na
leitura.

Corrigido derivando a contagem: a paleta tem tamanho fixo (64), o que sobra na frente e metrica.
Agora a leitura acompanha a probe sozinha.

**O `None` em vez de `0` foi o que tornou o furo visivel.** Se `_peak_frame` devolvesse 0 na
ausencia, os tres campos leriam "pico no quadro zero" e ninguem olharia duas vezes.

### Medido

| | valor | quadro |
|---|---|---|
| `max_scanline_sprites` | **21** de 20 | **405** |
| `max_cpu_load` | **212** | **403** |
| `max_active_sprites` | 58 | 91 |
| `sprite_alloc_spawned` / `failed` | 0 / 0 | — |

Sessao de 1111 quadros, 1021 estourados.

### O que os quadros dizem

**Pico de scanline (405) e pico de CPU (403) estao a 2 quadros de distancia: e o mesmo evento.**
O pico de sprites ativos (91) esta longe dos dois, entao a alocacao maxima nao e o que estoura a
linha — coerente com `max_active_sprites` ser so a contagem de objetos alocados, que e constante
nesta cena.

Quadro 405 a 60 fps sao ~6,8 s de cena, com o tiro segurado desde ~1 s. Ainda **nao atribui o
evento**: saber o quadro estreita o cerco, nao fecha. Para fechar falta gravar tambem o estado do
boss e a contagem de projeteis vivos naquele quadro.

`sprite_alloc_spawned=0` confirma que o GOTHAM ainda nao chama `MDRuntimeProbe_noteSpriteAlloc` —
o contador chegou com o port da Fase 35 e nao foi ligado ao `GOTHAM_PARTICLES_spawnParticle`, que
e onde o `FALSE` silencioso mora.

## Fase 39 — sealer entra no meta-gate

`seal_fresh_evidence_bundle.py` produz **todo numero de runtime que esta curadoria cita** e nao
estava na lista de ferramentas de medicao. A Fase 38 provou por que ele deveria estar: um corte
hardcoded fazia campo existente na SRAM chegar ao report como `None`, e antes disso fazia
`spawned`/`failed` nunca chegarem.

### O self-check, nos dois sentidos

Passam:
- bloco de **32 metricas** lido como 32, nao truncado em 24;
- par hi/lo reconstruido acima de 65535 (`0x0001_86A1` = 100001), que e o caso em que um
  `u16` sozinho mentiria;
- bloco de **26 metricas** (ROM com probe anterior) lido como 26, com os campos novos em
  **`None` e nunca `0`**;
- `words[24..25]` chegando ao report como `sprite_alloc_spawned`/`failed`.

Reprovam:
- SRAM sem bloco -> `vlab_block_missing`;
- `total_bytes` maior que a SRAM -> `vlab_block_size_invalid`;
- bloco com 10 metricas -> `vlab_metrics_incomplete`.

### Teste de mutacao

Reintroduzi o bug (`metric_count = 24`) e o self-check reprovou com a mensagem certa:

```
self-check failed: 32 metricas lidas como 24 — o corte voltou a ser fixo
exit=1
```

Restaurado, volta a passar. **O self-check ja reprovou de verdade uma vez**, que e o que a secao
37 exige antes de a trava valer.

### Meta-gate

**9/9 com self-check passando, verdict=OK.**

## Fase 40 — meta-gate passa a medir deriva de fonte por projeto

A deriva de copia ja era detectada para os `.py` da lista `MEASUREMENT_TOOLS` — foi assim que as
4 copias defasadas do simulador apareceram. A **probe nunca esteve no radar**: e C, e por
projeto, e so apareceu porque fui olhar na mao. Deriva que nenhum gate mede so aparece quando
alguem vai procurar.

### O que entrou

`PROJECT_SOURCE_MIRRORS` declara as fontes que cada projeto carrega uma copia, com a canonica no
modelo — que e de onde `new_project.sh:37` copia:

```
tools/sgdk_wrapper/modelo/src/system/runtime_probe.c
tools/sgdk_wrapper/modelo/inc/system/runtime_probe.h
```

Blocker novo: `project_source_mirror_stale`, separado de `measurement_tool_stale_copy` porque a
acao e diferente — um se resolve copiando a ferramenta, o outro exige rebuild do projeto.

### Comparacao normaliza fim de linha

O GOTHAM usa CRLF de proposito e o modelo usa LF. Comparar byte a byte acusaria **toda** copia
CRLF como defasada. Fim de linha nao e deriva de versao, e reprovar por isso e o gate que grita
lobo da secao 37. O self-check tem fixture para os dois lados: copia so-CRLF **precisa passar**,
copia com corpo diferente **precisa reprovar**.

### Medido na arvore

| | |
|---|---|
| ferramentas com self-check ok | **9 de 9** |
| espelhos de fonte **defasados em uso** | **20** |
| espelhos em sincronia | 2 |
| copia de ferramenta arquivada | 1 (aviso) |

Veredito: **BLOCKED** por `project_source_mirror_stale`, exit 1.

Os 20 sao `runtime_probe.c` e `.h` em 10 projetos: BLUE_CIRCUIT, Celestial Chase Revive,
Celestial Chase visual benchmark, FORGE_REFERENCE, os dois KIRBY, MARE_BRAVA, SMOKE_TEST,
`_agent_laboratory` e `_agent_training`. Os 2 em sincronia sao o GOTHAM, portado na Fase 38.

### O que isso muda daqui pra frente

- **Projeto novo nasce correto**: `new_project.sh` copia do modelo, que e a canonica.
- **Projeto existente nao se conserta sozinho**: os 20 continuam defasados ate alguem sincronizar
  e reconstruir. A diferenca e que agora **o gate diz**, em vez de depender de alguem suspeitar.
- O sealer, por ser arquivo unico compartilhado, ja valia para todos sem copia nenhuma. A
  assimetria entre ferramenta compartilhada e fonte espelhada era invisivel e agora e medida.

### Nao sincronizei os 20

Sincronizar `runtime_probe.c` muda `src/` de 10 projetos e exige rebuild de cada um para valer.
E decisao de curadoria, nao efeito colateral de um gate.
