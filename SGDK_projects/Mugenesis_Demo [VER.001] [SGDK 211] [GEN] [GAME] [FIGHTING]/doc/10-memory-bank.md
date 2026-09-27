<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-09-26T13:21:52.5053892-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 0
- Ultimo build versionado: nenhum
- ROM vigente: `200346548a57cb6196cf21773c9233bd53b72b02e1bdf7f6548fd3331aa81c2c` (`1048576` bytes)
- Validation summary: errors=14 warnings=20
- Blockers vigentes: perceptual_motion_unvalidated, gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, budget_doc_mismatch, changelog_missing, emulator_evidence_stale, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_stale, report_rom_identity_mismatch, report_status_conflict
- Evidencia de emulador: rom_path_mismatch
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=nao_testado performance=unproven audio=nao_testado hardware_real=nao_testado
<!-- SGDK GENERATED STATUS END -->
## 2026-09-26 — Retomada de fidelidade ao Suzaku original

- Direcao vigente: preservar pixels/composicao DEF/SFF; conceitos V1–V16 ficam historicos. Plano: `doc/mugen/suzaku_source_fidelity_recovery_2026_09_26.md`.
- Auditoria offline com hashes e self-check7/7: quinze cores proprias melhoram erro RGB; PAL3 compartilhada e condicional, nao adotada. 446 tiles e teto da alocacao historica, nao do VDP. Camera e movimento autonomo do ceu exigem reconciliacao.
- Corrigido arredondamento divergente de `stage_measure` usando `vdp_word`; novos testes reproduzem defeito antes da correcao. Suite completa do conversor: 133 passed. Relatorios historicos de cores nao foram revalidados automaticamente.
- Nenhum novo asset promovido, build ou gate visual/runtime fechado. Arte e cena continuam pendentes; metricas offline nao aprovam qualidade.


# 10 - Memory Bank & Context Tracker - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

**Ultima atualizacao:** 2026-09-25
**Fase atual:** D1 - pre-producao medida do stage Suzaku; HUD/combate seguem em integracao WIP
**Proxima fase:** resolver BG_B, furos mascarados e custo simultaneo de tiles antes do runtime do cenario

## 1. Estado operacional

### Checkpoint autoritativo mais recente (2026-09-25)

- O bloco gerado acima esta stale: `ROM vigente=595116bc...` e os contadores
  de validacao nao correspondem ao estado operacional. A fonte auditada nesta
  rodada reporta a ROM principal atual como `200346548a57cb6196cf21773c9233bd53b72b02e1bdf7f6548fd3331aa81c2c`;
  ela foi vista no BlastEm com fundo ainda solido. Esta rodada nao compilou ROM.
- Ultimo fechamento global conhecido continua bloqueado; nao confundir a
  infraestrutura de medida aprovada com aprovacao do jogo. Build, teste em
  emulador, cadencia sustentada, audio final e visual do stage continuam por
  provar. O closeout report registrou `14 erros / 18 avisos`; qualquer nova
  validacao precisa ser vinculada a mesma ROM e aos relatorios correspondentes.
- Um bug no auditor compartilhado `tools/sgdk_wrapper/audit_doc_sync.py`
  considera o ultimo hash de 64 hex do changelog como SHA de ROM e seu bloco
  de memoria associado esta stale. O bug fica registrado; nao foi alterado
  codigo canonico do wrapper nesta rodada.

- documentado: sim (tools/mugen2sgdk_forge/doc/ROADMAP.md e doc/mugen/ken_conversion_report.json)
- implementado: cena de luta (src/scenes/scene_demo.c) + runtime generico (src/mg/, copiado da ferramenta)
- buildado: sim, pela ponte Wine canonica; ROM SHA-256 da3548308324606da3f71584a6b48bf441f0d9884e32df33166893ab3534fcfc
- testado_em_emulador: sim, BlastEm; sessao selada out/mugenesis_evidence/e3_ken/blastem-linux-20260923T070143Z-1272238 (arvore principal)
- validado_budget: NAO. 598 de 3631 quadros acima de 100% de CPU (16%), pico 156%; 10 sprites/linha no pico
- audio: sons convertidos tocam via XGM2 (RMS nao nulo em todos os segundos da captura)
- visual: technical_candidate (conversao automatica; aprovacao humana pendente); gate semantico de tela rejeita por baixa densidade de bordas (sem cenario)
- ready_for_aaa: false

### Direcionamento 2026-09-23 (P1..P6)
- P1 faiscas ancoradas no contato: FECHADO (ROM normal 38a67c94..., teste f1f4df6a...; 22,6% acima do orcamento).
- P2 rampas de roupa: FECHADO (ROM 5690eafe...; doc/mugen/p2_palette_calibration.md). Regerar SEMPRE com --vivid-clothing.
- P4/P4.1 HUD: FECHADO (ROM b138fb35...; doc/hud/p4_hud_contract.md). Regerar HUD: convert-hud <sfa2_lifebars.zip>.
- Paleta ocupada: PAL0 9..15 = HUD; PAL0 1..8 livres p/ estagio (E4) e fundo de super usa 1..14 (HUD escondido).
- P5 sombra: FECHADO (dither; ROM 46a9cd65...; doc/hud/p5_shadow_memo.md). S/H reavaliar no E4.
- P3 memo aneis: NO-GO recomendado (doc/hud/p3_ring_multiplex_memo.md; simulador 16/20 atual vs 21/20 multiplex 16x16), aguarda aprovacao.
- P6 catalogo: registrado como consultivo (doc/mugen/p6_effects_catalog_fit.md); nada implementado.
- Build: ROMs com --output-dir alternativo exigem out/ ja buildado (sega.s inclui out/rom_head.bin).

### Rodada 2026-09-24 (direcionamento pos-P6)
- Etapa 1 desempenho com audio real: FECHADA. A luta foi de 29,3% para 8,5% de quadros acima do orcamento (pos-warmup), ROM 6bbef58a... (doc/perf/etapa1_perf_audio_real.md).
- Medir CPU com -DMG_PCPROF (amostragem de PC por H-Int) + tools/mugen2sgdk_forge/perf/read_sram_metrics.py. O -DMG_PROFILE (getSubTick) distorce: a ROM de perfil fica 77% acima do orcamento.
- A sonda canonica custava ~10% do quadro (laco por linha). Corrigida so neste projeto; o template ainda tem o custo.
- Q1 proveniencia: FECHADO. O manifesto passa no schema (audit rc=0, nenhum bloqueio).
  - MUGEN = procedural_composed_from_authored + placeholder, com licenca NAO verificada.
  - Sons foram para doc/mugen/ken_audio_provenance.json.
  - neg1_masks vira tabela logica por analise de uso (nao por nome); um pixel renomeado continua bloqueado (fixtures + mutacao).
  - Migrar manifesto antigo: python3 -m mugen2sgdk_forge fix-provenance --project <P>.
- Q2 SuperPause: FECHADO. Teste focal no personagem sintetico (tests/host/superpause.c):
  - pos 17,-23 com facing -1 -> explod em (83,-23);
  - time 31 / movetime 5 exatos em ticks; poweradd 250; som S2,0 identificado pelo ponteiro.
  - Tres mutantes (TIME<->MOVETIME, POS_X<->POS_Y, sem espelho) fazem o teste falhar.
- Q3 fechado: indice de intake gerado (`intake-index`, lint `--check`); 12 licoes, todas pending_human_review.
- Etapa 3 (shake + flash): implementada e testada no host, parada no branch `feat/mugenesis-impact-fx` (commit WIP 29d99535). Faltam as capturas flash/shake/both, interrompidas por falta de memoria no host.
  - Achado: a janela da sonda variava com a duracao da captura e com o reset por fim de luta, entao o A/B era invalido. No branch ha uma janela fixa de 1200 quadros travada; base = 5,5%.
- **Contrato de paletas (REGRA 1, engine):** PAL0 = cenario (15), PAL1/PAL2 = lutador (corpo + efeitos, 15), PAL3 = HUD.
  - Emprestimos so declarados: o fundo de super usa PAL0 enquanto cobre a tela; o flash de impacto fica na linha do lutador atingido.
  - Todo personagem novo passa por `palette-check` (reprova > 15).
  - Ken precisa de 23 slots exatos: 14 classes de corpo (1 e 6 fundiveis sem perda) + 9 cores so de efeito.
  - Orcamento do piloto: 8 estaveis + 6 de roupa + 1 de efeito.
- A migracao espera o piloto de uma familia de FX pelo agente grafico (`doc/mugen/palette_contract_rule1.md`).
  - Divisao de papeis: o agente tecnico integra e mede; o agente grafico produz candidatos; a aprovacao visual e humana.
  - Fusao 6 -> 1 APLICADA (conversor, sem perda, provada). Pacote do piloto hadouken pronto em `doc/mugen/fx_pilot_hadouken/`, aguardando o agente grafico.
  - Defeito conhecido na linha antiga de FX: nucleo preto -> vermelho.
