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

## Continuidade do ciclo — up r2 clean e run_cycle r6

`run_up_r2` foi reexecutado em `out/v11_native_edit/run_up_r2_clean` após a
remoção do pixel isolado `(29,16)`. O resultado foi `native-edit rc=0`, 36
operações, SHA `45afd0c29fd213fe011b22ad8d8e261d57fe51069c013c2d03e5bb583e442a01`,
conteúdo canônico `86f9cee8ce49a5bcef4f91236568d21363d4eeb2df12ae6cc24b77ba56ac1504`,
e analyzer `rc=0`.

O ciclo r6 foi então remontado com `contact r4_r3`, `down r2`, `passing r3` e
`up r2 clean`, sem redimensionamento de autoria. A strip tem SHA
`4f6717e3ccd227aa42fd7b25c5a23111019b9ded1d01a7beb92f9da745a518df` e o GIF
tem SHA `3cc1ac67c0083504162c35998731f5091830b154a50d7331a3f032bd07e0a02d`.
O analyzer retornou `rc=0/status=passed`: quatro componentes principais únicas,
zero ilhas, zero resíduos, zero matte/FX, bbox global 30×15–20 px.

As evidências 1×/2×/3×/8× e composições 320×224 claro/escuro/chroma estão em
`out/v11_visual_production/run_cycle_r6/evidence/`; o diagnóstico hash-bound está
em `out/v11_visual_production/run_cycle_r6/reports/agent_curated_diagnostic_review.json`.
O passe estrutural não equivale a aprovação: a revisão cega mantém
`technical_pass_visual_semantic_fail`, `visual_pass=false`,
`human_gate_ready=false`, `animation_candidate=false` e
`claim_ceiling=technical_temporal_probe`, porque a fidelidade ao R1, o acabamento
facial/pés e o timing locomotivo ainda não são suficientes.

## Hipóteses artísticas do run_contact — seleção provisória B

Foi produzida uma segunda hipótese real a partir do canvas vazio, sem pixels de
v04–v10. A hipótese A foi mantida em
`out/v11_native_edit/run_contact_r4_r3/candidate.png` (SHA
`a8325235742eb020bd259d0867d13b3930d4e40a159a2422f84e8799d20d2fef`). A hipótese
B está em `out/v11_native_edit/run_contact_hypothesis_b/candidate.png` (SHA
`24c74a4b07a8b319afffe74c355aa1cc46af487674099958d2ae568ba623590c`) e foi
selecionada provisoriamente por apresentar clusters de rosto, boca, luz e sombra
mais observáveis em 8×, mantendo o perfil direito e o apoio de contato.

As duas hipóteses foram comparadas em
`out/v11_visual_production/run_contact_hypotheses/contact_A_vs_B_1x.png` e
`contact_A_vs_B_8x.png`. B passou a medição estrutural com 327 pixels visíveis,
bbox 30×16, uma componente, zero ilhas, zero matte e zero resíduos. A seleção
continua `needs_rework`: em 1× o acting ainda não é instantâneo, e a lineart
independente e o timing ainda não foram fechados. O diagnóstico está em
`out/v11_visual_production/run_contact_hypothesis_b/reports/agent_curated_diagnostic_review.json`.

## Lineart independente — hipótese B

A lineart da hipótese B foi autorada separadamente no grid 32×32 por
`data/staging/v11_native_edit/run_contact_hypothesis_b_lineart_actions.json`.
O `native-edit` terminou com `rc=0`, 11 operações, SHA do candidato
`7ba5293cceb1f63b89609737aa49400ef01650990253f49ca6afbbc3e9830780`, e o
`validate_lineart_topology.py --input` terminou com `rc=0/status=ok`: 84 pixels,
`interior_ratio=0`, `max_erosion_depth=0`, sem blockers. A lineart está vinculada
ao diagnóstico B, mas a correspondência semântica e o acabamento ainda não
foram aprovados; o gate humano permanece fechado.

## Agregado r7 — hipótese B de contato

