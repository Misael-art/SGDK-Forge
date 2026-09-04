# V11 — marco causal do run cycle

Data: 2026-09-04
Branch: `codex/kirby-full-visual-production-v11`

## Estado honesto

```text
status=technical_temporal_probe
claim_ceiling=technical_temporal_probe
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

O ramo de inhale avançou com duas key poses adicionais autoradas no grid: `inhale_open`
(`out/v11_native_edit/inhale_open_r2/candidate.png`, SHA-256
`50f211d9979a1bc1bea74bf3328deb07d689cd11f7859c59725c88538f62f31f`) e
`inhale_expand` (`out/v11_native_edit/inhale_expand/candidate.png`, SHA-256
`b34ebe020be9ed9b5c50110f36777170a23b78b9fadcd85ed89fdf605fa32f8f`). O strip parcial
de três frames `out/v11_visual_production/inhale_r2/inhale_v11_partial_3f.png` tem
SHA-256 `75381be040d413dd764395ea17eefe7ac4e028185676f8efdbc98a5464d0874e` e o GIF
correspondente tem SHA-256 `f6be4b1bc3a04993b4b2f0c8d78b55c6a0837aeccc1274c9dc66f85cb34d3897`.
O analyzer passou com bbox de largura 24–26 px, altura 17–19 px e zero problemas
de borda, matte, ilhas ou FX assado; o contrato de pixels também passou. Ainda falta
o release e a revisão visual de conjunto, portanto o ramo continua parcial e fora
do runtime.

O quarto estado `inhale_release` foi então autorado e executado com rc=0. O strip
completo de quatro frames `out/v11_visual_production/inhale_r3/inhale_v11_candidate.png`
tem SHA-256 `af55ac0c18b78b51b30aa629abd19b40c8fd53886e9e8a797f3bd415ebc31804`;
o GIF tem SHA-256 `a3f3ddc6a0967c8420180ccb8fbc0f78a10da7c2c95a190b281f2107f1886ab5` e
a composição 1× 320×224 tem SHA-256
`e3d8991ab8852feded06d8e8f3198fa7b0b957826622f6ea81992843be98197f`. Strip analyzer
rc=0/status=passed, bbox 24–26×17–19 px, sem problemas de borda, matte, ilhas ou
FX assado; contrato de pixels rc=0/status=`technical_candidate`. A revisão 8× mostra
continuidade de abertura e fechamento da boca, mas a forma geral ainda é um probe
esquemático; não há aprovação visual nem integração no runtime.

O ramo jump/float iniciou com `jump_crouch` (SHA-256
`f56b4306868cbfc7af31cb0f03c4043363abaf3bea99b2bb308b5d2b027750a8`) e
`jump_launch` (SHA-256
`d75e7da0c3b127292c567661133c68e4b4fc1b9edb02a855d59bc0cc31ee54d9`). O par foi
selado como strip parcial `out/v11_visual_production/jump_r1/jump_v11_partial.png`
(SHA-256 `5891dbb81110fb99dcb0eedbeb391d80f3e366d6f8a7f3b474fa8161774ef49e`),
GIF `a259a51a2d19bb72654b62a0b540671be6b555ebdf21333d4ec5f7853e4a1f17` e
composição 320×224 `15f9e569305d01213a75d666a7dac31a0d98a861f6421a2da831bc3b23df3fb3`.
Analyzer rc=0/status=passed, bbox 24×16–17 px, sem problemas estruturais; ainda
faltam apex/float e landing, e a leitura artística permanece probe simplificado.

O jump/float foi fechado tecnicamente com quatro poses: crouch, launch, apex e
landing. O strip `out/v11_visual_production/jump_r3/jump_v11_candidate.png` tem
SHA-256 `1e99ab309a6b0764d191841acba580329f0c64ada547800c1dce9566f16c6f7f`, o
GIF tem SHA-256 `acbe05db27590593da62da1bd37bc42ece2e9fed2422d30dd7e675a07478018b`
e a composição 320×224 tem SHA-256
`d0bdad44b2be7dd4a21ad3f2ea84e7655b6c7be2681bc87ab24563df16f2928f`.
O analyzer passou com bbox de largura 24–26 px e altura 16–17 px, sem problemas
de borda, matte, ilhas ou FX assado; o contrato de pixels também passou. O conjunto
mostra a sequência temporal e ainda é um probe visual simplificado, não um asset
final nem uma prova de integração jogável.
## Atualizacao de continuidade — run_contact r4/r4_r2/r4_r3

As tentativas `run_contact_r3`, `run_contact_r4` e `run_contact_r4_r2` permanecem
descartadas ou superseded por acabamento/ilhas observadas; nenhuma delas foi usada
como fonte de pixels para a seguinte. A hipótese atual foi reautorizada do canvas
vazio pelo action file `data/staging/v11_native_edit/run_contact_v11_r4_actions.json`.

Resultado técnico do reseal `run_contact_r4_r3`:

- `native-edit`: `rc=0`, 49 operações, 32×32, 9 cores visíveis, alpha/index 0,
  fonte R1 inalterada;
- candidato: `out/v11_native_edit/run_contact_r4_r3/candidate.png`, SHA-256
  `a8325235742eb020bd259d0867d13b3930d4e40a159a2422f84e8799d20d2fef`;
- conteúdo canônico: `1d2736a15248eda82564293766dd0157db370164f6547a0922e456a2f658d8b1`;
- analyzer: `rc=0`, `status=passed`, bbox `30×20`, área conectada `403`, ilhas
  pequenas `0`, resíduos externos `0`;
- lineart independente: `out/v11_native_edit/run_contact_r4_lineart_r3/candidate.png`,
  SHA-256 `ac1f7c7053cbb4dc2d706918aa6f53d44b5705a2f16983edd8873ec355b55bab`,
  `validate_lineart_topology.py rc=0`.

Revisão cega diagnóstica do agente em 1×, 2×, 3×, 8×, 320×224 e fundos claro,
escuro e chroma foi registrada em
`out/v11_visual_production/run_contact_r4_r3/reports/agent_curated_diagnostic_review.json`.
O resultado permanece `needs_rework`: o perfil único e os apoios alternados são
observáveis, mas os pés ainda estão blocados e o rosto é mais esquemático que o
running do R1. `visual_pass=false`, `human_gate_ready=false` e
`claim_ceiling=native_candidate` continuam obrigatórios.

## Atualização de integração — run_cycle r4 e runtime BlastEm

O ciclo agregado r4 foi montado somente com candidatos nativos produzidos pelo
`native_edit`; não foram usados pixels de v04–v10. A strip tem 128×32, quatro
frames 32×32 e SHA-256
`884cb75dab145c31cacf2baae8b55a409521a94988a522ba3b751b2f4d2d45dd`. O GIF de
quatro frames tem SHA-256
`11373ff9e9cbfa63003da1dc8157013ed84903134267926f4678ae276806f9b3`.

O analyzer do strip retornou `rc=0`, mas sua medição não autoriza promoção
visual: o frame `down` possui `component_count=7`, `small_island_count=4` e
`non_largest_component_pixels=58`. Esse blocker foi preservado no diagnóstico
agregado, em vez de ser escondido pelo status textual do analyzer. As quatro
poses também permanecem esquemáticas em 1×/8×; o ciclo é `needs_rework`.

Evidência visual do agregado:

- [strip 1×](../out/v11_visual_production/run_cycle_r4/evidence/run_cycle_r4_1x.png),
  [2×](../out/v11_visual_production/run_cycle_r4/evidence/run_cycle_r4_2x.png),
  [3×](../out/v11_visual_production/run_cycle_r4/evidence/run_cycle_r4_3x.png) e
  [8×](../out/v11_visual_production/run_cycle_r4/evidence/run_cycle_r4_8x.png);
- [composição 320×224 claro](../out/v11_visual_production/run_cycle_r4/evidence/run_cycle_r4_composition_light_320x224_1x.png),
  [escuro](../out/v11_visual_production/run_cycle_r4/evidence/run_cycle_r4_composition_dark_320x224_1x.png) e
  [chroma](../out/v11_visual_production/run_cycle_r4/evidence/run_cycle_r4_composition_chroma_320x224_1x.png);
- [diagnóstico hash-bound](../out/v11_visual_production/run_cycle_r4/reports/agent_curated_diagnostic_review.json).

A ROM nova foi construída pelo wrapper com `exit_code=0`, tamanho 262144 bytes e
SHA-256 `a3e526634288fb6a83013c059fdca5221c40abff9efc5dd9835624c0ae6785c5`.

Captura BlastEm da cena 4, sessão
`blastem-linux-20260904T114255Z-3619436`, passou os gates de runtime com 61,1
fps no título, cena 4, 0 hard failures, CPU p99 68%, pico de 26 sprites e 16
sprites por scanline. Ela não prova o run porque o personagem ficou parcialmente
fora da janela.

Captura BlastEm da cena 5, sessão
`blastem-linux-20260904T114357Z-3622671`, mostrou o personagem integrado e
alcançou `11/11` estados locomotivos, com 0 frames acima do orçamento, CPU p99
68% e pico de 18 sprites por scanline. O gate canônico falhou em
`playtest_completed` (`finished=0`, passo 16) e emitiu apenas o aviso soft de
cores rasterizadas; portanto a cobertura é parcial e não fecha gameplay.

Arquivos da captura da cena 5: [screenshot](../out/evidence/v11_run_cycle_r4_playtest/blastem-linux-20260904T114357Z-3622671/screenshot.png),
[gate report](../out/evidence/v11_run_cycle_r4_playtest/blastem-linux-20260904T114357Z-3622671/gate_report.json),
[runtime metrics](../out/evidence/v11_run_cycle_r4_playtest/blastem-linux-20260904T114357Z-3622671/runtime_metrics.json),
[SRAM](../out/evidence/v11_run_cycle_r4_playtest/blastem-linux-20260904T114357Z-3622671/save.sram) e
[VDP dump](../out/evidence/v11_run_cycle_r4_playtest/blastem-linux-20260904T114357Z-3622671/visual_vdp_dump.bin).

O estado canônico continua `technical_temporal_probe`,
`animation_candidate=false`, `human_gate_ready=false` e `res_promotion=false`.
O próximo gate causal é reautorizar `down` como pose nativa conectada, depois
reconstruir o ciclo completo e repetir a medição antes de integrar outro ciclo.

## Continuidade de key poses — down r2 e passing r3

`run_down_r2` foi reautorizado do canvas vazio por
`data/staging/v11_native_edit/run_down_v11_r2_actions.json`: `native-edit rc=0`,
44 operações, SHA `1ebb6c716057e4653bb01160bd90024288af149420ef3474ae613bb714d266fe`,
conteúdo canônico `3578a9cc3d16abb7b0c851b3d74fbb6f1c2ac4d3616dc491bfbab64b442f2b66`.
Sua medição é uma componente conectada, área 373, bbox 30×17, zero ilhas,
matte ou resíduos. A revisão 1×/8× lê o squash lateral, mas rosto e clusters
de pés ainda são esquemáticos; status `technical_candidate_needs_visual_rework`.

`run_passing_r3` também foi reautorizado do canvas vazio por
`data/staging/v11_native_edit/run_passing_v11_r3_actions.json`: `native-edit rc=0`,
37 operações, SHA `ddc7683aee729bfb7d0d2c6386d5b2d69b9716603cb03e9d6832ace958f43678`,
conteúdo canônico `7b773d90f109258c639d25231be0ee9f2828f84066db94dca42e6afcbd0e06a6`.
Sua medição é uma componente conectada, área 321, bbox 30×15, zero ilhas,
matte ou resíduos. A pose é um candidato passing lateral, ainda parcial em 1×
e não aprovado visualmente. Os diagnósticos não simulam revisão humana e mantêm
`visual_pass=false`, `human_gate_ready=false` e `animation_candidate=false`.

O próximo gate é autorar `up` do canvas vazio, montar um ciclo com as quatro
poses reautorizadas, validar continuidade e somente então reabrir a integração
do recurso no runtime.
