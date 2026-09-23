# Changelog Canonico - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

## 2026-09-22 - Contraprova causal do especial sem promoção sensorial

- Fechado o ciclo baseline pré-correção (`d6b7...eb9618`) → commit `dee2356e`
  → ROM pós-correção (`47db...c4db6d58`) para Ryo/700.
- O recibo `out/audiovisual_review/marker_event_capture_v4_correction_cycle_special_001.json`
  vincula fonte, asset, ROMs e imagens dos mesmos índices do harness; registra
  mudança da folha de quatro células e preserva as limitações de execução
  separada, playback e audição.
- Resultado técnico: `counterproof_supports_visible_change`. Movimento, áudio,
  qualidade visual e AAA continuam bloqueados; P10 histórico não foi reescrito.

## 2026-09-22 - Gate audiovisual P0 e separação de qualidade

- `audiovisual_review.py` 2.6.0/schema 2.3.0 separa observação do evento,
  legibilidade visual e qualidade visual. Qualidade exige critérios e comparação
  de referência; frames vistos não são aprovação.
- HCAD recalcula contagens, ticks, apresentação, zero-tick, região e identidade
  ROM, rejeitando janela vazia, contradição, booleano, overflow e SHA stale.
- Wrapper: 8 testes; projeto audiovisual: 26 testes; P10 histórico stale segue
  preservado. O V5 real foi reemitido em
  `out/audiovisual_review/marker_event_capture_v4_v5_p0_recomputed.json` com execução
  passada e claims finais bloqueados quando não sustentados.
- O especial foi comparado a `src/fsm.c`, `src/physics.c` e `spr_ryo_701`; o
  candidato continua sem causa confirmada e sem patch de jogo.

## 2026-09-20 - KO transitório e revanche same-ROM no SHA 86b15dac

- O banner KO autoral deixou de reservar SAT/VRAM durante toda a luta; agora é
  criado somente ao entrar na mensagem KO e liberado ao sair dela.
- Build wrapper SGDK/Wine passou; ROM SHA
  `86b15dacb48a7df790cc68dde5b204309089f183ff84c9ad44339a95fa83d147`.
- BlastEm confrontou KO, resultado e revanche em
  `out/emulator_evidence/visual_ko_20260920T060858990521Z-1139143/`.
  `zero_1_settle.png` mostra KO, `after_combat.png` mostra o resultado e
  `rematch_round.png` mostra ROUND 1 reiniciado com HUD e palco BGB2.
- HPRB/HSEM same-ROM: 22 hits, 1 KO, 7184 B DMA, 55 links VDP e 12
  sprites/scanline; decisão `cabe`, todos dentro do envelope nominal NTSC.
- O estado permanece `prototype_partial_current_sha`: especial/guarda/throw,
  P10, áudio crítico, cobertura total de animações, pior frame combinado e
  revisão independente ainda não estão recapturados neste SHA.

## 2026-09-20 - Renovação visual same-ROM das rotas abertas

- Especial recapturada em `out/emulator_evidence/visual_ko_20260920T061306821952Z-1151049/`;
  frame de projétil visível, HPRB nominal com 7424 B DMA, 42 links VDP e 12
  sprites/scanline.
- Guarda recapturada em `out/emulator_evidence/visual_ko_20260920T061605480382Z-1160600/`;
  impacto/FX de bloqueio visíveis. O probe isolado não emitiu SRAM, portanto
  não foi inventada telemetria.
- Throw recapturado em `out/emulator_evidence/visual_ko_20260920T061717479666Z-1164845/`;
  contato/recuperação visual registrados, ainda sob revisão de acabamento e
  sem HPRB/HSEM do probe isolado.
- Seleção P1/P2 recapturada em
  `out/emulator_evidence/visual_ko_20260920T061842171974Z-1169299/`; título,
  opções e retornos recapturados em `out/emulator_evidence/title_return_20260920T061912Z/`.
- Todas as capturas acima têm ROM SHA `86b15dac...`; o status permanece parcial,
  com P10, áudio crítico, animações completas, pior frame combinado, VRAM
  residency e revisão independente ainda abertos.

## 2026-09-19 - HUD visual e prova de dano no SHA c6019980

- Integrados retratos em close para Ryo/Ken/Musgo, chapa de vida autoral, camada de dano recente e especial azul com palette indexada compatível com PAL1.
- Corrigida a profundidade/posição da chapa para que o trilho vazio permaneça visível atrás do preenchimento; BGB2 continua como baseline do combate.
- Seletor refinado com `ROSTER // VS`, identificação P1/P2, previews, nomes e `STAGE // BGB2`.
- Build SGDK/Wine passou; ROM SHA `c6019980e96f08492844d85407c1df5e3f67da22a5a0606cda58ad27b99231ba`.
- BlastEm comprovou dano, combo, spark, reação e estabilidade visual em `out/emulator_evidence/visual_ko_20260919T122930Z/`; a captura curta comprovou HUD em `out/emulator_evidence/visual_ko_20260919T122736Z/`.
- Não promovido a pronto: KO/revanche no SHA atual, message font autoral final, áudio, parallax/ambiente e auditoria completa de proveniência permanecem pendentes.
- A rota real de time-over no mesmo SHA terminou com relógio `00` e tela `PLAYER 1 WINS` em `out/emulator_evidence/visual_ko_20260919T124155Z/after_timeover_observation.png`; o manifesto mantém a limitação de que o terminal semântico não foi fechado.

## 2026-09-19 - CPU sustentada separada da carga de entrada e DRAW selado

- O probe passou a usar `SYS_getCPULoad()` e diferença absoluta entre cargas consecutivas para `max_cpu_load`/`max_cpu_jitter`; o contrato do VLAB e o self-check do sealer passaram.
- Build SGDK/Wine: ROM `c17af26742c71840462b9da9f7f2037993ff81eb8dd6170f92b3f3916af4ce86`, 2.490.368 bytes.
- `HAMOOPIG_probeFightInit()` marca a inicialização de luta e sua cauda de 16 frames; o agregado sustentado só aceita amostras de `SCENE_FIGHT`, sem misturar título/seletor nem a média móvel de 8 frames com o upload inicial.
- BlastEm selou `out/emulator_evidence/visual_ko_20260919T061243Z/evidence_manifest.json`. VLAB: 7350 amostras, DMA 7016 B, 17 sprites/scanline, 22 sprites ativos, zero frames acima do orçamento VDP, `max_cpu_load=139%` no frame 6869 e `max_cpu_jitter=7`. A carga de entrada ficou separada em `initialization_cpu_peak=744%` no frame 7050; 139% sustentado ainda mantém a reivindicação de performance como não provada.
- Ranges observados no VLAB: pool de sprites `[1020,1440)` e stage `[1,1010)`; a extensão mede residência exportada, não uploads dinâmicos individuais.
- A captura `visual_ko_20260919T054050Z` com áudio falhou por ausência de stream monitorável único; áudio e performance sustentada seguem sem aprovação. O contrato VLAB, o teste host e o self-check do sealer passaram; a validação PowerShell e o rebinding da revisão independente seguem pendentes. Claim continua `prototype_partial`, sem AAA.

## 2026-09-16 - Composição limpa da tela de título

- `title_scene.png` combina um fundo azul pixel-art autoral com o logo/pig
  reduzido do projeto; a conversão usa paleta fixa Mega Drive e 151 tiles,
  preservando o orçamento de VRAM e evitando o quadriculado de quantização.
- A camada de abertura `room_0_bga` deixou de ser reutilizada no título, então
  créditos, contador e sprites residuais não atravessam o fade.
- Captura BlastEm: `out/emulator_evidence/title_return_20260916T082401Z/`
  (ROM SHA `2ba2aaf883a489ac1d2966cc71b448b66a2f3561812dfd8f9c929fae1e06f5e8`).
  A revisão visual independente continua pendente; P10 histórico permanece
  vinculado ao SHA anterior até nova recaptura.
- P10 foi então recapturado no SHA 2ba2 (`36/36`, HPRB schema 7); a captura
  dirigida `visual_ko_20260916T090920Z` registra HIT=1 e áudio isolado com
  sinal não auditado criticamente.
- O estresse de boot/reset concluiu 100 ciclos no mesmo SHA em
  `scene_reset_cycles_20260916T092844Z`; isso cobre estabilidade de cena, não
  substitui o teste semântico de reset de round.
- Vídeo da rota completa abertura→título→seletor foi capturado em
  `visual_ko_20260916T095216Z/opening_title_transition.mp4`; a captura prova a
  sequência temporal, mas a aprovação estética dos fades continua pendente.
- A reprodução P11 isolada foi refeita com `TMPDIR=/tmp` para evitar o tmpfs
  compartilhado e passou em `out/p11_isolated_reproduction_20260916T202748Z/`.
- A rota de captura de THROW foi corrigida para respeitar a propriedade das
  teclas P1/P2 (L118). A execução ainda resultou em zero eventos THROW, então
  o comportamento permanece pendente e não foi promovido por hipótese.

## 2026-09-16 - Fade de saída transacional do título e revalidação 16d3

- `src/title.c` ganhou `TITLE_PHASE_FADE_OUT`: `START` consome a borda,
  executa fade assíncrono de 8 ticks e só então faz `CLEAR_VDP`/`SCENE_SELECT`.
  Isso elimina a sobreposição da composição do título com a carga do seletor.
- Build SGDK/Wine: ROM
  `16d3572ed49818e1170dbd690b74d8596b31ced543678f0c5eb03e2e2cb79248`.
- P10 foi recapturado no mesmo SHA (36/36 probes); title-return, vídeo de
  transição, áudio isolado, 100 resets e HIT também foram renovados. THROW
  teve duas tentativas sem evento e permanece pendente de rota determinística.
- Os gates sensoriais continuam explícitos: revisão visual independente,
  audição crítica, gameplay completo, pior-frame, streaming nativo e hardware.

## 2026-09-16 - Stage 2 sem preto opaco e revalidação 30c2

- `convert_stage2.py` passou a reservar o índice transparente e a excluir
  entradas de paleta preenchidas após o snap de 9-bit. `res/gfx/bgb2.png` foi
  regenerado sem pixels RGB `(0,0,0)` e permaneceu em 864 tiles.
- O build SGDK/Wine gerou a ROM
  `30c2b7f779b98b9f594c7b605f6b8cc14a86793cddf804be846e5c30bc7ae873`.
- P10 foi recapturado (36/36), além de title-return, transição, áudio isolado,
  100 resets, HIT e THROW; todos os resultados continuam sujeitos aos gates
  de revisão visual, audição crítica, pior-frame e hardware.
- O capturador de áudio agora aguarda o sink e reconhece app-id Flatpak, sem
  relaxar a exigência de rota isolada.

## 2026-09-16 - revalidação de sessão no SHA f424

- Retorno ao título: cinco capturas não vazias na sessão
  `title_return_20260916T062339Z`.
- Áudio isolado: sessão `visual_ko_20260916T062527Z`, 174,6 s, rota BlastEm
  verificada, RMS -27,96 dBFS e zero clipping; audição crítica continua sendo
  um gate separado.
- Reset: `scene_reset_cycles_20260916T062909Z` completou 100/100 ciclos no
  mesmo binário. Lição L111 registra os hashes e limites destas provas.
- Uma rota curta de combate real registrou um HIT no HPRB, confirmando que a
  matriz de orçamento pode ser combinada com uma interação de dano sem injeção;
  a evidência está na lição L112.

## 2026-09-16 - THROW alcançável em rota real-keyboard (P04)

- A rota isolada de agarrão foi corrigida para aproximar P1 e P2 simultaneamente
  e emitir bordas de Y apenas em estado neutro; o teste não injeta posição,
  estado ou SRAM.
- No SHA `f4248208cec58ee0fec57b89f46f535e2c21026b9a34685449ce3204be1cab86`,
  o HSEM registrou `throw_frames_p1=64`/`throw_frames_p2=3` e o HPRB do mesmo
  SRAM registrou dois eventos THROW, além de dois HIT.
- O budget observado permaneceu nominal (7008 B DMA, 41 sprites ativos,
  63 links VDP e 17 sprites por linha). Isso prova alcançabilidade do evento;
  animação, balanceamento, revisão visual e gameplay completo continuam
  pendentes.
- Lição L110 registra que o roteiro de teste deve respeitar o mapeamento de
  teclado e separar aproximação de emissão de ataque.
- A matriz P10 foi recapturada no SHA f424: 36/36 bundles decodificados pelo
  schema 7, todos `probe_passed` e ainda `pending_visual_review`; os retries
  PAL transitórios foram resolvidos sem alterar o código da ROM.

## 2026-09-15 - inventário de handoff P11

- Criado `doc/engine/release_inventory.json`, vinculando a ROM eeb5 às fontes
  de runtime, documentação e bundles de evidência necessários para reproduzir a
  engine.
- `tests/reproduce_p11_isolated.py` passou a conferir os caminhos do inventário
  e o estado `candidate_not_release`; o teste não promove a entrega enquanto
  os gates visual, auditivo, gameplay, pior-frame, streaming e hardware não
  forem fechados.
- Lição L102 registra a diferença entre inventário reproduzível e aprovação de
  release.

## 2026-09-15 - transição abertura/título revalidada no SHA eeb5 (P02/P10)

- A captura `--transition --select-only` foi refeita em sessão BlastEm limpa
  após a correção do KO de Musgo. O vídeo
  `out/emulator_evidence/visual_ko_20260915T191614Z/opening_title_transition.mp4`
  está vinculado ao SHA `eeb50ff819ba5e3027dd3a23067f2329038039027ef4b1a7a1add97cddf9f750`.
- A sequência observada permanece abertura legal → título persistente com
  `START/OPTION` → seletor → combate, sem painel sobre os créditos. A revisão
  visual independente, legibilidade final e avaliação sensorial continuam
  pendentes; a captura não é promoção AAA.
- Lição L101 registra a proveniência e evita reutilizar as capturas a187 como
  evidência do binário atual.

## 2026-09-15 - back-pressure de sprites e orçamento NTSC (P01/P09)

- O pior frame NTSC foi isolado pelo HPRB schema 7: uploads automáticos de
  frames grandes dos lutadores usavam `SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE`
  e podiam acumular 8288 B contra 7782 B nominais.
- `src/player.c`, `src/player_ken.c` e `src/player_musgo.c` agora deixam o
  sprite engine aplicar back-pressure; o frame é postergado quando a fila não
  comporta o upload, sem desligar `AUTO_TILE_UPLOAD`.
- Os mapas transitórios de HITS/mensagens em `src/hud.c` passaram a usar CPU,
  mantendo DMA para assets e uploads de sprites. Build SGDK/Wine aprovado:
  ROM `c90aaa166634a7435665be43e111ff20b34bd13bec6721536a9f9964c2b7f372`.
- A sessão NTSC BGB2 em
  `out/emulator_evidence/visual_ko_20260915T063954Z/` mediu schema 7,
  `screen_height=224`, 1710 amostras, pico DMA 7008 B, 17 sprites/scanline e
  status `cabe`. A suíte host/estática permanece 18/18.
- A lição L074 registra que o budget passou, mas atraso de animação, áudio,
  eventos dirigidos de combate e revisão visual do cenário continuam pendentes.

## 2026-09-15 - regressão PAL-240 da ROM nova

- A rota limpa `--pal --h240 --stage2 --probe-short` foi repetida sem outra
  instância BlastEm e confirmou `screen_height=240` no HPRB schema 7.
- Bundle: `out/emulator_evidence/visual_ko_20260915T064928Z/`; 2520 amostras,
  pico DMA 8160 B, 17 sprites por linha e decisão `cabe` no envelope PAL.
- A captura valida altura/cenário/budget da ROM nova; não substitui combate
  dirigido, revisão visual, áudio ou teste de hardware.

## 2026-09-15 - candidato de cenário derivado do estudo nativo (P08)

- O laboratório `[_ESTUDO]_mugen_sff_showdown_v1` foi revisado. A fonte nativa
  768×480 foi copiada com hash para
  `data/source_art/showdown/lab_frame_0000_source.png` e o conversor agora
  aceita `--source`/`--crop` sem alterar o pipeline padrão.
- `res/gfx/showdown.png` foi regenerado a partir do recorte `[128,224,640,480]`,
  mantendo 14 índices opacos, 768 tiles e o contrato SGDK de índice zero.
  Build: ROM `c9ae1c999525f31a387d06d491488870019d09eda95050954371d085f1a53849`;
  suíte completa executada.
- A captura `out/emulator_evidence/visual_ko_20260915T053414Z/01_round.png`
  mostra composição mais próxima da referência, mas ainda com repetição visível.
  O estudo continua sendo fixture técnico, não arte final; streaming nativo,
  DMA/worst-frame e revisão visual independente permanecem pendentes.

## 2026-09-15 - vídeo da transição abertura para título (P02)

- `tests/capture_visual_ko.py` ganhou `--transition`, iniciando o x11grab antes
  da espera de boot. A sessão
  `out/emulator_evidence/visual_ko_20260915T053734Z/` tem 2946 frames a 60 fps:
  preto inicial → abertura → fade-out → intervalo preto → título/menu.
- A sequência observada não mostra o menu interrompendo a abertura no frame
  estável. A revisão de CRAM/VDP e os ciclos PAL/skip continuam pendentes;
  a captura temporal não é aprovação definitiva.

## 2026-09-15 - transição revalidada no SHA e170 (P02)

- Refeito `--transition` em sessão BlastEm limpa após a promoção do Stage 2:
  `out/emulator_evidence/visual_ko_20260915T135842Z/`.
- O vídeo confirma a ordem abertura → fade-out → preto → título/menu → seletor
  → combate, sem sobreposição observada. A evidência permanece exploratória e
  aguarda review visual independente e medições de pior-frame.

## 2026-09-15 - KO e reset de round revalidados no SHA e170 (P04)

- A rota real Ryo × Musgo alcançou KO, exibiu `PLAYER 2 WINS` e confirmou a
  restauração das duas barras em `special_reset_health.png`.
- Bundle: `out/emulator_evidence/visual_ko_20260915T140256Z/`; GUARD, THROW,
  simultaneous hit e time-over continuam como casos dirigidos pendentes.

## 2026-09-15 - StageDefinition orientada a dados (P08/P11)

- Showdown e BGB2 passaram a declarar câmera, plano/paleta, loading model,
  orçamento de tiles, BGM e proveniência no contrato usado pelo loader.
- `init.c` aplica o orçamento declarado e o build SGDK/Wine passou; streaming
  nativo permanece explicitamente reservado para a próxima etapa.

## 2026-09-15 - revalidação integrada no SHA a187 (P10)

- A nova ROM foi vinculada a 36/36 probes P10, title-return, transição,
  KO/reset e áudio isolado; os bundles antigos de e170 ficaram históricos.
- Resumo HPRB atual: 8.024 B DMA enfileirados, 41 sprites ativos, 61 links VDP
  e 17 sprites por scanline. Isso não fecha gameplay completo, escuta crítica,
  revisão visual independente ou pior-frame.

## 2026-09-15 - HPRB exercitado com combate real (P04)

- A sessão dirigida
  `out/emulator_evidence/visual_ko_20260915T054142Z/` percorreu golpes e
  especiais na ROM `c9ae1c999525f31a387d06d491488870019d09eda95050954371d085f1a53849`.
- O decoder registrou 16 HIT e uma origem PROJECTILE, sem inferência por
  pixels. A mesma amostra atingiu 72 links VDP, 17 sprites/scanline e DMA
  máximo 8288 B. GUARD, THROW, DOUBLE e KO ainda precisam de sequências
  dirigidas próprias.

## 2026-09-15 - telemetria HPRB de eventos de combate (P04)

- O probe SRAM passou ao schema 6 (68 bytes declarados) e exporta contagens
  saturantes de eventos, HIT/GUARD/THROW, projéteis, colisões DOUBLE, KO e o
  último tick observado. A consolidação ocorre depois do consumidor central,
  sem inferir colisão a partir de pixels.
- Decoder fechado e contrato novo: `tests/test_hprb_event_probe_contract.py`;
  a suíte executou 16 arquivos. Build SGDK/Wine aprovado, ROM
  `713cfe0751e49706bd6d75e844e114032963dfe04e228e02bc475f8b4e792e7b`.
- Sessão real curta em
  `out/emulator_evidence/visual_ko_20260915T052605Z/` decodificou schema 6;
  ela não produziu eventos, portanto ainda falta captura dirigida de HIT/GUARD,
  projétil, colisão dupla e KO.

## 2026-09-15 - correção do segmento de vida do HUD (P07)

- `energy_yellow_segment.png` foi normalizado para o contrato SGDK: índice 0
  transparente e índice 2 amarelo, compatível com a PAL1 compartilhada. O
  preto que ocupava o índice 0 era a origem dos artefatos quadriculados nas
  barras após atualizações de vida.
- Novo teste `tests/test_hud_segment_contract.py` e normalizador versionado em
  `data/source_art/hud/normalize_segment.py`.
- Build aprovado, suíte 15/15, ROM
  `74d402437490e31b0dc95332bf2b30c98ccae19a9b18f85154cbc03fd4b268ac`.
  A captura `out/emulator_evidence/visual_ko_20260915T051731Z/combat_005.png`
  mostra as barras sem o padrão corrompido; revisão independente e budget ainda
  são necessários.

## 2026-09-15 - identidade de origem dos eventos e guarda de vitória (P04)