O agregado r7 substituiu o contato A pela hipótese B e manteve `down r2`,
`passing r3` e `up r2 clean`. A strip
`out/v11_visual_production/run_cycle_r7/run_cycle_v11_r7_candidate.png` tem SHA
`36b54d741621bd06697a8a61bdb6520822269df18d34c374161bb4fca9569593`; o GIF
correspondente tem SHA `92cab6a2324e2e5e5e35fbccc35bd9a07350d71d769328761e8e6b5f88bce8e2`.

O analyzer terminou com `rc=0/status=passed`: os quatro frames têm uma componente
única, zero ilhas, zero resíduos, zero matte e bbox global 30×15–17 px. As
evidências 1×/2×/3×/8× e composições 320×224 estão em
`out/v11_visual_production/run_cycle_r7/evidence/`. A revisão do conjunto ainda
é `technical_pass_visual_semantic_fail`: os deltas de silhueta são limitados,
o acting de corrida é fraco, e down/passing/up ainda precisam de linearts
independentes e acabamento visual. O r7 não foi integrado no runtime.

## Hipótese C e agregado r8 — fechamento estrutural, falha semântica preservada

A hipótese C foi reexecutada do canvas 32×32 com paleta de autoria equivalente ao
R1, sem usar pixels de v04–v10. O resultado final está em
`out/v11_native_edit/run_contact_hypothesis_c_r5/candidate.png`: `native-edit
rc=0`, 37 operações, SHA do arquivo
`2956297f54d26dd33cba834776634fda319836e96b8defd5b834f0ecb45bc746` e SHA de
conteúdo canônico `4011bf9b85a28a715fb62f3927ea21563542a1f3ba01d68f488a8fc2b931da96`.
O analyzer retornou `rc=0/status=passed`, uma componente, zero ilhas e bbox
30×16 com 340 pixels visíveis.

A lineart C foi autorada em arquivo separado por
`data/staging/v11_native_edit/run_contact_hypothesis_c_lineart_actions.json`.
Após duas correções topológicas cirúrgicas, o `native-edit` terminou com
`rc=0` e `validate_lineart_topology.py --input` com `rc=0/status=ok`: 84
pixels visíveis, `first_erosion_interior_pixels=0`, `max_erosion_depth=0` e SHA
`fd76ac1913672db1ae7e0952b94cab42d7ce7eed07db482c14315dced68725ed`.

O agregado r8 foi montado sem redimensionamento de autoria com C, down r2,
passing r3 e up r2 clean. A strip
`out/v11_visual_production/run_cycle_r8/run_cycle_r8.png` tem SHA
`514477bee2e91ce5ed00225de27abb7ffed413cc0325a013fc8084cd48695e9d`; o GIF
tem SHA `7c133625af20dc1dadd1c45f5ed2042d4b236ab9ac56a05c4761d22b3047f824`.
O analyzer retornou `rc=0/status=passed`: frames com áreas 340/373/321/316,
bbox 30×16, 30×17, 30×15 e 30×15, uma componente por frame e zero ilhas ou
resíduos. As superfícies 1×/2×/3×/8× e as composições 320×224 claro/escuro/
chroma estão em `out/v11_visual_production/run_cycle_r8/evidence/`; o
diagnóstico está em
`out/v11_visual_production/run_cycle_r8/reports/agent_curated_diagnostic_review.json`.

A comparação cega B/C está em
`out/v11_visual_production/run_contact_hypotheses/contact_B_vs_C_r8_1x.png`
e `contact_B_vs_C_r8_8x.png`. C é a hipótese provisória mais fiel à paleta
observável do R1, mas o agregado continua
`technical_pass_visual_semantic_fail`, `visual_pass=false`,
`human_gate_ready=false`, `animation_candidate=false` e
`claim_ceiling=technical_temporal_probe`: a ação ainda não é imediatamente
reconhecível como corrida em 1×, há quebra de acabamento/paleta entre C e os
demais frames, e down/passing/up não têm linearts independentes fechadas. Nada
foi integrado em `res/`, runtime ou ROM.

## Linearts nativas dos quatro key frames — probe fechada tecnicamente