- **Continuidade segura do piloto Hadouken (2026-09-24):** usuario aceitou a pose original `source_750_1.png`. Anexo e copia do projeto sao 56x28 RGBA; mascara alfa e 1.154 pixels visiveis coincidem, enquanto os 414 RGB ocultos transparentes diferem (`(0,0,0)` no anexo, `(250,0,250)` na copia). Hash da copia: `2a60f8b75e12156a6d4c8e2fb2a3bbb099cf4ed38a9210e3cd9a63d443764164`; nucleo escuro opaco confirmado (68 pixels `(8,8,8)`). Registro de aceitacao com os dois hashes em `doc/mugen/fx_pilot_hadouken/user_source_approval_2026_09_24.md`. Uma alternativa ImageGen ficou em `data/raw_ai/...` como `visual_lab_control`, falhou no gate pixel-strict e nao substituiu a fonte.
  - Uma pose tecnica em staging foi remapeada a indices do contrato: SHA-256 `4f9f30abcfa23dc6d7db21369d64c689d3b1d2d61764c8bfca68e57bc1a75d66`, 56x32, mascara identica, index 0 transparente, preto opaco no index 15. Forge-art passa como `technical_candidate`; o contato 1x/3x ficou mais quente e achatou a rampa azul/branca. A fonte aceita continua preferida; nada foi para `res/`.
  - Slot 6 `0xE82` e somente estudo global de 15 familias; RGB canonico `(34,136,238)`, decisao humana pendente. Workset hash-bound em `doc/art/visual_workset_manifest.json` permite apenas auditoria, validacao pixel e conversao tecnica. AIR preview e da fonte original, preserva 8 elementos/3 vazios; compilacao e custo VDP continuam sem medicao.
  - Revalidacao independente: PR21 segue aberta/mergeable em `f3b92bb9`; checkout detached da PR passou `test_provenance_preserve.py` (4/4) e a suite completa (61 passed, 11 skipped), mas a protecao segue ausente na branch PR22 `7cf00ed8`; nenhum merge/cherry-pick feito.
  - `git merge-tree` read-only PR22 + PR21 reporta conflitos em `doc/changelog/changelog.md`, `doc/curation/lessons_2026-09-24_mugenesis.json`, `doc/curation/mugen_intake_index.json` e `.md`. Nao integrar/reconverter ate resolver o historico com a aprovacao apropriada.
  - Contexto antes `unclassified`; classificado por inferencia, com escopo limitado, como `technical_demo` no manifesto. Validator passou em `planning` e `implementation`; teto de claim `technical_demo`, mudança futura de contexto ainda requer confirmacao humana.
  - Hygiene manifest alinhado ao schema atual: `.gitignore` e `out_pcprof/out_prof/out_test` classificados; entrada externa localizada, hash-bound e sem caminho absoluto externo. `validate_project_hygiene` passou (0 blockers). Metodologia classificou `critical_motion=required`, `road_physics/modular_boss=not_applicable`; resta blocker `perceptual_motion_unvalidated` (quatro eixos sem prova da candidata integrada). `validate_project_methodology` continua bloqueado legitimamente.
  - Releitura da captura Stage 3 na pasta local `out/`: ROM SHA `595116bc...` produziu 71/1141 pos-warmup (6,2%), 10 sprites e 280 px por linha; faltam 59 quadros para 1200. Segunda sessao continua rejeitada. `fx_*` sob o `out/` da raiz sao snapshots separados de 32 amostras, nao fecham a matriz. Host apos testes: 1,3 GiB disponiveis, 14 GiB swap usado; ciclo de captura encerrado apos duas tentativas.
  - Recheck do host em 2026-09-24T19:34Z: rota SGDK `linux_wine_bridge` e rota de captura `linux_flatpak_blastem` selecionadas, sem bloqueio de rota; preflight reportou 1 lint (`drawText-in-update`). Memoria disponivel caiu a 641 MiB, swap 13 GiB; nenhuma nova captura iniciada e PR22 segue draft.
  - Recheck de recurso em 2026-09-24T19:47Z: `MemAvailable` oscilou de 856 para 690 MiB; PSI de memoria sustentado (`some avg10=16,04%`, `full avg10=13,48%`), swap usado 14 GiB. `chrome-headless` estava com ~2,7 GiB RSS. O wrapper nao possui guarda de pressao de memoria; seletor de rota sem blockers nao prova prontidao de recurso. Nenhum processo encerrado/captura iniciada; Stage 3 segue sem relancar sob essa pressao.
  - Recuperacao do host em 2026-09-24T23:55Z: 5,6 GiB disponiveis, PSI quase zero; ciclo de captura retomado. Nova sessao BlastEm `out/mugenesis_evidence/stage3_matrix/flash_only/blastem-linux-20260924T235547Z-112747`, cena 3, NTSC, audio em disco, ROM flash-only SHA-256 `595116bccccd83e0fc45c30cd8a3da9d31dfe0c385182854821eca02494d3623`. MDRT fechado em 1200 quadros pos-warmup: 71 (5,9%) acima do budget, CPU max 145, 10 sprites/linha, 288 px/linha, sem overflow. Screenshot/SRAM/VDP/audio (19.9 MB) presentes. Burst atrasado mostra luta/projetil, nao hit flash/shake; titulo 58.4 fps e apenas snapshot. Outras tres variantes e observacao de eventos continuam pendentes.
  - Estudo das 15 familias ranqueou `0xE82`/RGB `(36,144,252)` como slot 6 provisional pelo criterio minimax de erro medio; pior media por familia 37,4 dE. **Nao aprovado**; `palette_roles.json` permanece sem valor no slot 6. Sem asset indexado, reconversao ou alteracao em `res/`.
  - AIR 750/751 continua exatamente conforme `frame_contract.json`: 8 elementos, 3 vazios, tempos, offsets, pivots e Clsn sem mudanca. Fonte/RGB precisa de traducao e indexacao antes da integracao.
- **Atualizacao Stage 3 controlada (2026-09-25):** quatro builds temporarios na mesma fonte/script fecharam MDRT de 1200 quadros cada em BlastEm, com bundles selados e hashes completos em `doc/mugen/stage3_matrix_2026_09_25.json`. Base `46747958...`, flash-only `50aad339...`, shake-only `77f63784...`, ambos `94139f16...`. Todas mediram 250/1200 (20,8%) acima do budget, CPU maxima 145, 9 sprites/linha, 248 pixels/linha e zero quadros alem dos limites de scanline. O flash-only historico `595116bc...` (71/1200) e ROM/estado diferentes, logo nao entra na matriz. O burst complementar da ROM `both` mostrou o flash do defensor em torno dos quadros 83-85 e a animacao de impacto. A tentativa anterior com `rom.out` ELF foi rejeitada; `rom.bin` e o artefato correto. `freshness_audit.ps1` reportou warning: validation report stale, scene-contract/res-graph reports ausentes, zero errors. FPS sustentado e qualidade de audio seguem sem prova; nenhuma ROM de producao foi substituida.
- **Probe visual de carga alta (2026-09-25):** ROMs base/both com `MG_TEST_FULL_POWER`, mesmos parametros e bursts de 150 quadros; hashes e bundles em `doc/mugen/stage3_event_probe_2026_09_25.json`. No `both`, a pose do atacante casa a 95-98% dos pixels apos deslocamento de (+4,+4) na captura nos quadros 26-28, com retorno/reversao nos quadros 29-31; HUD segue fixo e a sombra de chao tambem desloca verticalmente. Isso registra movimento de tela visivel no BlastEm. A janela base separada nao esta sincronizada ao evento, e EnvShake legado tambem alimenta o eixo vertical: a contribuicao isolada do Stage 3 e a aprovacao perceptiva ficam pendentes. FPS sustentado e qualidade de audio nao aprovados. Nenhuma mudanca de producao.
- **Alternativa visual 2/2 do Hadouken:** SHA `7df530ee8a86926b9544baf28195481e4cc14ff6b4110742a423c8726a42b2b2`, RGBA 1659x948. Source-audit bloqueia traducao direta por motion blur e recomenda manter como `effect_reference`; nao superou a fonte aceita. Estudo e hashes em `doc/mugen/fx_pilot_hadouken/alternative_study_2026_09_24.md`. O limite de duas alternativas foi alcancado; nenhuma outra foi produzida.
- **Stage 3 — captura de flash-only (2026-09-24):** ROM local SHA-256 completo `595116bccccd83e0fc45c30cd8a3da9d31dfe0c385182854821eca02494d3623` (flash-only). Sessao `out/mugenesis_evidence/stage3/blastem-linux-20260924T161051Z-3448566` observou a ROM no BlastEm e tem screenshot, SRAM, VDP dump, audio e burst. Snapshot: 71/1141 quadros pos-warmup acima do budget (6,2%), 10 sprites/linha, 280 px/linha; denominador insuficiente para a janela exigida de 1200. O burst mostrou Round/Fight, nao flash/shake.
  - Segunda tentativa isolada teve screenshot preto de 640x480, audio zero, SRAM 300 B e faltaram VDP dump/metricas (`161519Z-3457713`); bundle rejeitado. Captura invalida, sem diagnostico de runtime. Host estava com 1,7 GiB disponiveis e 11 GiB de swap usados apos a falha.
  - Matriz A/B 1200 quadros continua incompleta: ha ROMs de snapshots `fx_*` na raiz do workspace, mas cada uma tem so 32 amostras e frame/ROM distintos; nao compoem uma comparacao controlada. O `out/rom.bin` do projeto e flash-only, SHA completo `595116bccccd83e0fc45c30cd8a3da9d31dfe0c385182854821eca02494d3623`. PR #22 continua draft.
- Dieta de VRAM (2026-09-24): reserva do corpo 102 (guarda para sheet maior), fundo de super sob demanda, especial compacto no rodape (BG_A linha 26, precisa de scroll 0 quando houver palco).
  - Livre para cenario: 180 tiles, 452 com emprestimo. O pool de sprites (600) ainda nao foi medido.
  - Achado: o super passa de 320 px/linha em 128 de 1200 quadros (ja na main).
- E4.0 (stage Suzaku): NO-GO para inclusao direta. Livre na luta: 90 tiles e 8 cores (PAL0 1-8); o stage pede ~1280 tiles e 56 cores.
  - Proximo passo depende de decisao: re-autoria, CRAM ou enxugar a VRAM da luta (+272 do bgfx temporal, +90 da reserva de corpo, pool a medir).
  - Memo: doc/mugen/stage/e4_suzaku_viabilidade.md.

### Conteudo de terceiros
Ken Masters ADV (autor Chok): uso local autorizado pelo usuario; redistribuicao nao verificada.
Saidas convertidas (res/mugen/, res/mgres_*, src/mg_gen/, inc/mg_gen/, out_prof/) ficam fora do Git.
Regerar: `python3 -m mugen2sgdk_forge convert-char <ken_masters_adv.zip> --id ken --project .`

### Licoes
- No 68000 cada iteracao de laco custa centenas de ciclos: o reconhecimento de comandos e o estado -1
  so cabem guiados por eventos/indices gerados pelo compilador (portoes de comando e de tempo).
- Numero em [State N, ...] e rotulo: controlador pertence ao ultimo Statedef (Ken reaproveita rotulos).
- `B` = direcao tras, `b` = botao; caixa importa no .cmd.
- Indice derivado deve ser GERADO das fontes e ter lint de deriva; indice editado a mao vira mais um status concorrente.
- Ferramenta que chama git precisa tolerar repo sem commits (fixture de teste pegou isso no intake).
- Inventario do acervo nao e o .def: o Suzaku tinha 10 secoes e 320x240, nao ~23 e 384. Abrir a fonte antes de planejar rodadas.
- Orcamento de VRAM se le da ROM (SpriteDefinition.maxNumTile e TileSet.numTile via symbol.txt), nao dos PNGs.
- A reserva fixa do corpo usa o maior sheet de EFEITO (147), nao o de corpo (102): 90 tiles possivelmente recuperaveis.
- A sonda de runtime media a si mesma (~10% do quadro); perfilar por amostragem de PC via H-Int, nao por getSubTick.

## 2. Pendencias atuais

