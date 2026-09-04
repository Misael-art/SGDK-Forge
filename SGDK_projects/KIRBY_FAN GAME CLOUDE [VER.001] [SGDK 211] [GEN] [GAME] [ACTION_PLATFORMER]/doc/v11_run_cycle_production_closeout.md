# V11 — marco causal do run cycle

Data: 2026-09-04
Branch: `codex/kirby-full-visual-production-v11`

## Estado honesto

```text
status=full_visual_runtime_candidate
claim_ceiling=run_cycle_visual_runtime_candidate
visual_pass=false
human_gate_ready=false
final_acceptance=false
ready_for_aaa=false
animation_candidate=false
res_promotion=false
```

Este documento registra somente o marco do `run_cycle`. A produção visual completa
de idle, inhale e jump/float ainda não foi concluída. V04–v10 continuam históricos;
nenhum pixel deles foi usado.

## Autoridade e linhagem

- Fonte única de identidade: `data/source_art/r1/r1-01/concept.png`.
- SHA-256 da autoridade R1: `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`.
- Rota produtora: `forge-art native-edit`, ações editoriais explícitas em grid 32×32.
- A fonte R1 não foi alterada. `data/` e `res/` foram protegidos durante a execução
  do editor; a integração v11 em `res/sprites/v11_review/` é um recurso de revisão,
  não promoção final.

## Arte produzida

Quatro key poses de uma câmera lateral única foram autoradas separadamente:

| pose | candidato | SHA-256 |
|---|---|---|
| contact | `run_contact_r2/candidate.png` | `1754b9d685cf2329d09e33f504fb89983f5784ace114b2e620c26bd028c83a4a` |
| down | `run_down/candidate.png` | `4d4a7f87e6ba7ce61716afd7a1e73c659623631c1714fe94ead5c244bcc74b7c` |
| passing | `run_passing_r2/candidate.png` | `c0956699a838157386e41279c35b83f84186fe7f4131741c15c8984754f6167e` |
| flight/push | `run_flight_push_r2/candidate.png` | `5fb235d361347bc8850c1f864d45f43a028f80a8f2b1038865569fd5351d1ce4` |

Strip final do marco: `run_cycle_v11_r3_candidate.png`, 128×32, SHA-256
`d09d2627fd4538b0f828023acd2e45bbc19cbcf868877b80de143daed3fb1dea`.
GIF: `kirby_run_cycle_v11_r3.gif`, SHA-256
`49bcfab264d89506e4edd9d5d7497969117f50ece19b5a558bafd5852ed74e62`.

O contato r2 tem SHA novo e as quatro poses são distintas no grid. A inspeção em
1× mostra leitura lateral simplificada, mas ainda não equivale à riqueza de volume
do R1; por isso `visual_pass=false` permanece obrigatório.

## Validação e métricas

Comandos executados a partir da raiz do projeto:

```bash
export PYTHONPATH="/mnt/sdcard/Projects/Sgdk Forge/tools/sgdk_wrapper"
python3 -m forge_art validate res/sprites/v11_review/run_cycle_v11_candidate.png --index0-role transparent0
# rc=0, status=technical_candidate, blockers=[]

python3 tools/image-tools/analyze_sprite_strip_integrity.py \
  --image out/v11_visual_production/run_cycle_r3/run_cycle_v11_r3_candidate.png \
  --frame-width 32 --frame-height 32 \
  --output out/v11_visual_production/run_cycle_r3/reports/run_cycle_strip_integrity.json \
  --asset-kind character --asset-id kirby_run_cycle_v11_r3 --state-profile run
# rc=0, status=passed, findings=[]
```

Medições do strip: quatro frames, largura de bbox 29–30 px, altura 17–22 px,
`edge_problem_frames=0`, `matte_problem_frames=0`, `island_problem_frames=0` e
`baked_fx_frames=0`. Isso é integridade técnica, não aprovação anatômica.

```bash
python3 tools/sgdk_wrapper/ci/test_native_edit.py
# rc=0, native-edit physical suite: 9/9
python3 -m forge_art self-check
# rc=0, 136/136 fixtures
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_golden_validate.ps1
# rc=0, 8/8; nenhum projeto dourado encontrado, somente guard generalista
```

## Runtime real

Integração v11: `res/resources.res` declara `spr_native_run_cycle_v11` e
`src/scenes/scene_stage.c` seleciona esse recurso somente enquanto o estado real de
Kirby é `KIRBY_RUN`; os demais estados continuam no recurso anterior. Não foi criado
hook que força o estado para mascarar a captura.

Build canônico:

```bash
env SGDK_TARGET_BLOCKER=visual_gate_blocked \
SGDK_CHANGE_CATEGORY=art \
SGDK_CHANGE_SUMMARY=Integracao_da_run_cycle_v11_native_edit_no_gameplay_real \
bash "/mnt/sdcard/Projects/Sgdk Forge/tools/sgdk_wrapper/build_sgdk_wine_bridge.sh" --project-root .
# rc=0
```

ROM: `out/rom.bin`, 262144 bytes, SHA-256
`68f59e9c072a1671b723e8677c40c046f552684b93e5c6daf719a4439f972a10`.

Captura BlastEm da cena jogável 4, com input real `Left` mantido até o screenshot:

```bash
bash tools/sgdk_wrapper/capture_blastem_evidence_linux.sh \
  --project-root . --rom out/rom.bin \
  --output-base out/evidence/v11_run_cycle_interactive_left \
  --warmup-seconds 18 --target-scene 4 --audio-driver disk
# rc=0, bundle sealed
```

Sessão: `blastem-linux-20260904T094658Z-3181717`.
Artefatos: screenshot, SRAM e VDP dump foram selados e vinculados à ROM.
ROM no bundle: `68f59e9c072a1671b723e8677c40c046f552684b93e5c6daf719a4439f972a10`.
Screenshot: SHA `44399ffdf18d649c147a670b7fdc7b3a67edbcd67dc1f20a50b98b411f6b102d`.
SRAM: SHA `eb878c9ec4ee06b331765eed3e5eec37c0902d86395bcc2d23e47f409e6017a8`.
VDP dump: SHA `aca765cd25edd525f09b9338f519db56735e416091c43f225bd5ad34c90559f9`.

Snapshot VLAB: cena 4, frame 1020, 59,6 fps, CPU máximo 72, jitter máximo 13,
16 sprites por scanline, 26 sprites ativos e 0 frames acima do budget. O snapshot
não prova performance sustentada. A captura mostra o ator no estágio real; não prova
por si só a qualidade visual, continuidade de quatro estados ou gameplay completo.

## Falhas e descartes

- A captura normal da cena 4 em 4 s foi selada, mas o pan deixou o ator fora da tela;
  não é evidência visual do run.
- A cena 5/playtest não selou: `rc=1`, blockers
  `vlab_block_missing`, `artifact_missing:vdp_dump` e
  `artifact_missing:runtime_metrics`; não foi promovida.
- A captura interativa com `Right` também selou, mas atravessou um gap e perdeu o
  ator no screenshot; descartada como prova do frame.
- A tentativa `run_cycle_r2` foi descartada por contato de borda do passing; a
  correção `run_cycle_r3` passou integridade.
- O diagnóstico visual R1 lado a lado revela simplificação/achatamento; não há claim
  de fidelidade final nem gate humano.

## Próximo gate causal

Produzir uma ação por vez para idle, inhale e jump/float pelo mesmo caminho
`native-edit`, com key poses nativas independentes, lineart hard-edge e evidência
1× antes de integrá-las ao stage. Somente após todas as quatro ações passarem os
validadores técnicos e a revisão cega diagnóstica poderá ser solicitada revisão
humana; este marco não abre o gate.

## Continuidade v11 — idle e inhale (2026-09-04)

O estado de verdade permanece `visual_pass=false`, `human_gate_ready=false`,
`animation_candidate=false` e `res_promotion=false`. O registro de escopo foi
corrigido para não afirmar gate humano aberto.

Idle r3 foi produzido a partir de dois documentos explícitos de ações nativas no
grid 32×32, sem resize/crop/quantização como autoria final:

- `out/v11_native_edit/idle_neutral_r3/candidate.png` — SHA-256
  `dab1718ce0e4918f46fe906b5095dfca464c943379f6873828d4ab8b3592f4f8`;
- `out/v11_native_edit/idle_rise_r3/candidate.png` — SHA-256
  `697e56a154f8e3fbb19a464af1d31555c9cc87eb5e273abd2d914ca1ec61dc35`;
- strip `out/v11_visual_production/idle_r3/idle_v11_r3_candidate.png` — SHA-256
  `d29a0c1fc4b3cf649d3fa163490039b15a23c36d319e3fbb0c43b5daa7b34abc`;
- GIF `out/v11_visual_production/idle_r3/idle_v11_r3_candidate.gif` — SHA-256
  `cb108467a9cd44787074e27c070fc9b40e4f225fc033a1fd35d2ae17ee58e3f9`.

Comandos técnicos do idle r3:

```bash
python3 -m forge_art native-edit --project-root . \
  --actions data/staging/v11_native_edit/idle_neutral_v11_actions.json \
  --out out/v11_native_edit/idle_neutral_r3
python3 -m forge_art native-edit --project-root . \
  --actions data/staging/v11_native_edit/idle_rise_v11_actions.json \
  --out out/v11_native_edit/idle_rise_r3
python3 tools/image-tools/analyze_sprite_strip_integrity.py \
  --image out/v11_visual_production/idle_r3/idle_v11_r3_candidate.png \
  --frame-width 32 --frame-height 32 \
  --output out/v11_visual_production/idle_r3/idle_strip_integrity.json \
  --asset-kind character --asset-id kirby_idle_v11 --state-profile idle
```

Resultados: ambos `native-edit` rc=0; strip analyzer rc=0/status=passed,
`edge_problem_frames=0`, `matte_problem_frames=0`, `island_problem_frames=0`,
`baked_fx_frames=0`, bbox 24×17–19 px; contrato de pixels rc=0/status=
`technical_candidate`. A revisão cega 1× ainda encontrou simplificação visual
excessiva; portanto o pacote não entra em `res/` nem no runtime.

Inhale antecipação foi executado nativamente em
`out/v11_native_edit/inhale_anticipation_r3/candidate.png`, com rc=0 e SHA-bound
ao R1. A hipótese foi descartada como `needs_rework` na inspeção 1× por volume
quadrado e material ainda esquemático. Nenhuma declaração de aprovação visual foi
emitida e as ações não foram integradas ao stage.
