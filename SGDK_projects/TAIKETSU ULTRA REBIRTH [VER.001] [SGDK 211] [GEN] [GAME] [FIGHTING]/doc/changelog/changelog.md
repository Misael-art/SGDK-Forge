# Changelog Canonico - TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

## 2026-09-09T17:45:00Z - VLAB runtime ranges e reconciliacao da evidencia atual

- Recompilada a ROM após instrumentação observacional de ranges VLAB; SHA-256 vigente e preservado antes/depois: `869a0eedde787d632aa1997edfebe36c556f386bc40c57fba3e14cdc8a660e18`.
- Captura exclusivamente Linux/Flatpak/BlastEm selada na sessão `blastem-linux-20260909T173215Z-3070928`, cena 3 observada, janela `59.4 fps`, com screenshot, SRAM, manifest, selo, métricas e `audio.raw`. O `visual_vdp_dump.bin` é payload VLAB real de 240 bytes, não dump integral de VRAM.
- O runtime registrou quatro faixas de tiles sem overflow (`[16,516)`, `[516,616)`, `[1376,1391)`, `[1391,1406)`); a prova é parcial e não sustenta `validado_budget` final, performance sustentada ou AAA.
- O áudio atual foi analisado objetivamente a partir de `audio.raw`: 26,624 s, sinal não silencioso e sem clipping. Mix, loop, SFX, arbitragem e escuta humana continuam pendentes.
- Corrigido `finalize_emulator_evidence.ps1` para propagar `session_id` ao `evidence_closeout_report`. Os relatórios ativos foram reconciliados com a ROM/sessão atuais; a regressão atual capturou seis cenas, com quatro baselines aprovados e divergência de screenshot em `branding_sequence` e `front_end_main_menu`, sem sobrescrever baselines.
- O erro de backend continua apenas `host_executor_route_mismatch_resolved`; nenhuma dependência Win32/substituto foi instalada ou usada. `ready_for_aaa=false` permanece e a produção continua nos blockers reais de arte nativa, animação, VDP completo, áudio e performance.

## 2026-09-09T13:26:00-03:00 - reconciliacao final de identidade e guard Linux

- `assert_agent_environment.ps1` terminou `agent_environment_status=ready`, `graph_status=fresh` no host Linux BigLinux/Arch KDE/Wayland, com `DISPLAY=:0` e `WAYLAND_DISPLAY=wayland-0`.
- `evidence_closeout_report.json`, `emulator_session.json`, `code_review_report.json`, `validation_report.json`, memória e changelog foram reconciliados para ROM `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3` e sessão `blastem-linux-20260909T124600Z-1554938`; claim reconciliation confirma `same_rom=true` e `same_evidence_session=true`.
- `audit_doc_sync` passou e `freshness_audit` está sem stale/missing. O erro histórico permanece somente como `host_executor_route_mismatch_resolved`; nenhum backend Win32/substituto foi instalado ou usado na captura Linux.
- `ready_for_aaa=false` permanece. Arte final/aprovação, animação, budget runtime, áudio escutável, performance sustentada e regressão completa continuam blockers.

## 2026-09-09T12:40:00-03:00 - Budget VDP e continuidade pós-correção de rota

- Self-checks de `audit_tile_residency`, `vdp_scanline_simulator` e `dma_queue_planner` passaram; o parecer D1 foi consolidado como `cabe com recuo` em `out/logs/d1_runtime_vdp_budget_assessment_20260909.json`.
- Medição offline: pico residente 946/1740 tiles; pior scanline 4 sprites, 120 pixels e 7 links; DMA sem violações. Isso não substitui residência runtime, densidade final de lutadores ou performance sustentada.
- Atualizada a memória para manter explícito que o route-fix Linux não promove AAA. Permanecem abertos arte nativa/aprovação, animação, áudio audível e regressão de cenas sem bootstrap.

## 2026-09-09T12:46:00-03:00 - Audio QA baseline sem falso claim

- Criado `out/logs/audio_qa_baseline_20260909.json` separando validação estática aprovada de prova runtime escutada.
- A sessão Linux continua provando somente sidecar `audio.raw` não vazio, hash-bound à ROM/sessão; formato, loop audível, mix, arbitragem de SFX e aprovação humana permanecem pendentes.
- Nenhum asset ou código de áudio foi alterado; `ready_for_aaa=false` permanece.

## 2026-09-09T12:15:33-03:00 - Reconciliacao de baselines da regressao de cenas

- Atualizados, a partir de evidência selada e `--reuse-evidence`, os baselines
  de `first_playable_slice` e `combat_cinder_circuit`; ambos agora passam por
  SHA na ROM vigente.
- A matriz atual permanece honesta: 2 cenas passaram e 4 seguem abertas por
  bootstrap/captura ou falta de bundle; nenhum artefato VDP foi inventado.
- Revalidados `validate_resources` (`errors=0`, `warnings=13`), closeout,
  freshness e claims; `ready_for_aaa=false` permanece.

## 2026-09-09T12:05:48-03:00 - Revisao visual de staging e reconciliacao da barra viva

- Persistida revisão observável do candidato Kairo 88x136 em staging; o
  candidato mantém `technical_candidate` e fica bloqueado por reautoria nativa
  de olhos/mãos, animação e aprovação humana.
- Variante v02 de ImageGen foi explicitamente rejeitada e preservada somente
  como evidência negativa: checkerboard rasterizado, SHA
  `30d819ab3442771102b3b406df86e5b170384b140639c08f925e1e363af16fae`; não
  entrou no workset, `/res`, build ou ROM.
- Reconciliado `live_scene_bar_report.json` com a sessão BlastEm Linux atual,
  `visual_vdp_dump.bin` real, `audio.raw` e a regressão host-aware. O laudo
  continua `needs_review` e não promove cena, áudio, performance ou arte final.
- Validação final da rodada: `errors=0`, `warnings=14`; closeout e freshness
  passaram; ROM preservada em
  `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3`.

## 2026-09-09T11:39:33-03:00 - Higiene e reconciliacao do closeout