- Contexto `technical_demo` validado em planning/implementation e higiene aprovada (0 blockers). Metodologia tem um blocker: `perceptual_motion_unvalidated`, sem os quatro eixos positivos vinculados a candidata integrada.
- Fonte Hadouken e slot 6 (`0xE82`) receberam aprovacoes distintas. A candidata `750,1` exata, SHA `89425892906b151b15ea32345737f0f9653440e8810858b3e2c3f0e07a8b3e9f`, foi aprovada com paridade visual pelo usuario e integrada apenas na worktree isolada de prova; as outras poses AIR continuam sem aprovacao e nenhuma promocao para a ROM principal ocorreu.
- Build isolado normal SHA `52311f4f84d37887cecbe766055bff236794f073d3997f8c53355eacf11912aa` e ROM de teste de evento SHA `794dd6e8ffbf45f96cb744dd2cbfe19730bcddba7dc9c304e307376db0ff4398` foram observadas/seladas no BlastEm para a mesma ROM de teste. Slot 6 `0xE82` esta configurado em PAL1/PAL2 nas 12 variantes. A captura normal mostra o projétil em voo e a transicao para flash no impacto.
- Sonda CRAM separada SHA `9ce731d5ba7d48d69e277f3116b198c55a7522fc37136fd641ff4b3f35efd46c`, bundle BlastEm `out/mugenesis_evidence/flash_projectile_cram_probe_frozen/sessions/blastem-linux-20260925T130718Z-45717`: test-only ROM disparou o Hadouken real, ativou `flash_lvl[0]=3` quando `proj[0].active` e congelou a simulacao mantendo a renderizacao. O SRAM registra `CRAM`, flash 2 apos render, projetil ativo 1, `removing=0`; o screenshot mostra lutador PAL1 e projetil clareados na mesma captura. Isso confirma compartilhamento de CRAM em estado simultaneo, mas nao um impacto natural nem a cadencia real do flash em gameplay.
- `palette-check` apos o piloto em copia isolada segue FAIL: 24 cores exatas para 15 slots (excesso de 9); o estado pre-piloto era 23/15 (excesso de 8). As demais familias continuam fora do escopo desta aprovacao.
- Matriz Stage 3 das quatro variantes tem janelas de 1200 quadros comparaveis, mas todas ficaram em 250/1200 acima do budget. O flash foi visto; a atribuicao isolada do transiente ao shake continua pendente. Nao ha claim de 60 fps sustentado, AAA ou qualidade audiovisual.

### Atualizacao 2026-09-25 — paleta e candidato AIR Hadouken

- Slot 6 compartilhado aprovado pelo usuario: `0xE82`, RGB de autoria canonico `(34,136,238)`. Escopo: escolha da cor somente; evidencia em `doc/mugen/fx_pilot_hadouken/slot6_user_approval_2026_09_25.md`.
- Candidatos tecnicos dos cinco sprites Hadouken estao somente em staging; AIR 750/751 mantem os oito elementos, tres vazios, timings/offsets/axes e hitboxes. Contato/preview/hash e medicao ResComp em `doc/mugen/fx_pilot_hadouken/candidate_sequence_slot6_e82_report.json`. O contato 1x mostra candidato mais claro e com rampa azul mais achatada; aprovacao visual hash-bound pendente. `forge_art.pixel_contract` valida sintaxe 4bpp/PLTE/alpha de 5/5 sem blockers; `forge_art.vdp_color --self-check` e `pixel_contract --self-check` passaram 20/20 cada. Reconstrucao em copia isolada reproduziu os 5 PNGs byte a byte. Isso nao aprova visualmente a sequencia.
- `palette-check` pre-piloto no Ken de producao: 23 cores exatas requisitadas para 15 slots (14 classes de corpo + 9 classes FX); excede 8. Nao inclui candidatos em staging e deve ser repetido apos integracao aprovada.
- Medicao ResComp `BALANCED FAST`: 750,0..4 = 24/28/12/8/16 tiles e 2/2/1/1/1 sprites. 750,1 excede 26 tiles. `TILE FAST` atinge 22/26 tiles nos dois primeiros quadros, mas exige 3 sprites; `BALANCED MEDIUM/SLOW` e `TILE MEDIUM` chegam a 25 tiles/3 sprites; `SPRITE MEDIUM/SLOW`, `TILE SLOW` e `NONE FAST` medem 28/2. Sweep de 13 combinacoes (inclui BALANCED MAX=25/3 e SPRITE/TILE MAX=28/2) nao encontrou estrategia que atenda ambos os tetos; AIR e probes isolados estao identificados em `candidate_sequence_slot6_e82_report.json`. A compilacao da sequencia preserva 8 frames, vazios e timers. A integracao continua bloqueada ate decisao sobre arte/contrato de budget. Nao mexer em `res/`, build/ROM/BlastEm pendente. Stage 3 continua uma trilha independente.

### Atualizacao 2026-09-25 — obstaculo de budget Hadouken superado em staging

- A busca exaustiva de dois retangulos de sprite sobre os pixels atuais confirmou custo minimo de 28 tiles sem mudar a silhueta. Uma variante altera somente cinco pixels perifericos do indice 6 em 750,1: `(22,3)`, `(23,3)`, `(21,28)`, `(22,28)`, `(23,28)`, todos para indice 0. Preserva 1149/1154 pixels opacos (99,5667%), nucleo escuro e celula 56x32. SHA-256 da variante: `89425892906b151b15ea32345737f0f9653440e8810858b3e2c3f0e07a8b3e9f`.
- A variante se divide em duas definicoes de sprite com posicionamento na celula `(0,4)` e `(24,0)`. ResComp 3.95 compilou 9 tiles/1 sprite e 16 tiles/1 sprite, total simultaneo **25 tiles/2 sprites**, dentro do teto 26/2. A composicao dos PNGs recortados reproduz exatamente a variante; `forge_art.pixel_contract` aprovou os tres arquivos sem blockers. O efeito isolado atinge no maximo 2 sprites e 56 pixels por scanline H40; custo combinado da cena continua sem medicao. Recurso, assembly e hashes no `doc/mugen/fx_pilot_hadouken/budget25_split_report.json`.
- A nova variante recebeu aprovacao visual do usuario vinculada ao SHA em `budget25_user_approval_2026_09_25.md`; a aprovacao da fonte e do slot 6 seguem como decisoes distintas. O conflito de custo foi resolvido apenas em `750,1`; os demais quadros seguem no estudo anterior, sem alterar AIR, offsets, pivots, hitboxes ou timings. A integracao ainda depende de confirmar e executar a protecao de proveniencia da PR21 nesta branch. Nenhuma alteracao em `res/` ou build integrado foi feita nesta retomada.
- Aprendizado local capturado em `doc/agent_learning/`: 47 licoes, 30 candidatos; a nova proposta ficou `human_review_required` e foi encaminhada ao owner visual existente. `canonical_promotion_performed=false`.
- Continuidade da integracao: PR #21 permanece aberta no commit `f3b92bb9`, separada da PR #22/branch `feat/mugenesis-impact-fx-v2` no HEAD `7cf00ed8`. Seus 4 testes `test_provenance_preserve.py` passaram em worktree isolada. Isso confirma a protecao no checkout da PR21, nao nesta branch. A simulacao de merge aponta conflitos documentais em changelog e indices de curadoria; nao houve merge, reconversao de producao nem mudanca em `res/`. Proximo gate: integrar a protecao em worktree dedicada, reconciliar os conflitos preservando Stage 3, repetir os testes e fazer conversao em copia antes de qualquer promocao do piloto.

## 3. Regra de continuidade

Atualize este arquivo, o changelog e os manifests sempre que a verdade
operacional mudar. Nunca copie hashes, builds, aprovacao ou evidencia do modelo.

- **Hadouken 750,1 em ROM de teste isolada (2026-09-25):** no worktree `/tmp/sgdk-mugenesis-pr21-pr22`, o candidato aprovado SHA `89425892906b151b15ea32345737f0f9653440e8810858b3e2c3f0e07a8b3e9f` foi integrado em dois sheets e reconstruído exatamente; ROM candidata preliminar (depois supersedida: index 6 ainda era zero) SHA `18e14682263e4ce6acbd475d451e3cbdde63fbf2d1c29a0ac795e9060f85fca8`. ROM separada de teste de entrada Hadouken SHA `68d3ee9064f1f14097aaa947fa52b0d5f58885313ffa8bba91438b20657beb24` observada no BlastEm, bundle `out/mugenesis_evidence/hadouken_750_1_fireball/blastem-linux-20260925T103514Z-3548982`; frames 60/61 mostram a pose aprovada e o projétil em voo, em paridade visual com a candidata aprovada. Captura de 90 quadros, áudio dummy; não prova cadência sustentada nem qualidade de áudio. Aprovação segue limitada a 750,1: AIR completo, demais poses, pressão de pixels por scanline da ROM de teste não foi exportada; a captura registrou no máximo 9 sprites/linha, max CPU 146 e 897/1200 amostras acima do budget. Cadência sustentada, AIR completo e metodologia perceptiva continuam pendentes. Relatório: `rascunho/processado/fx_pilot_hadouken/isolated_integration_report.json`.

- **Limites do piloto Hadouken (2026-09-25):** `palette-check --project . --id ken` segue 23/15 (excesso de 8 por nove cores FX sem gemeo estavel); outras familias mantêm o blocker global. A sequencia candidata preserva 8 elementos/3 vazios, mas so o hash 750,1 está aprovado. Duas capturas de tentativa de flash com projétil ativo nao mostraram projétil (combo/contato corpo a corpo); a atribuicao de interação CRAM permanece inconclusiva e o ciclo de entradas foi encerrado após duas tentativas. Proximo passo: desenhar gatilho deterministico baseado no estado interno do projétil ou deixar esta prova pendente, sem inferir isolamento.

- **Suite depois da integracao isolada (2026-09-25):** 65 passed / 9 failed / 0 skipped. Oito falham ao tentar spawn do `build_host.sh` (modo git 100644, nao executavel); uma falha porque o fixture estrutural espera slot 6 ja livre (14 indices), enquanto o estado medido tem 15 indices com remap 15->6 apenas calculada. Nenhuma expectativa mudou. Detalhes no relatorio `rascunho/processado/fx_pilot_hadouken/isolated_integration_report.json`.

### Atualizacao 2026-09-25 — paridade confirmada e captura de paleta corrigida