- `CombatEvent` registra a origem (`BODY`, `PROJECTILE`, `THROW`, `DOUBLE`) e a
  instância do ataque; a chave de deduplicação inclui esses campos, evitando
  colapsar projéteis distintos com o mesmo estado da FSM.
- Cada disparo recebe uma instância estável, reiniciada junto com os dados do
  round. O caminho legado `COMBAT_EVENTS_EMIT` continua representando golpes
  corporais.
- Corrigida a condição de vitória que usava `||` e podia premiar o vencedor
  repetidamente durante a animação. O placar passa a ser incrementado uma vez
  por resolução.
- Build SGDK/Wine aprovado, ROM
  `30c7eb6fb2b1c66a9cbe092a49055395cc6b2e61bc34cfcb420a78a0069641f0`;
  suíte host/estática 14/14. Captura de colisões no emulador ainda pendente.

- Percurso exploratório recapturado com o mesmo SHA em
  `out/emulator_evidence/visual_ko_20260915T045157Z/`; o manifesto confirma
  título, seletor, luta e amostras de KO. A sessão não substitui a revisão
  visual do palco quadriculado nem captura crítica de áudio/VDP.

## 2026-09-15 - chip de projétil no consumidor central (P04)

- O caminho de defesa de projétil agora emite `GUARD` antes de aplicar o chip;
  o delta passa pelo mesmo consumidor central de vida usado pelos golpes
  corporais, preservando clamp, resultado e deduplicação.
- Build SGDK/Wine aprovado, ROM
  `54333ae8109bb499dab9a3fae109e2886c313dceb0e1c698cbda8f0b4e7f6dcb`;
  suíte host/estática 14/14 em
  `out/logs/continuation_p04_projectile_chip_suite.log`.
- A captura anterior permanece histórica (SHA anterior); nova captura de
  emulador será vinculada antes de qualquer conclusão visual.
- Captura exploratória atualizada em
  `out/emulator_evidence/visual_ko_20260915T045548Z/`, com manifesto vinculado
  ao SHA `54333ae8109bb499dab9a3fae109e2886c313dceb0e1c698cbda8f0b4e7f6dcb`.

## 2026-09-15 - tipo THROW explícito no ledger (P04)

- Agarrões aceitos nos estados 801/802 agora emitem `COMBAT_EVENT_THROW`,
  mantendo `source=THROW`. O consumidor trata THROW como acerto confirmado para
  combo e medidor, enquanto GUARD permanece separado.
- O cálculo fixo de medidor foi generalizado para HIT/THROW; nenhum ganho novo
  é criado fora do evento emitido.
- Build SGDK/Wine aprovado, ROM
  `dfdb6cb181c22f9d3e151a694abdad3cf0a66ca1ec3b0664c9a346b3e3e3b3cd`;
  suíte 14/14 em `out/logs/continuation_p04_throw_kind_suite.log`.
- Captura exploratória atualizada em
  `out/emulator_evidence/visual_ko_20260915T050018Z/`, vinculada ao mesmo SHA;
  não constitui aprovação visual, auditiva ou de budget.

## 2026-09-15 - refinamento medoid do cenário Showdown (P08)

- O conversor de 768 tiles mantém representantes nativos de 8×8, mas executa
  quatro passagens de refinamento Lloyd/medoid após a inicialização farthest;
  não cria pixels artificiais nem aumenta o orçamento de VRAM.
- O erro RGB médio caiu de `199.9134` para `177.0296`, com 768 tiles únicos,
  14 cores opacas e a mesma origem autoral declarada.
- Build aprovado, ROM
  `93c94843df3843628ac8d32fedf24edbcf50bc9660122cd4c0bf9c4ef72763f0`;
  captura em `out/emulator_evidence/visual_ko_20260915T050519Z/`.
- A melhoria é candidata: a captura ainda mostra reutilização de tiles visível;
  revisão visual independente e budget VDP permanecem pendentes.

## 2026-09-15 - consumidor central de vida (P04)

- `CombatEvent` passou a carregar o delta de vida resolvido. A primeira
  atualização `EnergyType==1` após HIT/GUARD é consumida depois da FSM;
  duplicatas no mesmo evento não aplicam dano novamente.
- O comportamento de KO, clamp `0..96` e fallback sem evento foi preservado.
- Build SGDK 2.11 aprovado, ROM
  `b0734777882bffb18e2ea2b01ae9eeb0329583b9e665ab04abb4ac6faa4f1441`;
  suíte host/estática 14/14. O caso simultâneo foi incluído no contrato de
  vida para garantir associação por defensor, não apenas pelo último evento.
- Resultado do round, reset simétrico e prova instrumentada no emulador ainda
  permanecem pendentes.

## 2026-09-15 - manifesto de captura sem configuração Flatpak

- `tests/capture_visual_ko.py` registra configuração ausente como `null` em vez
  de abortar no final da sessão. A captura atual foi vinculada ao mesmo SHA da
  ROM e contém manifesto, telas e vídeo em
  `out/emulator_evidence/visual_ko_20260915T043123Z/`.
- Isso é evidência exploratória de percurso; não aprova visual, áudio, VDP,
  runtime probe ou pior-frame.

## 2026-09-15 - resultado do evento e reset explícito (P04)

- `CombatEvent.result` registra `HIT` ou `KO` após o consumidor aplicar a vida;
  `COMBAT_EVENTS_RESET()` limpa a fila no início de cada inicialização de luta.
- O contrato cobre HIT, KO, guard, simultaneidade e reset explícito; suíte
  host/estática 14/14.
- Build SGDK 2.11 aprovado, ROM
  `e4a85eed0a4c297e13607e76da314ac62b8823e731c26c5b2530599112070e87`.
- A captura exploratória foi repetida e vinculada ao mesmo hash em
  `out/emulator_evidence/visual_ko_20260915T044013Z/`; as capturas anteriores
  permanecem históricas.

## 2026-09-15 - deduplicação do ledger de combate (P04)

- O ledger suprime eventos HIT/GUARD duplicados da mesma combinação
  atacante/defensor/estado/tipo no mesmo tick; a segunda observação não cria
  outro combo nem outro ganho central de medidor.
- O índice do evento original continua recebendo o delta legado apenas como
  telemetria de migração. Dano e resultado permanecem na rota legada nesta
  etapa.
- Build SGDK 2.11 aprovado, ROM
  `daa412775ec319764be97c59acb7cd58922db2c75a788900999e51c59a5bcb32`;
  suíte host/estática 13/13.
- Evidência exploratória vinculada: `out/emulator_evidence/visual_ko_20260915T041529Z/`;
  revisão visual, VDP/runtime e budget continuam pendentes.

## 2026-09-15 - contador de hits (P06, primeiro corte)

- Acertos físicos e de projétil agora incrementam o contador do atacante;
  colisões simultâneas contam para ambos.
- HUD mostra `N HITS` no BG_A, linha 21, com o atlas de mensagens e sem novos
  sprites. O valor é limpo abaixo de dois hits e segue o reset de estado neutro.
- Build aprovado, ROM `a85cb58f91a5bcfd71c53f88eeae0f12b1253df3dfcdd07d70d3aef157879639`.
- Multi-hit real e revisão visual no emulador continuam pendentes.

## 2026-09-15 - toggles de especial e combo

- `OPTIONS` ganhou `SPCL ON/OFF`, `HITS ON/OFF`, `TBG ON/OFF` e `RULES ON/FREE`, todos
  ligados a efeitos reais; a paginação permanece em cinco itens por página.
- `SPECIAL OFF` oculta a barra, `HITS OFF` oculta somente o texto e `RULES FREE`
  libera 700/730 sem custo.
- Build aprovado, ROM
  `134dfd0980f306ed35ab02454baeb072bd087ea2a0077382e2862a462ea4207d`.
- Rotas de menu e revisão visual ainda pendentes no emulador.

## 2026-09-15 - pool de dois cenários

- `STAGE2 ON/OFF` entrou em OPTIONS. No seletor, P1 alterna `SHOWDOWN`/`BGB2`
  com `C`; OFF força o primeiro cenário.
- A seleção usa os ramos existentes `gfx_showdown` e `gfx_bgb2`. BGB2 segue
  provisório (duas cores) e não é promovido como arte final.
- Contratos de cena/regressão foram atualizados; captura real e revisão visual
  continuam pendentes.

## 2026-09-14 - primeiro corte da barra de especial (P05)

- `energiaSP` deixou de ser caminho inerte: atualizações `EnergyType==2` agora
  usam a faixa fechada `0..32`, com clamp contra underflow/overflow.
- A barra é desenhada no BG_A com oito células de 16×8 reutilizadas, sem criar
  16 sprites adicionais nem faixa preta; células vazias usam tile 0 e deixam o
  cenário visível.
- O custo de especial é cobrado uma única vez ao aceitar os estados 700/730;
  o buffer apenas guarda a transição e não cobra novamente.
- Build SGDK 2.11/Wine passou (`exit_code=0`), ROM
  `39e48a8ca8e9a525ec013fc05c0afaf550b14dbcf955db462688ca52339a6b52`.
- Suíte host/estática executada individualmente: 7/7 passou, incluindo
  `tests/test_special_bar_contract.py`.
- Pendente antes de promover P05: custo único de especial, toggle de HUD,
  captura no emulador e revisão visual independente.

## 2026-09-14 - repaginação e validação P03

- Repaginado o front-end para uma geometria única: painel na linha 13, cinco
  itens por página e página derivada de `cursor / 5`; o logo HAMOOPIG fica
  preservado no BG_B.
- `OPTIONS` agora cobre SFX, MUSIC, LIFE, CLOCK, TIME, DEBUG, DEFAULTS e BACK;
  DEBUG mantém nove itens em duas páginas. `LIFE OFF`/`CLOCK OFF` têm efeito
  dentro da luta e `MUSIC ON` retoma BGM na borda da preferência.
- INTRO/FADE permanecem internos em `GameConfig` e não são expostos como opções
  inertes sem persistência ou retorno observável ao título.
- ROM verificada: `out/rom.bin`, sha256
  `3e46ac068062cfa83f305e85dd66b0c5822bcedd48766749e3a36c74e3ea1841`;
  HEAD `2eee6522`. Contratos `tests/test_*.py` executados individualmente:
  6/6 passaram. Evidências de menu: `out/emulator_evidence/p03_menu_final`,
  `p03_options2` e `p03_efeito`.
- Revisão visual independente e escuta crítica ainda pendentes; teto permanece
  `prototype`.

## 2026-09-14 - plano de evolução para modelo de engine

- Registrado plano em `doc/engine/fighting_engine_improvement_plan.md` com 12 etapas,
  contratos de especial/combos/configuração, separação abertura→título, timing,
  HUD transparente, dois cenários e documentação de extensão.
- Criado `doc/engine/fighting_engine_roadmap.json` com dependências e eixos de
  evidência separados para agentes com e sem visão.
- Revisão de fontes/atlas e validação de contexto/higiene; sem alteração de C/assets/ROM
  e sem nova execução de emulador. Melhorias propostas continuam `planejado`.

## 2026-09-14 - tela de titulo e menu OPTION

- `gRoom==1` deixou de avançar automaticamente após dois segundos e agora possui menu persistente `START`/`OPTION`.
- `OPTION` alterna `SFX ON/OFF` e `MUSIC ON/OFF`, com `BACK`; as preferências permanecem durante a sessão e controlam `FUNCAO_PLAY_SND` e o BGM de combate.
- P1 usa D-pad, A/START e B; P2 não interfere no front-end. A fonte `message_font` é reutilizada em células 16×16 e o cursor custa um tile.
- Build SGDK 2.11/Wine aprovado: ROM `out/rom.bin`, 2.490.368 bytes, sha256 `b77300943f5739f34010a39f877afce716da1658bd0e7eef5d115e4584bc36d9`.
- Evidência visual/áudio do menu ainda deve ser capturada no BlastEm; teto permanece `prototype`.

## 2026-09-12 - correções persistentes HUD, cenário e Musgo

- Energia zero agora apaga as 16 colunas de cada barra e a atualização ocorre durante o congelamento de KO.
- Showdown usa a reconstrução do laboratório `_agent_training/[ESTUDO]_mugen_sff_showdown_v1/work/reconstructed_viewports/frame_0000_viewer_default.png`, 14 cores e 604 tiles; o mundo completo não deixa vazio no scroll.
- Musgo em estado 570 é ancorado no piso e reaproveita 550. O derivado de derrota foi quarentenado após `ADDRESS ERROR` no emulador.
- Texto pós-luta recebe PAL2, prioridade alta e espaçamento; fidelidade integral à fonte autorada continua pendente.
- ROM final desta iteração: `62df66bc9aa96d0e61d8b94742b2d14423e29b7a616a4df32ee27a1c68127827`. BlastEm 61.2 fps sem crash no percurso observado: `out/emulator_evidence/interactive-round-integrity-20260912T072145Z/`.

## 2026-09-12 - integridade de round e encerramento da partida

- Corrigida a cópia de paletas para slots CRAM de 16 cores, eliminando a escrita além de `palette[64]`; corrigidos também facing do especial P2 e uso de profundidade não inicializada.
- Removido o piso temporário de energia que impedia KO. Implementados melhor de três, empate por tempo sem ponto, reset integral em fase de commit (`gRoom==12`) e tela pós-luta (`gRoom==11`).
- `CLEAR_VDP` invalida handles liberados; chamadas sensíveis de sprite verificam `NULL`; reset cobre física, input, projéteis, sparks, HUD e relógio.
- A/START permanecem disponíveis no menu pós-luta mesmo com `gPodeMover==0`; START retorna ao seletor. A revanche existe no código, mas ainda não foi exercitada no emulador.
- ROM final: 2.490.368 bytes, sha256 `2a2ce843cebb1a756f460f0274b6b02b3ad3c9f5a796df41d7087d4f81cac559`. BlastEm 60.2 fps: `out/emulator_evidence/interactive-round-integrity-20260912T064603Z/` prova KO natural, reset, segunda vitória, pós-luta e retorno ao seletor.
- Time-over/empate e reset limpo foram observados no binário anterior à correção isolada do input pós-luta: `out/emulator_evidence/interactive-round-integrity-20260912T063457Z/`.
- Ícone solto movido para `rascunho/upstream_reference/hamoopig_icon.png`; validadores de contexto, higiene e metodologia sem blockers. Teto permanece `prototype`.

## 2026-09-11 - palco Showdown park + camera H/V

- GIF `xmen-vs-streetfighter-stage-showdown-at-the-park.gif` copiado para `data/source_art/showdown/` com `showdown.def`. Capcom XMvSF = estudo/placeholder (mesmo teto do Ken).
- Builder `convert_showdown.py`: 512x256, bloco 4px, 10 cores 9-bit, 444 unique tiles. `IMAGE gfx_showdown` em BG_B PAL0 (`compare_flat`). Unique nativo ~3191 nao cabe; 4 paletas ja ocupadas.
- Camera: H no ponto medio dos lutadores, clamp 0…192. V `camPosY = max(air)/2` clamp 0…32 (`verticalfollow 0.5` do `.def`). Rest `vscroll=32` (chao no viewport 224). Pulo revela ceu. Lutador/sombra/spark/fireball usam `+camPosY`.
- Parallax BG0/BG1/BG2/BG3 gravado em `doc/art/showdown/camera_motion_contract.json`, nao executado.
- ROM sha256 `1eb99f6c33cc6fe1c7fb776f5635f31b453a6419f27ff77cd4a215db9e6b00d6`. BlastEm 59.6 fps: `out/emulator_evidence/interactive-showdown-20260911T225648Z/` idle/walk H/jump V/hit. Prototype.
- Aprendizado: `doc/agent_learning/showdown_stage_lessons.md`. `canonical_promotion_performed=false`.

## 2026-09-11 - relogio no WINDOW

- Digitos `spr_n*` saiam do AUTO_VRAM com dois grappler. Agora `ts_hud_clock` (n0–n9, 160x16, index 0→11) no WINDOW rows 3-4, cols 18-21. `VDP_setWindowOnTop(5)`. `ClockL`/`ClockR` nao spawnam.
- ROM sha256 `a53bc06beba88ace362e8e4b226c5db0d22cb4a18a8c10cc7b818d11afec1561`. BlastEm 61.1 fps: `out/emulator_evidence/interactive-musgo-fight-20260911T221658Z/01_idle_hud.png` (98) e `06_hit.png` (89) com dois Musgos. Prototype.

## 2026-09-11 - barra P1 no WINDOW

- Dois Musgos no idle expulsavam o sprite 128px da barra P1 (`AUTO_VRAM`). P1 passou para o mesmo contrato da P2: `TILESET` NONE/NONE, `VDP_setWindowOnTop(2)`, PAL1 prio FALSE, index 0→11.
- `ts_hud_p1_bar` cols 1-16 (esvazia pela direita, rumo ao KO). `hud_window_load/init/update/off` dono das duas barras. GE[3]/GE[5] nao spawnam. Lag vermelho continua omitido.
- ROM sha256 `77ea0cdd2433881b16d515ef5dd7af0e2c48475c987dc75cefdc6ff61202f8bc`. BlastEm 60.3 fps: `out/emulator_evidence/interactive-musgo-fight-20260911T220349Z/01_idle_hud.png` — amarelas nos dois lados no idle. Prototype.

## 2026-09-11 - Musgo grappler original (id=3)

- Personagem autoral Musgo (monstro do pantano) entra no roster como `id==3`. A sheet CPS2 de grappler pesado foi ancora tecnica de massa/timing/cell, nao fonte de pixel nem IP.
- Concept + idle de perfil + ciclos video-first em `data/source_art/musgo/`. Converter `convert_musgo.py` gera strips 9-bit, index 0 magenta, idle 80x104 (maior que Ken 64x96), walk 88x104, slam 88x120, teto 128. Arte olha para a direita.
- Runtime: `PLAYER_STATE_MUSGO` / `inc/player_musgo_table.h` / `res/musgo.res`. Hitboxes case 3 (active no ultimo/unico quadro). Gravidade 550 igual ao Ken. Paletas PAL2/PAL3 via `FUNCAO_APPLY_FIGHTER_PALETTE`. MODE cicla Ryo->Ken->Musgo. Seletor LEFT/RIGHT pelos 3; default P2=Musgo. SFX reusa GPL HAMOOPI. 700 e slam, sem fireball.
- Claim: `source_candidate` / prototype. Nao e pixel nativo final nem AAA. Idle ~7-9 HW sprites / ~95-100 tiles por frame.
- ROM 2.490.368 B, sha256 `c81fee9f9f7b799f30514418f01ceeb8d293788c51b5b6c89fb4376964e98589`. Seletor observado no BlastEm: `out/emulator_evidence/blastem-linux-20260911T212135Z-1769103/screenshot.png` (P1 Ryo, P2 Musgo). Bundle canonico bloqueado sem VDP dump; luta ainda sem captura.
- Aprendizado local capturado: caderno `doc/agent_learning/musgo_roster_lessons.md`; ledger 57 licoes; `canonical_promotion_performed=false`. Capture nao editou `.agent`.
- Palco BlastEm 61.1 fps, mesma ROM: `out/emulator_evidence/interactive-musgo-fight-20260911T214421Z/` — P1/P2 Musgo, walk, jump aereo, jab com spark. P1 barra some no idle (AUTO_VRAM de 2x ~100 tiles); P2 WINDOW ok. Prototype.

## 2026-09-11 - barra P2 em WINDOW/tiles

- Sprite 128px da barra direita continuava sumindo (H40 320 px/scanline e/ou pool AUTO_VRAM 1532-1951). P2 amarela passou para o plano WINDOW.
- `VDP_setWindowOnTop(2)`, tiles depois do BG em `gInd_tileset`, PAL1 prio FALSE (sprites de P1/KO/relogio por cima). Faixa preenchida com index 11 (preto); tile 0 do PNG remapeado porque plano nao tem transparencia de sprite.
- GE[4]/GE[6] nao spawnam. Deplecao = colunas esquerdas da barra P2 trocadas pelo tile preto (`hud_frame_for`). `hud_p2_window_off()` no `CLEAR_VDP`.
- ROM sha256 `21f1654d076b072d5bdb5710994df0f45ef037be99268d77a533fc94845eb575`. Evidencia BlastEm 59.9 fps: `out/emulator_evidence/interactive-hud-p2-window-20260911T170914Z/00_hud_both.png` — barras amarelas nos dois lados + KO. Prototype, nao AAA.

## 2026-09-12 - orientações Discord para revisão futura da engine

- Lidos `#ff-rheo-bout` e 14 canais complementares do RETRODEVBR (histórico, exemplos e anexos).
- Registradas orientações atribuídas ao desenvolvedor original GameDevBoss/Daniel Moura e complementos comunitários, com autoria separada.
- Conteúdo consolidado em `doc/engine/discord_guidance_original_engine_review_2026-09-12.md`.
- Backlog definido: resolução/paleta, tilesets e tilemaps, `gInd_tileset`, `SPR_initEx`, fronteiras de VRAM, ciclos/camadas, áudio, animações, manuais e validação em BlastEm/Gens KMod/ClownMDEmu.
- Nenhum código, asset, ROM ou claim de entrega foi alterado.

## 2026-09-11 - sombra, queda Ken, HUD P2 ainda aberto

