# Plano de avaliação audiovisual rastreável — HAMOOPIG

**Escopo:** infraestrutura de prova, não aprovação de arte, áudio, gameplay ou
AAA. O teto do projeto continua `technical_demo/prototype`.

**Regra de verdade:** um MP4, screenshot, metadado, título de janela, contador
de apresentação ou probe isolado não é aprovação. Cada claim tem um gate
independente e deve apontar para a ROM, mídia, hashes, intervalo realmente
consultado e método de revisão.

**Status atual auditado:** infraestrutura parcial de captura, indexação e
diagnóstico de mídia. O piloto agora possui HDBG/HSTR para correlação causal
de gameplay, mas a associação HSTR↔PTS ainda é estimada pelo relógio do host,
não é timestamp de scanout VDP. O overhead foi medido tecnicamente em dois
pares comparáveis, com boot/captura/finalização separados e HCAD válido; isso
não é FPS, fluidez ou desempenho perceptivo. A avaliação perceptiva completa,
a sincronização por âncora comum e a audição/playback qualificados ainda estão
pendentes. Este plano não declara V0–V5 concluído como avaliação audiovisual do
jogo.

## Referências e estado inicial

- Projeto: `SGDK_projects/HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]`.
- Qualidade de referência: `/home/misael/Imagens/GAME/` — somente baseline de
  comparação; não é fonte de pixels nem prova de runtime.
- Captura existente: `tests/capture_visual_ko.py`; cadência: HCAD e
  `tests/analyze_hcad_cadence.py`; áudio: `tests/capture_sound_test.py`,
  `tools/sgdk_wrapper/analyze_audio_capture.py`; BlastEm: rota existente do
  wrapper Linux/Flatpak.
- Bundle histórico preservado:
  `out/emulator_evidence/visual_ko_20260920T074931694042Z-1506141/`.
- O bundle contém MP4 sem áudio e WAV separado. Seus hashes são registrados no
  relatório V1; nenhum master é reencodado, CFR-normalizado, interpolado ou
  deduplicado.

### Regressão de integridade observada no bundle histórico

`combat_window.mp4` tem 10.822 frames, duração 194,683333 s, `r_frame_rate`
60/1 e `avg_frame_rate=649320/11681` (aprox. 55,59). O último `drop=858` está
no `video.log`. Isso é cadência da captura/encoder, **não FPS do jogo**.

O audit de PTS encontrou saltos de 1,850000 s, 1,883334 s e 10,633334 s;
o maior ocorre entre os frames 7037/7038, em 120,983333 → 131,616667 s.
O WAV tem 195,150000 s; a diferença de duração é 466,667 ms e não existe
marcador audiovisual comum, portanto o erro de sincronização de evento fica
`needs_review`, não `0 ms`.

O histórico continua válido como evidência de que prints espaçados não
detectam a perda temporal. Ele não sustenta FPS, fluidez, qualidade sonora ou
aprovação estética.

## V0–V5

### V0 — congelar identidade e preflight

1. Rodar guard/preflight do workspace e selecionar a rota do host.
2. Copiar `out/rom.bin` para o freeze, registrar SHA-256/tamanho e registrar a
   configuração BlastEm, `capture_visual_ko.py`, HCAD e rota escolhida.
3. Verificar `ffmpeg`, `ffprobe`, `ffplay`, `pactl` e módulos de imagem/áudio.
4. Declarar capacidades: extração de frames/PTS e métricas de sinal são
   suportadas; percepção audiovisual direta do agente e audição crítica não
   são alegadas.

**Saídas:** `freeze_manifest.json`, `preflight_report.json`.

### V1 — ingestão, hashes, timestamps e sincronização

1. Ler o `manifest.json` do bundle e calcular hashes dos masters, ROM e logs.
2. Consultar `ffprobe` frame a frame. PTS ausente, não monotônico, duplicado ou
   buraco acima de 1,5 período nominal é excluído dos claims temporais, mas
   permanece listado no audit; o master não é alterado.
3. Ler `drop`/`dup` do log do encoder e separar `artifact_identity` de
   `media_temporal_integrity` e `game_cadence`.
4. Medir duração WAV/MP4. Sem marcador comum, registrar apenas a diferença de
   duração e `measured_event_sync_error_ms=null`.