- O usuario confirmou que a estrategia de remocao localizada de cinco pixels e decomposicao 24x24/32x32 foi bem-sucedida e manteve paridade visual. A decisao e hash-bound somente a `750,1`; registro visual em `doc/mugen/fx_pilot_hadouken/budget25_user_approval_2026_09_25.md`.
- A captura anterior (ROM `68d3ee90…`, frames 60/61) foi supersedida: as doze variantes de PAL1/PAL2 ainda tinham `index 6 = 0`, portanto nao comprovavam o azul aprovado. Com `0xE82` aplicado em todas as variantes, o ROM candidato normal tem SHA `52311f4f84d37887cecbe766055bff236794f073d3997f8c53355eacf11912aa`; ROM de evento com `MG_TEST_SCRIPT`/`MG_TEST_FIREBALL` SHA `794dd6e8ffbf45f96cb744dd2cbfe19730bcddba7dc9c304e307376db0ff4398`. Bundle BlastEm selado `out/mugenesis_evidence/hadouken_750_1_palette_corrected/blastem-linux-20260925T115621Z-3988558`, manifest SHA `f5c0ed7243c2ee41a74fd3598558198f75770d948bd800d4a0009ab7b8b903c2`; o `rom_sha256` confere com a mesma ROM observada.
- Frames 64/66 mostram o projétil azul do slot 6 em voo; frame 75 mostra-o chegando ao Ken de P2 e frame 76 mostra o flash do impacto depois de o projétil desaparecer. A transicao esta observada, mas nao e prova de projétil e flash simultaneos no mesmo quadro. O proximo diagnostico usa posicao e inputs fixos em ROM test-only, com o projétil ativo na linha PAL1 enquanto P2 acerta P1.
- Auditoria de proveniencia na copia integrada: 127 simbolos visuais, zero bloqueios. Hygiene passou apos remover tres diretorios de build temporarios que haviam sido criados na raiz daquela worktree. `validate_resources` segue com 12 erros/20 avisos, incluindo manifestos/metadados pendentes e sprites grandes preexistentes; isso nao foi tratado como verde.
- A suite `python3 -m pytest tools/mugen2sgdk_forge/tests -q -ra` passa com 70 testes na worktree principal apos o runner de `build_host.sh` passar a ser chamado via `bash`; asserts nao foram alterados. Esta suite nao exercita os assets integrados na worktree temporaria. A verificacao anterior 65/9 da copia stale permanece como historico, nao como resultado atual.
- Aprendizado local foi atualizado em `doc/agent_learning/success_patterns.md`; capturar/auditar o ledger segue obrigatorio antes de encerrar este ciclo. `canonical_promotion_performed=false`.

### Atualizacao 2026-09-25 — paridade e interferencia de paleta observadas

- O usuario confirmou explicitamente que a estrategia local teve sucesso e manteve a paridade visual. Essa aprovacao continua limitada ao candidato `750,1` com SHA `89425892906b151b15ea32345737f0f9653440e8810858b3e2c3f0e07a8b3e9f`; nao promove as demais poses da sequencia.
- A prova CRAM usa ROM separada com `MG_TEST_SCRIPT`, `MG_TEST_FLASH_PROJECTILE` e `MG_TEST_DISABLE_STAGE3_SHAKE`. Apos o disparo real, injeta flash nivel 3 so quando o projétil P1 esta ativo e congela a simulacao para permitir a captura; nao dispara HitDef. O estado selado e `flash_lvl=2`, `projectile.active=1`, `removing=0` em SRAM `out/mugenesis_evidence/flash_projectile_cram_probe_frozen/sessions/blastem-linux-20260925T130718Z-45717/save.sram` (offset `0x1F00`, assinatura `CRAM`). Screenshot sem shake: `out/mugenesis_evidence/flash_projectile_cram_probe_frozen/canonical/screenshot.png`. A paleta do Ken P1 e do projetil em PAL1 fica visivelmente mais clara, enquanto P2 permanece normal; comparativo normal em `out/mugenesis_evidence/hadouken_750_1_palette_corrected/blastem-linux-20260925T115621Z-3988558/animation_frames/frame_64.png`.
- Esta sonda prova a interferencia visual de CRAM partilhada com um projétil ativo; nao prova que um hit natural ocorre ao mesmo tempo, nem timing de gameplay, cadencia sustentada, 60 fps ou qualidade de audio. O window-title mediu 59.5 fps como snapshot; `performance_claim=unproven`. Audio dummy, 0 bytes.
- Artefatos e roteiro: ROM de sonda SHA `9ce731d5ba7d48d69e277f3116b198c55a7522fc37136fd641ff4b3f35efd46c`; manifest SHA e screenshot SHA em `out/logs/hadouken_flash_projectile_cram_probe.json`; patch test-only SHA `2bb71efeb069fe2288fd60ab230a36905277b961ea43f37048617ec274b9992a` em `rascunho/processado/fx_pilot_hadouken/flash_projectile_cram_probe.patch`.
- `palette-check` integrado continua FAIL em 24/15, excesso de 9. Auditoria de proveniencia na worktree integrada: 127 simbolos, 0 bloqueios; hygiene: 0 bloqueios apos a limpeza dos diretorios de build temporarios; `validate_resources`: 12 erros/20 avisos. Suite do workspace principal: 70 passed/0 failed/0 skipped, com asserts intactos; nao foi executada contra a copia integrada temporaria. Relatorio: `rascunho/processado/fx_pilot_hadouken/isolated_integration_report.json`.
- O padrao de sucesso foi atualizado para curadoria futura em `doc/agent_learning/success_patterns.md`; ainda deve passar pelo capture/audit local. `canonical_promotion_performed=false`.

- **Suíte e idempotência da integração isolada (2026-09-25):** worktree PR21+PR22: `74 passed / 0 failed / 0 skipped`. Os três launches do `build_host.sh` no teste de host agora chamam `bash`, sem mudança de asserts; a expectativa estrutural do Ken foi atualizada para o estado medido pós-piloto (15 índices usados, 9 classes estáveis + 6 variáveis, 24/15 e excesso 9), mantendo o teste de falha global. Duas reaplicações do helper `apply_approved_750_1.py` retornaram `already_applied`; hashes de `.res`, C gerado, manifesto, contrato de paleta e dois sheets permaneceram idênticos. A suíte base da workspace principal segue registrada separadamente: 70/70. Relatório detalhado: `rascunho/processado/fx_pilot_hadouken/isolated_integration_report.json`.
- **Curadoria local (2026-09-25):** Capture/Audit em `doc/agent_learning/` ficou `learning_context_present` sem blockers nem warnings: 48 lições, 30 candidatos; a proposta `lesson_9e62ed31b1a9f329` aguarda revisão humana para possível ajuste de `visual-excellence-standards`. Nenhuma mudança canônica foi aplicada.

## Fechamento tecnico desta rodada (2026-09-25)

- ROM isolada final SHA-256 `f5eb26a3b057c3439c344aa9d8863386dc6eb9662dc3f20ebe7356aee0b62d1d`, identica ao bundle BlastEm `out/hud_review_2026_09_25/normal/blastem-linux-20260925T144223Z-420049/`. A sonda de estado do HUD usa ROM separada `24183495bb4e43fefbc3447ca53db9bb05cfd24773e1bc0128b8ec75e75ba871`, em `out/hud_review_2026_09_25/probe/blastem-linux-20260925T144644Z-432661/`; nao comprova gameplay natural, FPS sustentado ou audio.
- Os 19 PNGs finais do HUD foram sincronizados da compilacao isolada; `rascunho/processado/hud_review_2026_09_25/integration_receipt_v2.json` registra os hashes. Todos passaram no `pixel_contract` como `technical_candidate`, sem blockers. O retrato usa PLTE no grid autoral 0x22, transparencia do indice zero e mascara do sprite fonte.
- `validate_resources` anterior encontrou 14 erros e 20 avisos em 123 recursos: 11 limites de sprite preexistentes e tres status bloqueados. Nenhum recurso `mg_hud` causou erro; o gate global permanece reprovado. O retrato precisa de moldura nativa desenhada e avaliacao estetica; a imagem gerada em alta resolucao e apenas conceito.

## 2026-09-25 — curadoria e coordenacao da continuidade MUGEN

Pedido humano autoriza curadoria e planejamento da continuidade SGDK/SMS.
Parecer canonico por ID em `doc/curation/2026_09_25_mugen_coordination/` do
workspace: 24 instrucoes pendentes promovidas com qualificacoes; nove
formulacoes nao promovidas/corrigidas; sete aprendizados novos; cinco
promocoes anteriores preservadas. Ledger herdado nao foi promovido em bloco.
Prompts novos em `doc/prompts_modelo/prompt_mugen_sgdk_completion_2026_09_25.md`
e `prompt_mugen_sms_port_2026_09_25.md` no workspace. Escopo ampliado pelo
usuario inclui cenario/musica no SGDK; executor deve sincronizar contexto/GDD
antes da producao. Esta rodada nao alterou gameplay/ROM nem executou uma nova
aprovacao audiovisual. Instrucoes SMS sao plano, nao port implementado.

## 2026-09-25 — executor: checkpoint, escopo ampliado e protecao de proveniencia

Rodada do prompt de conclusao da demo (anexo `prompt_mugen_sgdk_completion_2026_09_25.md`).
Branch `feat/mugenesis-impact-fx-v2` @ `7cf00ed8`; 54 itens WIP preservados; sem commit/merge/push.

- **Baseline medida nesta branch (nao copiada de docs):** suite conversor `74 passed / 0 failed` (88,9s); `palette-check` Ken **FAIL 23/15** (14 indices corpo, slot 6 livre, 11 FX exatas, estoura por 8, `lossless_merges={}` aqui); `validate_resources` `14 erros / 20 avisos`, `closeout_gate=False`; `out/rom.bin` = `595116bc` (flash-only Stage3, superseded).
- **Escopo ampliado registrado:** `project_intent` do manifesto de contexto atualizado para demo completa de combate com cenario+audio; `context_type` e `delivery_claim_ceiling` permanecem `technical_demo` ate gates AAA medidos. Backlog operacional criado em `doc/mugen/completion_backlog.json` (itens A1–F1 com dependencia, criterio de aceite, owner, evidencia, proxima acao).
- **A1 fechado.** Classificacao dos 14 erros por causa (A3): 11x `VDP_SPRITE_LIMIT` (g42/g270/g272/g745_fx/g760_fx/g810 ~20; super g8000_0/1/p1_0/p1_1/p2_fx 32–64 sprites >16) = trabalho de arte/contrato da Etapa B com aprovacao humana por familia, nao waiver/metadado; 1x `res_graph` ausente; 2x `claim_reconciliation` (`report_rom_identity_mismatch` + `report_status_conflict`) por report apontar ROM != flash-only atual. Root comum: falta build de producao limpo de fonte reconciliada.
- **A2 — protecao de proveniencia INTEGRADA no working tree** (autorizacao humana explicita, opcao 'aplicar ao working tree', SEM commit/merge/res/producao). Cross-control em worktree isolado: `provenance.py` da PR21 `f3b92bb9` sobre HEAD → 4/4 `test_provenance_preserve.py` PASS; `provenance.py` atual → 4/4 FAIL (`no attribute load_annotations`) = protecao estava genuinamente ausente. Aplicado `provenance.py` (+112/−3) + arquivo de teste; suite completa com WIP impact-FX = **78 passed / 0 failed** (46,9s), zero regressao. Coberto: nota humana/restricao sobrevivem e rerun idempotente, pixel novo nao herda aprovacao, simbolo removido fica no historico, edicao manual capturada nao perdida.
- **Pendencias A2 (nao iniciado; exigirao copia + preflight de memoria, host ~3,3 GiB):** fix-provenance do manifesto em copia (o `asset_provenance_manifest.json` esta entre os 54 WIP — nao migrar na producao); reconversao idempotente em copia provando que `750,1` (SHA `89425892906b151b15ea32345737f0f9653440e8810858b3e2c3f0e07a8b3e9f`) sobrevive byte a byte; reconciliar changelog/curation PR21+PR22 antes de qualquer commit/promocao.
- **A2 verificado em copia controlada (2026-09-25):** `/tmp/mugrecopy` (excluiu `out/`; producao intocada — manifesto real segue `377482ae`, sem `provenance_annotations.json`). `convert-char` nao usa Wine/ResComp (unico `subprocess` no conversor e git), entao o teste e leve. Resultados: (1) IDEMPOTENCIA — run#1==run#2 byte a byte nos 125 arquivos regeneraveis+proveniencia; (2) MIGRACAO S0->S1 tocou s6 2 arquivos (manifesto `377482ae`->`6eb0342c` + `provenance_annotations.json` criado `b44736e0`), pixels/C intactos; (3) SOBREVIVENCIA — nota humana injetada em `mg_ken_portrait.human_notes` sobreviveu ao run#3 e foi capturada no manifesto (`8c234fe7`), pixels idempotentes. Recibo reproduzivel: `rascunho/temporario/reconversion_copytest/receipt_2026-09-25.json`. Candidato aprovado `750,1` confere SHA `8942589…` em `rascunho/processado/fx_pilot_hadouken/candidate_750_1_slot6_e82_budget25.png`; zip-fonte Ken `822936f0` confere hygiene. Falta ao humano: commit da integracao (2 arquivos de tooling) + reconciliar changelog/curation PR21+PR22 antes de migrar `fix-provenance` na producao ou promover o piloto. Etapa B pode comecar sob o contrato de protecao verificado.