- Sombra: `sombra.png` usava indices da paleta antiga; PAL1 agora e HUD amarelo/vermelho, virava blob no chao. Pixels opacos remapeados para index 11 (preto da PAL1). VRAM da sombra em 1460 (fora do pool 1532-1951).
- Queda: Ken 550 nao setava `gravidadeY`/`impulsoY`; a fisica faz `impulsoY -= 1` e o lutador subia e sumia. Agora 550 inicia como o Ryo (`impulsoY=-14`, `gravidadeY=3`). Pulo Ken 300 ultimo quadro 99 (antes encerrava no ar).
- HUD: barra vermelha some com vida cheia (H40 320 px/scanline). P2 passou a ter strip espelhada (sem `SPR_setHFlip` no metasprite 128px). HUD spawna depois dos lutadores com AUTO_VRAM.
- Barra da direita **ainda nao aparece** na evidência (P1+KO sim). Proximo: encolher barras ou WINDOW/tiles.
- ROM sha256 `aa17b5b70507100ebb291dd83ae47e37e44d00973fa39f805ccdbaf170dbadbc`. Evidencia `out/emulator_evidence/interactive-hud-shadow-fall-20260911T163434Z/`. Prototype.

## 2026-09-11 - paleta no reset + hitbox/golpes do Ken

- Soft reset do emulador (BlastEm Tab = `ui.soft_reset`) nao zerava a RAM 68k: CRAM limpava, `gFrames`/`gRoom` sobreviviam, `FUNCAO_INICIALIZACAO` nao recarregava PAL2/PAL3. `int main(bool hardReset)` agora chama `SYS_hardReset()` quando `!hardReset` (SGDK 2.11 `sys.h` / sample platformer).
- Paletas da luta passam por `FUNCAO_APPLY_FIGHTER_PALETTE` em vez dos `if` duplicados.
- Ken (`id==2`) nao tinha `case` em `FUNCAO_FSM_HITBOXES`: sem hurtbox nem hitbox. Case 2 alinhado aos strips curtos (`101`/`104` 1 quadro, `102`/`106`/`151` 2, `105` 3). Close 152/154/155 aliasam 102/104/105. Jab/kick 1 quadro held em 8 frames.
- ROM 1.966.080 B, sha256 `c0a084e4a3340d1086b89bad6225641cd0a14d1c170b4f69e53f9888fae38168`.
- Evidencia BlastEm 59.8 fps: `out/emulator_evidence/interactive-ken-hit-reset-20260911T155121Z/` — `05_ken_attack.png` chute do Ken com spark; `07_after_soft_reset.png` title fade apos Tab; `11_fight_after_reset.png` Ryo+Ken paletas corretas apos reset. Prototype.

## 2026-09-11 - Ken frente, HUD SF, seletor

- Ken: a sheet arcade olha para a esquerda; cada frame foi `FLIP_LEFT_RIGHT` no converter para o padrao HAMOOPIG (Ryo olha para a direita). P1 Ken passa a encarar o oponente.
- HUD: sheet SF (shezzor) fatiada em barra amarela (`energiaBase`), vermelha (`energia` atrasada) 128x16 / 13 frames, e KO 48x24. Spawn em GE[3..7] com VRAM fixa 1600+. P2 usa HFlip. `res/hud_gfx.res`.
- Seletor: `gRoom==2` depois do title. Esquerda/direita troca Ryo/Ken, A confirma, Start do P1 fecha P2 com a escolha atual. Defaults P1=Ryo P2=Ken.
- palID 0 nao carregava paleta do lutador (CRAM lixo / verde-azul). Select agora grava `cursorP*ColorChoice`; init trata 0 como pal1.
- ROM 1.966.080 B, sha256 `ff1c205b9d574c5e2af3c4b372e3326563a58eb0bb3a4521dbe8a8ac7cbecac4`.
- Evidencia: `out/emulator_evidence/interactive-hud-select-20260911T151757Z/` (select + barras/KO). FPS nesta cena ~41–55. Prototype.



## 2026-09-11 - Ken arcade nativo + BGM Ken Stage + MODE

- Personagem Ken incluido a partir da sheet arcade `ken_arcade_st_v1.png` (1549x11279, sha256 `23ae9176...`), copiada para `data/source_art/ken_arcade/`. Sem o shrink 32x64 do MSSF2T SMS. Idle 64x96, especiais ate 128x128, paleta compartilhada 15 cores 9-bit, magenta index 0. Builder `convert_ken_arcade.py`; `res/ken.res` 116 KB packed.
- Runtime: `P[].id==2` via `PLAYER_STATE_KEN` / `ken_anim_for()`; especiais QCF/DP do Ryo tambem no Ken; sem fireball `spr_ryo_701` para id==2; SFX reusa GPL do HAMOOPI.
- MODE/SELECT: `JOY_MODE` sozinho em gRoom==10 cicla Ryo<->Ken no pad; MODE+START permanece debug. BlastEm default.cfg: tecla `f` = pad1 MODE.
- Musica: MIDI vgmusic Ken Stage (30751 B, sha256 `44804801...`) transcrito para VGM NTSC 9333 B (YM2612 3ch + PSG noise, 16 compassos @ 90 BPM, sem PCM). `XGM bgm_ken_stage` no driver XGM1 ja usado pelo projeto.
- ROM: 1.441.792 B, sha256 `62befee38c53603c166f3eb1703be47b308320eb91e163dc1f01e5ef13971f7a`.
- Evidencia BlastEm: `out/emulator_evidence/interactive-ken-mode-20260911T144506Z/` — screenshot Ken apos MODE, ~60 fps. Audio disk nao-silencioso em `...144351Z/audio.raw`. Relogio HUD pode sumir apos o spawn do Ken (AUTO_VRAM_ALLOC vs indices fixos).
- Aprendizado local: `rascunho/ken_integration_technical_conditions.json`. `canonical_promotion_performed=false`. Teto prototype; sheet/MIDI Capcom/vgmusic nao sustentam claim comercial.

## 2026-09-10T17:11:35.6659733Z - bootstrap

- projeto criado a partir da estrutura canonica
- historico de ROM, hashes e evidencia do modelo removido
- status inicial: documentado; nao buildado; nao testado em emulador
- proximo gate: classificar contexto e metodologia

## 2026-09-10 - porta SGDK 2.11 (porta direta de SGDK_Engines/HAMOOPIG-SGDK)

- materializado `new_project.sh` (estrutura canonica completa) e classificado como `technical_demo` com ceiling `prototype`
- copiados 11 .c (src/) e 11 .h (inc/) do upstream, byte-idempotentes (verificados com cmp)
- `res.zip` upstream extraido para res/ (70 pngs; gfx.res/sprite.res/sound.res) sem junk e sem headers gerados
- sound.res upstream vazio substituido por placeholder: 17 PCM silenciosos XGM 800 amostras @16kHz (player.c/fsm.c/main.c exigem os simbolos snd_*); registro em rascunho/upstream_reference/sound_placeholder_manifest.json
- fix_migration_issues.ps1: 10 reescritas aplicadas; 8 revertidas como falso-positivo (sprite.h/sound.h aqui sao headers de RECURSO rescomp, nao de engine); mantidas VDP_showFPS_1to3 e SPR_init_args_to_void
- material upstream de referencia (README, docs, Makefile, Doxyfile, CI, web, res.zip) arquivado em rascunho/upstream_reference/
- Makefile Docker upstream nao portado: build passa a ser tools/sgdk_wrapper/build.sh (SDK sdk/sgdk-2.11)
- build: rota Wine flatpak → out/rom.bin 917.504 bytes, wine_bridge_status=buildado
- boot BlastEm 0.6.2 NTSC via wrapper canonico de captura: arena de luta a 60 fps (evidencia em out/emulator_evidence/blastem-linux-20260910T192043Z-1434440/ — screenshot, save.sram, log, session_runtime)
- status: buildado e bootado em emulador (boot only; input nao exercitado; audio placeholder declarado)

## 2026-09-10 (2) - header de ROM real + gameplay basico provado

- src/boot/rom_head.c: domestic/overseas "(HAMOOPI MD PORT BY HUMBERTODIAS)" e copyright "(C)GAMEDEVBOSS26" (antes SAMPLE PROGRAM); rebuild limpo (ROM sha256 558bea6c...)
- sessao interativa de input (out/emulator_evidence/interactive-20260910T195804Z/): xdotool -> gamepad 1; P1 anda com scroll de camera, golpes A/B animam, 60 fps sustentados; manifest com sequencia de inputs e limites de claim
- status: gameplay basico provido (movimento/golpe/camera); dano/HUD, fim de round e audio continuam nao provados

## 2026-09-11 - complementar o que o res.zip nao trazia

- PCM: placeholders silenciosos substituidos por WAV GPL do HAMOOPI (Daniel Moura), 16 kHz 16-bit mono, mapeados aos 17 `snd_*`; `FUNCAO_PLAY_SND` descomentado para P1/P2 id=1; `Z80_loadDriver(Z80_DRIVER_XGM)` no boot
- HUD relogio: `spr_n0..n9` convertidos de `system/spr_num_*.pcx`, remapeados a PAL1 16x16; `FUNCAO_RELOGIO` ligado com `SPR_releaseSprite` NULL-safe e spawn inicial 99
- sombra: `spr_sombra` 64x16 composto do frame de `ryo/100.png`; spawn em `FUNCAO_INICIALIZACAO` e follow em `FUNCAO_SPR_POSITION`
- docs: README e visao-geral deixam de ser o template; engine docs copiados para `doc/engine/`
- barras de energia GE[3..6] continuam sem sprite de HUD (codigo ja no-op se GE.sprite e NULL)
- rebuild Wine 2026-09-11: `out/rom.bin` 917.504 bytes, sha256 `6e5e846e7bc3f8393ba7b9e26639fe5806ebb95101252e76b8551ad521b40ca9`; sound.res 160 KB PCM XGM
- captura BlastEm 2026-09-11 (`out/emulator_evidence/blastem-linux-20260911T140738Z-109961/`): screenshot com relogio `99` e sombra no chao, 60.0 fps no titulo; bundle AAA rejeitado por VDP dump ausente; audio_driver=dummy nesta rota
- status: buildado + boot observado na ROM nova; audio nao provado por escuta (driver dummy)


## Curadoria local — 2026-09-11

Analise registrada em `doc/curation/2026_09_11/curadoria_hamoopig.md`. Confirmados estaticamente: copia de paleta ultrapassa palette[64] por 4 bytes; facing de especial P2 compara x consigo; round restart vazio. Prioridade: integridade, round completo e provas simetricas antes de ampliar roster. Contexto planning passou; higiene bloqueada pelo icone da raiz. Nenhum C/asset/ROM alterado, nenhuma nova execucao BlastEm, nenhuma promocao canonica. ROM preservada: `1eb99f6c33cc6fe1c7fb776f5635f31b453a6419f27ff77cd4a215db9e6b00d6`.
## 2026-09-12T09:18:42.3760666-03:00 - Correção da animação final de derrota do Musgo

## 2026-09-14 - P00/P01/P02 executados

- P00: vinculo fonte->ROM PROVADO. Rebuild a partir de artefatos limpos deu ROM
  bit-identica (`e2ca5833...be0f4`); o build e deterministico. Ressalva:
  `library_rebuild=false`, entao vale para as fontes do projeto, nao para a cadeia toda.
- P00: decoder HPRB endurecido. Quatro defeitos, tres produzindo FALSO VERDE --
  bloco truncado, par schema/size cruzado e `samples==0` eram aceitos com
  `decision='cabe'`. Agora ha `--self-check` com fixtures positivas e negativas.
- P01: `inc/timing.h`/`src/timing.c`. Logica passa a 60 ticks/s nas DUAS regioes
  (PAL alterna 1,1,1,1,2). Antes PAL rodava 17% mais lento. Relogio de round
  passou de 38 para 60 ticks por unidade: uma unidade agora e um segundo real.
- P01: o modo `TICK 50` era o defeito oferecido como opcao; virou perfil LEGACY,
  explicitamente de diagnostico.
- P01: o pico de DMA de 8448 B contra envelope NTSC de 7782 NAO e frame de combate.
  E o frame de CARGA da cena, dominado pelo tilemap 512x256 de `FUNCAO_INICIALIZACAO`.
  Confirmado nas duas regioes (frames 271 e 226, razao 1,199 = 1,2).
- P02: `inc/scene.h`/`src/scene.c`. As 8 trocas de cena migraram para
  `SCENE_request`/`SCENE_commit`; a convencao posicional de `gFrames=0/1` morreu.
- P02: abertura virou cena propria (`opening.c`), com fade in/hold/fade out. Os
  creditos agora aparecem inteiros, em vez de ficarem atras do painel do menu.
- P02: corrigido painel de titulo sem letras -- `PAL_fadeIn` levava PAL1 a preto
  porque `palette[]` nao continha as quatro paletas.
- Pendente e declarado: arte propria do titulo sem creditos embutidos; revisao de
  suavidade dos fades; harness de replay deterministico.


- Task: Correção da animação final de derrota do Musgo
- Asset snapshots:
  - room_0_bga -> v001 (/res/gfx/room_0_bga.png)
  - room_0_bgb -> v001 (/res/gfx/room_0_bgb.png)
  - gfx_bgb1 -> v001 (/res/gfx/bgb1.png)
  - gfx_bgb2 -> v001 (/res/gfx/bgb2.png)
  - gfx_showdown -> v001 (/res/gfx/showdown.png)
  - spr_hud_energy_y -> v001 (/res/sprite/hud/energy_yellow.png)
  - spr_hud_energy_r -> v001 (/res/sprite/hud/energy_red.png)
  - spr_hud_energy_y_p2 -> v001 (/res/sprite/hud/energy_yellow_p2.png)
  - spr_hud_energy_r_p2 -> v001 (/res/sprite/hud/energy_red_p2.png)
  - spr_hud_ko -> v001 (/res/sprite/hud/ko.png)
  - ts_hud_p1_bar -> v001 (/res/sprite/hud/energy_yellow_p1_window.png)
  - ts_hud_p2_bar -> v001 (/res/sprite/hud/energy_yellow_p2_window.png)
  - ts_hud_clock -> v001 (/res/sprite/hud/clock_digits_window.png)
  - spr_ken_pal1 -> v001 (/res/sprite/ken/palettes/pal1.png)
  - spr_ken_pal2 -> v001 (/res/sprite/ken/palettes/pal2.png)
  - spr_ken_100 -> v001 (/res/sprite/ken/100.png)
  - spr_ken_101 -> v001 (/res/sprite/ken/101.png)
  - spr_ken_102 -> v001 (/res/sprite/ken/102.png)
  - spr_ken_104 -> v001 (/res/sprite/ken/104.png)
  - spr_ken_105 -> v001 (/res/sprite/ken/105.png)
  - spr_ken_106 -> v001 (/res/sprite/ken/106.png)
  - spr_ken_151 -> v001 (/res/sprite/ken/151.png)
  - spr_ken_200 -> v001 (/res/sprite/ken/200.png)
  - spr_ken_201 -> v001 (/res/sprite/ken/201.png)
  - spr_ken_300 -> v001 (/res/sprite/ken/300.png)
  - spr_ken_420 -> v001 (/res/sprite/ken/420.png)
  - spr_ken_501 -> v001 (/res/sprite/ken/501.png)
  - spr_ken_550 -> v001 (/res/sprite/ken/550.png)
  - spr_ken_606 -> v001 (/res/sprite/ken/606.png)
  - spr_ken_700 -> v001 (/res/sprite/ken/700.png)
  - spr_ken_710 -> v001 (/res/sprite/ken/710.png)
  - spr_ken_720 -> v001 (/res/sprite/ken/720.png)
  - spr_ken_730 -> v001 (/res/sprite/ken/730.png)
  - spr_musgo_pal1 -> v001 (/res/sprite/musgo/palettes/pal1.png)
  - spr_musgo_pal2 -> v001 (/res/sprite/musgo/palettes/pal2.png)
  - spr_musgo_100 -> v001 (/res/sprite/musgo/100.png)
  - spr_musgo_101 -> v001 (/res/sprite/musgo/101.png)
  - spr_musgo_102 -> v001 (/res/sprite/musgo/102.png)
  - spr_musgo_104 -> v001 (/res/sprite/musgo/104.png)
  - spr_musgo_105 -> v001 (/res/sprite/musgo/105.png)
  - spr_musgo_106 -> v001 (/res/sprite/musgo/106.png)
  - spr_musgo_151 -> v001 (/res/sprite/musgo/151.png)
  - spr_musgo_200 -> v001 (/res/sprite/musgo/200.png)
  - spr_musgo_201 -> v001 (/res/sprite/musgo/201.png)
  - spr_musgo_300 -> v001 (/res/sprite/musgo/300.png)
  - spr_musgo_420 -> v001 (/res/sprite/musgo/420.png)
  - spr_musgo_501 -> v001 (/res/sprite/musgo/501.png)
  - spr_musgo_550 -> v001 (/res/sprite/musgo/550.png)
  - spr_musgo_606 -> v001 (/res/sprite/musgo/606.png)
  - spr_musgo_700 -> v001 (/res/sprite/musgo/700.png)
  - spr_musgo_710 -> v001 (/res/sprite/musgo/710.png)
  - spr_musgo_720 -> v001 (/res/sprite/musgo/720.png)
  - spr_musgo_730 -> v001 (/res/sprite/musgo/730.png)
  - spr_point -> v001 (/res/sprite/point.png)
  - spr_rect_bb -> v001 (/res/sprite/spr_rect_bb.png)
  - spr_rect_hb -> v001 (/res/sprite/spr_rect_hb.png)
  - spr_spark0 -> v001 (/res/sprite/spr_spark0.png)
  - spr_spark1 -> v001 (/res/sprite/spr_spark1.png)
  - spr_spark2 -> v001 (/res/sprite/spr_spark2.png)
  - spr_spark3 -> v001 (/res/sprite/spr_spark3.png)
  - spr_n0 -> v001 (/res/sprite/hud/n0.png)
  - spr_n1 -> v001 (/res/sprite/hud/n1.png)
  - spr_n2 -> v001 (/res/sprite/hud/n2.png)
  - spr_n3 -> v001 (/res/sprite/hud/n3.png)
  - spr_n4 -> v001 (/res/sprite/hud/n4.png)
  - spr_n5 -> v001 (/res/sprite/hud/n5.png)
  - spr_n6 -> v001 (/res/sprite/hud/n6.png)
  - spr_n7 -> v001 (/res/sprite/hud/n7.png)
  - spr_n8 -> v001 (/res/sprite/hud/n8.png)
  - spr_n9 -> v001 (/res/sprite/hud/n9.png)
  - spr_sombra -> v001 (/res/sprite/hud/sombra.png)
  - spr_ryo_pal1 -> v001 (/res/sprite/ryo/palettes/pal1.png)
  - spr_ryo_pal2 -> v001 (/res/sprite/ryo/palettes/pal2.png)
  - spr_ryo_000 -> v001 (/res/sprite/ryo/000.png)
  - spr_ryo_100 -> v001 (/res/sprite/ryo/100.png)
  - spr_ryo_101 -> v001 (/res/sprite/ryo/101.png)
  - spr_ryo_102 -> v001 (/res/sprite/ryo/102.png)
  - spr_ryo_103 -> v001 (/res/sprite/ryo/103.png)
  - spr_ryo_104 -> v001 (/res/sprite/ryo/104.png)
  - spr_ryo_105 -> v001 (/res/sprite/ryo/105.png)
  - spr_ryo_106 -> v001 (/res/sprite/ryo/106.png)
  - spr_ryo_107 -> v001 (/res/sprite/ryo/107.png)
  - spr_ryo_108 -> v001 (/res/sprite/ryo/108.png)
  - spr_ryo_113 -> v001 (/res/sprite/ryo/113.png)
  - spr_ryo_151 -> v001 (/res/sprite/ryo/151.png)
  - spr_ryo_152 -> v001 (/res/sprite/ryo/152.png)
  - spr_ryo_154 -> v001 (/res/sprite/ryo/154.png)
  - spr_ryo_155 -> v001 (/res/sprite/ryo/155.png)
  - spr_ryo_200 -> v001 (/res/sprite/ryo/200.png)
  - spr_ryo_201 -> v001 (/res/sprite/ryo/201.png)
  - spr_ryo_202 -> v001 (/res/sprite/ryo/202.png)
  - spr_ryo_204 -> v001 (/res/sprite/ryo/204.png)
  - spr_ryo_205 -> v001 (/res/sprite/ryo/205.png)
  - spr_ryo_207 -> v001 (/res/sprite/ryo/207.png)
  - spr_ryo_208 -> v001 (/res/sprite/ryo/208.png)
  - spr_ryo_300 -> v001 (/res/sprite/ryo/300.png)
  - spr_ryo_301 -> v001 (/res/sprite/ryo/301.png)
  - spr_ryo_302 -> v001 (/res/sprite/ryo/302.png)
  - spr_ryo_304 -> v001 (/res/sprite/ryo/304.png)
  - spr_ryo_306 -> v001 (/res/sprite/ryo/306.png)
  - spr_ryo_310 -> v001 (/res/sprite/ryo/310.png)
  - spr_ryo_320 -> v001 (/res/sprite/ryo/320.png)
  - spr_ryo_324 -> v001 (/res/sprite/ryo/324.png)
  - spr_ryo_325 -> v001 (/res/sprite/ryo/325.png)
  - spr_ryo_410 -> v001 (/res/sprite/ryo/410.png)
  - spr_ryo_420 -> v001 (/res/sprite/ryo/420.png)
  - spr_ryo_471 -> v001 (/res/sprite/ryo/471.png)
  - spr_ryo_472 -> v001 (/res/sprite/ryo/472.png)
  - spr_ryo_501 -> v001 (/res/sprite/ryo/501.png)
  - spr_ryo_502 -> v001 (/res/sprite/ryo/502.png)
  - spr_ryo_503 -> v001 (/res/sprite/ryo/503.png)
  - spr_ryo_550 -> v001 (/res/sprite/ryo/550.png)
  - spr_ryo_551 -> v001 (/res/sprite/ryo/551.png)
  - spr_ryo_552 -> v001 (/res/sprite/ryo/552.png)
  - spr_ryo_570 -> v001 (/res/sprite/ryo/570.png)
  - spr_ryo_606 -> v001 (/res/sprite/ryo/606.png)
  - spr_ryo_607 -> v001 (/res/sprite/ryo/607.png)
  - spr_ryo_608 -> v001 (/res/sprite/ryo/608.png)
  - spr_ryo_611 -> v001 (/res/sprite/ryo/611.png)
  - spr_ryo_612 -> v001 (/res/sprite/ryo/612.png)
  - spr_ryo_615 -> v001 (/res/sprite/ryo/615.png)
  - spr_ryo_700 -> v001 (/res/sprite/ryo/700.png)
  - spr_ryo_701 -> v001 (/res/sprite/ryo/701.png)
  - spr_ryo_702 -> v001 (/res/sprite/ryo/702.png)
  - spr_ryo_710 -> v001 (/res/sprite/ryo/710.png)
  - spr_ryo_730 -> v001 (/res/sprite/ryo/730.png)