- removido o artefato duplicado criado dentro de
  `SGDK_projects/TAIKETSU.../SGDK_projects/.../out/logs/`; nenhum arquivo de
  código, asset, `.res` ou ROM foi removido;
- `validate_project_hygiene.ps1` passou com zero blockers;
- validação regenerada com `errors=0`, `warnings=13`; os blockers estruturais
  de raiz órfã e nome não canônico foram resolvidos;
- closeout seguro reexecutado sem build/captura/regressão: `warn/blocked`,
  preservando apenas visual, animação e regressão como blockers;
- o guard semântico continua apontando o diretório irmão com tag `[SGDK 211]`
  duplicada; seu conteúdo foi inspecionado e permanece preservado sem deleção
  ou renomeação automática;
- claims reconciliados em `ready_for_aaa=false`, com performance e prontidão
  técnica ainda não provadas; freshness permaneceu `ok`.

## 2026-09-09T11:05:35-03:00 - Direct pixel-art staging hypothesis and VDP envelope

- Adicionada uma hipótese nova de pose pixel-art direta para Kairo, com fonte persistida em staging, triagem aprovada e workset atualizado para a manifest SHA `f91dddf3478ba392668994c5949879bff7e8aa23b5368121973997e38a9e3d4d`.
- Route-shootout 88x136 executou Lanczos3, Catrom e Nearest; o handoff registra apenas guia primário/challenger/controle, sem vencedor automático e sem promoção.
- Conversão técnica v01 passou ResComp: 15 cores, index 0 transparente, canvas 88x136, conteúdo SHA `d8ef6c8bf90b7a0ac53055eeac6e8cb960d862110be84cc11db834b564654f51`; permanece `technical_candidate` fora de `/res`.
- Envelope VDP H40 offline: 100 tiles únicos/3.200 bytes, 27 links, pico de 9 sprites e 280 pixels por scanline, sem overflow. Escopo não inclui runtime, DMA, residency ou animação.
- A leitura nearest 8x melhorou sobre a probe anterior, mas olhos/rosto ainda não fecham visual pass. Uma edição corretiva foi descartada por checkerboard e não foi copiada para o projeto.
- Nenhum código, asset ativo, build ou ROM foi alterado; `ready_for_aaa=false` permanece. Próximo passo: reautoria nativa/revisão humana, depois material topology, animação e cena viva.

## 2026-09-09T10:15:45-03:00 - Fighting semantic guard and art routing

- Refeito o diagnostico de arte: os 20 assets ativos em `/res` estao tecnicamente conformes; o bloqueio vigente e visual/produtivo, nao uma dependencia grafica ausente ou conversao faltante.
- Validado o workset ativo `d1_scale_reset_20260905`; fontes Kairo, underlays e probes continuam fora de promocao para `/res`, build e ROM.
- Adicionado `doc/art/kairo_vant/fighting_sprite_semantic_contract.json`, com referencias Jack/Ryo declaradas como `scale_reference` nao-promoviveis e formula do GDD reconciliada. O guard calcula minimo de 128px visiveis.
- O guard permanece bloqueado somente por `duplicate_project_identity_detected` na raiz vazia `[SGDK 211] [SGDK 211]`, preservada conforme inventario e sem delecao autorizada. Self-check do guard: 9/9.
- Nenhum codigo, asset ativo, ROM ou evidencia de emulador foi alterado; `ready_for_aaa=false` permanece. Proxima acao: reautoria nativa C e depois gates de pixel, animacao, budget, audio e runtime.

## 2026-09-09T09:56:00-03:00 - Preload DMA separation and Linux evidence reseal

- Build v007 gerado com a ROM `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3`; o hash foi preservado antes/depois da captura.
- Captura exclusivamente Linux/Flatpak BlastEm selada na sessão `blastem-linux-20260909T124600Z-1554938`, alvo e cena 3 observados, com screenshot, SRAM, manifest, selo, `audio.raw` e VLAB real de 222 bytes.
- O probe agora separa gameplay e preload: gameplay 32 bytes/1 entrada/7200 bytes no frame 91 após 90 frames de warmup; preload 1000 bytes/4 entradas/7200 bytes no frame 1 em 90 observações. Completude de loading/streaming e performance sustentada continuam abertas.
- `audio.raw` mede 12.591.104 bytes, 84,2975% não-zero, SHA `17a08c1c7b0f65fd77b34bdc0301a15f453e9ea2689ee7cadc7c7580dfdc5471`; isso prova apenas sidecar não vazio, não áudio final.
- Reconciliados `runtime_metrics`, `performance_capture`, `audio_runtime_capture`, `code_review`, `evidence_closeout`, `emulator_session`, `dma_queue_contract`, memória e snapshot VDP; `ready_for_aaa=false` permanece.

## 2026-09-09T09:02:00-03:00 - DMA probe correction and Linux evidence reseal

- Corrigida a colisão de offsets no probe: MDRT/VLAB agora separa pico DMA (`[18]/[19]/[20]`) de alocação de sprites (`[30]/[31]`), com VLAB schema 2 e payload real de 210 bytes.
- Build SGDK 2.11 concluído com a ROM `5b482354c4f96f3a058cf675c77c0d5edabdae7f60719887460bc7bda1e46536`; hash preservado antes/depois da captura.
- Captura exclusivamente Linux/Flatpak BlastEm selada na sessão `blastem-linux-20260909T115558Z-1366905`, alvo e cena 3 observados, screenshot/SRAM/manifest/selo/VLAB real e `audio.raw` publicados no bundle canônico.
- Medição real de gameplay após 90 frames de warmup: DMA máximo 32 bytes, 1 entrada, capacidade 7200 bytes, frame 91. Preload/streaming DMA, residency viva e performance sustentada continuam não medidos.
- O sidecar `audio.raw` hash-bound foi atualizado para 12.419.072 bytes, 84,1476% não-zero, SHA `f452f10330a69a1f54d06aa37385a4ffce7de51dd6f72c4edf8175048017b507`; não promove áudio final.
- Reconciliados `runtime_metrics`, `performance_capture`, `audio_runtime_capture`, `code_review`, `evidence_closeout` e `emulator_session`; `ready_for_aaa=false` e os blockers visuais/áudio/performance/regressão permanecem.