Foram autoradas no grid 32×32, em arquivos de ações separados, as linearts de
down, passing e up: `run_down_lineart_actions.json`,
`run_passing_lineart_actions.json` e `run_up_lineart_actions.json`. Cada uma
teve `native-edit rc=0` e `validate_lineart_topology.py rc=0/status=ok`, com
alpha binário, `first_erosion_interior_pixels=0` e `max_erosion_depth=0`.
Os SHAs dos PNGs são respectivamente
`8a1b7c30b79c34d1ac0dccc3a10dfb6c5ec487e2923d39871e78c63b773f05f5`,
`86a7a496b0ab206c4a984a20289c70d5b350d77cefc067b67b517663a1f5bcf1` e
`bb2bdcacda187a2d48f7b6fcaff0b3c4650c782530ced1f9603f05a3de43c37b`.
A lineart C permanece com SHA
`fd76ac1913672db1ae7e0952b94cab42d7ce7eed07db482c14315dced68725ed`.

A evidência conjunta está em
`out/v11_visual_production/run_cycle_r8/evidence/run_cycle_r8_lineart_contact_sheet_8x.png`.
O fechamento topológico não promove a arte: as quatro linearts ainda são
diagnósticos autorados e precisam de revisão semântica contra os volumes reais,
olhos, pés e materiais antes de qualquer claim de animação.

## Harmonização R1 do agregado — novo staging isolado

As tabelas de cor de down, passing e up foram ajustadas nos próprios specs
nativos para a equivalência de autoria observável do R1; nenhum pixel foi
redimensionado ou quantizado. As novas saídas são
`run_down_r3_r1_palette/candidate.png` SHA
`d58c8bb8684da7c9e1f247b4f4d9102e01c0ec5e6ab34513005751cd11bb115b`,
`run_passing_r4_r1_palette/candidate.png` SHA
`a8cb4f83417d5efad74c9ac48d1e0078311956c6a8bcd709e4a980267acf4154` e
`run_up_r3_r1_palette/candidate.png` SHA
`5ef62978c7f14a081e37bbd8432d5564b2a822321712342ba9dde80a08b71a77`.

O agregado isolado `run_cycle_r8_r1_palette` tem strip SHA
`4789cce1ac9654ff75b20017130dc4f9561936989b52fccb11e6da0efd7a983c` e GIF
SHA `69334ef1ee527b082e5564f9e3618eccfacb64f280d0c0440cf4d8e3ce941a65`.
O analyzer retornou `rc=0/status=passed`, com áreas 340/373/321/316, uma
componente por frame, zero ilhas e bbox 30×16/17/15/15. A revisão diagnóstica
hash-bound está em
`out/v11_visual_production/run_cycle_r8_r1_palette/reports/agent_curated_diagnostic_review.json`.
Visualmente, a paleta agora é coerente, mas a leitura de corrida em 1× ainda é
parcial e o conjunto permanece `technical_pass_visual_semantic_fail`, sem gate
humano, sem candidato de animação e sem integração em runtime.

## Agregado r8 com suporte corrigido — validators canônicos fechados, sem promoção

O staging `out/v11_visual_production/run_cycle_r8_r1_palette_support/` corrige
causalmente o falso contato dos frames grounded: os contatos declarados agora
tocam pixels visíveis em `y=21`, e o frame up permanece sem contato. A strip tem
SHA `f60fdc628936c306563a3ad47f9f5e093101609fb46836cc1fc47ff6be74a0b4`; o GIF
com timing medido `[4,3,3,3]` tem SHA
`3d2092a2a844c2ebfcd914c02fd7cfd044bdfe50832a419c156ceac05d1fcb1e`; a
lineart nativa separada tem SHA
`7f6c6a82cc832e3fe5cccf5d5e2af6498c7368e0cbd412dda9d6f01e87860329`.

O analyzer da strip terminou em `rc=0/status=passed`: áreas `340/336/321/316`,
bboxes `30×16/30×15/30×15/30×15`, uma componente por frame e zero ilhas ou
resíduos. O contrato v3 tem SHA
`8d3460e805c7c6aad2181396f13a6306058e5b8df3be5b7c0326fe2d445a5299`. Os
entrypoints canônicos terminaram:

- `validate_animation_strip_artifact.py`: `rc=0`, `status=ok`, `blockers=[]`;
- `validate_motion_semantics.py`: `rc=0`, `status=ok`, `blockers=[]`;
- GIF holds rederivados: `[4,3,3,3]`;
- motion: quatro frames distintos, sem slide, sem drift de pivot, fases
  `contact_left/down_compression/passing/up_flight`.