5. Preservar HCAD/HDBG/HSTR/VLAB/HPRB como telemetria da ROM, sem confundir
   vídeo, lógica, apresentação, estado de animação, emissão de entidade ou
   upload DMA. HSTR registra estado por apresentação durante o especial; não
   prova sozinho que o estado foi observado no mesmo scanout do frame de vídeo.

**Saídas:** `audiovisual_ingest_report.json`, `frame_index.json`.

### V2 — consulta efetiva da mídia

1. `query` recebe um evento e intervalo temporal, acrescenta pré/pós-contexto
   configurável (0,5 s por padrão), extrai frames sem CFR e produz numeração
   por PTS, hash por frame, segmento (`pre_context`/`event`/`post_context`) e
   ROIs.
2. Gera `query_report.json`, `play_event.sh`, clipe de vídeo lossless derivado
   por `select` de índice-fonte e clipe WAV nominal por evento. Os clipes são
   conveniência de consulta: o relatório de frames/PTS é a autoridade e o WAV
   não é declarado sincronizado sem âncora runtime comum.
3. O relatório registra quantos frames foram solicitados/decodificados; uma
   divergência não é escondida.
4. A revisão deve citar os intervalos realmente vistos e o que ficou fora.
   O gate valida que os intervalos não examinados são válidos e correspondem
   exatamente ao complemento dos intervalos realmente vistos; `null`, texto
   inválido ou complemento inconsistente não qualifica o pacote. Sequência de
   imagens é evidência temporal limitada; não libera claim de movimento sem
   revisor capaz ou humano.

**Saídas:** `events/<event_id>/frame_*.png`, ROIs, `query_report.json`, player.

### V3 — achados causais e contexto

Cada achado exige:

- timestamp inicial/final e frames adjacentes;
- SHA do MP4/WAV/ROM;
- ROI, confiança e método;
- cena/evento/input/frame emulado/tick/apresentação/DMA quando disponíveis;
- hipótese causal, impacto, teste causal e cobertura não examinada.

Quando HSTR/HDBG estiver disponível, o achado também registra a janela de
apresentação, estado/animFrame/evento e o método de associação à mídia. A
associação por relógio do host é diagnóstica e deve permanecer com confiança
limitada até existir um marcador compartilhado com PTS/VDP.

Detecção automática gera `candidate`/`not_approved`. O caso histórico gera
achado de descontinuidade de captura, não defeito de jogo. Hitstop e conteúdo
estático válido não são automaticamente classificados como frame perdido.

**Saída:** `findings.json`.

### V4 — gates e fixtures

Gates independentes:

| Eixo | Claim máximo | Regra de bloqueio |
|---|---|---|
| captura | integridade do pacote | SHA/master/config ausente ou divergente |
| cadência | continuidade técnica da mídia | PTS inválido, buraco ou `drop>0` |
| visual | diagnóstico visual | screenshot/metadata nunca vira aprovação |
| movimento | fluidez/temporal | revisão ausente, cobertura insuficiente ou cadência falha |
| áudio | qualidade/mix/sincronia | sinal sem audição, marcador ou revisão capaz |
| cobertura | escopo examinado | intervalos não vistos continuam `needs_review` |

Fixtures cobrem: glitch de um frame, hitstop válido, buraco de PTS, áudio
desalinhado, SHA errado, vídeo sem revisão, trecho não examinado, intervalo
declarado inválido, complemento de cobertura inconsistente, capabilities
ausentes e veredito sem evidência. Thresholds não são adaptados ao resultado
corrente.

**Saídas:** `audiovisual_gate_report.json`, regressões em `tests/`.

O contrato também é executado pelo wrapper em
`tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode schema`, através de
`test_audiovisual_review_contract.py`. Esse teste é autocontido e prova a
separação dos eixos, o recebimento de revisão qualificada limitada e a rejeição
de revisão ausente ou cobertura inválida.

### V5 — ciclo end-to-end no BlastEm

1. Congelar ROM/configuração.
2. Usar `tests/capture_visual_ko.py` para captura real; a captura pode ser
   executada com e sem `--no-video` para medir overhead e registrar HCAD/título
   apenas como observação, nunca como FPS do jogo.
3. Fechar BlastEm pelo caminho existente, preservar SRAM/logs/master.
4. Rodar V1, V2, V3 e V4 contra o mesmo SHA.
5. Emitir somente o claim sustentado. Para este piloto, o resultado esperado é
   integridade de artefatos liberável quando os hashes batem, cadência histórica
   bloqueada pelos buracos/drop, temporal/sonoro `needs_review` e sem aprovação
   AAA.