## 2026-09-09T07:57:00-03:00 - Host route curation and current evidence reseal

- Reexecutado `assert_agent_environment.ps1`: host real Linux 6.18.45-1-MANJARO, KDE/Wayland, `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`; ambiente pronto e graph fresh. Nenhuma dependência WinForms, Mono, Xvfb ou Wine foi instalada para captura.
- Recompilada a ROM pelo `linux_wine_bridge` apenas para refrescar o log operacional; build terminou com exit code 0 e o SHA permaneceu `fff6cb2c7608af143a27dd5d0d89a6cf2712193edea1d91058410c5ad2e30027` antes/depois da captura.
- Recapturada exclusivamente por `capture_blastem_evidence_linux.sh`: sessão `blastem-linux-20260909T102939Z-719188`, alvo 3 observado como cena 3, selo com screenshot/SRAM/métricas/VLAB real de 200 bytes/`audio.raw`; `evidence_closeout_report` e `emulator_session` estão `ok`, sem artefato inventado.
- O sidecar bruto desta sessão mede 12.148.736 bytes, 85,0769% não-zero, SHA `9cd2f06d44b8698149d66e0203e8205ff5110ad5fb7624e984ad939194a4d1b5`; isso prova somente saída não vazia, não escuta humana, loop, mix, SFX ou áudio final.
- `freshness_audit` terminou `ok` com zero stale/missing; `validation_report` tem `errors=0`; closeout continua `warn/blocked` apenas por higiene herdada, gate/direção/animação visual e três comparações de regressão não aprovadas. O orçamento/arte final/áudio/performance sustentada seguem não promovidos.
- Fixtures permanentes do seletor foram ampliados e passaram: Linux não seleciona `System.Windows.Forms`/PowerShell, Windows não seleciona Flatpak, DISPLAY presente não vira backend ausente, DISPLAY ausente é blocker X11 distinto e report/comando pertencem ao mesmo host. `test_scene_closeout_gate.ps1` também passou.
- Consolidado o parecer VDP D1: `cabe com recuo` tecnicamente (946/1740 tiles, 8 sprites/160 pixels no pior scanline do envelope, 16 links, sem overflow), com DMA/VBlank, tiles carregados por código e desempenho sustentado ainda abertos. O parecer perceptivo permanece não avaliado enquanto os probes não forem substituídos por arte nativa aprovada.

## 2026-09-09T07:32:00-03:00 - Current ROM evidence and audio candidate reconciliation

- Rebuilt the project after integrating the original Cinder Circuit PSG BGM candidate: 8-bar loop, 120 BPM, 3 PSG tone channels, VGM/XGM2 conversion, `psg_score.py --self-check` and `vgm_to_xgm2.py --self-check` passed. `validate_audio.ps1` reports 8 resources, 6 samples, 2 music assets, 0 issues and 38.87 KB estimated audio footprint.
- The candidate is technically compiled and selected by the combat scene, but it is not final audio: human listen, real-driver arbitration, hit/guard/special masking and heavy-scene runtime capture remain open. Contract ceiling is `vertical_slice_candidate`.
- ROM hash before and after the Linux capture is `fff6cb2c7608af143a27dd5d0d89a6cf2712193edea1d91058410c5ad2e30027` (262144 bytes). BlastEm session `blastem-linux-20260909T102939Z-719188` observed target scene 3 through `linux_flatpak_x11_bridge`; the seal contains screenshot, SRAM, runtime metrics, hash-bound `audio.raw` and the real 200-byte VLAB `visual_vdp_dump.bin`.
- Reconciled `runtime_metrics.json`, `evidence_closeout_report.json`, `emulator_session.json`, claim identity and the current build. The old PowerShell diagnosis remains classified as `host_executor_route_mismatch_resolved`; `blastem_capture_host_dependency_missing` and `display_backend_missing` are not current findings.
- Refreshed the static tile residency report for the current build. It remains an offline source measurement and does not promote live VDP/DMA, performance, final art or AAA.
- Audited the same-session BlastEm `audio.raw` sidecar: 12,148,736 bytes, 85.0769% non-zero, SHA-256 `9cd2f06d44b8698149d66e0203e8205ff5110ad5fb7624e984ad939194a4d1b5`. This is evidence of non-empty emulator audio output only; the raw stream has no declared sample format/rate/channels, so contextual listen, loop seam, arbitration and SFX masking remain unproven.
- Current status is still partial: visual probes, final art, scene baselines/protocols, sustained performance and final audio remain blockers. `ready_for_aaa=false`.
- Host-aware scene regression then captured current-ROM baselines for `front_end_main_menu` and `first_playable_slice`; both now pass artifact-SHA comparison. Remaining scene blockers are the branding target mismatch and unsupported CS-C/CS-E protocols.
- Curadoria do pipeline: `seal_fresh_evidence_bundle.py` e o schema agora aceitam `audio_raw` opcional hash-bound, e a rota Linux publica esse arquivo no bundle canônico. `validate_resources.ps1` passou a calcular frescor do tilemap contra fontes/contratos, não contra relatórios derivados; isso removeu o falso ciclo `scene_tilemap_conversion_report_stale`. Self-checks do sealer, fixtures de rota/bundle e `test_scene_closeout_gate.ps1` passaram.

## 2026-09-09T06:17:30-03:00 - Host-aware scene regression reconciliation