- ROM: build_v001 (sha256 363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f, 2490368 bytes)
- Validation: errors=1, warnings=11
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, code_loaded_tiles_unmeasured, technique_usage_manifest_empty, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Estado 570 agora mantém o último frame autoral após a queda; build SGDK 2.11 concluído e o bundle antigo foi invalidado até nova captura.

## 2026-09-12T09:45:48.0720148-03:00 - Registro da correção terminal do KO do Musgo

- Task: Registro da correção terminal do KO do Musgo
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f, 2490368 bytes)
- Validation: errors=1, warnings=11
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, code_loaded_tiles_unmeasured, technique_usage_manifest_empty, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Estado 570 segura o último frame; build 363774d9 validado. Captura canônica recente bloqueada por framebuffer preto e ausência de probes VDP/runtime.

## 2026-09-12T09:54:10.1645136-03:00 - Captura canônica pós-correção do capturador

- Task: Captura canônica pós-correção do capturador
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f, 2490368 bytes)
- Validation: errors=1, warnings=11
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, code_loaded_tiles_unmeasured, technique_usage_manifest_empty, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: windowactivate adicionado ao capturador; screenshot agora legível em blastem-linux-20260912T125335Z-2562833. Gates ainda bloqueiam por VLAB/VDP dump/runtime metrics.

## 2026-09-12T09:55:43.5627911-03:00 - Fechamento da iteração P0 KO e captura

- Task: Fechamento da iteração P0 KO e captura
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f, 2490368 bytes)
- Validation: errors=1, warnings=11
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, code_loaded_tiles_unmeasured, technique_usage_manifest_empty, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Build 2.11 exit 0; ROM 363774d9. Estado 570 terminal corrigido. Captura canônica legível e gate semântico passou; VLAB/VDP/runtime continuam pendentes.

## 2026-09-12 - Experimento de residência Showdown 2x2 revertido

- `BLOCK=2` (1.393 tiles) com `SPR_initEx(320)` foi executado e capturado em
  `out/emulator_evidence/interactive-round-integrity-20260912T132630Z/`.
- Resultado: corrupção de HUD, mapa e sprites por sobreposição da região de
  VRAM automática; variante rejeitada.
- Configuração restaurada: `BLOCK=4` + `SPR_init()`, ROM estável
  `363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f`.

## 2026-09-12 - Blindagem de KO/HUD

- `hud_window_update()` invalida o cache de frame quando `energiaBase<=0`,
  forçando a reescrita das 16 colunas pretas de P1 e P2.
- `FUNCAO_UPDATE_LIFESP()` zera `energia` junto com `energiaBase` no dano letal,
  evitando residual do medidor atrasado na troca de round.
- Build e captura dedicada de KO ainda são necessários para promoção.

## 2026-09-12 - Revisao visual/KO com provas novas

- ROM vigente: `532d44539809e40ad3ae8150532f27c91d7f638ee12d6b194cd53897f294a953`, 2490368 bytes; wrapper canonico exit 0, log `out/logs/visual_ko_verified_build.log`.
- Recortes de barras/KO corrigidos; alfabeto do atlas solicitado em PAL1 e mapa BG_A enviado no VBlank. Painel compacto deixa a pose de vitoria visivel.
- Supersede Blindagem acima: cache nao e invalidado continuamente, e residual sobrevivendo ao reset nao foi confirmado. Zero preenche 16 colunas uma vez. EnergyType 2 nao relanca o derrotado.
- Novas poses Musgo: queda, derrota deitada, vitoria; espera pelo pouso antes de proximo round. Fonte/prompt ImageGen persistidos com proveniencia source_candidate.
- Showdown sem ampliacao 4x4: 768 tiles representantes; indice 0 reservado para impedir buracos pretos no chao. Primeiro tile livre 1018, sprite region 1020. Degrau 832 rejeitado estaticamente.
- Testes host de vida/HUD e paleta/hash passaram. Sessoes finais Ken x Musgo e Musgo x Musgo mostram dois KOs, reset e revanche. Videos sem audio; sem certificacao de pior budget/PAL/P2 vencedor.
- Nove licoes JSON locais e fechamento em `doc/curation/2026_09_12/visual_ko_closeout.md`; framework canonico nao promovido.

## 2026-09-13 - QA simetrico, PAL, time-over e audio isolado

- ROM 532d4453 preservada, sem rebuild ou mudanca de C/assets.
- P2 vence e START retorna ao seletor em NTSC e PAL; DRAW e vencedor por tempo com vida desigual observados, seguidos por reset.
- Capturador recebe controles P2, regiao PAL, entrada de luta verificada, dano observado antes do time-over, configuracao e SRAM locais por sessao.
- Audio: corrigido roteamento do host para sink isolado; captura com sinal e sem clipping digital. Auditor PCM com self-check; silencio/rota ausente retorna erro. Audicao e SFX dedicados permanecem pendentes.
- Regressao nova do bloco C real de time-over: 9.216 pares de vida e idempotencia da pontuacao; testes anteriores de vida/paleta continuam passando.
- Finalizador canonico sela identidade/integridade de arquivos da ROM; nao promove pior budget, FPS do loop, VLAB/VDP/runtime ou AAA.
- Fechamento `doc/curation/2026_09_13/qa_continuation_closeout.md`, licoes locais `test_harness_lessons.json`; nenhuma promocao canonica.

## 2026-09-13 - Especiais antes/depois do reset

- Captura vinculada à ROM `532d44539809e40ad3ae8150532f27c91d7f638ee12d6b194cd53897f294a953` em `out/emulator_evidence/visual_ko_20260913T230125Z/`.
- Sequência de baixo/frente+golpe foi observada nos dois jogadores antes e depois do reset; Ryo emitiu `spr_ryo_701` e Musgo executou `spr_musgo_700`.
- O capturador passou a manter 24 quadros por tentativa para alcançar o frame de emissão do projétil. Resultado é evidência exploratória, sem promoção de budget ou áudio.

## 2026-09-13 - Sonda HPRB de VDP/DMA/SAT

- Adicionada sonda diagnóstica opt-in no loop, após `SPR_update()` e antes do VBlank; SRAM HPRB registra DMA pendente, sprites ativos, links VDP, pico por scanline e amostras.
- Build SGDK 2.11: ROM `ae6f5dab51c6c50b9e5ad94315f2bf8d89dcedfef724b83f6ab41277c59c1a62`.
- BlastEm observou DMA máximo 10.064 B (acima do envelope NTSC ~7.782 B), 58 links VDP e 12 sprites/scanline. Decisão `cabe com recuo`; reduzir/parcelar uploads é o próximo trabalho.
- Decoder e laudo em `rascunho/temporario/analyze_hprb_probe.py` e `doc/curation/2026_09_13/vdp_probe_closeout.md`. Selo final rejeitado por captura preta precoce; o resultado não promove performance.
- Janela PAL curta na mesma ROM mediu DMA máximo 7.984 B, 38 links VDP e 8 sprites/scanline; PAL cabe no envelope, mantendo o recuo apenas para NTSC.
- Plano aberto em `doc/curation/2026_09_14/dma_reduction_plan.md`: atribuir o frame de pico, separar preload e reduzir uploads de frame único/janela ativa; truncar a fila foi explicitamente rejeitado.
- HPRB v2 localizou o pico NTSC: frame 3480 (DMA 10.064 B) e pico de scanline no frame 3158. PAL na mesma ROM permaneceu em 7.984 B; a redução deve focar o trecho NTSC de combate/efeito.

## 2026-09-14 - Experimento DMA do efeito forte

- Variante de laboratório `HAMOOPIG_DMA_LAB_REDUCED=1` trocou apenas `spr_spark3` por `spr_spark2` no `SparkType==3`; ROM `91591dac…` buildou.
- HPRB parcial manteve o pico em 10.064 B (frame 4.469), acima do envelope NTSC; impacto visual menor. Hipótese rejeitada e binário oficial voltou a `ae6f5dab…`. Próximo passo: atribuição por componente no frame de pico, não redução cega de FX.

## 2026-09-14 - Atribuição HPRB v3

- Instrumentação em torno de `SPR_update()` mostrou 7.176 B de delta máximo
  de sprites e 5.536 B já pendentes antes da atualização, com total de 10.064 B.
- A medição confirma sprites como ramo dominante; plano passa a priorizar
  preload/janela ativa de frames. ROM diagnóstica `8544c31d…`, sem promoção de
  budget ou alteração da lógica de combate.

## 2026-09-14 - Laboratório de reuso de estado

- Reentrada no mesmo estado de `PLAYER_STATE()` reduziu o delta de sprites de
  7.176 B para 6.408 B, sem regressão visual observada.
- O pico total permaneceu 10.064 B; variante não promoveu e o macro foi
  restaurado. Próximo alvo é a fila prévia/preload de frames.

## 2026-09-14 - Backpressure nativo não acionado

- Variante sem `SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE` manteve o mesmo pico
  10.064 B; `DMA_getMaxTransferSize()` está sem teto efetivo nesta rota.
- Hipótese rejeitada, macro restaurado e backlog de uploads continua o alvo.

## 2026-09-14 - Ritmo neutro não reduz pico

- Alongar idle/crouch/walk em 2× não alterou o pico DMA de 10.064 B; ataques
  e transições são o alvo real. Macro restaurado, sem promoção.

## 2026-09-14 - HPRB v5: atribuição no frame crítico

- No frame 4.469, 10.064 B = 4.576 B de backlog prévio + 5.488 B de
  `SPR_update()`. Mensagem HUD mediu 480 B; o restante é backlog de sprites.
- ROM diagnóstica `e91823b7…`; links 54 e 9 sprites/scanline. O próximo ciclo
  deve reduzir uploads de animação entre frames, sem truncar a fila.

## 2026-09-14 - Life bar compacta orientada pelo Rheo

- Investigação registrada em `doc/curation/2026_09_13/discord_life_bar_multiplex.md`.
- Barras migradas do WINDOW para células fixas 16×8 (`energy_yellow_segment.png`), oito por jogador; vazios são ocultados e o cenário permanece visível atrás do HUD.
- O primeiro recorte tinha amarelo no índice 0 e produziu quadriculação; o asset foi corrigido para índice 0 transparente e índice 2 amarelo, conforme a PAL1 do HUD.
- Build wine bridge passou; ROM final `f001418a654fc0aaf4a3c53cc4eb9f62470ac0f747c0dd2b3ba2b0c86453ec0b`. Captura de combate `visual_ko_20260914T030007Z` e HPRB `hprb_probe_report_20260914_life_bar_final.json`.
- HPRB da sessão curta: 5.688 B DMA, 17 links VDP, 5 sprites/scanline; resultado dentro do envelope da amostra, sem promoção de `validado_budget` global.
## 2026-09-14 - Transição splash → menu

- `gRoom==1` mantém a abertura HAMOOPIG íntegra durante 120 frames; entrada
  inicial apenas pula o splash e não dispara `START` no mesmo frame.
- O menu restaura o tilemap original antes de desenhar o painel estreito,
  evitando DMA/fade concorrente e a corrupção visual observada na transição.
- Evidência manual BlastEm: `out/emulator_evidence/title-transition-final-20260914/`.
- ROM: `68baca0e2845a00d057e0d8b892102247f5674350194dcf8509b07e895734d7d`.

## 2026-09-14 - Stage 2 amplo

- Adicionada a fonte `data/source_art/stage2_swamp/generated_stage2_v01.png`
  (prompt e hash preservados) e conversor reproduzível para o palco 2.
- `res/gfx/bgb2.png` agora é 512×256, paleta Mega Drive 9-bit sem uso do índice
  zero e 768 tiles residentes; o relatório registra o vínculo fonte→saída.
- A seleção `STAGE2 ON/OFF` permanece de sessão e foi coberta por regressão
  estática. Build SGDK 2.11 concluído (ROM SHA-256:
  `7ca637e0fbcb4cd22abc5f04c6fd84006a886d41f084f6ad811e52e64a1b3bd2`).
- A arte ainda é `source_candidate`: falta validar no emulador a transição,
  câmera, PAL/NTSC, áudio e pior frame antes de promoção.

## 2026-09-14 - Combo orientado a eventos

- Acertos válidos agora passam por `FUNCAO_REGISTER_HIT()` e alimentam uma
  janela de 60 ticks; o contador não desaparece ao retornar a idle e expira
  de forma determinística. Colisões simultâneas registram P1 e P2 uma vez.
- Adicionado `tests/test_combo_contract.py`; suíte estática/host 9/9 passou.
- Build SGDK 2.11: ROM SHA-256
  `641ce1620c67a1ee0ed248aa2e9200122445f923d2df09d404c80011728c466c`.
- Multi-hit real, fidelidade do texto e áudio continuam pendentes de emulador.

## 2026-09-14 - Relógio transparente e contrato de superfície HUD

- Fundo opaco do relógio corrigido por máscara derivada do índice 11 do atlas;
  o novo PNG compartilha PAL1 e usa índice 0 transparente.
- Adicionados `doc/ui_pixel_surface_contract.json`, relatório de conversão e
  `tests/test_clock_transparency.py`.
- Build SGDK 2.11 após a correção: ROM SHA-256
  `0a10f366bdd47dd6969862dc466fccb6e7bde5cd5b3dc554fd2879ddfe7088f4`.
- A aparência no framebuffer NTSC/PAL e as medições de DMA/scanline continuam
  pendentes de emulador.

## 2026-09-14 - Captura fresca e fechamento estático

- Suíte estática/host consolidada em 11/11; roadmap atualizado para refletir o
  teste dedicado da máscara transparente do relógio.
- Captura nova da ROM `0a10f366bdd47dd6969862dc466fccb6e7bde5cd5b3dc554fd2879ddfe7088f4`
  mostra a sequência abertura → fade → menu. O selador permanece bloqueado por
  falta de probe VLAB/VDP/runtime; a captura não promove orçamento ou áudio.

## 2026-09-14 - Ledger observacional de combate

- Adicionada fila estática `CombatEvent` (8 entradas por tick), emitida por
  cada `FUNCAO_REGISTER_HIT()` com atacante, defensor, estado e índice.
- A camada é observacional nesta etapa: dano, hit-pause e estados continuam
  sob controle da FSM, evitando regressão por dupla aplicação. Overflow retorna
  falha em vez de sobrescrever evento válido.
- Build SGDK 2.11 passou; ROM SHA-256:
  `37204b1dacc9833cb57ba6d3a8302d069c37c1ddad7d4326383bf9fb37ae80c1`.

## 2026-09-15 - TIMER BG opcional e compacto

- `GameConfig.hudTimerBg` e o item `TBG ON/OFF` agora controlam uma moldura de
  apenas 6×2 tiles atrás do relógio. O default é OFF e o cenário permanece
  visível fora dessa área.
- Testes estáticos/host: 12/12. Build SGDK 2.11: ROM SHA-256
  `0f578230d3ddc2a5f8285f4783030e51b6abea1d026070f8a9354415637fa232`.

## 2026-09-15 - Composição inicial do título protegida

- O mapa do menu inicial agora usa DMA síncrona antes de iniciar `PAL_fadeIn`.
  Isso impede que o primeiro quadro do título revele logo/personagem com os
  textos ainda na fila, causa provável da interrupção visual observada.
- A captura do ROM atual mostra o título composto; o selador segue bloqueado
  por VLAB/VDP/runtime metrics ausentes.

## 2026-09-15 - Fila de DMA da navegação do título

- A carga inicial usa DMA síncrona; páginas e alterações posteriores usam CPU,
  evitando duas DMAs síncronas consecutivas ao restaurar a arte de fundo.
- A captura exploratória ainda não certifica a entrada OPTIONS: o canal de
  teclado do BlastEm não produziu uma sequência de confirmação reproduzível.
- Build SGDK 2.11: ROM SHA-256
  `9613d9ba8c4b0cb7ba7d76c0644551ad8dd6280994abb10ed5796558cb4b5d41`.

## 2026-09-15 - Barreira de conclusão DMA no menu

- `title_restore_artwork()` espera `VDP_waitDMACompletion()` antes de escrever
  a página por CPU. A troca para OPTIONS/DEBUG não disputa mais o tilemap do
  BG_A com a restauração do artwork.
- Build SGDK 2.11 e suíte estática/host 12/12; ROM SHA-256:
  `90688a5d4f8dc5e613b12fc3a4e8e81ef1df5c5c56916e2d9f978b6fba811651`.
- A captura de OPTIONS após a estabilização foi observada, mas continua
  exploratória por falta de VDP dump e runtime metrics no bundle canônico.

## 2026-09-15 - Consumidor central do combo por evento

- `FUNCAO_REGISTER_HIT()` agora somente produz eventos. O contador e a janela
  de combo são atualizados pelo consumidor único após a FSM; uma reivindicação
  por tick impede dupla aplicação.
- Vida e medidor de especial ainda usam caminhos legados e permanecem no
  backlog de migração P04/P05.
- Build SGDK 2.11 e suíte estática/host 12/12; ROM SHA-256:
  `1c685106ecbbe51e888eeeaddaa75132030ad01f27c52b22e49cc88b6b8bbb4f`.

## 2026-09-15 - Classificação HIT/GUARD no ledger

- Colisões confirmadas emitem `COMBAT_EVENT_HIT`; bloqueios normais e de
  projétil emitem `COMBAT_EVENT_GUARD`.
- O consumidor de combo descarta GUARD, eliminando incremento de combo por
  defesa e preparando o ganho de medidor centralizado.
- Build SGDK 2.11 e suíte estática/host 12/12; ROM SHA-256:
  `1ab2396c7028ba4698e97abf6c442c484cab088fc36015592cff320a5a8d5d1a`.

## 2026-09-15 - Harness de gameplay atualizado para abertura e título

- `capture_visual_ko.py` passou a capturar o título e confirmar START antes do
  seletor, refletindo a separação de cenas implementada.
- Sessão exploratória alcançou a luta na ROM vigente em
  `out/emulator_evidence/visual_ko_20260915T035136Z/`; o bundle canônico e a
  prova de eventos continuam pendentes.

## 2026-09-15 - Delta do medidor de especial centralizado

- `CombatEvent` agora transporta o delta do medidor do defensor. O caminho de
  colisão anexa o valor e `FUNCAO_CONSUME_COMBAT_EVENTS()` aplica o clamp uma
  única vez; o projétil foi ordenado para seguir a mesma regra.
- Fallback direto permanece apenas para chamadas sem evento, preservando
  compatibilidade temporária.
- Build SGDK 2.11 e suíte estática/host 13/13; ROM SHA-256:
  `fbbdc278613daa06d9a5677408daa2f755976c97054d7d9612b1b9276e53759e`.

## 2026-09-15 - Política fixa HIT/GUARD do medidor

- O consumo central aplica `+4` ao atacante e `+2` ao defensor em HIT, e `+1`
  ao atacante em GUARD. O valor legado do golpe é preservado apenas para
  telemetria e não causa uma segunda carga.
- Build SGDK 2.11 e suíte estática/host 13/13; ROM SHA-256:
  `5cef44779afe5356243d3ddcd486d40fd404b0461eca6dbcf4dfe257831d1de6`.
## 2026-09-15 - Definição compartilhada de cenários

- `StageDefinition` (`inc/stage.h`/`src/stage.c`) passou a concentrar id, nome,
  dimensões, piso, limites de luta e capacidade de 240 linhas. A inicialização
  carrega o `Image` selecionado por essa definição e a seleção usa o mesmo
  contrato, removendo bifurcações específicas de `SHOWDOWN`/`BGB2`.
- A suíte estática/host passou a 17 arquivos e o build SGDK/Wine gerou a ROM
  `5cca18f17931b9d6eae814b542a5e1f4775a3059642e7c444ea3f7fa9e4cebc6`.
- A regressão em BlastEm alcançou título, seletor e round com o loader novo;
  o probe HPRB schema 6 foi decodificado. O caminho registrou zero eventos de
  combate e não substitui a captura dirigida anterior (16 HIT/1 PROJECTILE).
  DMA máximo segue em 8288 B contra 7782 B nominais, portanto budget, câmera,
  PAL, áudio e revisão visual continuam pendentes.
## 2026-09-15 - Limites de luta derivados do cenário