## Overhead e sincronização

`tests/measure_capture_overhead.py` compara duas sessões BlastEm com o mesmo
script/input: `--no-video` e vídeo passthrough. O relatório mede duração de
parede, SHA da ROM, título observado e status da sessão; qualquer diferença é
overhead do processo de captura, não FPS lógico. Falhas de prontidão do HUD
ficam registradas como `needs_review`, não entram como medição válida.

A captura agora registra `capture_clock.json` com monotonic clocks de início de
vídeo/áudio e timeline de screenshots. Isso mede o deslocamento de inicialização
dos gravadores; não substitui uma âncora audiovisual comum. Sem essa âncora, o
gate não inventa sincronização.

## Execução inicial do piloto — 2026-09-21 (histórica; superseded pelo freeze HSTR)

O V0 congelou `out/rom.bin` com SHA-256
`3c82c14b3c959098f09b57de7a387147b970eb42fabb1bf8af986c20e46938f9`, 2.490.368
bytes, e congelou a rota `linux_flatpak_blastem` sem blockers. O preflight
encontrou `ffmpeg`, `ffprobe`, `ffplay`, `pactl`, PIL, NumPy e OpenCV; o módulo
`soundfile` não está instalado, mas o WAV é lido por `wave` e pelo analisador
existente. Não há percepção direta de vídeo nem audição crítica disponível ao
agente.

O bundle histórico foi ingerido e consultado de fato. Os eventos
`capture_gap_01` e `capture_gap_03` possuem frames consecutivos numerados por
PTS, ROIs, hashes e players; os pares 1882/1883 e 7037/7038 mostram por que
prints espaçados não bastariam. A revisão registrada em
`out/audiovisual_review/historical_v1/review_manifest_images_only.json` é
explicitamente limitada a imagens: não libera movimento, áudio ou estética.

O overhead antigo de 842,215 ms é apenas uma diferença de parede entre duas
execuções completas e não é um claim de custo de quadros. A versão faseada
`out/audiovisual_review/v5/capture_overhead_phased_repeated.json` separa boot,
captura, finalização e total, mas ficou `needs_review`: houve tentativas sem
HUD e somente um par bem-sucedido; a repetição seguinte teve zero pares
válidos. O resultado correto é insuficiente para estimar overhead estável.

Uma captura audiovisual posterior do BlastEm foi ingerida, indexada e
consultada no intervalo 2,4–5,2 s, gerando 34 candidatos de buraco de PTS,
todos `candidate_only`. A rota especial atual também foi capturada com áudio,
frames e SRAM no SHA `3c82…e46938f9`; o intervalo 10,2–13,2 s foi consultado e
produziu um achado de gameplay candidato, separado dos achados de gravação.

Os relatórios agora separam `artifact_identity`, `media_temporal_integrity`,
`av_sync`, `game_cadence`, visual, movimento, áudio e cobertura. No bundle atual
de combate, HCAD passou com 6.060/6.060 frames e commits, mas a mídia falhou
com `drop=36` e quatro buracos PTS; isso não é contraditório. Uma revisão
qualificada de evento pode liberar visual somente no escopo observado: no
especial, o gate liberou `visual_approval` do evento, mas manteve movimento,
áudio e cobertura bloqueados. Nenhum claim global de qualidade ou AAA foi emitido.

O contrato estrutural do pacote de revisão está em
`tools/sgdk_wrapper/schemas/audiovisual_review_manifest.schema.json` e exige
revisor, método, capacidades, hashes de vídeo/ROM, intervalos realmente vistos,
evidências, cobertura declarada e vereditos por eixo. O gate histórico em
`out/audiovisual_review/gameplay_special_v3_v2/audiovisual_gate_event_review_v2.json`
é mantido como regressão; o gate revalidado no piloto atual está em
`out/audiovisual_review/gameplay_special_hstr_v4_event/audiovisual_gate_event_review_hstr_revalidated.json`.
Ambos são deliberadamente bloqueadores fora do claim visual limitado ao evento.

## Encaminhamentos