- **Nada** de `res/`, ROM de producao, gameplay, capture BlastEm ou aprovacao audiovisual foi alterado/promovido nesta rodada.

## 2026-09-25 — Suzaku: medicao de conversao sem promocao

- A fonte `ssf2_01_ryu.zip` (SHA `d781b8d5...23fb96`) foi aberta e medida;
  `stage-candidate` gera apenas vistas tecnicas indexadas e relatorio em
  `rascunho/processado/stage_takeover/v1/`. O parser exige paleta SFF comum e
  sete camadas nomeadas; ainda nao e conversor generico de stage MUGEN.
- Corrigido o subdimensionamento de largura: camera 448 px com deltas
  aproximados .43/.67 exige BG_B 520 px e BG_A 624 px, nao ambos 512.
  Resultado atualizado: 689+679 tiles por vista, uniao 1366; por janela
  simultaneamente visivel 697..845. A reserva medida da ROM congelada e
  446 tiles com emprestimo bgfx e sprite pool 600 na ROM atual `05a27a06...`.
  O valor anterior 452 pertencia a ROM anterior. Logo o candidato esta
  `blocked_budget`; nenhuma copia a `res/`, build, emulador ou aprovacao.
- PAL0 provisoria conserva sete cores do HUD em 9..15 e escolhe oito cores
  de stage em 1..8. Isso recolore 55,7%/69,0% dos pixels visiveis das
  duas vistas; a aparencia 1x e somente referencia de direcao.
- O plano `doc/mugen/stage_suzaku_route_2026_09_25.md` define storyboard,
  modulos autorais, comparacao residente/streaming/controle flat, medicao
  compilada e prova de restauracao do super. D1 passou a pre-producao medida;
  D2/D3, musica, validacao de recursos e cadencia final continuam abertos.
- Licao para o workflow: uma vista 4bpp com paleta valida pode ocultar um
  estouro de VRAM, e um crop insuficiente pode esconder o custo da borda.
  Exigir largura derivada de camera+delta, pior janela visivel, custo
  compilado e inspeccao 1x antes de admitir um asset de cenario.
- Build normal a partir da fonte atual passou pelo wrapper: ROM SHA-256
  `05a27a0612522b6909c7089019c5164870b744e4657773888aec7d2654fef3f8`.
  `fight_vram` nesta ROM encontrou HUD 142 tiles, 174 livres e 446 incluindo
  o emprestimo bgfx de 272. Controle central achatado `IMAGE BEST` compilou
  719 tiles pelo ResComp 3.95, fora do budget e sem parallax; nao entrou no
  jogo. A captura BlastEm `out/stage_takeover_audio_menu/` mostra luta com
  fundo solido. `target_scene=2` nao selecionou menu porque `APP_boot` define
  `MG_DIRECT_FIGHT=1` por padrao. O arquivo de audio dessa captura nao e
  prova de BGM. Nenhum claim de 60 fps/audio final.
- `AUDIO_playCue` deixou de chamar `AUDIO_stopAll` nos cinco cues PSG simples;
  isso evita desligar a trilha FM em navegacao/menu, mas falta build especifico
  de menu, comparacao auditiva antes/depois e faixa de luta original.
- Perfil isolado `-DMG_DIRECT_FIGHT=0` buildou ROM SHA
  `1898bdc77f31077a7488f409ef8f87a93d644ee1e98fce0d8e411ee59f24d1f2`.
  Captura BlastEm `out/stage_takeover_menu_probe/blastem-linux-20260925T213409Z-275674`
  mostrou o menu, SRAM `scene_id=2` e `audio.raw` nao vazio. Nao houve input
  de menu, escuta qualificada nem teste de loop; BGM segue `needs_review`.
- O runner `capture_blastem_evidence_linux.sh` agora valida target_scene contra
  `runtime_metrics.vlab.scene_id` antes da publicacao canonica. A captura
  anterior pedindo 2 mas observando 3 reprova; o menu real passa. Três testes
  dirigidos cobrem match/mismatch/ID ausente. A ponte `.agents/skills` estava
  como copia rastreada obsoleta (34 arquivos vs 159 na fonte canonica); a copia
  foi preservada em `out/agent_bridge_backup/skills_2026_09_25`, substituida
  por symlink e `assert_agent_environment.ps1` confirmou ambiente pronto.
- `validate_resources.ps1 -CloseoutGate` na ROM atual fechou com **27 erros,
  7 avisos**: 11 sprites acima do limite e 16 status bloqueados. O gate
  perceptivo, GDD substancial, arte visual, audio, evidencia stale e relatorios
  de cena ainda precisam de trabalho. O erro da ponte foi corrigido depois
  desta medicao; nao apagar os demais por causa dela.
- VGM do branding/menu: builder escrevia `total_samples`, `loop_offset` e
  `loop_samples` quatro bytes depois do especificado. Corrigido o builder e
  regenerado `res/music/forge_brand_loop.vgm` SHA `7a65bfa6...`; teste novo
  fixa cabecalho VGM 1.70, loop absoluto `0x100` e comprimento valido. ROM
  de menu separada SHA `f08d3fcd...` compilou e foi capturada em BlastEm.
  Comparacao longa com a ROM anterior (`1898bdc7...`) mostrou audio float32
  nao nulo em ambas ao longo da janela de menu (`scene_id=2`, 1411 frames);
  logo a captura NAO prova que o cabecalho antigo causava silencio nem que a
  juncao do loop esta perfeita. Escuta/cue continuam pendentes.
- O rebuild final da branch (apos regenerar VGM) gerou ROM principal SHA
  `200346548a57cb6196cf21773c9233bd53b72b02e1bdf7f6548fd3331aa81c2c`.
  BlastEm selado em `out/stage_takeover_fight_latest/blastem-linux-20260925T215732Z-346516`
  observou `scene_id=3` e fundo ainda solido. `fight_vram` desta ROM mantem
  174 tiles livres/446 com emprestimo. Foto unica e 32 amostras de VLAB nao
  provam 60 fps sustentado nem entrega do cenario.
- `res_graph_audit.ps1` percorria rascunhos e contou 11 `.res`/484 issues,
  maioria duplicatas falsas. A descoberta padrao foi corrigida para `res/`
  ativo; teste confirma `-ResPath` para drafts. Novo laudo:
  `out/logs/res_graph_report.json`, 3 `.res`, 161 declaracoes OK, 1 aviso
  `code_loaded_tiles_unmeasured`. Isso nao valida residencia real.
- `validate_resources.ps1` acusou link relativo de `.agents/skills` como
  mismatch porque resolveu contra cwd do projeto. Corrigido para resolver
  contra a pasta da ponte; manter link relativo portavel. A execucao de
  closeout anterior, antes da correcao, registrou 28 erros/7 avisos,
  incluindo ainda um `.pytest_cache` do teste VGM na pasta de fonte; esse
  cache foi removido. Revalidacao completa e gate AAA ainda pendentes.

## 2026-09-25 — Sonda SRAM da residencia do sprite pool

- ROM diagnostica SHA-256 `37fd9eb8e35464262bec4fa876c6ef0ff19d96d7678125152e42c534ae44ac11`, capturada no BlastEm em `out/stage_takeover_vram_stress/blastem-linux-20260925T225314Z-558452`; SRAM, VDP dump, screenshot e runtime metrics selados.
- Estado: dois Ken em potencia maxima, P2 AI ativo, `SPR_initEx(600)`, sem stage e audio dummy. SRAM somou 2.941 amostras: minimo247 tiles livres, maior bloco contiguo72, pico11 sprites ativos, zero falhas.
- Conclusao limitada: free total nao mede o maior pedido contiguo; nao diminuir pool de producao com base nesta sonda. Sem stage/audio e com 116/1200 quadros acima do budget, o snapshot 59,9 fps nao prova cadencia sustentada.
- Relatorio `doc/mugen/vram_residency_probe_2026_09_25.json`; arquitetura e rotas ainda abertas em `doc/mugen/stage_architecture_record_2026_09_25.json`. Nenhum recurso entrou em `res/`, nenhuma paleta/cena foi aprovada.
- Licao para o fluxo: overlays de debug podem contaminar a medicao; medir por pares com mesmas flags/estado e registrar `SPR_getLargestFreeVRAMBlock()` junto ao free total. O A/B ainda nao foi isolado com paridade perfeita.

## 2026-09-25 — Cobertura de animacao e H-scroll no Suzaku