- Os empurrões de borda, o recuo de defesa e o clamp final da física agora
  usam `gLimiteCenarioE/D`, valores fornecidos pelo `StageDefinition`, em vez
  de assumir `30` e `gBG_Width-30`. Isso evita que um cenário novo herde a
  largura efetiva do primeiro.
- O contrato de StageDefinition e o build SGDK/Wine passaram; a ROM atual é
  `28f7f94cc9a1ba6fb317a61f2afa4e49c09bb5b61b7900827688f294975aec0d`.
  A regressão em BlastEm chegou ao round e decodificou HPRB schema 6; DMA
  máximo continua em 8288 B/7782 B nominais e o caminho não gerou eventos de
  combate, portanto não há promoção de budget ou de cobertura de colisões.
## 2026-09-15 - Stage 2 ampliado para 512x256

- A conversão reproduzível de `data/source_art/stage2_swamp/` deixou de cortar
  32 pixels verticais: `res/gfx/bgb2.png` agora mede 512×256, mantém o teto de
  768 tiles e passa a ser elegível para a rota PAL/240 da definição de estágio.
- O harness de captura ganhou `--stage2`, usa `D` para o botão C no mapa padrão
  do BlastEm (Q/W/E são X/Y/Z) para o
  botão C e registra o palco no manifesto. A captura
  `out/emulator_evidence/visual_ko_20260915T060720Z/` mostrou a luta no novo
  cenário e inclui manifesto com o hash da ROM e `stage: BGB2`.
  cenário; a captura de seleção imediata pode conter um frame intermediário,
  por isso a comprovação principal é `01_round.png`.
- Build SGDK/Wine: ROM
  `2a3516df1dc4150134b3e12ef64c3b7ab42aef29da25cd6610d2b003e82df13e`.
  HPRB schema 6 registrou 8288 B de DMA contra 7782 B nominais, 17 sprites por
  linha e zero eventos nessa rota curta. A arte continua candidata, sem
  promoção visual; PAL, câmera, áudio e otimização de DMA permanecem abertos.
## 2026-09-15 - Stage 2 exercitado em PAL

- O mesmo build `2a3516df1dc4150134b3e12ef64c3b7ab42aef29da25cd6610d2b003e82df13e`
  foi executado com `--pal --stage2 --probe-short`.
- O bundle `out/emulator_evidence/visual_ko_20260915T061029Z/` contém manifesto
  (`region_requested: E`, `stage: BGB2`) e HPRB schema 6: 1470 amostras,
  8288 B enfileirados, 40 sprites ativos, 56 links VDP e 17 sprites por linha.
  O decoder classificou o DMA como `within_nominal` contra 17408 B PAL.
- A sonda ainda não exporta a altura efetiva, portanto PAL-224/PAL-240,
  câmera, áudio e revisão visual permanecem pendentes; a captura não é
  promoção de qualidade artística.
## 2026-09-15 - HPRB schema 7 e PAL-240 observado

- O probe agora exporta `screen_height` e usa schema 7 (70 bytes/31 words),
  mantendo o decoder fechado para schemas 1–6. O novo contrato inclui
  truncamento, round-trip e compatibilidade legada.
- A captura `out/emulator_evidence/visual_ko_20260915T062548Z/` usou a ROM
  `4df3e5b9bbc1441c34595d3c464a54d41480dfb154f1d7e3bbaed884bee5c503`,
  selecionou BGB2 com C (`D` no mapa do BlastEm), ativou H240 pelo menu DEBUG e
  registrou `screen_height: 240` no SRAM. O round visual ficou sem o overlay
  TEXT de debug.
- HPRB mediu 2430 amostras, DMA máximo 9568 B, 40 sprites ativos, 56 links e
  17 sprites por linha; o DMA permanece dentro do envelope PAL de 17408 B.
  A rota NTSC continua acima de 7782 B, e revisão visual/auditiva segue
  pendente.

## 2026-09-15 — Estabilidade de sprites e reset do HUD compacto

- `PLAYER_SET_SPRITE` mantém um objeto Sprite por lutador e troca definição,
  posição, atributos e frame sem o ciclo release/add a cada estado.
- Aliases das barras seguem o tile proprietário após compactação de VRAM e o
  reset de round libera o HUD anterior antes da nova alocação.
- Build `146116cd3a05a6c8b84bf28cda92f47f7444b29df65532a9381443fc67d51f6c`;
  19 testes estáticos passaram. Stage 2 chegou ao round e o stress dirigido
  alcançou KO sem o fatal anterior; reentrada pós-KO, áudio e revisão artística
  permanecem pendentes.

## 2026-09-15 — Liberação completa no reset e prova de vida zerada

- O reset de round agora libera os 16 sprites `Rect*` de hitbox/debug antes de
  reconstruir o HUD. Isso fecha o vazamento que podia culminar em
  `HUD segment sprite allocation failed` depois de um KO.
- ROM: `82501c1e6a41e19bdd42317c239ca4d9eb5f2e9bc690460e68122c40262e8871`;
  build: `out/logs/continuation_p09_rect_release_build.log`.
- Captura: `out/emulator_evidence/visual_ko_20260915T074433Z/`. A vida de P2
  fica zerada no quadro de KO (`combat_025.png`), volta no round seguinte
  (`special_reset_health.png`) e a luta continua sem fatal.
- O detector do harness foi corrigido para não confundir a barra de especial
  com a barra de vida. A revisão artística do cenário e a audição do áudio
  continuam pendentes.

## 2026-09-15 — Showdown regenerado pela referência nativa solicitada

- `res/gfx/showdown.png` agora usa `rascunho/showdown_native_crop_preview.png`
  como fonte explícita, com 768 tiles e quatro iterações de medoid. O MSE RGB
  medido caiu de 201.3010 para 177.0296.
- Build `14d8ac73b4cf176d9c933e9645c52d6b8237a72e3fe26fa956d0e38ec320d440`;
  captura fresca em `out/emulator_evidence/visual_ko_20260915T075323Z/`.
- O palco está vinculado e executa no emulador; repetição quadriculada,
  saturação e composição continuam aguardando revisão visual independente.

## 2026-09-15 — Handoff inicial e matriz P10

- Adicionados os manuais `doc/engine_quickstart.md`,
  `doc/engine_extension_guide.md` e `doc/controls_and_options.md`.
- `doc/engine/p10_qa_matrix.json` agora enumera as 36 combinações ordenadas de
  roster, palco e região. As 36 estão honestamente como `not_run`; o contrato
  `tests/test_qa_matrix_contract.py` impede declarar a matriz concluída sem
  evidência de emulador.

## 2026-09-15 — Integração de combate no SHA atual

- A captura `out/emulator_evidence/visual_ko_20260915T080351Z/` vinculada à ROM
  `14d8ac73b4cf176d9c933e9645c52d6b8237a72e3fe26fa956d0e38ec320d440` exercitou
  BGB2 NTSC com Ryo vs Musgo: 21 HIT, 1 KO, 7008 B de DMA enfileirados,
  68 links VDP e 17 sprites por linha.
- O caso foi registrado na matriz como runtime aprovado, com revisão visual e
  auditiva ainda pendentes; os 35 casos restantes continuam sem execução.

## 2026-09-15 — Sinal de áudio isolado no SHA atual

- A captura `out/emulator_evidence/visual_ko_20260915T080946Z/` gravou o sink
  exclusivo do BlastEm em 48 kHz estéreo por 36,05 s. O auditor encontrou
  sinal presente, RMS `-28,29 dBFS`, pico `5816` e zero clipping.
- O resultado valida roteamento elétrico e a política de captura, não timbre,
  volume percebido ou qualidade do mix; a revisão auditiva segue pendente.

## 2026-09-15 — Degraus de tiles do Showdown avaliados

- Foram medidos candidatos de 864 e 1024 tiles (MSE RGB 138.7790 e 84.8591),
  porém ambos excedem `TILE_SPRITE_INDEX=1020` após o HUD. Eles ficam como
  rascunhos rejeitados; o runtime seguro continua com 768 tiles.
- O próximo ganho visual deve vir de streaming/cache por janela, não de uma
  sobreposição silenciosa da região de sprites.

## 2026-09-15 — Runner P10 de pares e regiões

- O harness agora seleciona P1/P2 explicitamente usando o `default.cfg` do
  BlastEm mais `tests/blastem_qa.cfg`, sem alterar a ROM.
- A execução de seleção vinculou as 36 combinações de roster, palco e região
  ao SHA `14d8ac73b4cf176d9c933e9645c52d6b8237a72e3fe26fa956d0e38ec320d440`.
  O relatório é `out/logs/p10_matrix_runner_report.json`.
- A repetição `probe-short` gerou 36 manifestos e 36 relatórios HPRB decodificados
  no mesmo SHA; dois casos PAL foram recapturados após estabilização do
  framebuffer. A evidência ainda não fecha gameplay por caso, revisão
  visual/auditiva ou ciclos de reset.
- O resumo por região encontrou NTSC 7024 B DMA / 59 sprites VDP / 17 por
  scanline e PAL 8024 B / 57 / 17. Esses números são probe enfileirado, não
  bytes efetivamente transferidos nem aprovação sensorial.

## 2026-09-15 — Estresse de reset de cena P10

- `tests/run_scene_reset_cycles.py 100` completou 100/100 soft resets no
  BlastEm usando a ROM `14d8ac73...20d440`; o processo e a janela ficaram
  presentes em todos os ciclos e as capturas 1/50/100 não ficaram vazias.
- Evidência: `out/emulator_evidence/scene_reset_cycles_20260915T093244Z/manifest.json`.
- O claim é limitado a boot/reset de cena; reset de round, gameplay completo,
  revisão visual/auditiva e worst-frame continuam pendentes.

## 2026-09-15 — Reprodução isolada dos manuais P11

- `tests/reproduce_p11_isolated.py` materializa uma cópia mínima dos três
  manuais, verifica seus tokens de contrato e compila/proba `StageDefinition`
  com stub explícito de tipos SGDK; a sessão
  `out/p11_isolated_reproduction_20260915T094345Z/` passou.
- O resultado é host-only: não substitui build SGDK/Wine, ROM no emulador,
  revisão visual/auditiva ou medição de budget.

## 2026-09-15 — Revalidação P11 no SHA vigente

- A reprodução isolada foi executada novamente após a promoção Showdown 864:
  `out/p11_isolated_reproduction_20260915T125901Z/report.json` passou.
- O vínculo desta rodada está registrado em `doc/curation/2026_09_15/p11_current_rom_revalidation.json` (L088).
- O escopo continua host-only; o inventário final de release, a ROM no emulador
  e as revisões sensoriais permanecem gates separados.

## 2026-09-15 — Transição abertura → título observada no framebuffer

- A captura `out/emulator_evidence/visual_ko_20260915T130109Z/opening_title_transition.mp4`
  foi gravada a 60 fps no SHA vigente e inspecionada em amostras temporais.
- A sequência apresenta abertura, intervalo preto limpo e fade-in do título sem
  sobreposição aparente; a lição L089 registra o vínculo e mantém review visual
  independente e métricas canônicas como pendências.

## 2026-09-15 — Ocupação das janelas de câmera do Showdown

- A ferramenta `tests/analyze_stage_streaming.py` mediu o PNG convertido em
  posições alinhadas a 8 px. Com viewport 320×224 e preload de uma tile, o
  pico é 588 tiles únicos em uma janela 42×30; o atlas global tem 864.
- O relatório `out/logs/showdown_stream_window_report.json` orienta o desenho
  do cache, mas não promove streaming: a capacidade do laboratório é apenas
  referência e a implementação/upload em C ainda é o próximo bloco.

## 2026-09-15 — Stage 2 promovido para 864 tiles e revalidado

- O cenário do cais de pântano passou de 768 para 864 representantes; a fonte
  continua 512×256, com paleta Mega Drive e índice 0 reservado. Build vigente:
  `e17027c059396f296ee417da773e1a145bb59efc10999d005cfc5b23679ecf56`.
- A seleção/round Stage 2 foi capturada no BlastEm; P10 36/36, resets 100/100,
  INTRO/FADE e áudio isolado foram recapturados no mesmo SHA. L091 registra os
  vínculos e limitações; a arte permanece candidata até revisão independente.

## 2026-09-15 — INTRO/FADE observáveis no retorno ao título

- `INTRO` e `FADE` entraram no menu de opções. `B` em SELECT e AFTER_MATCH
  agora retorna pela abertura quando INTRO está ON, ou direto ao título quando
  está OFF; FADE controla as transições dessa rota.
- Build `66a4793895151ea03ed384f20c95e0e9bee625f91af12f13afaacbcff223e3c3`;
  evidência fresca em `out/emulator_evidence/title_return_20260915T095040Z/`.
- A captura comprova a rota e o vínculo ROM→manifesto, mas não promove
  suavidade ou legibilidade visual sem revisão sensorial.

## 2026-09-15 — P10 revalidado após mudança de ROM

- A alteração do retorno ao título produziu o SHA
  `66a4793895151ea03ed384f20c95e0e9bee625f91af12f13afaacbcff223e3c3`;
  os probes antigos foram rejeitados pelo teste de integridade.
- A matriz foi recapturada: 36/36 casos `probe_passed`, dois PAL repetidos com
  espera maior, e HPRB decodificado no mesmo SHA. O estado sensorial continua
  `pending_visual_review`/`pending_audio_review`.
- `tests/run_scene_reset_cycles.py 100` também passou novamente no SHA atual;
  manifesto em `out/emulator_evidence/scene_reset_cycles_20260915T101210Z/`.

## 2026-09-15 — Probe de combate mínimo na matriz P10

- A recaptura P10 passou a enviar uma sequência limitada de ataques (`P1:
  Right+Q x3; P2: J+X x2`) em cada caso. Os 36 casos do SHA atual produziram
  pelo menos um HIT e tiveram HPRB decodificado; uma falha PAL foi estabilizada
  com repetição de espera ampliada.
- O resumo registra máximos de 8.024 B DMA enfileirados, 41 sprites ativos,
  60 links VDP e 17 sprites/scanline. O probe é deliberadamente bounded e não
  promove gameplay completo, KO, classes de colisão, reset de round ou revisão
  visual/auditiva.
- Lição canônica: `doc/curation/2026_09_15/p10_combat_probe_current_rom.json`
  (L083). Relatórios: `out/logs/p10_matrix_runner_report.json` e
  `out/logs/p10_matrix_hprb_summary.json`.

## 2026-09-15 — Mensagens de round sem faixa preta

- O atlas `message_font.png` agora reserva índice 0 transparente em todas as
  células. `ROUND`, `FIGHT` e `KO` deixam o palco visível; somente o resultado
  com rematch mantém um painel preto compacto para contraste.
- Build SGDK/Wine: ROM `b74d2bcebfce1d7e9e831e90a6e029f610ddd5c30e95bb5f62e52d53f6a3aca1`;
  captura `out/emulator_evidence/visual_ko_20260915T105026Z/01_round.png`.
- A matriz P10 (36 casos) e o estresse de 100 resets foram recapturados no
  mesmo SHA; as lições canônicas são L083, L084 e L085.

## 2026-09-15 — Revalidação final do SHA b74d2bce

- A ROM `b74d2bcebfce1d7e9e831e90a6e029f610ddd5c30e95bb5f62e52d53f6a3aca1`
  foi exercitada novamente na matriz P10 (36/36 HPRB), em 100 resets de cena
  e na rota INTRO/FADE do título (`title_return_20260915T112050Z`).
- A suíte host/estática encerrou com 27 testes aprovados; revisão visual
  independente, audição crítica, gameplay completo e worst-frame continuam
  explicitamente pendentes.

## 2026-09-15 — Showdown promovido para 864 tiles

- O candidato de 864 representantes foi promovido após build e smoke route
  BlastEm sem acionar o guard de VRAM. O MSE RGB medido caiu de `177.0296`
  (768 tiles) para `138.7790`; o candidato de 1024 continua rejeitado.
- A ROM vigente é `da6f6e1b4ede10c6f9feebcaa5b0984d40937d7033df774a41c4cf5dd54bd9d7`.
  P10 (36 casos), 100 resets de cena e INTRO/FADE foram recapturados nesse SHA.
- A fonte permanece fixture de estudo; revisão visual independente, streaming,
  parallax, gameplay completo e pior-frame ainda não estão fechados.

## 2026-09-15 — Sinal de áudio no SHA da promoção visual

- Captura isolada em `out/emulator_evidence/visual_ko_20260915T125437Z/` foi
  auditada com 48 kHz estéreo, 13,55 s, RMS `-27,21 dBFS`, pico `5842`, sem
  clipping e rota exclusiva do BlastEm confirmada.
- O resultado prova sinal/roteamento no SHA `da6f6e1b…bd9d7`, mas não substitui
  audição crítica de timbre, mix ou volume percebido.

## 2026-09-15 — Stage 2 promovido para 864 tiles e revalidado

- O cenário do cais de pântano passou de 768 para 864 representantes; a fonte
  continua 512×256, com paleta Mega Drive e índice 0 reservado. Build vigente:
  `e17027c059396f296ee417da773e1a145bb59efc10999d005cfc5b23679ecf56`.
- Seleção/round Stage 2, P10 36/36, resets 100/100, INTRO/FADE e áudio isolado
  foram recapturados no mesmo SHA. L091/L092 registram os vínculos e limites;
  a arte permanece candidata até revisão independente.
## 2026-09-15 — KO do Musgo aterrado e pose terminal visível

- O estado `551` deixou de aplicar deslocamento horizontal após o pouso; o
  limite X do palco é aplicado antes de entrar em `570`.
- A física não é mais throttled enquanto o derrotado está em `550/551`, evitando
  que o slow-motion suspenda a queda. Os estados KO do Musgo recriam o handle
  do metasprite para evitar tiles VRAM stale nas mudanças de footprint.
- `570` usa o segundo frame de `fall_v1`, comprovado no emulador, como pose
  terminal. `defeat_v1` permanece em quarentena até revisão de paleta/VRAM.
- Build SGDK/Wine: ROM `eeb50ff819ba5e3027dd3a23067f2329038039027ef4b1a7a1add97cddf9f750`;
  captura dirigida em `out/emulator_evidence/visual_ko_20260915T182445Z/` mostra
  Musgo deitado no chão em `zero_1_settle.png` e `zero_1_result.png`.
- Lição canônica: `doc/curation/2026_09_15/musgo_ko_grounded_pose.json` (L099).
  P10/title/audio anteriores a este SHA ficam stale até recaptura.
## 2026-09-15 — Revalidação integrada no SHA eeb5

- A matriz P10 foi recapturada integralmente: 36/36 casos com manifests e HPRB
  no mesmo SHA; resumo: 8.024 B DMA, 41 sprites ativos, 60 links VDP e 17 por
  scanline.
- A rota de título/retorno (5 capturas), áudio isolado (24,8 s, -27,67 dBFS,
  pico 5.808, sem clipping) e 100 ciclos de boot/reset passaram no mesmo
  binário. Nenhum desses resultados substitui revisão visual/auditiva.
- Lição canônica: `doc/curation/2026_09_15/eeb5_integrated_revalidation.json`
  (L100). Gameplay completo por matchup, pior-frame, streaming nativo e
  hardware físico continuam pendentes.

## 2026-09-15 — Gate persistente de overlap e revalidação final 6c6d

- O ledger de combate agora mantém a identidade `attackInstance` entre ticks e
  bloqueia dano/medidor repetidos enquanto o mesmo ataque permanece sobre o
  defensor; guard e hit compartilham a mesma trava e o reset de round limpa o
  estado. Multi-hit autorado continua sendo uma decisão explícita da FSM.
- Build SGDK/Wine aprovado: ROM `6c6da7e38dc8d382ec329a604457b1053be4eae2dba00bb327a73230871e3005`;
  log `out/logs/combat_event_persistent_gate_v2_build.log`.
- P10 foi recapturado no mesmo binário: 36/36 probes HPRB schema 7, com três
  casos inicialmente transitórios (`hprb_missing`) aprovados após retry. Os
  máximos medidos foram 8.024 B DMA, 41 sprites ativos, 60 sprites VDP e 17
  sprites/scanline.
- Também foram renovados título/retorno (5 capturas), KO Musgo aterrado,
  transição INTRO/FADE, áudio isolado com sinal e 100 resets. A inventariação
  P11 agora aponta para esses artefatos, mas o status permanece
  `candidate_not_release`: revisão visual/auditiva independente, gameplay
  completo, pior-frame SGDK, streaming nativo e hardware continuam pendentes.

## 2026-09-16 — Identidade do HUD e estrelas de rounds

- O HUD de combate agora apresenta `RYO`, `KEN` ou `MUSGO` e duas posições de
  vitória por jogador nas margens livres. As estrelas usam a fonte 8×8 do SGDK
  e só são redesenhadas quando lutador ou placar mudam; a barra de especial,
  vida e contador de hits mantêm seus consumidores e linhas independentes.
- Nenhum sprite ou tileset novo foi alocado. O contrato estático
  `tests/test_hud_identity_contract.py` documenta as linhas e limites.
- Build SGDK/Wine: ROM `70bd7e57a667e4cedc1c2a56db92f5959b2b43fdfa75a02e436162167d5e9b35`;
  P10 recapturado no mesmo SHA (36/36 probes, um retry), além de título, KO,
  transição, áudio isolado e 100 resets. Revisão visual independente e retratos
  dedicados continuam pendentes; Ken permanece congelado para a próxima etapa.

## 2026-09-16 — Rota semântica de combate corrigida e observabilidade HSEM