O bundle histórico aponta para uma regressão de infraestrutura de gravação
(encoder/host/captura), não autoriza correção do jogo. O teste causal é repetir
o mesmo SHA com timestamps passthrough, áudio/vídeo iniciados com clock
registrado e, idealmente, uma âncora runtime comum. Nenhum antes/depois de jogo
é inventado neste ciclo.

## Atualização do piloto HSTR — SHA d6b7ea5e (2026-09-21)

O V0 foi refeito para o ROM efetivamente capturado no BlastEm: SHA-256
`d6b7ea5e3e43c97b75caff47fa113c841378704b423de50adc2f287732eb9618`,
2.490.368 bytes. O freeze rastreável está em
`out/audiovisual_review/v5/freeze_hstr_v4/freeze_manifest.json`, com a rota
`out/logs/blastem_capture_route_report.json` e os hashes do harness/configuração.

O bundle `out/emulator_evidence/visual_ko_20260921T085100974673Z-2406057/`
foi capturado no BlastEm com vídeo e WAV separado, ingerido sem CFR,
interpolação ou deduplicação, e consultado no intervalo 9,7–13,7 s, com 0,5 s
de pré e pós-contexto. A mídia
falha em `media_temporal_integrity` por gaps de PTS; HCAD passa no estado SRAM
com 2.970 commits de apresentação/lógica e zero ticks inválidos. Isso libera
identidade/cadência do jogo, não continuidade da mídia nem fluidez.

HDBG schema 2 e HSTR schema 1 registram estados do especial por apresentação.
O HSTR contém 128 slots, 116 registros com fireball ativo e estados `100/700`;
o evento de 10,2–13,2 s foi consultado por PNG consecutivo com ROIs, hashes,
pré/pós-contexto e mismatch de decodificação preservado. O achado
`gameplay-special-emission-latency-004` é `candidate`, não aprovado: na
associação host-clock estimada, o HSTR aponta `state=700/animFrame=4` e
fireball ativo perto do source index 620, enquanto a imagem não mostra o
projétil; nos source indices 631 e 652 ele aparece. Apenas esses três frames
foram efetivamente vistos pelo agente.

O gate `out/audiovisual_review/gameplay_special_hstr_v4_context_v9/audiovisual_gate_event_review_hstr_strict_v9.json`
libera apenas `artifact_identity`, `game_cadence` e `visual_approval` no escopo
do evento efetivamente consultado. `media_temporal_integrity`, movimento,
áudio/sincronismo e cobertura global permanecem bloqueados. A revisão declara
0,049998 s observados de 65,125 s; todo o restante permanece explicitamente
não examinado.

O overhead repetido mais recente está em
`out/audiovisual_review/v5/capture_overhead_hstr_repeated_v3.json`: seis sessões
foram preservadas no mesmo SHA, mas somente um par foi completo; uma baseline e
uma captura terminaram sem ROM/telemetria. O relatório fica `needs_review`.
No único par utilizável, a mediana observada foi +26,729 ms na fase de captura
e +580,808 ms na finalização. A diferença de contagem de frames ou o título de
janela não é FPS nem frames perdidos; HCAD não fechou nos dois lados e ainda
falta uma âncora de duração/execução suficientemente controlada.

### Fechamento do contrato de revisão qualificada — 2026-09-21

`audiovisual_review.py` agora rejeita um pacote que apenas declara uma lista de
intervalos. Reviewer, método e a lista de `tools` precisam ser registrados;
cada capacidade (`video_playback`, `audio_audition`) deve ser booleanamente
declarada; cada eixo precisa de `evidence_refs` não vazios; e a
lista `unexamined_intervals` deve usar intervalos parseáveis e coincidir com o
complemento calculado da união dos intervalos `actually_seen`. A saída também
emite `unexamined_union` normalizada para auditoria. O caso real HSTR foi
revalidado em
`out/audiovisual_review/gameplay_special_hstr_v4_context_v9/audiovisual_gate_event_review_hstr_strict_v9.json`;
ele continua liberando somente identidade, HCAD e visual nos três frames
explicitamente vistos.

### V2/V3 — vínculo exato ao frame-fonte — 2026-09-21

O `query` foi endurecido na versão 2.2.0: não usa mais `-ss` como fonte de
identidade ordinal do PNG. Ele constrói um filtro `ffmpeg select` pelos
índices-fonte retornados pelo `ffprobe`, registra o filtro, o intervalo de
índices, a contagem decodificada e `pts_binding=ffprobe_source_index_exact`.
Se a contagem divergir, o vínculo passa a
`ordered_pair_unresolved_after_decoder_mismatch` e o relatório não sustenta
um achado preciso por frame.