- Reavaliada a matriz de seis cenas exclusivamente pela rota Linux selecionada por host; nenhum backend Win32, `System.Windows.Forms`, Wine, Xvfb ou instalação substituta foi usado.
- `front_end_main_menu` e `first_playable_slice` agora têm evidência selada com `scene_match=true`, mas sem baseline; `combat_cinder_circuit` compara por SHA e passa. Branding permanece mismatch (alvo 0, observado 2); CS-C e CS-E permanecem sem protocolo/evidência.
- Atualizados `scene_regression_report.json`, `scene_regression_matrix.json`, `code_review_report.json`, `validation_report.json`, `doc_sync_report.json`, `claim_reconciliation_report.json` e `freshness_audit_report.json`. Estado final: validation `errors=0`, freshness `ok`, claims `passed`, ready_for_aaa `false`.
- Refrescado `scene_tilemap_conversion_report.json` para o BG_B vigente. O snapshot de 615 tiles/19.680 bytes continua source-bound; não é prova de residency/DMA ao vivo.
- O blocker residual `scene_closeout_gate_stale` é temporal/governança; arte final, animação, áudio real, performance e baselines continuam trabalho obrigatório.

## 2026-09-08T15:52:00-03:00 - VRAM residency snapshot and blocker reconciliation

- Added `doc/vram_residency_report.json` for D1 scene 3, bound to the current ROM and source hashes: 615 unique resident tiles / 19,680 bytes across BG_B, BG_A and the deduplicated fighter probe set.
- Kept the scope honest: this is a ResComp/source-hash snapshot, not a full runtime VDP dump or sustained residency/DMA proof.
- Updated `validate_resources.ps1` and `scene_closeout_gate.ps1` so valid explicit VRAM evidence closes the static code-loaded-tile blocker while preserving the raw static scan in `res_graph_report.json`.
- Re-ran measurement self-checks and the D1 H40 envelope: no scanline overflow, peak 8 sprites/160 pixels; workspace-wide measurement audit still reports inherited version/source drift in unrelated projects.
- Refreshed BG_B tilemap conversion/per-tile reports and validation: `errors=0`; remaining blockers are visual rework/direction, animation, scene regression and unvalidated live audio/performance.

## 2026-09-08T14:45:00-03:00 - Linux capture route reconciliation

- Reexecutado o guard de ambiente no Linux BigLinux/Arch KDE/Wayland; a causa permanece `host_executor_route_mismatch_resolved`, sem System.Windows.Forms, Mono, Wine ou Xvfb para captura.
- `scene_closeout_gate.ps1` passou a auditar o manifesto em `out/evidence/blastem_current`, mantendo o caminho legado apenas como fallback de leitura. A rota Linux agora registra separadamente sandbox interno e cópia publicada da evidência.
- Corrigido o parser da rota para ler `scene_id` de `runtime_metrics.vlab` e recapturado o alvo 3. Sessão BlastEm: `blastem-linux-20260908T175405Z-2417733`; cena observada: 3; ROM: `27deb2e6ed47948c1eb55b1e093a0d26b72bdd2257dc6cd0b03f0e89a2cc79cc`.
- Hash da ROM preservado antes/depois. Bundle selado contém screenshot, SRAM, GIF, métricas e `visual_vdp_dump.bin` VLAB real de 200 bytes (SHA `3749a24533fd607ed7bde0e79400a209eb7edcdbdf24f56552943a936bf14eda`); ele é telemetria parcial e não prova VRAM completa, gameplay sustentado ou AAA.
- `validate_audio.ps1` passou 7 declarações, 6 samples, 1 music asset, 0 issues e 0.9% estimado da ROM. A validação de reprodução/arbiter em cena pesada continua aberta.

## 2026-09-08T15:18:00-03:00 - GDD closure and BG_B tilemap audit

- Expanded the GDD with the missing production contracts: player kit, systemic rules, phase progression/map, threats and risks, pacing, diegetic onboarding, climax, visual quality criteria, technical ambition and sound direction.
- Audited the existing `res/fighting/stage/room_0_bgb.png` through `analyze_tilemap_dedup_flags.py`: 1120 tiles, 500 flip-aware unique tiles, 55.3571% deduplication, 16,000 estimated VRAM bytes and zero per-tile palette conflicts.
- Promoted only the generated JSON reports to `out/logs/`; no image or staging candidate was promoted. The report scope is BG_B only and does not close BG_A, runtime residency/DMA, final art or AAA.

## 2026-09-06T12:20:00-03:00 - golden slice visual reset and audio teardown correction

- Continued production after resolving the capture backend mismatch; Linux evidence remains partial and `ready_for_aaa=false`.
- Persisted the original Cinder Circuit visual source in `rascunho/golden_slice_visual_reset_20260906/` with SHA-256 `281778896b3e7d6098686ac4bccf954d0a812d67ed34d9db56dfa8a60600c914`; it is visual-source-only and not a final resource.
- Emitted semantic parsing/derived structure with four stage regions and a shared 320x224 composition contract: BG_B atmosphere, BG_A reactor/arena, foreground composition and WINDOW HUD fallback.
- Ran the translation control: basic `0.5864`, elite underlay `0.4629`, delta `-0.1235`; the elite direct conversion was rejected with `NO_ELITE_DELTA` and `WHOLE_IMAGE_CONVERSION_RISK`.
- Generated preliminary tilemap/flip/palette reports in staging only; no staging candidate was promoted into `res/`. A captura Linux posterior produziu um `visual_vdp_dump.bin` VLAB real, mas ele não é relatório de conversão/tile residency nem substitui a reautoria final.
- Fixed `AUDIO_stopAll()` so scene teardown clears pending PSG cue frames before the next scene takes ownership. Real-driver audio capture, arbitration proof and heavy-scene performance remain open.

## 2026-09-06T11:24:00-03:00 - Linux BlastEm capture route and evidence reconciliation