- O roteiro de teclado P04 passou a aproximar somente o P1 por mais tempo,
  usar RIGHT como recuo do P2 (que olha para a esquerda), X para o comando de
  especial e Y para agarrão. Cada golpe agora aguarda o fim do ciclo para não
  mascarar contatos pela trava persistente de `attackInstance`.
- O runtime exporta um bloco HSEM separado do HPRB legado, com distância,
  posições, estados e contadores de guarda/projétil/agarrão. A captura real
  `visual_ko_20260916T042349Z` no SHA `2342db83…c70c` decodificou 11 HIT,
  2 GUARD, 2 PROJECTILE e 3 DOUBLE; THROW ainda não foi emitido. Isso fecha
  observabilidade e duas classes reais, não gameplay completo.
- Lição canônica: `doc/curation/2026_09_16/combat_semantics_probe_v2.json`
  (L106). Nenhuma ausência de evento foi promovida como aprovação.
- Build vigente desta observabilidade: ROM `2342db83a8e76eecbac42536168a1c9a193da11d7752d83a671e1f9d2834c70c`.

## 2026-09-16 — Janela de agarrão e matriz P10 renovada

- A FSM agora aceita o comando de agarrão em toda a janela de proximidade
  `0..45`, antes do despacho de ataque normal; o contrato preventivo
  `tests/test_throw_window_contract.py` e o build SGDK/Wine passaram.
- A rota semântica real foi recapturada no SHA
  `9148c2afb7e95e77cab6d4c98266b49820d945466d879339b6071d772e6079de`:
  HSEM observou 1 guarda e 2 janelas de projétil; `COMBAT_EVENT_THROW` ainda
  não foi emitido, portanto a cobertura de agarrão permanece pendente.
- A matriz P10 foi renovada no mesmo binário: 36/36 probes HPRB passaram
  (31 diretos + 5 retries), todos `pending_visual_review`; os máximos atuais
  são 8.024 B DMA, 41 sprites ativos, 61 links VDP e 17 sprites/scanline.
- A rota de retorno ao título também foi recapturada no SHA atual em
  `title_return_20260916T052717Z`: cinco framebuffers não vazios cobrem
  INTRO/FADE desligados (corte direto) e ligados (abertura + fade). A captura
  prova o caminho de estados; suavidade e composição continuam em revisão
  visual independente.

## 2026-09-16 — Agarrão alcançável no espaçamento real do cenário

- A janela de agarrão foi alinhada ao espaçamento produzido pelas caixas de
  massa no palco Showdown: `throwDistance <= 100` é avaliado com posições
  atuais, antes dos ataques normais, e aceita os estados de recuperação/queda.
  O comentário e o contrato estático registram que o par nasce a cerca de
  94 px no mundo, evitando que o limite nominal de 45 px torne o comando
  inerte.
- A rota de captura usa uma única aproximação do P2 e bordas Y do P1 com
  RIGHT mantido; não injeta RAM, posição ou estado. No build
  `4c273bd5803913acbd62a55e6386f7c1e50e4d707cd14fd2fdd6c715ffa0ebbc`, o
  emulador observou `combat_total_throws=2` e `throw_frames_p1=80` em
  `out/emulator_evidence/visual_ko_20260916T205914Z/`.
- HPRB/HSEM são telemetria diagnóstica; revisão visual independente, áudio,
  balanceamento e gameplay completo continuam pendentes. A matriz P10 foi
  marcada para recaptura no novo SHA, sem reaproveitar evidência histórica.


## 2026-09-18 — Curadoria incremental canonica

- O usuario autorizou assimilar o aprendizado acumulado com o projeto incompleto. Oito principios entraram na referencia canonica `tools/sgdk_wrapper/.agent/references/hamoopig_engine_learning_2026_09_18.md` (caminho relativo ao workspace), acionada por quatro skills existentes.
- ROM auditada: `4c273bd5803913acbd62a55e6386f7c1e50e4d707cd14fd2fdd6c715ffa0ebbc`. Referencias a outros hashes em narrativas anteriores sao historicas; nao substituem esta identidade. Runtime e ROM nao alterados; nenhuma nova captura nesta rodada.
- 33/33 testes de host, self-check HPRB, 84/84 casos de schema e quatro quick_validate passaram. Framework global continua com falhas preexistentes, comparadas em `doc/curation/2026_09_18/framework_comparison.json`. Contexto passou; higiene possui dois tipos de blocker.
- 36 casos P10 permanecem `pending_visual_review`; nao equivalem a partidas aprovadas. Permanecem pendentes robustez de eventos, budget completo, sincronismo visual, streaming real, qualidade visual/audio e higiene. Sem promocao AAA.
- Diagnostico, plano, inventario e logs: `doc/curation/2026_09_18/curadoria_aprendizado_canonico.md`.


## 2026-09-18 — Diagnostico visual comparativo com imagens GAME

Oito referencias fornecidas pelo usuario foram vistas e preservadas com hash em `rascunho/inputs/quality_reference_board_2026_09_18/`, somente para referencia de qualidade. Comparadas a quatro capturas persistidas da ROM 4c273bd5, ao codigo e aos recursos ativos. Diagnostico e plano: `doc/curation/2026_09_18/visual_gap/diagnostico_visual_comparativo.md`; prancha: `comparison_board.html` nessa pasta; backlog: 14 itens em seis marcos mais expansao posterior.

Conclusao: base ja possui sprites grandes, barras, combo, rounds, selecao, camera, hitpause e SFX. Prioridades sao identidade/legibilidade do HUD, retratos, poses especificas em lugar de aliases genericos, reautoria do palco, profundidade/animacao ambiental e integracao sonora. Camera existente nao deve ser confundida com parallax; imagens paradas nao comprovam movimento, FPS ou voz. Auditoria de arte: 132 ativos sem issues criticos nas verificacoes executadas; fontes em data com pendencias nao bloqueiam o grafo ativo. Sem runtime/ROM alterados, nova captura, aprovacao visual final ou promocao AAA.

## 2026-09-19 — Seletor visual e probe runtime no SHA atual

- Adicionado `title_backdrop` ao grafo ativo e reorganizado o seletor para P1/P2, nomes, cursores e palco; o texto de estágio agora é limpo antes de ser redesenhado.
- Build SGDK/Wine passou: ROM `10242282b1ccedccbf37bcad0579b13298009bb67bfe24678bebe0f0486020a6`.
- Testes host passaram: `test_title_menu_contract.py`, `test_hud_identity_contract.py`, `test_hud_segment_contract.py`, `test_stage_definition_contract.py` e `test_stage_selection_contract.py`.
- Evidência BlastEm no mesmo hash: `out/emulator_evidence/visual_ko_20260919T022950Z/00_select.png` e manifesto selection-only; probe curto `out/emulator_evidence/visual_ko_20260919T023454Z/` registrou 2 hits, HPRB/HSEM e 60,2 fps no título da janela.
- V10 do backlog passou a `implemented_partial`. Próximo passo: estabilizar e capturar a troca de palco/confirmacão, depois fechar HUD/impacto/áudio com o mesmo ciclo de evidência.

## 2026-09-19 — VLAB e evidência BlastEm selados

- Build atual: `662ca81644013736f0ac01d0365d277d36b8f5b463192278532a5c7aedfe75dd`.
- Probe visual `VLAB` adicionado em SRAM `0x200`; HPRB/HSEM preservados em
  `0x500`/`0x580` para gerar dump visual e métricas canônicas sem quebrar os
  decoders diagnósticos.
- BlastEm selou `out/evidence/blastem/` com ROM, screenshot, SRAM, VDP dump e
  runtime metrics. A luta foi selada em
  `out/emulator_evidence/visual_ko_20260919T025744Z/`, com 7008/7782 B DMA,
  41 sprites ativos, 17/scanline e 1 hit observados.
- O seletor SHOWDOWN está evidenciado no SHA atual; a captura visual de BGB2,
  confirmação/desconfirmação, partida completa/revanche e audição crítica ainda
  não foram promovidas. Claim permanece `prototype_partial`.

## 2026-09-19 — Áudio de sinal e captura de palco estabilizada

- Probe BlastEm `visual_ko_20260919T031410Z` foi selado no SHA atual; HPRB/HSEM
  foram decodificados e o WAV isolado passou a auditoria de sinal/rota (48 kHz,
  estéreo, 11,55 s, sem clipping).
- `capture_visual_ko.py` passou a aguardar 1,5 s após o C e a respeitar
  `--select-only` sem confirmar A/X. A nova captura mostra o seletor completo
  Ryo/Musgo com `STAGE BGB2`, corrigindo a falsa captura de luta no manifesto.
- A audição crítica do mix e a prova visual final do rótulo BGB2 continuam
  pendentes; claim permanece `prototype_partial`.

## 2026-09-19 — Partida completa e revanche no SHA atual

- Playtest BlastEm `visual_ko_20260919T032351Z` observou Ryo/Musgo em BGB2,
  dois KO, duas telas `PLAYER 1 WINS` e `rematch_round.png` com input normal.
- Bundle selado: 42 hits, 2 KO, 3180 amostras, 7016/7782 B DMA, 71 links VDP
  e 17 sprites/scanline. Os picos de DMA e scanline vieram de frames distintos.
- V13 passou a `implemented_partial`; escuta crítica, CPU/jitter, pior frame
  combinado e revisões independentes continuam pendentes.

## 2026-09-19 — DRAW por time-over observado e selado

- ROM atual: `a602c21d29607ff36d34355c92081833ec7060c9ebc2433c134e33daaa69ec38`.
- `out/emulator_evidence/visual_ko_20260919T042046Z/evidence_manifest.json` foi selado no BlastEm com `combat_175.png` mostrando `DRAW` e SRAM/VLAB/VDP dump do mesmo SHA.
- HDBG da sessão confirma `clock=00`, estados `615/615`, energia `96/96`; HPRB confirma zero hits e zero KO. O harness agora preserva o primeiro estado terminal e não usa mtime histórico da ROM.
- O ciclo segue parcial: P2 confirmation, audição crítica, CPU/jitter, pior frame combinado, governança e revisões independentes não estão fechados.

## 2026-09-19 — Confirmação/desconfirmação do seletor

- A rota `visual_ko_20260919T032851Z` capturou `OK` no P1 após A e retorno ao
  título após B, sem misturar gameplay ao manifesto da seleção.
- A confirmação visual explícita do P2 permanece pendente; V10 segue
  `implemented_partial`.

## 2026-09-19 — Correção do contrato VLAB e evidência atualizada

- Corrigida a escrita extra no bloco `VLAB` que deslocava a paleta: `words[24..42]` agora emite exatamente 19 palavras; o teste de contrato e o self-check do sealer passaram.
- Novo build: ROM `3ca61393cc365661dec9a3a1ee1b753ee27dd319bc972d0abb201cadb31a663a`.
- DRAW real selado no BlastEm em `out/emulator_evidence/visual_ko_20260919T045421Z/evidence_manifest.json`, com screenshot `combat_175.png`, HDBG `clock=00`, estados `615/615`, energia `96/96`, HPRB `7020` amostras, `7008/7782 B` DMA e `17/20` sprites por scanline.
- P2 confirmado visualmente no mesmo SHA em `out/emulator_evidence/visual_ko_20260919T050147Z/02_both_confirmed.png`; a captura inclui P1 confirmado e desconfirmação.
- O ciclo continua parcial: performance sustentada, áudio auditado, gameplay completo e gates de governança/arte ainda não estão fechados.

## 2026-09-19 — Validação e revisão independente rebindingadas

- Validação canônica reexecutada com `-CloseoutGate`: 130 checks, 18 erros e 66 warnings no estado atual. O projeto segue `technical_incomplete`; os blockers foram persistidos em `out/logs/validation_report.json`.
- `doc/independent_quality_review.json` foi rebindingado ao relatório de validação atual e passou `quality_review_router.py validate-report`. A decisão é `revise_before_growth`; claim `unproven`; `ready_for_aaa=false`.
- O backlog e a iteração registram que P2 confirmation já foi observada, enquanto escuta crítica, CPU/jitter, residência VRAM, pior frame combinado, recaptura de eventos no mesmo SHA e gates de governança permanecem abertos.

## 2026-09-19 — HUD: banner autoral de KO

- Adicionado `spr_hud_ko_banner`, recurso nativo 48x24 derivado de fonte
  autoral persistida, com conversão indexada, transparência e entrada no
  manifesto de proveniência.
- `src/hud.c` agora exibe o banner apenas durante o estado de KO e o oculta em
  ROUND/FIGHT/resultado, sem alterar a semântica da partida.
- Build e playtest BlastEm vinculados ao SHA
  `58199903b60bd69e1255cfdc8dcb5fa7c992879f838729972f884e74ab667efc`.
  Evidência: `out/emulator_evidence/visual_ko_20260919T131512Z/`.
- Os contratos estáticos visual probe, HUD identity, special bar, KO defeat,
  title menu, stage selection e combo passaram. O restante do pipeline continua
  parcial pelos blockers registrados na memória operacional.

## 2026-09-19 — Title e captura final da iteração visual

- `src/title.c` recebeu card azul e moldura de acento vermelho escuro para
  substituir o retângulo preto bruto do menu. A rota de retorno foi validada em
  BlastEm: `out/emulator_evidence/title_return_20260919T130908Z/`.
- O KO foi recapturado pelo lado P2/Musgo no BlastEm com a ROM final da rodada:
  `out/emulator_evidence/visual_ko_20260919T131512Z/`.
- SHA final: `58199903b60bd69e1255cfdc8dcb5fa7c992879f838729972f884e74ab667efc`.
  Status continua `prototype_partial`; não houve promoção AAA.

## 2026-09-19 — Cartões de seleção e limpeza de matte do Musgo

- `src/select.c` recebeu cartões BG_A azul profundo, moldura vermelha escura,
  identificação P1/P2, nomes e comandos reorganizados. Evidência final:
  `out/emulator_evidence/visual_ko_20260919T135125Z/selected_final.png`.
- `data/source_art/musgo/convert_musgo.py` passou a rejeitar cores rosa/púrpura
  de matte antes e depois da quantização, removendo o halo cromático na ROM.
  O mesmo conversor agora reemite `fall_v1`, `defeat_v1` e `victory_v1` no
  `.res` e na tabela C, evitando regressão em rebuilds.
- Build SGDK/Wine aprovado e ROM final:
  `fe5d55de3b713d9279b93abbe0194112e250bb10b84a70b76cc9746552267db8`.
- BlastEm: `out/emulator_evidence/visual_ko_20260919T134925Z/` confirma
  combate, KO, vida zerada, banner próprio e revanche a 60,0–61,1 fps.
  Título/opções/retorno: `out/emulator_evidence/title_return_20260919T135151Z/`.
- Sem promoção AAA: áudio, CPU/jitter, pior quadro combinado, parallax/ambiente
  e revisão independente continuam pendentes.

## 2026-09-19 — Legibilidade do HUD revalidada

- `src/hud.c` passou a usar PAL2/PAL3 para nomes e estrelas, removendo o texto
  preto sobre o palco sem alterar sprite count, VRAM ou CRAM budget.
- ROM nova: `9027cb528431b3e43ea6e735acf3792ebf42cdc518163dd4af0abcbacf7ec668`.
  BlastEm: `out/emulator_evidence/title_return_20260919T150646Z/` e
  `out/emulator_evidence/visual_ko_20260919T150750Z/`.
- A rota visual parcial foi validada entre 59,2 e 61,1 fps. Como a captura não
  fechou zero de vida, KO/revanche não foram promovidos para esse SHA; o status
  continua `prototype_partial`.

## 2026-09-19 — KO/revanche e áudio no SHA 9027cb52

- O harness agressivo ganhou janela de 360 passos, sem injetar estado. BlastEm
  confirmou `zero_1_result.png` e `rematch_round.png` em
  `out/emulator_evidence/visual_ko_20260919T151652Z/`.
- Probe curto com áudio real em
  `out/emulator_evidence/visual_ko_20260919T151846Z/` capturou WAV estéreo de
  41 s a 48 kHz, pico `-14,9 dB` e média `-28,2 dB`, sem clipping. A escuta
  crítica ainda é pendência.
- O status permanece `prototype_partial`; não houve promoção AAA.

## 2026-09-19 — Glints ambientais no BGB2

- Adicionado `data/source_art/stage2_swamp/build_water_glints.py` e o recurso
  `res/sprite/stage/water_glint.png`, quatro frames indexados derivados do
  palco autoral BGB2. A proveniência foi declarada como
  `procedural_composed_from_authored` e permanece `placeholder`.
- `src/stage.c`, `src/main.c` e `src/scene.c` integram três sprites PAL0 de 2
  tiles cada, atrás dos lutadores, com atualização temporal e teardown de cena.
- ROM de SHA
  `1f2120842f8820fecbadc4acd9265830aa7f8b493fa75f0abc577b0eb7b02312` passou os
  sete contratos selecionados e foi observada no BlastEm em
  `out/emulator_evidence/visual_ko_20260919T142855Z/`. A rota de telas foi
  recapturada em `out/emulator_evidence/title_return_20260919T143530Z/`.
- O avanço é parcial: há ambiente animado de baixa pressão, mas não existe
  ainda parallax/multi-plano real, cobertura completa de poses, golpe assinatura
  com áudio auditado, pior frame combinado ou revisão independente fechada.

## 2026-09-19 — Fechamento da iteração visual comparativa

- Corrigido o frame de vitória `612`: a animação permanece autoral, mas usa a
  folha compacta `spr_ryo_611`, eliminando a troca 8x17 que corrompia o KO.
- Adicionado aquecimento determinístico de sprite em `src/player.c`/`src/graphics.c`:
  definição nova fica oculta até o upload DMA completar; o reset não expõe
  tiles inválidos.
- Melhorado contraste do HUD: rótulos `SP` usam PAL2/PAL3; seleção usa o
  índice 15 da fonte padrão, deixando instruções e nomes brancos nos cards.
- Build final SGDK/Wine aprovado. ROM:
  `895642485a6269293ef3f812befc1aef7e61c711db78c7286dc5449d5f47dec5`.
- Evidências finais BlastEm: `visual_ko_20260919T183010Z`,
  `visual_ko_20260919T182850Z`, `visual_ko_20260919T182730Z` e
  `title_return_20260919T182758Z`.
- QA: oito contratos estáticos + self-check HPRB passaram; HPRB ficou em
  7520 B DMA, 12 sprites/scanline, 21 hits, 1 projétil e 1 KO.
- Áudio isolado do mesmo SHA foi capturado em
  `out/emulator_evidence/visual_ko_20260919T183824Z/emulator_audio.wav`:
  48 kHz estéreo, 40,55 s, pico -15,3 dB, RMS -28,17 dB e zero clipping.
  A captura comprova sinal vinculado à ROM; a escuta crítica do mix continua
  pendente.
- Status mantido em `prototype_partial`; áudio atual, cobertura integral de
  animações, parallax real, pior quadro combinado, CPU/jitter e revisão
  independente continuam pendentes.

## 2026-09-19 — HUD especial, telas e semântica recapturados no mesmo SHA

- Corrigidos os estados vazio/preenchido do especial com placas autorais opacas,
  removendo os buracos pretos observados no HUD durante o combate e KO.
- Título/opções, seleção, combate, KO, revanche e retorno foram recapturados no
  BlastEm usando a ROM `933ce216c18e6cc8ee74125426d524a3e3e493a1b73e8ec92fd5df0c91e647ac`.
- A rota semântica `visual_ko_20260919T192457Z` confirmou projétil visual, HSEM
  com 67 frames de fireball e HPRB com 2 projéteis, 2 hits, 1 guarda, DMA dentro
  de `7424/7782 B` e 12/20 sprites por scanline.
- A captura WAV `visual_ko_20260919T192047Z/emulator_audio.wav` passou a análise
  objetiva de sinal: 48 kHz estéreo, 84 s, sem clipping. Escuta humana permanece
  pendente.
- O backlog visual foi atualizado para apontar para essas evidências; nenhuma
  promoção AAA foi feita. O status segue `prototype_partial` até fechar poses,
  palco/parallax, pior quadro combinado, CPU/jitter e revisão independente.

## 2026-09-19 — Closeout operacional e revisão rebindingada

- Executado o closeout real de BGB2 sem rebuild/captura: seis etapas passaram,
  quatro ficaram em warning, uma foi pulada e o relatório final ficou em
  `out/logs/scene_closeout_gate_report.json` com `status=warn`.
- A validação final foi regenerada: `errors=4`, `warnings=85`; os blockers
  restantes estão registrados e não foram mascarados para produzir verde falso.
- Frescor, validação e closeout foram vinculados novamente à ROM
  `933ce216c18e6cc8ee74125426d524a3e3e493a1b73e8ec92fd5df0c91e647ac` na
  solicitação/parecer de qualidade. A validação do parecer passou, mas a decisão
  segue `revise_before_growth`, sem promoção AAA.

## 2026-09-19 — Seleção e palcos recapturados no SHA df648176