- `stage_measure.py` agora mede layers `type=anim`: frames AIR, sprite refs, duracao/ciclo, offsets e flips, tiles/pixels por frame, refs ausentes e janelas `BGCtrl Enable`. `stage-measure --crop-top 16` gerou `rascunho/processado/stage_takeover/suzaku_measure_v2.json` (SHA `b357e7e252337c01b521cdc68981ac25489d15adae34e0dd15507e5d99012257`) a partir do pacote de fonte SHA `d781b8d5...`.
- Suzaku tem tres camadas BG5 usando 51 frames/278 ticks, nove padroes compartilhados; os eventos IDs 51/53/52 cobrem 900–1178, 1778–2056, 3086–3364 em ciclo BGCtrl 3364, sem sobreposicao e com duracao coincidente.
- Crop provisório16 deixa as camadas frontais em bandas sem lacunas: BG3 `[0,176)`, BG4a `[176,212)`, BG4b `[212,224)`, deltas 0.671875/0.792410/1.102678. HSCROLL_LINE BG_A e uma rota candidata; SGDK 2.11 expoe `VDP_setHorizontalScrollLine` e recomenda DMA_QUEUE, mas runtime/owner/DMA continuam por projetar e provar.
- Padroes fonte nao vazios com flip: frente 700 sem reuse; fundo 1.021 unicos apos 378 reusos entre quatro layers (ou 959 sem fallback tiled BG0a); nao sao custo ResComp nem viewport. BG_B segue com conflito de delta entre camadas sobrepostas. Stage continua pre-producao, sem asset em `res/` e sem ROM com Suzaku.
- Targeted tests: `test_stage.py` + `test_stage_candidate.py` = 18 passed; suite completa de `tools/mugen2sgdk_forge/tests` = 90 passed/0 falhas. Schemas TDD/camera/technique passam; `validate_project_context` e hygiene passam; project methodology permanece bloqueada pelo review perceptivo humano do Hadouken. `validate_resources` foi regenerado: 14 erros/20 avisos. Freshness tem zero obrigatorios ausentes, mas uma evidencia antiga de emulador (e o `validation_report` passa a stale quando freshness e gerada depois); nao fechar gate por isso. Sem build/emulador porque esta rodada atualizou medicao/contratos de tooling, nao runtime nem assets ativos.
- Correcao de palette helper: stage-candidate agora usa `vdp_rgb` canonico e testa RGB primario, branco/preto e todas 512 palavras. Embora o helper anterior decodificasse canais/escala errado, a transformacao comum no espaco da distancia quadratica manteve o vizinho mais proximo; PNGs/paleta/tile counts v1/v2 permaneceram identicos. A causa do aspecto sem brilho nao foi comprovada como esse bug.
- Contratos locais criados: `doc/tdd_contract.json`, `doc/camera_behavior_contract.json` e `doc/technique_usage_manifest.json`; `doc/15-tdd.md` e Cena2 em `doc/13-spec-cenas.md` sincronizados. Eles registram HSCROLL_LINE/camera como planejamento, world768 como proposta, BG_B/paleta/budget como blockers; nenhuma tecnica foi promovida e nenhum C/runtime/res foi alterado.

## 2026-09-25 — Viewport Suzaku: parallax e semantica de transparencia

- `stage-bands` percorreu as 449 posicoes inteiras e mediu BG3 `[0,176)`, BG4a
  `[176,212)` com `xscale` interpolado de 0.792410 a 1.091517833, e BG4b
  `[212,224)`. O arredondamento nearest-even ainda nao foi comparado com MUGEN
  em execucao.
- Mapa frontal: 816 px/102 colunas; 64 colunas nao cobrem o percurso, 128 cobrem
  e usam 8 KiB de nametable. Padroes fonte por viewport: 299-460 (pico nas
  cameras 10/11), 796 distintos ao longo do curso. O pico ultrapassa em 14 o
  budget de palco estimado de 446 antes de BG_B.
- A candidata de paleta reduz o pico a 431, mas altera cerca de 69% dos pixels,
  deixa somente 15 tiles para BG_B/reservas e nao foi aprovada. Camera provisoria
  4 px/frame implica lower bound de ate 9 padroes novos/288 bytes, sem
  tilemap/DMA/cache/VBlank.
- Correcao factual: color code 0 nos planos A/B do Mega Drive e transparente e
  revela a camada inferior. Logo, `BG 3 mask=1` pode ser reproduzido pela
  transparencia de plane. Nas 449 posicoes das bandas frontais nao foi visto
  indice 0 opaco; zero visivel de uma layer MUGEN sem mascara ainda precisa de
  remapeamento para indice MD nao zero. Base: Genesis Software Manual, rev.
  1992-02-20, p.62; nota local hash-bound em `rascunho/entrada_bruta/`.
- O blocker de parallax corrigido e o numero de velocidades simultaneas: a
  composicao estatica excede dois grupos horizontais em 72/32/72 scanlines nas
  cameras left/center/right, maximo quatro. BG_A/B assignment nao foi modelado.
- `stage-plane-tradeoffs` escolheu um par por linha agregando as cameras: 19.655 /
  215.040 amostras de pixel (9,14%) mudam de velocidade; erro medio estimado
  0,04105 px/pixel/frame, maximo 0,803572 em y=62. Do anchor x=224 ao extremo,
  drift medio estimado 2,10254 px/pixel e maximo 45 px em y=62/BG3. E piso
  matematico, nao aceitacao: atribuicao muda por linha e pode gerar costuras.
  Previews fonte
  diferem por 9.625/0/6.356 indices (left/center/right), ainda sem aprovacao.
- Relatorios `suzaku_front_banded_hscroll_v1.json`,
  `suzaku_static_source_view_v1.json`,
  `suzaku_two_plane_scroll_tradeoffs_v1.json` e
  `suzaku_two_plane_scroll_candidate_v1.json` sao analise de fonte, nao ResComp,
  ROM, aprovacao visual ou prova de DMA. Nenhum asset entrou em `res/`; runtime e
  ROM nao mudaram neste trabalho.
- Suite completa do conversor: 103 passed. Higiene e contexto de implementacao
  passaram. O validador metodologico permanece bloqueado somente por
  `perceptual_motion_unvalidated`, que exige sinais perceptivos e aprovacao
  humana ausentes; nao houve waiver nem claim de movimento validado.
- Apos atualizar o adendo do Suzaku, `scene_contract_compiler.ps1 -Mode lab
  -WarnOnly` foi executado: 3 cenas compiladas, lint `ok`, nove achados apenas
  informativos. `scene-contracts.json` foi regenerado; o adendo Suzaku permanece
  pre-producao, sem runtime scene id proprio.
- A freshness anterior detectou `scene_contract_compile` e `emulator_session`
  stale; a compilacao foi refeita. A sessao velha aponta para ROM de teste
  Hadouken `68d3ee90...`, enquanto `out/rom.bin` atual e `20034654...`; nao prova
  a ROM atual. Auditoria final de freshness apos a compilacao ainda pendente.

## 2026-09-25 — Sweep integral e escolha de velocidade do Suzaku

- `stage-source-view --sweep-camera-step 1` percorreu as 449 posicoes inteiras
  da camera e agregou 32.184.320 amostras de pixels por velocidade/scanline sem
  reter 449 rasterizacoes. Fonte SHA `d781b8d5...23fb96`; report SHA
  `bd8060753db6c987f876070e5b7e4594cad0a4f1f10f561b99ca588367e8524e`.
- Comparacao justa no sweep completo: perfil discreto (preserva dois deltas da
  fonte) remapeia 1.618.094 amostras/5,03%, media de erro 0,02415 px/amostra/
  frame, drift medio desde camera224 de 0,95527 px/amostra e maximo45 px em
  BG3/y50. Perfil continuous endpoint minimax remapeia 4.611.304/14,33%, media
  0,04757 px/amostra/frame, drift medio1,48841px e maximo22,500016px em BG1/y40.
- Previews nos extremos diferem por 8.875/6.614 indices no discreto e
  11.920/18.102 no minimax; inspecao mostrou mudanca visivel da relacao
  telhado/castelo em ambos. Nenhum perfil foi aprovado ou promovido; o discreto
  preserva mais pixels medios, o minimax reduz o pior desalinhamento, mas ambos
  precisam de reautoria para caber em dois speeds sem quebrar a cena.
- Ferramentas em `tools/mugen2sgdk_forge`: sweep incremental de memoria,
  objetivos discreto/minimax e previews hash-bound. Suite completa:
  **108 passed**. Os dois relatorios/perfis e a decisao pendente estao em
  `doc/mugen/stage_suzaku_route_2026_09_25.md` e
  `doc/mugen/stage_architecture_record_2026_09_25.json`.
- Nenhum arquivo foi para `res/`; C/runtime/ROM nao foram alterados e nao houve
  nova prova BlastEm. Suzaku permanece pre-producao. Falta reautoria das massas,
  tilemap/priority/paleta, budget ResComp/VRAM/DMA/VBlank, BG5 runtime e ROM.
- Gates atualizados: higiene passed/0 blockers; contexto `technical_demo`
  validado/0 blockers; metodologia permanece blocked apenas por
  `perceptual_motion_unvalidated`. Closeout completo terminou com 27 erros,
  7 avisos e 123 checks; blockers incluem 11 SpriteDefinitions do Ken acima de
  16 sprites internos, GDD insuficiente, gate visual/audio ausente, budget
  divergente, conversao/per-tile reports ausentes e identidade de ROM stale.
- Freshness final: warning, um artefato stale (`emulator_session`), zero
  obrigatorios ausentes. A sessao velha usa ROM de teste Hadouken, nao o
  `out/rom.bin` atual. Learning capture/audit: 59 licoes, 30 candidatos,
  nenhuma promocao canonica.

## 2026-09-26 — Otimizações candidatas e ownership do Suzaku

- A pedido do usuário, registrei em `doc/mugen/vdp_optimization_options_2026_09_26.md`
  um portfólio **condicional**: alternância breve de sombras de P1/P2 quando
  elas forem sprites separados e contribuírem para um pico medido; reutilização
  de cores CRAM já existentes da paleta HUD sem mutar o HUD; multiplexação de
  adornos de especiais simultâneos preservando o corpo dos projéteis; e opções
  de recorte, deduplicação, pré-carga e FX em plano. Nada foi testado ou
  promovido. Piscar, troca aproximada de cores e desligamento temporário de
  sombras exigem aprovação visual e restauração de estado.
- Novo `stage-plane-profile` aceita mapeamento explícito por layer, exige
  posições inteiras consecutivas do sweep, amostras/linhas consistentes e no
  máximo dois speeds por linha. Seis testes dirigidos passam; suite completa
  do conversor: **114 passed**. A ferramenta não cria ownership BG_A/B,
  prioridade, tilemap nem prova de hardware.
- O sweep Suzaku concentra 3 velocidades nas linhas 0–39 e 4 em 40–111;
  112–175 têm duas velocidades, 176–223 uma camada por linha. Dois perfis
  semânticos foram medidos e vistos em 1x. O que preserva castelo/telhado
  desloca a lua até a borda (`120,50 px` de drift máximo); o que preserva o céu
  desloca castelo/muro e expõe uma lacuna magenta no extremo direito (`45 px`).
  Ambos seguem em estudo sem aprovação; nenhum `res/` foi alterado.