- Reclassified the previous PowerShell/Win32 failure as `host_executor_route_mismatch`; no dependency substitute was installed and no game code/assets were changed.
- Re-ran the agent guard on Linux BigLinux/Arch KDE/Wayland with `DISPLAY=:0` and recorded the host capability report.
- Executed the canonical Linux Flatpak route with BlastEm commit `c1f3f4435e9d009fa001322e26e73e785fe443fcedfae1f3187836685c602221`.
- ROM: `build_d1_runtime_contract_20260906` (sha256 `761bdd0f105f6a24e9deb21399bc3f8ad6f00ed7438d6ba5ee7b421a3688020f`, 262144 bytes).
- Sealed session `blastem-linux-20260906T111553Z-520147` against ROM SHA-256 `761bdd0f105f6a24e9deb21399bc3f8ad6f00ed7438d6ba5ee7b421a3688020f`; screenshot semantic gate, SRAM and freshness passed.
- No `visual_vdp_dump.bin` was produced, so none was declared. Claim remains partial: visual state observed, scene telemetry, sustained gameplay/performance, audio and VDP budget remain open.
- Added explicit `select_blastem_capture_route.py`, integrated route consumption into `scene_closeout_gate.ps1`, added Windows-only early failure to `run_runtime_capture.ps1`, and added permanent Linux/Windows/DISPLAY/host fixtures.
- Updated emulator session, evidence closeout and code review reports without promoting AAA or `ready_for_aaa`.

## 2026-09-06T01:02:00-03:00 - D1 contract and technical runtime pass

- Aligned `doc/13-spec-cenas.md` with the canonical scene compiler and materialized four compiled D1 scene entries.
- Added planning contracts for `stage_intro_cinder_circuit` and `dialogue_cinematic_d1`; production scene lint now reports zero structural errors.
- Expanded the D1 technical combat probe with move frame data, jump/landing, round clock, best-of-three flow, guard/whiff meter rules, delayed special refill, and static input repeat.
- Switched the combat diagnostic scene to its declared BG_A/BG_B stage plates and preserved XGM2 music across fight cues.
- Rebuilt through the SGDK 2.11 Linux/Wine bridge: ROM size 262144 bytes, SHA-256 `761bdd0f105f6a24e9deb21399bc3f8ad6f00ed7438d6ba5ee7b421a3688020f`.
- BlastEm capture was attempted but blocked before launch by missing `System.Windows.Forms.dll` and unavailable display backend; no new emulator evidence was promoted. Visual assets remain technical probes.
- Added validated `SBIS` SRAM scene bootstrap consumption for deterministic `MENU`/`DEMO` entry; normal boot remains unchanged when the marker is absent.
- Made the scene compiler portable on Linux by falling back from `powershell.exe` to `pwsh` and storing relative source paths; production compile now reports `lint=ok`.

## 2026-09-05T14:59:29.4860100Z - bootstrap

- projeto criado a partir da estrutura canonica
- historico de ROM, hashes e evidencia do modelo removido
- status inicial: documentado; nao buildado; nao testado em emulador
- proximo gate: classificar contexto e metodologia

## 2026-09-05 - fase_minus_one_e_d0_documental

- rota Linux provada por `build.sh` -> Wine bridge com ROM de prova de 262144 bytes; hash registrado no handoff da sessao
- `validate_measurement_tools.py`: 17/18; `validate_native_sprite_production.py` sem self-check mantem o teto abaixo de ready_for_aaa
- corrigido bootstrap seguro de `reset_new_project_state.ps1` para campos opcionais ausentes sob StrictMode
- contexto `aaa_game`, manifesto de genero fighting, referencia HAMOOPIG copiada para `rascunho/engine_reference/` e creditos registrados
- GDD/TDD/spec inicial e roster de seis lutadores preparados; nenhuma arte final, ROM ou evidencia BlastEm promovida
## 2026-09-05T13:01:06.4556300-03:00 - D1 runtime probe build

- Task: D1 runtime probe build
- Asset snapshots:
  - img_fighting_room_0_bgb -> v001 (/res/fighting/stage/room_0_bgb.png)
  - img_fighting_room_0_bga -> v001 (/res/fighting/stage/room_0_bga.png)
  - spr_kairo_vant_probe -> v001 (/res/fighting/fighters/kairo_vant_probe.png)
  - img_starfield_v2 -> v001 (/res/branding/starfield_320x224.png)
  - img_forge_bg_b -> v001 (/res/branding/forge_bg_b_320x224.png)
  - img_forge_bg_a_props -> v001 (/res/branding/forge_bg_a_props_320x224.png)
  - spr_forge_ember -> v001 (/res/branding/spr_forge_ember_16x16_strip.png)
  - spr_forge_shard -> v001 (/res/branding/spr_forge_shard_16x16_strip.png)
  - spr_forge_hammer -> v001 (/res/branding/spr_forge_hammer_48x48_strip.png)
  - img_logo_engine_v2 -> v001 (/res/branding/logo_engine_224x64.png)
  - img_logo_author_v2 -> v001 (/res/branding/logo_author_192x32.png)
  - img_logo_project_v2 -> v001 (/res/branding/logo_project_224x48.png)
  - img_presents_text_v2 -> v001 (/res/branding/presents_text_96x16.png)
  - img_presents_bar_v2 -> v001 (/res/branding/presents_bar_8x8.png)
- ROM: build_v001 (sha256 d14df2cd28108b080995844b357f829be1503c51e0e3b786462054d89f59f6e6, 262144 bytes)
- Validation: errors=8, warnings=18
- Blockers: technique_documentation_sync_missing, technique_status_mismatch, technique_tag_unknown, gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, scene_regression_incomplete, res_graph_missing_for_visual_delivery, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Wine bridge build succeeded; D1 fighting scene uses declared Kairo proxy; visual approval and BlastEm evidence pending.

## 2026-09-05T16:29:55Z - fase_minus_one_activation_closeout

- Sessao E2E ativada em `create_new_project` / perspectiva `director` para o projeto fighting autorizado.
- Fase -1: rota Linux `tools/sgdk_wrapper/build.sh` executada com sucesso via Wine bridge SGDK 2.11.
- ROM de prova: 262144 bytes; SHA-256 `bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0`.
- Medicao: 17/18 self-checks; `validate_native_sprite_production.py` continua sem self-check, portanto `ready_for_aaa=false`.
- Validacoes documentais de contexto, metodologia e higiene passaram; o validador fighting aprovou as regras, mas sua auto-validacao do relatorio encontrou `OrderedDictionary` e isso permanece explicitamente registrado.
- Sem evidencia de emulador, sem aprovacao visual/audio e sem promocao de cobertura de hardware; proximo gate e Q1 documental/chain antes de D1 runtime.