Na recaptura lógica do bundle existente, o evento 9,7–13,7 s produziu 241/241
frames com vínculo exato, 181 frames de evento, 30 de pré-contexto e 30 de
pós-contexto, sem CFR, interpolação ou deduplicação. A revisão visual efetiva
viu os source indices 620, 631 e 652. O achado
`gameplay-special-emission-latency-005` registra que o projétil está ausente
no 620 e visível nos 631/652 enquanto o HSTR indica emissão do especial.
Isso é um candidato de feedback/renderização do jogo, não um defeito de captura
aprovado: a associação ainda não é um timestamp de scanout VDP.

O gate v10 correspondente continua `blocked`: identidade, HCAD e visual
limitado aos três frames passam; integridade temporal da mídia, sincronismo,
movimento, áudio e cobertura global permanecem bloqueados.

### Overhead repetido — fechamento técnico — 2026-09-21

O harness de overhead agora separa a prontidão visual do modo `--probe-short`
e usa o HCAD persistido como gate de comparabilidade. O relatório
`out/audiovisual_review/v5/capture_overhead_hstr_repeated_v6.json` contém dois
pares no mesmo SHA `d6b7ea5e…eb9618`, todos com 1.530 frames de lógica,
apresentação e vídeo, zero ticks inválidos e janela de combate persistida.

Medianas pareadas: boot `-35,586 ms`, fase de captura `-0,304 ms`, finalização
`+444,197 ms` e total `+459,090 ms` com vídeo. Os intervalos de combate
variaram `-6` e `+2` frames entre os pares; por isso o resultado mede overhead
de fases e não FPS, fluidez ou perda de frames do jogo. O status é `measured`,
com essa limitação declarada e sem promoção perceptiva.

O contrato de revisão também exige `evidence_root`. O gate resolve cada
`evidence_ref` relativo ao diretório do manifesto, verifica que o arquivo
existe dentro da raiz declarada e rejeita referências órfãs ou fora da raiz.
Assim, uma lista não vazia de nomes não basta para qualificar uma revisão.

### Âncora audiovisual compartilhada — contrato e bloqueio — 2026-09-21

O `audiovisual_review.py` 2.3.0 passou a emitir `synchronization.anchor_contract`.
`capture_clock` continua sendo apenas relógio dos processos do host e é marcado
como rejeitado para sincronismo. Para liberar `av_sync`, um futuro bundle deve
fornecer `runtime_media_anchor` com `marker_id`, frame de apresentação do
runtime, índice-fonte do vídeo, PTS, índice/amostragem de áudio, erro medido,
SHA-256 do vídeo/áudio/ROM e evidências locais. Hash divergente, campo ausente
ou número inválido retorna `needs_review`; nenhuma duração aproximada vira erro
de evento.

No bundle real HSTR, o contrato permanece `needs_review`: vídeo
`e5338071…56eff6fd`, áudio `2b7221a…74ae4a5`, delta de duração 425 ms e nenhum
marcador comum. O gate v11
(`out/audiovisual_review/gameplay_special_hstr_v4_context_v10/audiovisual_gate_event_review_hstr_anchor_contract_v11.json`)
continua liberando somente identidade, HCAD e visual limitado aos três frames
vistos; sincronismo, movimento, áudio e cobertura permanecem bloqueados.
Na primeira cadeia HSTR não foi alterada a ROM nem criada uma build
instrumentada: a consulta confirmou que HSTR/HDBG são SRAM e que
`capture_clock` não representa scanout VDP. A rota diagnóstica posterior está
registrada separadamente abaixo e não substitui a ROM de release.
As rotas tentadas e a ação mínima para uma futura captura instrumentada estão
registradas em `out/audiovisual_review/v5/runtime_media_anchor_feasibility_v1.json`.

### Estado da suíte ampla — 2026-09-21

Os contratos audiovisuais, overhead, HCAD/HDBG/HSTR/HSEM e probes passaram em
20 testes direcionados, além de 2 casos do binder de marcador. A suíte completa do projeto não é verde: a coleta é
bloqueada por `tests/test_p10_evidence_integrity.py`, cuja matriz P10 ainda
aponta para bundles com ROM SHA `8ac1…`, enquanto o freeze atual é
`d6b7…`. A evidência antiga foi preservada e não teve o hash alterado para
fabricar aprovação; isso é uma pendência de recaptura/realinhamento P10 fora do
claim audiovisual deste plano.