- Refinada a tela de seleção com cards P1/P2 distintos, retratos, nomes, estados de confirmação e escolha de palco. A confirmação dupla foi comprovada com input físico no BlastEm.
- Recapturados no mesmo SHA: seleção `visual_ko_20260919T203208Z`, combate/KO `visual_ko_20260919T203454Z`, especial/guard `visual_ko_20260919T203704Z`, BGB2 `visual_ko_20260919T204301Z`, SHOWDOWN `visual_ko_20260919T204612Z` e transições `title_return_20260919T205316Z`.
- HPRB/HSEM permanecem diagnósticos: 7424 B DMA, 50 sprites VDP, 12 sprites/scanline, 2 projéteis, 2 hits e 1 guard na rota semântica; a rota completa registrou 41 hits e 2 KO. O projeto segue `prototype_partial` porque escuta crítica, coverage de animações, CPU/jitter, residency, pior frame e gates de higiene/proveniência ainda não fecharam.
- O harness agora espera a cena real antes de capturar, usa o binding correto de P2 A e separa o modo explícito `--showdown`; contratos de menu e palco passaram. A validação canônica atual reporta 137 checks, 18 erros e 73 warnings, sem promoção AAA.
- O parecer independente foi rebindingado ao request/plan atuais e validado novamente: `status=passed`, porém `revise_before_growth`, `quality_claim=unproven` e `ready_for_aaa=false` permanecem obrigatórios.

## 2026-09-19 — Evidência canônica BlastEm atualizada

- Regenerado `out/logs/blastem_capture_route_report.json` para a rota Linux/Flatpak com `target_scene=1`, compatível com o boot real da ROM.
- Selado `out/evidence/blastem/evidence_manifest.json` na sessão `blastem-linux-20260919T211315Z-3033329`, com screenshot, SRAM, dump VDP, ROM e métricas no SHA `df648176a73fa1ff67ba939f21226fc07d7da53e685da8d00eb986a3e56509fa`.
- Auditoria de frescor e closeout semântico passaram; o relatório mantém a limitação explícita de que um snapshot de `59,7 fps` não prova performance sustentada.

## 2026-09-19 — Matriz P10 recapturada e runner corrigido

- `run_p10_matrix.py` agora passa `--showdown` para os casos `showdown_park`; o contrato de palco foi validado com captura real.
- `capture_visual_ko.py` passou a usar nomes únicos por microssegundo/PID e fallback do `default.cfg` local quando o Flatpak falha transitoriamente por pressão de tmpfs.
- Os 36 casos P10 foram renovados no SHA `df648176`; `summarize_p10_hprb.py` e `test_p10_evidence_integrity.py` passaram. O resumo registra DMA máximo `8176 B`, 14 sprites ativos, 47 links VDP e 12 sprites/scanline.

## 2026-09-19 — Palco BGB2 reautorado, KO ampliado e evidência renovada

- Reautorado o BGB2 a partir de `generated_stage2_v02.png`, com prompt, hash,
  conversão, conflitos de paleta e flags registrados. A cena usa 960 tiles
  únicos e permanece declarada como `compare_flat`, sem inventar parallax.
- Promovido o KO para a folha `ko_banner_big.png` 12x6; BlastEm mostrou o
  letreiro ampliado, combo, HUD autoral, retratos e vencedor em
  `visual_ko_20260919T221705403442Z-3268880/zero_1_result.png`.
- A rota semântica atual confirmou projétil Ryo e FX de impacto em
  `visual_ko_20260919T222523465819Z-3299137/`; a seleção/dupla confirmação foi
  recapturada em `visual_ko_20260919T230347890426Z-3470306/`.
- Recapturados os 36 casos P10 no SHA `723ba8c2b69555965800f5e09dccc5fa9d5f90ff7194d3d5d0c9a2a1c7498454`;
  o teste de integridade passou e todos estão `pending_visual_review`.
- Áudio isolado do mesmo SHA foi capturado em
  `visual_ko_20260919T225923273658Z-3454647/`: 48 kHz, 43,8 s, sem clipping;
  escuta crítica ainda não realizada.
- Bundle canônico BlastEm selado na sessão `blastem-linux-20260919T230119Z-3462151`;
  frescor `ok`. Status permanece `prototype_partial`, sem promoção AAA.
- Proveniência voltou a `verdict=OK` após adequação do manifesto ao schema
  canônico; título/opções/retorno foram recapturados em
  `title_return_20260919T231045Z/` no mesmo SHA.

## 2026-09-19 — Ken ganhou terminais autorais e foi confrontado no BlastEm

- Adicionadas fontes autorais, conversão indexada e os sprites `victory_v1` e
  `defeat_v1` de Ken.
- Ken deixou de reutilizar idle em 611/612/570/615; Musgo deixou de reutilizar
  idle em 615. O runtime recria o handle nos terminais.
- Build SHA `8ac1bda70511fbd395af9a3fa3f49ca356e39dec31254b8f336f96a0a405e506`.
  BlastEm confirmou a vitória de Ken em
  `out/emulator_evidence/visual_ko_20260919T232926387580Z-3579731/zero_1_result.png`.
  A rota P2 por teclado ficou registrada como pendência de QA; status segue
  `prototype_partial`.

## 2026-09-20 — P10 renovado no SHA atual

Renovada a matriz P10 com a ROM
`8ac1bda70511fbd395af9a3fa3f49ca356e39dec31254b8f336f96a0a405e506`:
36/36 probes concluídos, 0 falhas, todos pendentes de revisão visual. A nova
rota semântica em
`out/emulator_evidence/visual_ko_20260920T001624972891Z-3780703/` capturou
entrada, round e frames de especial, porém não gerou SRAM/HSEM e terminou com
overlay de pausa/debug; foi registrada como evidência inconclusiva, não como
aprovação. O projeto segue `prototype_partial_current_sha`.

O fallback de seleção do harness foi corrigido para usar START exclusivo do P2 (`f2`), evitando que uma entrega tardia acione o painel de pausa/debug do P1. A recaptura em `out/emulator_evidence/visual_ko_20260920T002156365973Z-3833796/` ficou limpa desse overlay, mas não gerou SRAM/HSEM nem prova inequívoca do projétil; segue inconclusiva.

Título, opções e retorno foram recapturados no SHA atual em `out/emulator_evidence/title_return_20260920T002445Z/`; as cinco capturas têm framebuffer não vazio e seguem sem aprovação sensorial automática.

A seleção P2 foi recapturada com Ryo/P1 e Ken/P2 em `out/emulator_evidence/visual_ko_20260920T002637710025Z-3870542/selected_final.png`; cards, retratos e palco BGB2 aparecem no SHA atual. A pendência específica de teclado P2 foi resolvida, permanecendo confirmação dupla/mirror-match para revisão dedicada.

## 2026-09-20 — Projétil especial confrontado visualmente no SHA atual

- A rota isolada `--specials-only` foi executada com teclado real no BlastEm e
  gerou `out/emulator_evidence/visual_ko_20260920T033026169476Z-462317/` com
  `save.sram`, HSEM, HPRB, vídeo e quadros PNG.
- O frame `special_only_p1_try0_4.png` mostra o projétil autoral laranja de Ryo
  em voo contra Musgo; HSEM mede 204 frames de projétil e HPRB mede 3 eventos de
  projétil/3 hits. Pico: 7424 B DMA, 48 sprites VDP e 12 sprites/scanline.
- Guarda e throw continuam explicitamente sem prova: HSEM/HPRB mediram zero
  nesta rota. O projeto segue `prototype_partial_current_sha`, sem promoção AAA.

## 2026-09-20 — Agarrão same-ROM confrontado em quadro intermediário

- A rota `--throw-only` foi corrigida para excluir o fallback de START que
  abria `PAUSE/DEBUG` e repetida com teclado real. O bundle válido é
  `out/emulator_evidence/visual_ko_20260920T034410560385Z-533030/`.
- `throw_only_contact_4.png` mostra Musgo suspenso durante o agarrão, Ryo em
  recuperação e `2 HITS`; HSEM mede 68 frames de throw P1 e HPRB mede 2 throws/2
  hits no SHA atual. Envelope: 7424 B DMA, 48 sprites VDP e 12/scanline.
- Guarda segue sem prova positiva. O projeto permanece `prototype_partial_current_sha`,
  sem promoção AAA.

## 2026-09-20 — Guarda same-ROM confrontada com impacto sem dano

- A rota `--guard-only` foi ajustada para lançar primeiro e entrar em recuo no
  instante correto. O bundle válido é
  `out/emulator_evidence/visual_ko_20260920T035134604414Z-571565/`.
- `guard_only_06.png` mostra sparks de bloqueio sem dano; HSEM mede 76 frames de
  guarda P2 e HPRB mede 1 guard/1 projétil/0 hits. Pico: 7424 B DMA, 61 sprites
  VDP e 12 sprites/scanline.
- Com especial, agarrão e guarda agora confrontados no mesmo SHA, permanecem
  abertos hitstop, cobertura completa, áudio, pior quadro e revisão sensorial.
  Status continua `prototype_partial_current_sha`, sem promoção AAA.

## 2026-09-20 — Câmera de impacto e recaptura semântica no SHA 640c3223

- Implementado tremor determinístico de câmera para hit, guarda e throw aceitos;
  o HUD permanece screen-locked e os lutadores acompanham o deslocamento do palco.
- Build vigente: `640c3223ec5b674af237e7ed31895540c5b7e7e5e6d4acce2376345b5f06cf90`.
- BlastEm confirmou o projétil em
  `visual_ko_20260920T041415021491Z-688336/special_only_p1_try0_2.png`, o
  agarrão em `visual_ko_20260920T041830157874Z-704017/throw_only_contact_4.png`
  e a guarda em `visual_ko_20260920T040520275634Z-656638/guard_only_05.png`.
- HPRB same-ROM: especial 2 projéteis; throw 2 throws/2 hits; guard 1 guard/0
  hits. O bundle throw mediu 7424 B DMA, 48 sprites VDP e 12/scanline.
- A evidência reduz a lacuna de resposta e descarta bundles anteriores stale,
  mas não fecha telas, áudio, hitstop, cobertura de poses, pior quadro ou revisão
  independente. Status permanece `prototype_partial_current_sha`.

## 2026-09-20 — HUD compacto e seleção integrada no SHA 7431b4ee

- Seleção usando BGB2 autoral como BG_B, com cards, retratos, VS, estágio e
  comandos em placas PAL1; contrato estático e captura real atualizados.
- Chassis vazio da vida convertido em três tiles BG_A autorais (ponta, corpo,
  ponta), repetidos e espelhados no P2. O custo caiu de 32 para 3 tiles,
  evitando sobreposição com a região automática de sprites no BGB2.
- BlastEm validou especial e guarda no mesmo SHA: 7424 B DMA, 48/61 sprites VDP
  conforme a rota e 12 sprites por scanline. Proveniência segue sem blockers.
- KO, opções reais, revanche, throw, áudio e P10 ainda exigem recaptura/escuta;
  status continua `prototype_partial_current_sha`, sem promoção AAA.

## 2026-09-20 — KO e resultado validados no SHA 7431b4ee

- Bundle same-ROM: `out/emulator_evidence/visual_ko_20260920T053546652798Z-1001707/`.
- `zero_1_settle.png` mostra o letreiro autoral `KO`; `after_combat.png` mostra
  `PLAYER 1 WINS` e a pose de vitória de Ryo.
- HPRB: 2 KO, 41 hits, decisão `cabe`, 7424 B DMA, 66 sprites VDP e 12
  sprites/scanline. A tentativa anterior com PAUSE/DEBUG foi descartada.
- Revanche, throw, áudio, P10, cobertura completa de animações e revisão
  independente continuam abertos; não há promoção AAA.

## 2026-09-20 — Throw validado no SHA 7431b4ee

- `out/emulator_evidence/visual_ko_20260920T054131172698Z-1018183/throw_only_contact_4.png`
  mostra Musgo suspenso, Ryo na recuperação e `2 HITS`.
- HSEM mede 68 frames de throw P1; HPRB confirma 2 throws/2 hits, 7424 B DMA,
  48 sprites VDP e 12 sprites/scanline. A resposta de impacto agora tem
  especial, guarda, throw e KO com bundles same-ROM.

## 2026-09-20 — BGB2 reautorado com 1200 tiles e evidência same-ROM

- `data/source_art/stage2_swamp/convert_stage2.py` agora usa 1200 tiles
  residentes, após comparação controlada das variantes 1040/1120/1200.
- A variante preserva com mais clareza os landmarks da árvore, água e doca;
  `src/stage.c` registra o orçamento medido e a proveniência da fonte autoral.
- ROM atual: `7fd291d0757bd27e14dedb019ea2ba4c38c598fceb07b4927e455f7a559d7175`.
- BlastEm: captura visual em
  `out/emulator_evidence/visual_ko_20260920T064257144603Z-1254842/`; HPRB/HSEM
  same-ROM em `out/emulator_evidence/visual_ko_20260920T064514671796Z-1263807/`.
  O probe mediu 7360 B DMA, 36 links VDP e 12 sprites/scanline.
- Status continua parcial: outras telas e o pior quadro combinado ainda não
  foram renovados neste SHA.

## 2026-09-20 — Fatia de combate recapturada no SHA 7fd291d0

- Seleção, título, combate, KO e resultado foram recapturados no mesmo hash;
  a seleção está em `out/emulator_evidence/visual_ko_20260920T065443726553Z-1313427/`
  e KO/resultado em `out/emulator_evidence/visual_ko_20260920T065617081824Z-1329197/`.
- Probe same-ROM em
  `out/emulator_evidence/visual_ko_20260920T070346595817Z-1352074/` confirmou
  2 KO/42 hits, 7424 B DMA, 48 links VDP e 12 sprites/scanline; `decision=cabe`.
- A captura não promove AAA: opções, revanche dedicada, guarda/throw sem SRAM,
  áudio, P10, cobertura completa de poses, residência de VRAM e revisão
  independente permanecem abertos.

## 2026-09-20 — Título, opções e retorno recapturados no SHA 7fd291d0

- `tests/capture_title_return.py` gerou cinco capturas e a página de opções em
  `out/emulator_evidence/title_return_20260920T071630Z/`.
- O backlog visual foi rebindingado para o mesmo hash do palco e combate;
  tipografia e revisão independente permanecem abertas.

## 2026-09-20 — Fatia visual confrontada no SHA 9509ebbb

- Título final candidato: wordmark HAMOOPIG legível em escala nativa, porco
  separado à direita, pixel solto removido e painel principal compacto em
  `src/title.c` e `data/source_art/title/prepare_title_assets.py`.
- BGB2 foi limitado ao teto vivo de 864 tiles após a tentativa de 1200 gerar
  `Fight tiles overlap sprite VRAM`; a conversão e os testes de contrato
  passaram, e BlastEm confirmou o boot da luta sem esse guard.
- BlastEm recapturou título/opções/retorno em
  `out/emulator_evidence/title_return_20260920T075901Z/`, seleção em
  `out/emulator_evidence/visual_ko_20260920T075359233429Z-1521442/`,
  KO/resultado em `out/emulator_evidence/visual_ko_20260920T074931694042Z-1506141/`
  e especial/FX em `out/emulator_evidence/visual_ko_20260920T080009749866Z-1541958/`.
- A sessão de combate observou 59.5–60.8 fps; a evidência permanece parcial e
  não promove AAA. Ainda faltam revisão independente, áudio auditado, revanche,
  guarda/throw same-ROM, P10 e cobertura integral de animações.

## 2026-09-20 — Música autoral e Sound Test no SHA e9e0efc1

- Substituída a BGM de referência por `Forge Crystal`, score autoral em três
  vozes PSG, com loop NTSC de 12,8 s e atenuação separada para preservar
  clareza. Fonte: `data/source_audio/forge_crystal_score.json`.
- `res/sound.res` agora exporta `mus_forge_brand`; a luta usa essa faixa e
  mantém PCM CH3/CH4 para SFX. O recurso antigo `bgm_ken_stage` deixou de ser
  usado pelo runtime.
- Implementado Sound Test real em OPTIONS, com PLAY/STOP, retorno por B e
  reprodução do mesmo recurso da luta.
- Build bridge aprovado: ROM `e9e0efc1a8894434911cc6f1054f1c9a072853927a56b983c9eec8c43e12a833`
  (2490368 B). Captura same-ROM e WAV isolado em
  `out/emulator_evidence/sound_test_20260920T123713Z/`; auditoria de sinal
  passou sem clipping e com rota privada confirmada.
- A auditoria de áudio não substitui escuta humana: emenda de loop, balanço
  musical, timbre PSG e mascaramento de SFX ainda são revisão aberta. Sem
  promoção AAA.
## 2026-09-20 — Fechamento honesto do diagnóstico visual no SHA 3f6e57d2

- Reproduzida a diferença entre corrupção de plano e degradação do asset: o HUD
  agora escreve no WINDOW, mas a fonte dos retângulos restantes era a redução de
  1.887 tiles para 864 por substituição de tiles inteiros.
- Promovida a tradução BGB2 bloco 4, com composição de árvore, água e doca
  preservada, build ResComp regenerado e captura BlastEm válida no hash atual.
- Registradas as variantes bloco 2 (quadrados falsos em runtime) e bloco 3
  (falha de boot no BlastEm) como não promovidas; não contam como evidência.
- HPRB/HSEM foram decodificados no mesmo SRAM/ROM; envelope nominal cabe, mas a
  entrega continua parcial e sem claim AAA.
## 2026-09-20 — Sound Test same-ROM renovado

- Sound Test e `Forge Crystal` foram capturados no SHA `3f6e57d2…`, com PLAY,
  loop observado e STOP visíveis na tela.
- WAV isolado analisado: 48 kHz estéreo, 17,9 s, pico -19,07 dBFS, RMS
  -24,47 dBFS, sem clipping. O resultado é integridade objetiva de sinal; não
  substitui escuta crítica.

## 2026-09-20 — Seleção, HUD e BGB2 confrontados no SHA 8e7a34dc

- Seleção passou a usar a superfície autoral traduzida `generated_select_surface_v03.png`;
  204 tiles em BG_A, base 655, sem sobreposição da reserva de sprites. BlastEm
  confirmou a captura em `out/emulator_evidence/visual_ko_20260920T224941749302Z-331917/`.
- BGB2 adotou reuso regional preservador de material: 857 tiles efetivos dentro
  do orçamento 864. A captura same-ROM em
  `out/emulator_evidence/visual_ko_20260920T230426778949Z-380612/` mostra a
  composição de água/doca/raízes sem a corrupção retangular dominante.
- Life bars passaram a usar atlas autoral azul/dourado composto do chassis
  persistido; `VDP_setWindowFullScreen()` materializa nomes, especial, combo e
  mensagens no WINDOW.
- Sound Test recapturado no mesmo SHA em
  `out/emulator_evidence/sound_test_20260920T231117Z/`; a análise objetiva do
  WAV passou com 48 kHz estéreo, sinal presente e zero clipping.
- Status honesto: `prototype_partial_current_sha`; ainda sem claim AAA. KO,
  FX completo, partida/revanche, escuta humana e revisão independente continuam
  como gates abertos.

- A partida longa same-ROM em `out/emulator_evidence/visual_ko_20260920T232720289830Z-454619/`
  observou reset de round e 59,9–61,1 fps, mas não exportou um terminal de KO;
  essa sessão permanece diagnóstico, sem promoção de claim.

## 2026-09-20 — Captura de KO/revanche corrigida causalmente

- O detector de vida não tratava caps quentes da moldura autoral como estado
  vazio; por isso uma SRAM válida com `energiaBase=0` era reportada como luta
  incompleta. A heurística foi canonizada em `doc/03_art/02_visual_feedback_bank.md`.
- `tests/capture_visual_ko.py` agora registra a amostra visual de vida baixa,
  confirma o estado KO pelo HDBG da mesma ROM, aguarda `SCENE_AFTER_MATCH` e só
  chama A para capturar `rematch_round` depois de observar o retorno à luta.
- O build/ROM ainda não mudou nesta etapa; a próxima evidência deve ser gerada
  contra o SHA vigente e não pode promover qualidade antes de o bundle conter
  `terminal_capture`, `after_match_capture` e `rematch_capture`.
- O replay expôs que HDBG também precisava ser reinicializado por round; essa
  correção foi aplicada em `HAMOOPIG_probeFightInit` e exige novo build antes
  da próxima captura same-ROM.

## 2026-09-21 — Bundle final de partida e áudio no SHA 5a99b076

- BlastEm fechou dois KO visuais, `PLAYER 1 WINS` e retorno A à revanche em
  `out/emulator_evidence/visual_ko_20260920T235500737537Z-543800/`.
- HPRB same-ROM confirmou 3.750 frames, 2 KO, 7.424 B DMA, 50 links VDP e 13
  sprites por scanline; HSEM foi decodificado no mesmo SRAM.
- Sound Test foi recapturado no SHA atual em
  `out/emulator_evidence/sound_test_20260920T235813Z/`; Forge Crystal tem
  sinal estéreo 48 kHz, 17,05 s e zero clipping. A escuta crítica permanece
  explicitamente não executada.
- O roteador de revisão independente foi reexecutado e selecionou art,
  gameplay e audio; não houve executor independente disponível, portanto o
  parecer permanece pendente e `ready_for_aaa=false`.

## 2026-09-21 — Arranjo Forge Crystal v2, Sound Test corrigido e combate com áudio

- Criado `data/source_audio/build_forge_crystal_v2.py`, removendo a referência
  documental a um `psg_score.py` inexistente e compilando um loop autoral de
  quatro vozes PSG (lead, baixo, contraponto e ruído percussivo).
- Regenerados `res/music/mus_forge_brand.vgm`, `res/sound.rs` e a ROM pelo
  bridge canônico. O SHA vigente é
  `24262999f2390f14fe131ba3508e70ea348db024bd30cae43edc44082faad958`.
- Corrigido `tests/capture_sound_test.py` para usar bordas de input longas e
  não confundir START/OPTIONS com entrada no seletor. Sound Test foi provado na
  tela e no WAV isolado em `sound_test_20260921T002424Z`.