## 2026-09-05T16:45:00Z - q1_foundation_closeout

- Q1 foundation roteado para game design, narrativa e governança; taskset em modo read-only.
- Parecer independente validado pelo `quality_review_router`: `revise_before_growth`.
- Prioridades: unificar ordem CS-C/CS-D do D1, tornar o especial/refill mensurável e fechar fontes locais da especialização fighting.
- Bloqueios mantidos: sem pacote BlastEm do ROM vigente, medição 17/18 e divergência de época entre relatórios antigos e o build atual.
- Claims preservados: `quality_claim=unproven`, `ready_for_aaa=false`, teto `vertical_slice`.

## 2026-09-05T16:52:00Z - q1_revalidation_closeout

- Após a revisão documental, a sequência D1 foi fixada como CS-C stage-only -> revelação -> CS-D -> CS-E -> combate; CS-A retorna ao combate após refill para 100.
- A tabela numérica D1 do especial foi adicionada ao GDD e referenciada na especificação de cenas.
- Segunda passada independente: game design mantém apenas o risco de fonte local; narrativa passou; governança bloqueia por BlastEm incompleto e medição 17/18.
- `quality_review_router validate-report`: passed; decisão `revise_before_growth`; `quality_claim=unproven`; `ready_for_aaa=false`.

## 2026-09-05T22:40:00Z - kairo_c_scale_assisted_candidate_v02

- A guia assistida v02 foi adicionada ao workset ativo para corrigir a falha de escala observada na primeira candidata C; a redução direta v02 foi rejeitada como 118px visíveis.
- Probe fitted gerado mecanicamente a partir da matte v02: canvas 88x136, bbox 87x128, NEAREST, sem alteração em `data/` ou `res/`.
- Conversão técnica passou: PNG indexado 4bpp, 15 cores visíveis, index0 transparente; semantic gate do registro fitted passou com `promotable=false` e gates visual/humano/runtime bloqueados.
- Budget offline: 117 tiles únicos com flip dedup, 3744 bytes, 29 links; pior quadro candidato + Ryo + quatro FX: 9 sprites e 216 pixels/scanline, sem overflow H40. DMA, tiles de stage/HUD e prova em ROM permanecem pendentes.
- Evidências: `rascunho/scale_correction_20260905/c_scale_candidate_budget_report.json`; `doc/art/kairo_vant/combat_idle_3quarter_v02_fitted_native_sprite_production_record.json`; `doc/art/kairo_vant/scale_correction_report.json`.
- Claim preservado: candidato técnico medido; sem promoção para `res/`, sem animação e sem build/BlastEm da epoch atual.
- Revisão visual: 1x confirma leitura de combate, contato, cyan e âmbar; rosto/olhar, fronteiras de material e autoria nativa ficaram `needs_review`. Correção solicitada no laudo visual; baseline não atualizado.

## 2026-09-05T23:10:00Z - kairo_visual_generation_routes_closed

- Duas tentativas de guia high-res foram persistidas em `rascunho/scale_correction_20260905/generation_failures/` para auditoria, sem entrada no workset produtivo.
- v03 falhou por glow/gradiente e fundo opaco; v04 falhou por checkerboard assado em pixels RGB. Ambas foram marcadas `reference_only` e não serão matteadas, quantizadas, integradas ou usadas como fonte de geração.
- Rota ImageGen fechada após duas falhas equivalentes de contaminação. Próximo passo causal permanece reautoria nativa direta no grid C, mantendo visual/humano/runtime bloqueados.
- Relatório: `rascunho/scale_correction_20260905/generation_failures/generation_route_failure_log_v01.json`.
- `forge_art translate` foi executado como encaminhamento canônico e retornou exit 3 por design; o registro foi ajustado para a autoria direta C 88x136, sem fabricar pixels ou abrir integração.
- Auditoria do host confirmou ausência de backend nativo capaz: GIMP 3.2.4 expirou no preflight headless e ImageMagick permanece mecânico. Registro: `rascunho/scale_correction_20260905/native_authoring_capability_audit_v01.json`.
## 2026-09-05T13:50:21.4503920-03:00 - D1 fighting runtime probe and BlastEm evidence

- Task: D1 fighting runtime probe and BlastEm evidence
- Asset snapshots:
  - spr_c1_probe -> v001 (/res/fighting/fighters/c1_probe.png)
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=1, warnings=17
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, scene_regression_incomplete, res_graph_missing_for_visual_delivery, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: ROM bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0; manual BlastEm fallback observed scene 3 with screenshot, SRAM and VLAB dump; visual gate and final fighter art remain blocked.
## 2026-09-05T13:56:22.4423181-03:00 - D1 evidence closeout and validation refresh

- Task: D1 evidence closeout and validation refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=1, warnings=17
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, scene_regression_incomplete, res_graph_missing_for_visual_delivery, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: ok
- Notes: Evidence identity sealed against ROM bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0; screenshot semantic gate passed; manual BlastEm fallback remains warn and visual/AAA gates remain blocked.

## 2026-09-05T14:00:25.3163409-03:00 - D1 scene closeout report refresh

- Task: D1 scene closeout report refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=1, warnings=15
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing
- Emulator evidence: ok
- Notes: Scene contract compiler, res graph audit, screenshot semantic gate, freshness audit and learning capture executed; closeout status warn because visual/audio/regression/bridge gates remain incomplete.

## 2026-09-05T14:01:55.3238854-03:00 - D1 final validation and P1 stop

- Task: D1 final validation and P1 stop
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=1, warnings=16
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale
- Emulator evidence: ok
- Notes: Final validation preserves the D1 technical slice and BlastEm evidence identity; asset provenance passes. P1 remains active because the visual gate, audio validation, scene regression, explicit loaded-tile budget and canonical capture path are still incomplete; ready_for_aaa remains false.

## 2026-09-05T14:02:37.8962852-03:00 - D1 claim reconciliation and P1 handoff