### Cadeia V0–V4 reemitida com versão coerente — 2026-09-21

Para não misturar relatórios de versões diferentes, o piloto foi reemitido sem
substituir a evidência anterior: V0 em
`out/audiovisual_review/v6/freeze_hstr_v5/`, V1 em
`out/audiovisual_review/gameplay_special_hstr_v4_ingest_v6/`, V2 em
`out/audiovisual_review/gameplay_special_hstr_v5_context_v11/`, achado V3
`gameplay_finding_special_emission_latency_006.json` e gate V4
`audiovisual_gate_event_review_hstr_v12.json`. Todos registram
`audiovisual_review` 2.3.0/schema 2.2.0, preservam o SHA de ROM
`d6b7ea5e…eb9618` e mantêm o mesmo resultado: revisão qualificada apenas para
o diagnóstico visual limitado; movimento, áudio, sincronismo, integridade
temporal e cobertura total continuam bloqueados.

O gate também emite `claim_scopes`: no V12, `visual_approval` está limitado a
`three_explicitly_seen_special_frames_only`; movimento, áudio e cobertura têm
escopo `none`. Assim, o literal `released` não pode ser interpretado como
aprovação audiovisual global.
### Marcador runtime–vídeo–áudio e captura diagnóstica — 2026-09-21

Foi implementada uma rota diagnóstica isolada, sem alterar a ROM de release:
`build_sgdk_wine_bridge.sh --extra-flags -DHAMOOPIG_CAPTURE_MARKER
--output-dir out/marker_probe_v3` gerou a ROM SHA `3797bb8f…adb2a578`,
enquanto `out/rom.bin` permaneceu em `d6b7ea5e…eb9618`. O V0 correspondente
está em `out/audiovisual_review/marker_probe_v3_freeze/`, com rota/configuração
SHA `543d9c51…b6c7a3`. O harness aceita
`--rom=...` e registra sua origem/hash no bundle.

`HAMOOPIG_captureMarker` escreve um marcador diagnóstico em BG_A, dispara um
pulso PSG e salva HANC com `marker_id` e frame de apresentação na mesma
fronteira pré-VBlank. HANC é contexto runtime, não timestamp de mídia;
`seal_runtime_marker_manifest.py` só cria manifesto derivado após o flush
terminal do BlastEm.

O bundle real é `out/emulator_evidence/visual_ko_20260921T105816016474Z-2929360/`:
vídeo SHA `21a019d4…d179ab`, WAV SHA `cedfb6b9…52001e8`, HANC
`marker_id=16`/`runtime_presentation_frame=2880`. O analisador consultou os
masters e produziu 2 candidatos visuais e 209 candidatos de áudio; isso não é
aprovação. A seleção de teste foi rejeitada por reviewer/evidência ausentes e
erro candidate de 100 ms. O ingest rejeita binding derivado `needs_review`.

V1 mediu 59,65 s de vídeo, 60,10 s de áudio, delta 450 ms e um gap PTS de
33,333 ms. O gate `out/audiovisual_review/marker_probe_v3_gate.json` ficou
`blocked`: identidade e HCAD permanecem limitados aos próprios escopos;
integridade temporal, sincronismo, movimento, áudio, revisão visual
qualificada e cobertura global não foram liberados. Nenhuma promoção AAA foi
feita.
V2 também foi exercitado no marcador candidato: o evento
`marker_candidate_window` gerou 31/31 frames consecutivos pelos índices-fonte
689–719, com `ffmpeg_select_by_source_frame_index`, pré/pós-contexto de 0,2 s
e ROI declarada. A consulta é rastreável, mas não transforma os candidatos em
veredito.

O mesmo evento foi reconsultado como `marker_candidate_window_v2` após o
materializador de clipes: 49/49 frames, `event_video_clip.mkv` FFV1 lossless
com 49/49 frames e `event_audio_clip.wav` separado, ambos com SHA derivado.
O player aponta para os clipes, mas registra `not_asserted_without_shared_runtime_anchor`;
isso não libera sincronismo, áudio ou movimento.