- Evidência, hashes e direção seguinte em
  `doc/mugen/stage_plane_ownership_study_2026_09_26.md`; opções de contingência
  em `doc/mugen/vdp_optimization_options_2026_09_26.md`. Rascunho de storyboard
  criado em `doc/mugen/suzaku_plane_storyboard_draft_2026_09_26.json`: BG_B
  preserva céu/lua a 0; BG_A reúne castelo/muro/telhado a .671875 até y175 e
  preserva bandas frontais. Próxima ação é revisar HUD/fighters/endpoints e
  completar priority/overlap/bleed por tile, depois tiles/paleta/ResComp/VRAM/DMA.
  Sem runtime/ROM/BlastEm nesta etapa.
- Learning capture/audit concluído: **60 lições, 31 candidatos**, sem promoção
  canônica.
- `doc/13-spec-cenas.md` sincronizado com as duas candidatas rejeitadas; o
  `scene_contract_compiler.ps1 -Mode lab -WarnOnly` recompilou 3 cenas, lint
  `ok`, 9 achados informativos.
- Contexto `technical_demo/implementation` e higiene passaram com zero blockers.
  Metodologia segue bloqueada apenas por `perceptual_motion_unvalidated` e pelos
  quatro sinais perceptivos/aprovação humana ausentes. Freshness: warning,
  1 stale (`emulator_session` antiga), 0 obrigatórios ausentes.

## 2026-09-26 — Suzaku: reautoria de BG_B com paleta preservada

- Criado um plate de conceito para BG_B e um composite estático de 640x224; fonte
  e crops têm proveniência/hash em `doc/art/`. O plate está aguardando revisão
  visual. Não há pixels desse candidato em `res/`.
- `forge-art` passou a aceitar `locked_palette_v1`, com PNG indexado da paleta
  hash-bound. O `forge-art self-check` passou 142/142 fixtures. A primeira
  tentativa sem travar a paleta alterava BG_A e aumentava o custo; a comparação
  controlada isolou apenas a mudança do far plane.
- ResComp 3.95: candidato pareado BG_B 186 + BG_A 252 = 438 tiles/15.876 bytes;
  controle flat 408 tiles/14.648 bytes. Contra o controle anterior (460/425),
  economiza 22 tiles pareados e 17 flat. Headroom de oito tiles depende de uma
  estimativa de capacidade 446 e não prova VRAM residente. Quatro padrões
  compartilhados entre planos são só potencial: IDs comuns de runtime não foram
  implementados.
- Auditoria exata de todas as células 8x8: zero conflitos, máximos de 4/5
  índices visíveis nos planos BG_B/BG_A; índice 0 é ausente no far e transparente
  no near. `scene_tilemap_conversion_candidate_report.json` e
  `per_tile_palette_conflict_report.json` registram as métricas e os limites.
- APLIB comprime partes de `MAP`; sem decodificador/exportador não foi criado
  `tilemap_flag_report`, evitando alegar tile IDs, palette, priority ou flips
  não verificados. O tamanho 640 não implementa a câmera source de 768px. Não há
  integração, medição runtime de câmera/DMA/VRAM/scanline, áudio, revisão visual,
  ROM nem prova BlastEm.
- Evidência comparativa e próximos gates em
  `doc/mugen/suzaku_candidate_review_2026_09_26.md`. A suíte do conversor passou
  **120/120**. O claim permanece candidato de staging, sem promoção AAA.

## 2026-09-26 — Suzaku: alternativas de arte e contexto de HUD

- Corrigida uma interpretação visual: a folha de contato continha três janelas
  de câmera sobrepostas em 160 px; o mesmo castelo/lua em dois painéis era o
  mesmo ponto do mundo. Verificar coordenadas-fonte e limites dos crops antes de
  chamar uma textura de repetida ou substituir uma arte.
- O conceito detalhado V2 chegou a 1.664 tiles pareados e excedeu a estimativa
  por 1.218. V3 em 8 cores reduziu erro para weighted MSE 235.530, mas ainda
  excedeu 125 tiles. A paleta travada em seis cores deu 446 tiles e weighted MSE
  337.696; ficou exatamente no teto estimado, sem margem. Não aceitar menor MSE
  sem custo ResComp, nem tratar custo igual à estimativa como folga.
- O mock `suzaku_visual_context_mock_20260926.png` verifica contraste com HUD e
  sprites de uma captura antiga, usando deltas provisórios; não é captura de
  ROM nova nem aprovação. O candidato V3 locked-six permanece em revisão; o V1
  simples fica como controle mais leve com oito tiles estimados de headroom.
- Relatório/hash comparativo e tarefas em
  `doc/mugen/suzaku_candidate_review_2026_09_26.md`,
  `suzaku_far_overlay_v3_rescomp_measurement_report.json` e
  `suzaku_visual_context_mock_report.json`. Não há runtime, ROM ou promoção.
- O bloqueio de tile flags continua: não emitir um relatório com índices/flags
  supostos enquanto `MAP` estiver APLIB-packed e não existir decodificação
  validada. O conversor recusou inicialmente BG_B transparente; a rota de estudo
  foi corrigida explicitando a cor de fundo VDP e tornando BG_B opaco, sem
  alterar o runtime.

## 2026-09-26 — Suzaku: tile masks, modular concept e recurso real

- Reduções semânticas V8/V9 chegaram a 390/410/436 tiles pareados e preservaram
  exatamente a máscara alpha do BG_A, mas deformaram detalhes do castelo, da lua
  e do piso por substituição de tiles inteiros. O menor custo passou ResComp e
  falhou a leitura visual; não reutilizar o resultado como arte. Máscara igual
  não é contrato suficiente: é preciso preservar também classe do objeto,
  material, contorno e continuidade do tile vizinho.
- O V10 foi convertido primeiro à paleta compartilhada de 15 cores (989 tiles),
  depois a 8 cores (961) e à paleta travada de seis cores (844). O ganho pequeno
  de 15 para 8 e moderado para 6 mostra que a variação estrutural, não só a
  paleta, domina o custo. ResComp deve medir cada candidato depois da conversão.
- A janela 320px do V10 six-color exige 424–471 tiles alinhada; 442–483 com
  deslocamento sub-tile; e 454–494 incluindo uma coluna de prefetch. O pico
  excede a estimativa histórica de 446 antes de HUD/FX/runtime. A tela 1x mock
  com HUD/lutadores informa composição estática, não prova de emulador.
- A sonda do alocador em ROM diagnóstica sem palco mediu pool sprite=600,
  mínimo livre247 e maior bloco contíguo72. Não reduzir pool para encaixar o
  palco por estimativa: sombra intermitente reduz scanline entries/pixels, não
  tiles VRAM; cor compartilhada reduz índices CRAM, não bytes de tile. Cada
  alternativa só pode ser creditada ao recurso que realmente mediu.
- Próxima rota: criar/reautorizar módulos visuais reutilizáveis que preservem
  silhueta, material e contato do piso; medir cada módulo e a pior janela de
  câmera. Alternativa é streaming de tilemap com cache contíguo e DMA dentro de
  VBlank, após fechar a residência de lutadores/FX e conferir o pior estado.
  Nenhum ativo foi para `res/`; ROM, runtime, música e aprovação permanecem
  pendentes. Detalhes/hash: `doc/mugen/suzaku_candidate_review_2026_09_26.md`.

## 2026-09-26 — Trilha Suzaku candidata em staging

- Criado VGM autoral de 8 compassos/16s, 120 BPM, com baixo, motivo FM,
  sustentação harmônica e resposta esparsa; PSG noise acentua beats2/4 e a
  trilha não usa PCM para reservar espaço a vozes/impactos. A tabela melódica
  usa D/E/F/A/Bb; C3 aparece apenas como quinta harmônica sobre F2.
- O writer valida assinatura e versão VGM1.70, EOF/data/loop pointers, 960
  frames/705600 samples, key on/off e ausência de DAC PCM. SHA VGM
  `a6edd4b104935d86e7cef35013d69075506454a51e770fa4732e938f2dc6ef09`.
- O ResComp3.95 aceitou a declaração XGM2 e produziu resource de 1024 bytes.
  Isso prova conversão, não escuta nem loop sem clique. Nenhuma alteração em
  `res/resources.res`, `src/system/audio.c` ou ROM. Humano ainda precisa ouvir
  e aprovar mix/loop com vozes, impactos, PSG e driver em BlastEm.
- Evidência e geradores em `rascunho/processado/suzaku_fight_audio/`; detalhes
  em `doc/17-audio-design.md`. Manter a faixa em `staging_candidate` até audição,
  integração isolada e captura hash-bound.


## 2026-09-26 — BGM Suzaku: captura isolada e alerta de cadência

- A cópia descartável com a BGM candidata compilou pelo Linux SGDK bridge;
  ROM `fa7d859b666601ea3c0d2567031c15723a996d16237674c9c4b8076557427d72`.
  BlastEm selou evidência da cena 3 e do áudio no mesmo SHA; nenhum `src/`,
  `res/` ou ROM de produção recebeu a integração.
- `audio.raw` (15,319,040 bytes) foi identificado pelo log como SDL float32,
  estéreo, 48 kHz; WAV derivado de 39.893333 s passa duração/sinal/clipping,
  com pico -7.96 dBFS, RMS -22.60 dBFS e canais idênticos. Isso não avalia
  melodia, clique no loop, mix ou balanceamento de SFX; audição humana ainda
  é gate obrigatório.
- Em fight, screenshot da captura mostra o placeholder plano. O título BlastEm
  marca 59.7 fps apenas no instante; a janela fixa da probe de 1200 quadros
  registra 74 quadros acima do orçamento, `max_cpu_load=146`, pico de scanline
  10 e 5 sprites ativos. Performance sustentada não está aprovada e a BGM não
  foi isolada como causa. Próximo experimento causal: build pareado sem BGM;
  depois repetir com cenário, vozes/impactos/super no pior estado.
- Bundle e relatório hash-bound em `rascunho/processado/suzaku_fight_audio/blastem_auditions/blastem-linux-20260926T090235Z-2327237/`; classificação
  por camada em `audio_audition_review.json`. O helper de análise recebe WAV;
  a captura SDL salva float32 raw, portanto converter com parâmetros explícitos
  de 48 kHz/f32le antes da análise.

## 2026-09-26 — Suzaku: economia de tiles e backdrop

- A economia visual genérica de paleta já existia na skill de excelência; faltava
  a semântica específica do backdrop. A direção de arte agora deve escolher uma
  cor que mantenha contraste/hierarquia e verificar o índice CRAM global, não
  tratar `VDP_setBackgroundColor()` como RGB ou carregamento de cor.
- O candidato V15 tornou transparentes 64.630 pixels do céu ligado à borda e
  reconstruiu com CRAM[3]. ResComp passou de 915 para 924 tiles e de 32.068 para
  32.380 bytes; a pior janela de 42 colunas passou de 543 para 547. É evidência
  negativa para este cenário: transparência/backdrop não economizou VRAM nem
  uma cor. Tiles opacos podem continuar exigindo o slot CRAM.