- Task: D1 claim reconciliation and P1 handoff
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=1, warnings=16
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale
- Emulator evidence: ok
- Notes: Reconciled emulator evidence claims with validation: testado_em_emulador=true for the hash-bound BlastEm session, while probe/performance/budget remain partial and ready_for_aaa remains false.

## 2026-09-05T14:17:32.4966253-03:00 - P1 visual source and agent context repair

- Task: P1 visual source and agent context repair
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=1, warnings=14
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing
- Emulator evidence: ok
- Notes: Registered Kairo premium source and locked lineage contract; visual lineage validator passed; fixed physical project .agent via recoverable snapshot plus canonical symlink after cleanup tool lacked robocopy; closeout regenerated as warn. Jack source authority, human visual approval, audio, regression and explicit tile budget remain open.

## 2026-09-05T14:22:58.8318620-03:00 - P1 visual delivery gate and context repair

- Task: P1 visual delivery gate and context repair
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=1, warnings=16
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, visual_direction_failed, animation_gate_failed, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing
- Emulator evidence: ok
- Notes: Kairo premium source and visual lineage are now declared and pass lineage/manifest audits; the current visual delivery gate remains blocked pending human asset approval, Jack source authority, native visual review, animation evidence, live-scene-bar evidence, and explicit code-loaded tile budget measurement. Repaired project .agent to canonical symlink after the official cleanup apply was unavailable on Linux; preserved the physical snapshot under out/agent_context_cleanup/20260905_141437/manual_snapshot/agent. D1 BlastEm evidence remains partial and ROM identity unchanged.

## 2026-09-05T14:25:31.9934089-03:00 - P1 build evidence and visual delivery gate synchronization

- Task: P1 build evidence and visual delivery gate synchronization
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=1, warnings=16
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, visual_direction_failed, animation_gate_failed, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing
- Emulator evidence: ok
- Notes: Rebuilt through tools/sgdk_wrapper/build.sh and Linux/Wine SGDK 2.11 bridge with exit_code 0; ROM identity remains bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0. Added build_output.log for freshness traceability. Visual delivery gate remains blocked by explicit creative and measurement blockers; no AAA promotion.

## 2026-09-05T14:28:11.2486153-03:00 - P1 closeout synchronization

- Task: P1 closeout synchronization
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=1, warnings=16
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, visual_direction_failed, animation_gate_failed, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing
- Emulator evidence: ok
- Notes: P1 closeout: build wrapper succeeded with ROM hash bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0; BlastEm gate and screenshot semantic gate pass; scene contract and resource graph pass; freshness required artifacts present. Delivery remains technical_artifact_only and ready_for_aaa=false. Open blockers are human visual approval, final Jack source authority, native visual review, animation evidence, live-scene-bar evidence, audio validation, scene regression capture, and explicit measurement of code-loaded tile residency/VDP budget.

## 2026-09-05T14:45:36.8384176-03:00 - P1 live scene bar report

- Task: P1 live scene bar report
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=2, warnings=18
- Blockers: orphan_project_root_entry, noncanonical_project_entry_name, gdd_substantial_insufficient, visual_gate_blocked, visual_direction_failed, animation_gate_failed, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, runtime_capture_partial
- Emulator evidence: ok
- Notes: P1 formal stop emitted: out/logs/live_scene_bar_report.json status=needs_review for fighting_d1_runtime. Twelve shared-floor checks are recorded with explicit failures for native visual translation, material depth, palette roles, stage tile audit, motion proof, animation density, VDP budget, comparison, and CRT proof. Build/BlastEm evidence remains tied to ROM bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0; no elite/AAA promotion.

## 2026-09-05T15:37:23.0860323-03:00 - D1 Kairo native shape-block diagnostic

- Task: D1 Kairo native shape-block diagnostic
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=2, warnings=18
- Blockers: orphan_project_root_entry, noncanonical_project_entry_name, gdd_substantial_insufficient, visual_gate_blocked, visual_direction_failed, animation_gate_failed, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, runtime_capture_partial
- Emulator evidence: ok
- Notes: Created a 32x40 mechanical technical candidate from the front-pose conversion route, removed only the border-connected matte, and persisted distinct silhouette, semantic-region, contour, material-region and visual-evidence artifacts under rascunho/kairo_native_shape_probe_v01. validate_native_sprite_production.py now passes with zero errors; gates remain native_visual/human/SGDK/emulator blocked, material_topology in_progress, promotion false. Candidate remains a geometry prescreen and is not in res/.

## 2026-09-05T16:41:44.1259899-03:00 - D1 P1 Kairo native grid candidate v06

- Task: D1 P1 Kairo native grid candidate v06
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0, 262144 bytes)
- Validation: errors=2, warnings=18
- Blockers: orphan_project_root_entry, noncanonical_project_entry_name, gdd_substantial_insufficient, visual_gate_blocked, visual_direction_failed, animation_gate_failed, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, runtime_capture_partial
- Emulator evidence: ok
- Notes: ImageGen compact source v03/v04 audited with genuine alpha; route shootouts executed with manual guide selection. Authored 32x40 XPM logical pixel matrix registered in visual workset and premium source manifest, converted to indexed PNG candidate v06, pixel contract passed, native record passed, provenance and workset passed. Candidate remains technical_candidate with native_visual and human gates blocked; no res promotion or ROM rebuild. P1 human visual approval required.

## 2026-09-05T16:50:31.9594496-03:00 - D1 sprite budget reserve and ROM rebuild