- Recapturado combate com áudio em
  `visual_ko_20260921T002700587260Z-640941`; os limites VDP cabem, porém CPU/jitter
  continuam bloqueando performance sustentada e audição humana/revisão independente
  continuam pendentes.

## 2026-09-21 — Eventos isolados e partida same-ROM após ajuste de agarrão

- Corrigida a hitbox dos estados 800/801 em `src/fsm.c`: a separação física
  mantém os lutadores a 100 px, então o alcance autoral agora cobre esse limite
  sem injeção de estado.
- Corrigido `tests/capture_visual_ko.py`: `SPECIAL RULES` usa o item 9 real e o
  comando down-forward-button cabe na janela de input da FSM.
- ROM vigente: `b6f7cd649f829c21555883014721992b04261f0c32b34a620538d0548be7cc88`.
  HPRB same-ROM: 2 KO/42 hits no match, 2 throws no probe de agarrão, 1 guard e
  3 projectiles nos probes isolados; todos `cabe` no envelope VDP.
- Evidência principal selada em
  `out/emulator_evidence/visual_ko_20260921T005523892270Z-727484/`; Sound Test
  renovado em `out/emulator_evidence/sound_test_20260921T005842Z/`. Sinal e rota
  de áudio passaram; escuta, CPU/jitter sustentados, revisão independente e
  paridade visual permanecem gates abertos.

## 2026-09-21 — HCAD: cadência de lógica e apresentação

- Adicionado `HCAD` em `src/hamoopig_runtime_probe.c` e as chamadas de fronteira
  em `src/main.c`; a telemetria agora distingue vídeo, lógica e apresentação.
- Adicionado decoder/contrato em `tests/analyze_hcad_cadence.py` e
  `tests/test_hcad_cadence_contract.py`.
- Build canônico/Wine e BlastEm same-ROM passaram. O relatório registra 7.260
  frames de vídeo, 7.260 ticks e 7.260 commits na captura NTSC; 6.353/6.353/6.353
  na luta. Isso remove a hipótese específica de frame perdido nessa rota, sem
  elevar o claim visual ou de performance sustentada.

## 2026-09-21 — Faixa de elenco 24x24 e evidência same-ROM d9334271

- Ampliados os retratos da seleção para três frames 24x24 com molduras de
  identidade ouro/azul/verde, preservando as fontes autorais de HUD e PAL0
  compartilhada. O ativo continua marcado como `placeholder` até revisão.
- Build canônico e captura BlastEm confirmaram a faixa em
  `visual_ko_20260921T020818911985Z-993126/00_select.png` e o ciclo de luta
  em `visual_ko_20260921T020916512873Z-996433/`.
- O manifesto same-ROM foi complementado com o HCAD decodificado:
  7.980 frames/commits totais e 7.071 frames/commits de luta, sem frame sem
  lógica. Isso prova cadência NTSC normal, não performance sustentada nem
  paridade visual final.

## 2026-09-21 — Sound Test same-ROM d9334271

- `sound_test_20260921T021855Z/` confirmou PLAY, loop e STOP na ROM atual.
- A captura isolada tem 48 kHz estéreo, 18,15 s, pico 3865, RMS -25,68 dBFS e
  zero clipping. O relatório permanece sinal-only: audição humana, mix com
  SFX e aprovação de timbre continuam pendentes.

## 2026-09-21 — Contraste de Musgo e ROM SHA 3c82c14b

- A conversão de Musgo agora usa rampa verde/oliva com highlights separados
  para melhorar a leitura contra BGB2, sem pixels de personagem em runtime.
- Build canônico gerou SHA `3c82c14b3c959098f09b57de7a387147b970eb42fabb1bf8af986c20e46938f9`.
  BlastEm confirmou seleção e match completo; HCAD mediu 6.060 commits totais
  e 5.049 na luta. A janela variou de 58,8 a 61,1 FPS, então performance
  sustentada não foi promovida.
## 2026-09-21 — Avaliação audiovisual rastreável V0–V5

- Adicionado plano obrigatório `doc/curation/2026_09_20/video_review/plano_avaliacao_audiovisual.md`, schema e ferramenta compartilhada `tools/sgdk_wrapper/audiovisual_review.py`.
- Congelados ROM/configuração e hashes; adicionados preflight, ingestão frame/PTS, índice, consulta com ROIs/player, findings candidatos e gates sem substituição entre eixos.
- Reforçada `tests/capture_visual_ko.py` com `-fps_mode passthrough`, relógios monotônicos, timeline e manifesto de vídeo; adicionado ensaio de overhead com e sem gravação.
- Preservados os masters histórico e V5. O histórico tem `drop=858` e três buracos PTS; o V5 audiovisual também permanece bloqueado por falhas de cadência e sem âncora de sync.
- Adicionados fixtures/regressões. O rótulo inicial `capture_integrity` foi
  posteriormente decomposto em identidade, integridade temporal da mídia e
  cadência do jogo; visual, movimento, áudio e cobertura permanecem
  bloqueados/`needs_review`. Nenhuma aprovação AAA.
## 2026-09-21 — Correção de claims e achado de gameplay audiovisual

- Corrigido o modelo do pipeline audiovisual: identidade de artefatos, PTS/drop
  da mídia, sincronização, HCAD/game cadence e revisão perceptiva agora são
  gates independentes; `capture_integrity` amplo deixou de ser o nome canônico.
- Implementada validação de revisão qualificada com reviewer, método,
  capacidades, hashes, intervalos, evidências, vereditos e cobertura calculada.
  Fixtures cobrem `null` de cobertura, revisão qualificada e separação HCAD vs
  continuidade de mídia.
- `capture_visual_ko.py` agora preserva fases boot/capture/finalization e
  finalização bounded mesmo quando ffmpeg não encerra; a medição repetida
  continua `needs_review` por pares válidos insuficientes.
- Captura especial same-ROM gerou achado candidato
  `gameplay-special-startup-transition-001`, com query 10,2–13,2 s, ROI,
  Down-Right-Q, HSEM/HPRB/HCAD e teste causal. Visual do evento foi liberado
  apenas no escopo observado; movimento, áudio e cobertura global permanecem
  bloqueados. Nenhuma correção de jogo ou promoção AAA foi feita.

## 2026-09-21 — HSTR, freeze e gate audiovisual qualificado

- O build usado na captura BlastEm foi congelado no SHA
  `d6b7ea5e3e43c97b75caff47fa113c841378704b423de50adc2f287732eb9618`, com
  rota e inputs hash-bound em `out/audiovisual_review/v5/freeze_hstr_v4/`.
- O probe do projeto agora registra HDBG schema 2 e HSTR schema 1 por
  apresentação no especial. O harness declara esse transporte no manifesto;
  o decoder/teste HSTR valida slots vazios, estados, animação e fireball.
- A captura real foi ingerida e consultada por sequência PNG consecutiva e ROI.
  O candidato `gameplay-special-emission-latency-003` é a primeira evidência
  de um possível defeito de emissão/render que prints espaçados poderiam perder,
  mas a associação HSTR↔PTS é host-clock estimada e não aprova causa.
- O gate qualificado libera somente identidade, HCAD e visual limitado ao
  evento visto; bloqueia PTS, sincronismo, movimento, áudio e cobertura. O
  overhead v3 preserva seis sessões, mas segue `needs_review`: só um par foi
  completo e duas sessões terminaram sem ROM/telemetria. Nenhuma aprovação AAA
  foi emitida.

## 2026-09-21 — Cobertura e revisão qualificada com validação estrita

- A validação de review agora exige reviewer, método, `tools`,
  `video_playback` e `audio_audition` como booleans, `evidence_refs` não vazios
  em todos os eixos e intervalos não examinados parseáveis.
- O complemento dos intervalos efetivamente vistos é calculado e comparado
  com `unexamined_intervals`; `null`, intervalo inválido e declaração
  inconsistente bloqueiam cobertura e qualquer claim perceptivo dependente.
- O gate HSTR real foi revalidado com sucesso estrutural, mas continua
  liberando apenas a observação visual limitada do evento; PTS, movimento,
  áudio e cobertura global continuam bloqueados.
- O contrato audiovisual foi integrado ao wrapper através de
  `ci/test_audiovisual_review_contract.py`; `run_all_contract_gates.ps1 -Mode schema`
  passou com 84 casos de schema e 3 casos audiovisuais.
- O relatório canônico de ingestão passou a se chamar
  `audiovisual_ingest_report.json`; achados de gaps são classificados como
  `media_temporal_integrity`, removendo a ambiguidade de `capture_integrity`.

## 2026-09-21 — Consulta com contexto e escopo visual reduzido

- A consulta agora gera pré/pós-contexto explícito e marca cada frame como
  `pre_context`, `event` ou `post_context`, preservando PTS, ROIs, hashes e
  divergência entre frames solicitados e decodificados.
- A revisão HSTR foi reduzida ao que foi realmente visto: três frames hash-bound
  nos source indices 620/631/652. O gate v9 libera somente visual limitado a
  esses frames; não libera movimento, áudio ou cobertura global.

## 2026-09-21 — V2 por índice-fonte exato e candidato de gameplay

- `audiovisual_review.py` 2.2.0 agora extrai consultas por índice-fonte com
  `ffmpeg select`, preservando PTS e declarando explicitamente a força do
  vínculo PNG↔source index; seek aproximado não pode mais ser confundido com
  identidade de frame.
- O query v10 fechou 241/241 frames, mantendo contexto e sem normalização de
  cadência. A inspeção efetiva dos source indices 620/631/652 confirma ausência
  do projétil no primeiro e presença nos dois seguintes.
- O achado `gameplay-special-emission-latency-005` é candidato de possível
  atraso de feedback/renderização correlacionado a HSTR, não aprovação nem
  causa confirmada. O gate v10 continua bloqueando movimento, áudio,
  sincronismo, integridade temporal e cobertura global.

## 2026-09-21 — Overhead repetido com janela runtime válida

- O modo `--probe-short` deixou de abortar por ausência transitória do HUD:
  prontidão visual continua exigida nas capturas de revisão, enquanto o
  overhead usa HCAD persistido e `fight_video_frames>0` como critério técnico.
- A execução v6 fechou dois pares no mesmo SHA e mediu por fase boot, captura,
  finalização e total. Medianas com vídeo: `-35,586 ms`, `-0,304 ms`,
  `+444,197 ms` e `+459,090 ms`, respectivamente.
- A diferença de janela de combate (`-6`/`+2` frames) permanece explicitamente
  fora de qualquer claim de FPS ou fluidez; o relatório continua separado da
  avaliação perceptiva.

## 2026-09-21 — Evidência de revisão com resolução de arquivos

- A revisão qualificada agora exige `evidence_root` e verifica que cada
  `evidence_ref` existe dentro da raiz, resolvendo caminhos relativos a partir
  do diretório do manifesto.
- Referência órfã, raiz ausente ou caminho fora da raiz desqualifica a revisão;
  o contrato do wrapper passou a cobrir esse caso.

## 2026-09-21 — Contrato de âncora audiovisual compartilhada

- `audiovisual_review.py` 2.3.0 e o schema de relatório registram
  `synchronization.anchor_contract` e rejeitam `capture_clock` como prova de
  sincronismo VDP/PTS/áudio.
- `runtime_media_anchor` só pode liberar `av_sync` quando contém bindings de
  runtime/presentation, índice-fonte e PTS do vídeo, amostra/taxa do áudio,
  erro medido, hashes de vídeo/áudio/ROM e evidência local; incompleto ou
  divergente permanece `needs_review`.
- O bundle real HSTR foi reingerido como v6 e o gate v11 permanece bloqueado
  nos eixos temporal, sincronismo, movimento, áudio e cobertura. ROM e masters
  foram preservados.

## 2026-09-21 — Suíte ampla e evidência P10 stale

- A suíte direcionada audiovisual passou em 19 testes. A suíte completa ficou
  bloqueada na coleta por evidência P10 stale (`8ac1…` contra o freeze `d6b7…`);
  o hash antigo não foi alterado.

## 2026-09-21 — Escopo explícito de claims

- O gate V12 passou a emitir `claim_scopes`: `visual_approval` só é liberado
  com o escopo declarado da revisão qualificada; movimento, áudio e cobertura
  recebem escopo `none` quando não sustentados. Isso impede interpretar um
  `released` limitado como aprovação audiovisual global.
## 2026-09-21 — Marcador runtime–vídeo–áudio e gate de binding

- Adicionada build diagnóstica isolável via `--extra-flags`/`--output-dir` no
  bridge SGDK; `out/rom.bin` não é substituído.
- Adicionado `HAMOOPIG_captureMarker`/HANC sob macro
  `HAMOOPIG_CAPTURE_MARKER`, suporte `capture_visual_ko.py --rom=...`, selo
  pós-flush e analisador de candidatos vídeo/áudio.
- O binder exige seleção explícita, reviewer e evidência local; binding
  `needs_review` não libera `av_sync`.
- Captura real BlastEm v3 foi ingerida e bloqueada: vídeo 59,65 s, áudio 60,10
  s, gap PTS de 33,333 ms, 2 candidatos visuais/209 de áudio. O resultado não
  é aprovação temporal, sonora ou de movimento.

## 2026-09-21 — Pacote V14 de revisão consecutiva

- Preservado o manifesto V11 e criado pacote V14 sem reutilizar seus intervalos
  arredondados: revisão efetiva de 13 frames consecutivos, source indices
  620–632, PTS 10,3375–10,5375 s, ROI gameplay e pré/pós-consulta já emitida.
- Criado `gameplay_finding_special_emission_latency_007.json`: candidato
  visual com causa não confirmada, correlação HSTR limitada e teste causal
  explícito para separar runtime de transporte/captura.
- Gate V14 qualificado estruturalmente, mas `blocked`: só identidade, HCAD e
  diagnóstico visual do intervalo declarado são liberados. Movimento, áudio,
  sincronismo, integridade temporal e cobertura total não são substituídos.

## 2026-09-21 — Clipes derivados de consulta V2

- `audiovisual_review.py query` passou a materializar `event_video_clip.mkv`
  FFV1 por `select` de índices-fonte e `event_audio_clip.wav` nominal, além do
  player por evento; saída existente não é reutilizada silenciosamente.
- O vídeo derivado registra contagem esperada/obtida, SHA, comando e limite de
  claim. O query v2 do marcador fechou 49/49 frames; o áudio continua separado
  e sem claim de sincronismo na ausência de âncora compartilhada.

## 2026-09-21 — Recibo V5 end-to-end

- `audiovisual_review.py` 2.4.0 adiciona `end-to-end`, que verifica stages V0–V4,
  hashes da ROM/vídeo/WAV, arquivos reais da captura, consulta exata, finding
  candidato, revisão qualificada e igualdade entre gate armazenado e gate
  recomputado.
- A demonstração HSTR produziu `execution_status=passed` e `status=blocked`:
  a execução foi consumida corretamente, mas movimento, áudio, sincronismo,
  integridade temporal e cobertura total continuam sem liberação.
- Foi adicionada regressão positiva/negativa: pacote image-only qualificado
  pode liberar somente o escopo sustentado; reviewer ausente gera bloqueio.
- O V5 também exige `finding_query_binding`: `source_query` deve apontar ao
  `query_report` consumido e os frames do finding devem estar dentro do range
  consultado.
- Revisão formal do escopo audiovisual registrada em
  `out/audiovisual_review/code_review_v24.json` como
  `review_passed_with_risk`, sem aprovação de runtime, áudio ou AAA.
- `audiovisual_review` 2.4.1 tornou o ingest robusto ao MP4 diagnóstico:
  removeu `coded_picture_number` do `ffprobe -show_frames`, que travava a leitura,
  sem retirar PTS nem normalizar a mídia. O binding positivo do marker 16 passou
  com erro medido de 0,000333 ms e liberou apenas a âncora técnica `av_sync`; o
  gate derivado continua bloqueando integridade temporal pelo gap de 33,333 ms e
  não libera audição, movimento, estética ou cobertura.

## 2026-09-21 — Audiovisual review 2.5.0 e piloto runtime marker v2

- V5 exige overhead repetido/comparável com HCAD e medianas por fase; essa
  diferença não é FPS, cadência ou fluidez. `artifact_identity` substitui o
  sentido amplo de `capture_integrity`, e o alias legado é rejeitado.
- `analyze_media_marker.py` converte coordenadas VDP tile para pixels 8x8 e
  transforma falha de PTS em relatório fechado, preservando o master.
- A ROM diagnóstica `marker_event_probe_v2` e a captura BlastEm v2 preservam
  hashes, HANC 32773, HCAD e HSTR. A captura possui dois gaps PTS; o binding
  A/V permanece `needs_review`.
- Adicionados `marker_event_capture_v2_hstr_event_1560.json` e
  `marker_event_capture_v2_finding_special_animation_001.json`: candidato de
  transição visual do especial, com quadros consecutivos, ROI, hashes, estado
  e teste causal encaminhado ao owner de gameplay.
- Regressões: 15 testes pytest audiovisuais, 5 contratos do wrapper e self-check
  das ferramentas de medição passaram; nenhuma promoção AAA ou correção do
  jogo foi feita.
- O gate v2 consumiu uma revisão qualificada hash-bound e liberou apenas o
  escopo visual de sete frames; nenhuma saída de um eixo substituiu outro.

## 2026-09-21 — V5: binding de overhead e janela extraída

- Vinculado o overhead aos hashes de ROM presentes nos casos do relatório e à
  ROM real da captura; overhead de outro build agora bloqueia o V5.
- Corrigido o binding de finding para usar `query_interval` quando a consulta
  contém pré/pós-contexto, mantendo o intervalo-evento distinto.
- Regressões: 15 testes audiovisuais do projeto e 5 contratos do wrapper
  passaram. Nenhuma aprovação global ou promoção AAA foi feita.
- O medidor ganhou `--rom` para executar overhead contra snapshot diagnóstico;
  a tentativa v2 não produziu par/relatório válido, então o V5 mantém o bloqueio
  e não reutiliza o overhead de outro SHA.

## 2026-09-21 — V3 real, overhead comparável e áudio explicitamente ausente

- Corrigido `capture_visual_ko.py` para aceitar `--rom path`; a captura V3
  válida usa ROM/configuração diagnósticas congeladas e preserva o bundle
  histórico sem o reinterpretar como FPS do jogo.
- Medidos dois pares BlastEm com HCAD persistido e mesma ROM: medianas de
  overhead separadas por boot, captura, finalização e total. Diferenças HCAD
  entre sessões continuam sendo telemetria de comparação, não aprovação de
  cadência ou fluidez.
- V5 end-to-end agora executa integralmente e consome freeze, captura, ingest,
  query, finding, review, gate e overhead. O recibo permanece `blocked` nos
  eixos sem suporte: gaps PTS, A/V, movimento, áudio e cobertura.
- Captura sem WAV é aceita como `not_present` no hash-chain e nos artefatos,
  mas nunca libera `audio_approval`; schema atualizado para esse estado.
- Consulta do marcador 2288 materializa quatro frames consecutivos com PTS,
  ROI, clipe FFV1 e `play_event.sh`. Causal compare e finding real são
  `candidate_only`/`not_approved`; HSTR sem binding ao mesmo PTS permanece
  contextual.
- Regressão do wrapper ampliada para 7 testes, incluindo uma revisão positiva
  com playback/audição que libera apenas eixos sustentados; 26 testes do projeto passaram
  com o fixture P10 stale explicitamente ignorado. Nenhuma correção do jogo,
  promoção AAA ou aprovação audiovisual global foi feita.
## 2026-09-22 — V4 HAPE, query audiovisual e gate por eixos

- Adicionado probe HAPE e decoder/self-check para correlacionar apresentação,
  lógica, estado de especial, animação, DMA e pressão de sprites sem confundir
  esses contadores com PTS do vídeo ou FPS do jogo.
- Reforçado o caminho existente de captura: freeze hash-bound, ingest sem CFR,
  query com 38 frames-fonte, player por evento, ROIs, HSTR contextual e finding
  causal candidate-only. O caso real mostra uma transição do especial que uma
  screenshot espaçada perderia.
- Adicionado review V4 honesto com oito imagens realmente inspecionadas;
  `visual_quality` passa somente no escopo local, enquanto playback normal-speed,
  áudio e cobertura permanecem `needs_review`.
- Medidor de overhead passa a declarar `same_rom_sha256` pela uniformidade dos
  casos executados; pares sem HCAD continuam rejeitados e não contam para a
  suficiência mínima.
- Recibo V5 V4 consumiu V0–V4 com execução passada, mas bloqueou claims de
  integridade temporal, A/V, movimento, áudio e cobertura. Não houve correção do
  jogo, promoção AAA ou aprovação audiovisual global.
- O finding V3 passou a consumir também imagens da execução sem vídeo e o
  `causal-compare` HAPE dos dois modos. A repetição do especial no mesmo estado
  autoral orienta a investigação para gameplay/timing/legibilidade; continua
  candidate-only, sem patch ou aprovação global.
- Formalizado o protocolo em `audiovisual_review_manifest.schema.json` e endurecido o intake para
  exigir versão/protocolo, reviewer, método, capabilities, hashes, intervalos
  vistos e evidências por eixo.
- Preflight V4 registrou ferramentas de metadata/query/player e métricas de
  áudio disponíveis, mas percepção direta do agente para vídeo/áudio ausente;
  isso mantém a política de revisão fechada sem fabricar playback ou audição.