- V16 repete um módulo de piso já presente na fonte em uma faixa 64x8, sem criar
  padrões ou índices de paleta. O controle cai para 846 tiles/29.624 bytes e a
  pior janela para 510; ainda excede a estimativa histórica de 446 por 64 tiles.
  Repetição visual está sob revisão humana. Mock de fighters/HUD é montagem
  estática, não captura de jogo. Hashes e método: `doc/mugen/suzaku_candidate_review_2026_09_26.md`.
- V13–V16 seguem apenas em staging. Nenhum candidato foi carregado em `res/`,
  runtime ou ROM. Próximo gate: aprovar/refinar os módulos e desenho de planos,
  fechar camera/streaming/DMA, depois capturar a luta completa com stage e áudio.

## 2026-09-26 — Suzaku: preservar geometria de layer antes de reautorar

- V17 (panorama gerado a partir de cinco layers) e evidencia negativa: as fontes nao compartilham uma coordenada mundial porque tem velocidades distintas; o resultado desalinhou landmarks e encurtou o piso. Ficou reference-only no workset.
- O board de coordenadas hash-bound agora fixa os bounds por layer nas cameras 0/224/448 e deixa explicito que o atlas estatico ainda nao representa velocity de BG0 nem os ciclos BG5/BGCtrl.
- Errata 2026-09-26: nao tratar as 7 linhas superiores do WINDOW como oclusao opaca. `fight_hud.c` limpa o retangulo 40x7 e preenche celulas selecionadas; color code0 e transparente. Os 679/710 tiles medidos apos remover essa faixa sao limites inferiores para um overlay hipoteticamente opaco, nao o custo de producao. Ver `visible_window_report_erratum_20260926.json`.
- A recomposicao exata do frame completo a cada posicao de camera usa 466/481 padroes no centro e atinge 629/638 no sweep, mas um passo de 1 px pode exigir ~19,8 KB de uploads/mapa. Isso elimina a implementacao ingenua por recomposicao em cada quadro; nao reprova toda forma de streaming.
- Proximo trabalho: usar o atlas-fonte em 0/224/448 como teste de fidelidade e achar uma composicao em dois planos com perdas de parallax conscientes, budget real e comparacao visual. Nao gerar outro panorama unico antes de validar o quadro de coordenadas.
- Sem mudanca em `res/`, runtime ou ROM; detalhes/hash-bound em `doc/mugen/suzaku_source_fidelity_recovery_2026_09_26.md` e `doc/mugen/suzaku_plane_storyboard_draft_2026_09_26.json`.

## 2026-09-26 — Pool de sprites por estado

- `APP_boot` usa `SPR_initEx(16)` para branding, mas a luta encerra o pool e chama `SPR_initEx(600)` antes de criar atores. O validador de recursos pegou a primeira chamada textual e reportou 16 como se fosse o valor da luta; classificar isso como limitacao de analise, nao corrigir o jogo reduzindo VRAM.
- A capacidade de 304 tiles para o palco e somente calculo sob pool 600, sheets de 260 tiles por jogador e 112 tiles fixos, ainda sem HUD/retratos/FX/fragmentacao. ROM atual em `out/rom.bin` SHA `200346548a57cb6196cf21773c9233bd53b72b02e1bdf7f6548fd3331aa81c2c; identidade stale/mismatched; pool e budget de palco nao observados em runtime nesta rodada.
- Falha local registrada em `doc/agent_learning/failure_patterns.md`; nenhuma alteracao no wrapper canonico sem aprovacao separada.

## 2026-09-26 — Suzaku: controle de fonte, tiles e oclusao real do HUD

- A recomposicao source-derived do frame central 320x224 bateu exatamente com o compositor MUGEN offline antes de quantizar. ResComp3.95 mede 758 tiles/26.736 bytes em dois planos com paleta compartilhada de 15 cores; o flat de comparacao custa 712 tiles/24.994 bytes e perde movimento independente.
- A conversao a 15 cores e mais proxima da fonte que a de 8 cores: RGB MAE/RMSE 12.169/15.442 versus 15.030/19.390. A variante de 8 cores economiza 73 tiles no frame completo, nao o diferencial de 10 tiles observado com recorte superior.
- O runtime divide PAL0 em oito slots para o stage e sete para HUD; PAL1/2 pertencem aos corpos e PAL3 aos FX. A conversao de 15 cores e controle offline e nao pode ser aplicada sem migrar/revisar HUD e FX. A opcao atual de oito cores respeita o split mas perde fidelidade cromatica.
- Errata: `visible_window_residency_report.json` assumiu que WINDOW y0..55 era opaco pela geometria do plano. O codigo apaga as 40x7 celulas e preenche apenas partes com HUD; color code0 e transparente. As contagens clipped (516/506) nao representam o fundo visivel e nao podem fechar budget. Full frame deve ser contado ate uma captura real do palco provar mascara diferente.
- `SPR_initEx(446)` deslocaria o inicio do pool de VRAM 840 para994 e aumentaria a regiao user fixa de824 para978 tiles (+154); com emprestimo temporario dos272 tiles de BGFX, o stage hipotetico chega a516. A sonda atual mede353 tiles usados, maior bloco livre72, sem stage e com audio dummy; pool menor nao esta aprovado. O frame completo sem aplicar mascara de HUD mede758 e passa esse teto em242 tiles; qualquer economia por celulas totalmente ocultas ainda precisa ser calculada.
- Proximo passo: Pareto de reducao source-faithful por regioes sem remover ceu; reconstruir visibilidade por pixel a partir do Window/mapa; medir cameras e simultaneidade. Avaliar compartilhamento de sheets somente para definicoes identicas em P1/P2 e preservar fallback de personagens diferentes. Sem alteracao em `res/`, runtime/ROM ou promocao visual.
- Relatorio e hashes: `doc/mugen/suzaku_source_fidelity_recovery_2026_09_26.md` e `rascunho/processado/stage_takeover/suzaku_visible_window_residency_20260926_v2/visible_window_report_erratum_20260926.json`.



## 2026-09-26 — Suzaku jogável integrado e orçamento medido

- Primeira integração source-derived: BG_B carrega o frame central Suzaku convertido a 8 cores, P1/P2 Ken, portraits, HUD, round e super. VGM Suzaku existente agora inicia somente na luta; nenhum PCM/voz foi adicionado. Cena foi vista no BlastEm, não é aprovação visual final.
- ROM de avaliação mais recente após a captura: SHA `665bfa340b293d4943fec0c1fbdfde998d5cc5e1bf5fda6e4206b8bee38c856f` (antes da opção NONE; refazer identidade depois da build em curso). Captura `out/suzaku_music_integrated/evidence/blastem-linux-20260926T201504Z-379823` prova cena 3, VDP dump, SRAM e 10 frames; título 58.9 fps é só snapshot. Medição 1200 quadros: 87 over-budget, max CPU149, zero sprite allocation failures; cadência não passa.
- Experimento pareado exploratório: cópia temporária alterou apenas os 87 sprites `FAST` para `NONE`; frames/assets são os mesmos. ROM cresce 256 KiB (1.125→1.375 MiB). Captura: 40/1200 over-budget e CPU máx131; comparação determinística dos inputs ainda não foi estabelecida, então é opção promissora, não causalidade fechada. A rota será construída na ROM de trabalho para confirmar.
- Estado do VDP comprovado no binário compilado: corpo máximo102 por player, retrato compartilhado16, HUD142 (total pós-fight 158 tiles contíguos), pool430, uso observado no outro build353; menor maior bloco49. Stage640 mora em quatro bancos disjuntos: low360, font96, gap128, gap64. Os mapas C000/B, E000/A+WINDOW, scroll F000 e SAT F400 não colidem. A/WINDOW são superfícies fixas, scroll zero. O carregamento acontece com display desligado.
- Super usa sua região previamente reservada de tiles e muda o mapa BG_B. A ROM de teste dirigida executou duas devoluções, verificadas em SRAM (stage ready=1, restore count=2); a cópia persistente no DMA_QUEUE passou harness host que clobbera stack antes do VBlank.
- Escopo ainda reduzido: imagem fonte em 8 cores, quadro central de 320x224 fixo, sem world-camera, parallax layer-by-layer, partículas BG5, vozes ou aprovação humana de áudio. Não chamar o stage de terminado nem a demo de estável/AAA.
- Layout e alternativa opcional para agentes: `tools/sgdk_wrapper/.agent/references/mugen_cost_quality_decisions.md`. O runtime instalado local tem mudanças anteriores à fonte geradora compartilhada; `mg_fight.c` apresenta drift e requer reconciliação antes de `install-runtime`, sem apagar anotações/decisões.

## 2026-09-27 — Regressão de inicialização nos candidatos Suzaku

- Duas ROMs diagnósticas compilaram e chegaram à cena 3 no BlastEm, mas ambas exibiram fundo vazio: o bloco SRAM indicou `stage_ready=0`. Portanto, cena atingida e captura selada não provam palco carregado; nenhum dos dois candidatos é ROM jogável com cenário.
- Candidato de streaming: SHA `2c62c7f52c383954ad01dbd6d32dfd429576cfc4d095ba606b7de49ec8b97b19`; capacidade observada 456 tiles, residentes/pico 0, overflow 0, restaurações 0, `stage_ready=0`; VLAB: 50/1200 quadros acima do orçamento, CPU máxima 124. Bundle local `out/mugenesis_evidence/suzaku_stream/canonical` (sessão `blastem-linux-20260927T020859Z-1815492`).
- Candidato estático em dois planos: SHA `c1b03a491848803ccecc56c678b09c88c040069db132e61c6030610500788c9a`; `stage_ready=0`, restaurações 0, falhas de alocação de sprite 0, menor bloco contíguo observado 94 tiles; VLAB: 82/1200 quadros acima do orçamento, CPU máxima 141. Bundle local `out/mugenesis_evidence/suzaku_static_planes/canonical` (sessão `blastem-linux-20260927T022756Z-1860145`). Os snapshots de 59,9 e 59,5 FPS não demonstram cadência estável.
- A rota de streaming reservou apenas 456 tiles porque o BGFX de 272 tiles não estava disponível como empréstimo no estado medido; empréstimo e faixa-base compartilham a mesma faixa de VRAM e não podem ser somados como capacidade independente. Isso ainda não explica a falha da inicialização estática de dois planos.
- Próximo passo: instrumentar o resultado/capacidades exatas de `FIGHT_STAGE_init`, confirmar flags de compressão e dimensões dos recursos gerados e comparar com a última ROM âncora conhecida com `stage_ready=1`. Repetir BlastEm após a correção, verificando explicitamente pixels do cenário e SRAM antes de qualquer claim. Detalhe: `doc/mugen/suzaku_capture_regression_2026_09_27.md`.