### Pacote V14 — revisão consecutiva e correção de PTS declarado — 2026-09-21

O manifesto V11 foi preservado após a auditoria detectar que seus intervalos
declarados não coincidiam exatamente com os PTS do `query_report`. O pacote
V14 não altera masters: usa os mesmos hashes e registra a revisão efetiva de
13 ROIs gameplay consecutivas, source indices 620–632, em `10,3375–10,5375 s`.
O player por evento e a consulta V2 continuam no diretório V11, com
`ffmpeg_select_by_source_frame_index`, e o manifesto V14 referencia cada PNG
consultado dentro do `evidence_root`.

O finding V3 `gameplay-special-emission-latency-007` observa ausência do
projétil em 620/621 e primeira visibilidade em 622, enquanto HSTR registra o
estado especial. É um candidato visual rastreável, não uma aprovação temporal,
sonora, estética ou causal. A revisão foi image-only: `video_playback=false`,
`audio_audition=false`; portanto o gate V14 ficou `blocked`, com cobertura
0,3071%, movimento/áudio/sincronismo/integridade temporal/cobertura global
bloqueados e escopo visual limitado ao trecho consecutivo examinado. O finding
é encaminhado a `gameplay_runtime_owner` para executar o teste causal antes de
qualquer correção; a infraestrutura não inventa um patch a partir de imagens.

### V5 — recibo end-to-end hash-bound — 2026-09-21

`audiovisual_review.py` 2.4.1 com `end-to-end` agora consome V0, manifesto real de captura
BlastEm, V1, V2, V3, manifesto de revisão e V4. O recibo
`out/audiovisual_review/v5_end_to_end_hstr_v14.json` confirmou a mesma ROM
`d6b7…eb9618`, vídeo `e533…56eff6fd` e WAV `2b72…74ae4a5` em todos os elos,
241/241 frames na consulta, finding candidato e revisão `qualified=true`.

O `execution_status` é `passed`, mas o `status` de claims é `blocked`: somente
identidade, HCAD e o escopo visual explicitamente visto são liberados. O recibo
rejeita revisão ausente/inválida, cadeia de SHA divergente, consulta não exata
finding sem `source_query`/frames dentro da consulta, ou gate armazenado
diferente do gate recomputado. Ausência de
`cadence_probe` no manifesto da captura é reportada como `needs_review` e não
é promovida por HCAD ou por duração do vídeo.

### Âncora técnica compartilhada e limite do claim — 2026-09-21

O binder positivo foi executado no bundle diagnóstico
`out/emulator_evidence/visual_ko_20260921T105816016474Z-2929360/`, selecionando
explicitamente `video_event_index=0` (source frame 701, PTS 11,683333 s) e
`audio_event_index=46` (amostra 560800 a 48 kHz). A âncora referencia
`marker_id=16`, frame runtime 2880, ROM `3797bb8f…adb2a578`, vídeo
`21a019d4…d179ab` e WAV `cedfb6b9…52001e8`. Erro medido: `0,000333 ms`;
reviewer, método e evidência estão em `marker_sync_review_codex.json` no bundle.

O V1 derivado está em `out/audiovisual_review/marker_probe_v3_anchor_pass_ingest/`
e reporta `synchronization.status=passed`, sem confundir isso com audição. A
auditoria preservou um gap PTS de `33,333 ms` (source 1128→1129), portanto
`media_temporal_integrity=failed`. O gate
`out/audiovisual_review/marker_probe_v3_anchor_gate.json` prova a
não-substituição: identidade, âncora `av_sync` e HCAD são liberados nos próprios
escopos; integridade temporal, visual, movimento, áudio perceptivo e cobertura
permanecem bloqueados. O marker é um sinal diagnóstico injetado, não aprovação
de música ou efeito sonoro do jogo.

Durante a ingestão, `coded_picture_number` foi removido da consulta ffprobe
porque travava neste MP4, enquanto PTS, duração e tipo de frame eram lidos
corretamente. O índice mantém esse campo explicitamente nulo e não o usa para
afirmar FPS do jogo.

### V5 com overhead comparável e piloto audiovisual v2 — 2026-09-21