O agregado foi revalidado por
`validate_animation_candidate.py`: `rc=1`, `status=error`,
`maximum_proven_claim=technical_candidate`, `human_gate_ready=false`. Os
blockers honestos são `animation_principles_gate_failed`,
`blind_action_recognition_failed` e `model_sheet_to_sprite_fidelity_unproven`;
não há decisão humana simulada. A revisão diagnóstica e os relatórios
hash-bound estão no mesmo diretório de reports; o manifest é
`data/staging/v11_native_edit/run_cycle_r8_r1_palette_support_candidate_manifest.json`.

O comparador do validator de candidato também recebeu uma correção estrutural:
listas serializadas e tuplas rederivadas são normalizadas antes da comparação.
Isso removeu o falso `child_validation_report_tampered` sem relaxar qualquer
verificação de pixels, hashes, autoria, motion profile ou revisão visual. O
resultado permanece probe técnico-temporal, não candidato de animação; não houve
alteração em `res/`, runtime ou ROM.

## Continuidade de ramos independentes — idle, inhale e jump

O contato C r8 foi reautorado no grid nativo sem o topo horizontal que sugeria
topete: `native-edit rc=0`, SHA do PNG
`3e2845f52595d442e351d3c833bc506beacab50fb2e0496977641120fb0df03e`, analyzer
`rc=0/status=passed`, bbox `30×18`, 372 pixels visíveis, uma componente e zero
resíduos. A lineart correspondente r6 terminou em `rc=0/status=ok`, 88 pixels,
erosão máxima zero, SHA
`77ea5bda3204d3da01d159ec70ddbaed4133951ca2c11f0ad159d9722f7b3cbc`.

O ramo idle foi produzido diretamente por dois specs nativos R1-paletted,
`idle_neutral_r1_palette` e `idle_rise_r1_palette`, e agregado em
`out/v11_visual_production/idle_r4_r1_native/`. O strip tem SHA
`a830edb2900b1878b9b41aea0420464c664f289d2429900b1521e144332f5abc`, GIF SHA
`695f288bd39bc86adfd859307966c8ef97522bfc3f4918e07f7b35d05f319ed9`, holds
`200/200 ms`, e analyzer `rc=0/status=passed`: áreas `322/284`, bboxes
`24×19/24×17`, uma componente, sem matte, ilhas ou bordas. É evidência de
respiração pequena em duas poses nativas, ainda sem contrato canônico completo
ou revisão semântica fechada.

O ramo inhale foi corrigido após uma primeira composição com gutters, que foi
descartada por `edge_problem_frames=6` e `island_problem_frames=2`. O strip
sem gutters em `out/v11_visual_production/inhale_r5_r1_native/` tem SHA
`e178ff4542776dbfc4d36c92675d01fdae08e190a67af19a385dc5d555fd0a34`, GIF SHA
`2a2bed8838474297a3c2dac95eb5e33d83976392bdbe2a899c811bb0c3e4b31f`, holds
`80/80/120/80 ms`, e analyzer `rc=0/status=passed`: áreas `332/392/344/344`,
bboxes `24×17/26×19/24×18/24×18`, sem matte, ilhas ou bordas. O 8× mostra
antecipação, abertura, expansão/hold e release, mas a expressão ainda é
esquemática; permanece probe, não aprovação visual.

O ramo jump foi igualmente agregado sem gutters em
`out/v11_visual_production/jump_r4_r1_native/`. Strip SHA
`3c31c3b23bfca4fec484a382f8c57ae1edf331c97059e280709ad94473d19e96`, GIF SHA
`e1737f3208aa97d169a236575e1a4e277c3ad3fdf6df319494c5d6def26cb6d2`, holds
`80/60/120/80 ms`, analyzer `rc=0/status=passed`, áreas e bboxes dentro de
`24–26×16–17`, sem matte, ilhas ou bordas. O conjunto tem quatro estados
visuais distintos, mas ainda não prova continuidade perceptiva de crouch,
launch, apex e landing.

Todos os novos ramos mantêm a fonte exclusiva R1
`591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`, não usam
pixels v04–v10, e não foram promovidos a `res/`, runtime ou ROM.

