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