`audiovisual_review.py` 2.5.0 separa `artifact_identity` de integridade
temporal, sincronismo, cadência e qualidade. O alias `capture_integrity` é
rejeitado no recibo V5; identidade significa somente hashes e preservação dos
masters. V5 exige dois pares baseline/captura no mesmo SHA, HCAD persistido e
medianas separadas de boot, captura, finalização e total. O recibo real
`out/audiovisual_review/v5_end_to_end_hstr_v14.json` foi reemitido com
`execution_status=passed`, `status=blocked`.

`analyze_media_marker.py` converte coordenadas VDP em células 8x8 e falha
fechado quando ffprobe não lê PTS, preservando o master. A ROM diagnóstica
isolada `out/marker_event_probe_v2/rom.bin` tem SHA
`cf34ff61337200c050d278549e7ce7edcfa786a2df5db1fcea81fdf39e7b880f`; a ROM de
release não foi substituída.

O bundle BlastEm v2 em
`out/emulator_evidence/visual_ko_20260921T123619091866Z-3325366/` preserva
vídeo `21bb5045…d2e8a`, WAV `b689426f…8a8983f443`, HANC marker 32773 e frame
runtime 1560. HCAD mediu 3060/3060, zero-tick 0 e 1910 frames de luta, mas a
mídia falhou por dois gaps PTS. O binding A/V não foi promovido: o candidato
visual 1561/26,016667 s e o áudio 26,493333 s produziram erro de 476,666 ms.

V2 consultou 28 frames consecutivos, source 1547–1574, com pré/pós de 0,2 s,
ROI gameplay e clipe FFV1/WAV derivado sem CFR, interpolação ou deduplicação.
O HSTR em `out/audiovisual_review/marker_event_capture_v2_hstr_event_1560.json`
mostra `fball_active=0→1` no frame 1560, estado 700 e posição 232→242. O
finding `marker_event_capture_v2_finding_special_animation_001.json` é
`candidate_only`: a transição vermelho/branco do especial será repetida sem
captura e comparada com a animação autoral. Não é causa confirmada, aprovação
global ou autorização para corrigir o jogo.

O pacote de revisão `out/audiovisual_review/marker_event_capture_v2_review_images.json`
foi validado pelo gate `out/audiovisual_review/marker_event_capture_v2_gate.json`.
Ele libera somente `visual_approval` no escopo
`seven_consecutive_special_transition_frames_only`; movimento, áudio,
sincronismo, integridade temporal e cobertura completa permanecem bloqueados.

O piloto permanece infraestrutura parcial de captura, indexação, consulta e
diagnóstico; percepção normal-speed, audição, sincronismo A/V e cobertura global
ainda estão pendentes. Nenhum claim AAA foi feito.

### Fechamento de contrato V5 — 2026-09-21

Uma auditoria de segunda ordem corrigiu duas brechas de consumo. O relatório de
overhead agora precisa carregar `rom_sha256` nos casos observados e o V5 compara
esses hashes com o `rom.bin` real da captura, além de exigir
`same_rom_sha256=true`. Assim, o overhead histórico da ROM release
`d6b7…eb9618` é rejeitado quando apontado para a captura diagnóstica
`cf34…7b880f`; o recibo
`out/audiovisual_review/marker_event_capture_v2_v5_after_overhead_binding.json`
fica bloqueado com `capture_overhead_rom_hash_mismatch_or_missing`. O master e o
relatório histórico não são apagados nem reclassificados.

O binding de finding usa `query_interval` quando presente, pois é o intervalo
realmente extraído com pré/pós-contexto; o intervalo-evento estreito continua
registrado separadamente. O recheck da cadeia histórica compatível em
`out/audiovisual_review/v5_end_to_end_hstr_v14_contract_v2.json` passou em
`execution_status`, mas conserva `status=blocked`, visual somente no escopo
observado e motion/audio/cobertura bloqueados. Regressões: 15 testes do projeto
e 5 contratos do wrapper passaram. Isso não constitui aprovação audiovisual,
correção do jogo ou promoção AAA.

O medidor existente recebeu `--rom` para repetir pares com uma ROM diagnóstica
sem substituir `out/rom.bin`. A tentativa de executar quatro sessões com
`out/marker_event_probe_v2/rom.bin` não produziu relatório nem par aceito e foi
interrompida após não haver processo BlastEm observável; isso é uma rota de
medição pendente, não overhead válido. Até existir esse relatório compatível,
o V5 diagnóstico permanece bloqueado e não reutiliza o overhead `d6b7…`.