As composições diagnósticas 320×224 em escala 1× foram geradas separadamente
para `idle_r4_r1_native`, `run_cycle_r9_r1_palette_support`,
`inhale_r5_r1_native` e `jump_r4_r1_native`, cada uma em fundo claro, escuro e
chroma. As superfícies 2×/3×/8× permanecem separadas; os PNGs são evidência,
não novos assets de runtime.

O idle r4 tem contact sheet 8×
`out/v11_visual_production/idle_r4_r1_native/evidence/idle_r4_r1_native_8x.png`;
inhale r5, `out/v11_visual_production/inhale_r5_r1_native/evidence/inhale_r5_r1_native_8x.png`;
jump r4, `out/v11_visual_production/jump_r4_r1_native/evidence/jump_r4_r1_native_8x.png`.
As três ações continuam sem lineart/contrato agregado canônico e, portanto,
não são candidatas de animação.
## v11 continuation — canonical idle and inhale closure, jump blocker

The v11 staging branch now contains independently authored 32x32 lineart and
artifact-bound strips for the current idle and inhale probes. These are not
runtime assets and do not change `res/`, runtime, ROM, or protected versions.

| action | strip validator | motion validator | current reading |
|---|---:|---:|---|
| idle r5 | rc=0 / ok | not promoted | technical pass; round probe still lacks final arm/anatomy fidelity |
| run r9 | rc=0 / ok | candidate aggregate rc=1 | locomotion remains visually unproven |
| inhale r8 | rc=0 / ok | rc=0 / ok | four distinct masks; visual semantics still schematic |
| jump r5 | rc=0 / ok | rc=1 | `noncanonical_motion_profile`; no private registry entry was added |

Canonical strip evidence:

- idle contract: `data/staging/v11_native_edit/idle_r5_r1_native_contract_v3.json`
- idle strip SHA-256: `f2623456d67c65d42b2a2ae4da61751f3e193ab49f37d7681c61091a9d5a79b7`
- inhale contract: `data/staging/v11_native_edit/inhale_r8_r1_native_contract_v5.json`
- inhale strip SHA-256: `729a2afd6381e14b592a5651374ab4d53a04d5c70be5b492e4cdb851787e79f8`
- jump contract: `data/staging/v11_native_edit/jump_r5_r1_native_contract_v4.json`
- jump strip SHA-256: `9aca561e85b84f865b0ccaec5c8873624bb7898a27addee44644299b2544b8ef`

The canonical entrypoint re-derived frame pixels, source lineage, timing,
integer scale, and lineart topology. Inhale required two corrective iterations:
the first contract had a 63-character frame pixel SHA, and open/release shared
one silhouette mask; the release source was natively refined with four lateral
erase operations. The final motion report is clean with adjacent mask deltas
`[0.06640625, 0.046875, 0.00390625]` and four distinct frames.

Evidence files:

- [inhale contact sheet](../out/v11_visual_production/inhale_r8_r1_native/inhale_r8_r1_native_contact_sheet.png)
- [inhale 8x](../out/v11_visual_production/inhale_r8_r1_native/inhale_r8_r1_native_8x.png)
- [inhale GIF](../out/v11_visual_production/inhale_r8_r1_native/inhale_r8_r1_native_timed.gif)
- [jump contact sheet](../out/v11_visual_production/jump_r5_r1_native/jump_r5_r1_native_contact_sheet.png)
- [jump 8x](../out/v11_visual_production/jump_r5_r1_native/jump_r5_r1_native_8x.png)
- [jump GIF](../out/v11_visual_production/jump_r5_r1_native/jump_r5_r1_native_timed.gif)

Current truth remains:

`status=technical_pass_visual_semantic_fail`

`claim_ceiling=technical_temporal_probe`

`animation_candidate=false`, `human_gate_ready=false`, `res_promotion=false`.

The visual review rejects these probes as final art because the body contours,
feet volumes, and action-specific poses are not yet comparable to the R1 model
sheet at 1x. The next causal route is to obtain an authorized native pixel
producer or human-authored 32x32 key pose, then re-author one action at a time;
jump also requires a justified canonical registry change before motion can pass.