- Task: D1 sprite budget reserve and ROM rebuild
- Asset snapshots: nenhum hash novo
- ROM: build_v003 (sha256 97ce57eaf1707613b150c15af2556004c50f5cff69a5eb77aebc2222a9b23ea4, 262144 bytes)
- Validation: errors=2, warnings=18
- Blockers: orphan_project_root_entry, noncanonical_project_entry_name, gdd_substantial_insufficient, visual_gate_blocked, visual_direction_failed, animation_gate_failed, audio_validation_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, runtime_capture_partial
- Emulator evidence: ok
- Notes: Measured Kairo v06 native candidate at 19 unique tiles / 20 raw tiles. D1 H40 worst-frame envelope (2 fighters + 12 FX) measured max 8 sprites and 160 pixels per scanline with 16 total links. Current SPR_initEx(32) was insufficient for the 40-tile two-fighter upper bound; changed src/core/app.c to SPR_initEx(64). Rebuilt ROM through linux_wine_bridge; new ROM sha256 97ce57eaf1707613b150c15af2556004c50f5cff69a5eb77aebc2222a9b23ea4. P1 human visual approval remains pending; no visual asset promoted to res.

## 2026-09-05 - D1 scale reset and Kairo 3/4 combat-idle candidate

- Asset snapshots: Kairo 32x40 routes reclassified as negative evidence; new visual producer source SHA-256 `171846af73bdd131e85197aa4abf767a4ebb8720a3f029f154e8e29fa5d08b78`.
- Measurement: direct Jack/Ryo benchmark closed the invalid 24px ruler; A/B/C shootout measured 102/115/128px visible Kairo heights, with C=88x136 selected by the GDD minimum.
- Route: 3/4 source triage passed; `im_lanczos3` underlay SHA-256 `f9ba87d4e1eda89b094a83cb6bee0b00d1d48a428f168ae83db7be6d2c12948b` selected for native reauthoring, with Mitchell challenger and nearest control. No automatic visual winner.
- Evidence: provenance audit passed 20/20; workset validation passed; scale and pose reports persisted under `doc/art/kairo_vant/`.
- Status: no animation, `res/` promotion, current-epoch build or BlastEm capture. Native pixel authoring, pixel/fidelity/material/budget/human gates remain open. Claim ceiling is mechanical geometry/source translation only.
## 2026-09-08T14:52:31.3596498-03:00 - linux_capture_route_reconciliation

- Task: linux_capture_route_reconciliation
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 27deb2e6ed47948c1eb55b1e093a0d26b72bdd2257dc6cd0b03f0e89a2cc79cc, 262144 bytes)
- Validation: errors=1, warnings=17
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, visual_direction_failed, animation_gate_failed, changelog_missing, scene_regression_incomplete, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing
- Emulator evidence: ok
- Notes: Host route mismatch resolved; Linux BlastEm evidence sealed for scene 3; ROM hash preserved; ready_for_aaa remains false.
## 2026-09-09T06:44:13.0027402-03:00 - current_rom_audio_candidate

- Task: current_rom_audio_candidate
- Asset snapshots: nenhum hash novo
- ROM: build_v005 (sha256 fff6cb2c7608af143a27dd5d0d89a6cf2712193edea1d91058410c5ad2e30027, 262144 bytes)
- Validation: errors=0, warnings=19
- Blockers: orphan_project_root_entry, noncanonical_project_entry_name, visual_gate_blocked, visual_direction_failed, animation_gate_failed, changelog_missing, scene_regression_incomplete, scene_tilemap_conversion_report_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: ok
- Notes: ROM current built after original PSG candidate integration; Linux BlastEm session sealed; visual, sustained performance and final audio remain unproven.

## 2026-09-09T08:36:10-03:00 - closeout reconciliation and Kairo source rejection

- Task: Reconcile Linux host route, evidence closeout, freshness and current visual-source work.
- Asset snapshots: no `res/` or runtime asset promotion; rejected ImageGen challenger copied to `rascunho/scale_correction_20260909/` with SHA-256 `4a471b24e8caed917b14a71438361c1fcdada7aec47c60a0465757d8e2beef08`.
- ROM: build_v005, SHA-256 `fff6cb2c7608af143a27dd5d0d89a6cf2712193edea1d91058410c5ad2e30027`, unchanged before/after evidence.
- Validation: errors=0, warnings=15; freshness `ok` with `stale_count=0` and `missing_required_count=0`; doc sync and claim reconciliation passed.
- Evidence: sealed Linux BlastEm session `blastem-linux-20260909T102939Z-719188`, target scene 3 observed as scene 3; raw audio sidecar is non-empty but format/listen/mix remain unproven; VLAB dump remains partial telemetry, not full VRAM.
- Blockers: `orphan_project_root_entry`, `noncanonical_project_entry_name`, `visual_gate_blocked`, `visual_direction_failed`, `animation_gate_failed`, `scene_regression_incomplete`, plus closeout baseline gaps for unobserved scenes.
- Notes: the new generated challenger was rejected for luminous background/halo contamination; the 88x136 assisted candidate v07 was rejected as visually sparse. Both remain non-final and outside `res/`. `ready_for_aaa=false`; production continues through native reauthoring, animation, runtime DMA/performance and scene regression evidence.

## 2026-09-09T16:20:00Z - host-aware scene regression deterministic

- Task: remove the real scene regression blocker after the Linux capture-route correction.
- Changed: selector/runner now carry per-scene warmup; scene manifest uses SRAM bootstrap for the implemented branding, CS-C and CS-E states; visual baseline comparison is screenshot-only while sealed SRAM/VLAB remain evidence artifacts.
- Evidence: `scene_regression_report.json` passed 6/6 scenes on ROM `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3`.
- Scope: this closes only the regression capture gate. Native visual approval, animation evidence, sustained worst-frame/audio proof and code-loaded tile residency remain blockers; `ready_for_aaa=false`.

## 2026-09-09T17:05:00Z - audio sidecar format and signal integrity

- Task: reduce the audio evidence gap without claiming audible quality.
- Evidence: same-session `blastem.log` declares 48 kHz stereo `float32`; derived WAV analysis passed 32.789 s, non-silent signal, no clipping, peak -22.85 dBFS and RMS -29.17 dBFS.
- Scope: objective signal integrity only. Human listen, motif/loop verification, mix/arbitration and final audio remain open; `ready_for_aaa=false`.

<!-- active_rom_sha256: 869a0eedde787d632aa1997edfebe36c556f386bc40c57fba3e14cdc8a660e18 -->
