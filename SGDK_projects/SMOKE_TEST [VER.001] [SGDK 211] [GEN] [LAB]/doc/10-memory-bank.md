<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-06-05T17:13:49.3909615-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 16
- Ultimo build versionado: build_v038
- ROM vigente: `9c5a7e22515b9ebf03c9bc32e4c43d0ac6d3251cf72d32ee043f9c391f4eaaac` (`262144` bytes)
- Validation summary: errors=0 warnings=5
- Blockers vigentes: gdd_substantial_insufficient, visual_gate_blocked, audio_validation_stale, emulator_evidence_stale
- Evidencia de emulador: runtime_metrics_stale
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=stale performance=estavel audio=ok hardware_real=blastem_reference_emulator
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker - SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]

**Ultima atualizacao:** 2026-06-05
**Fase atual:** remaster LAB showcase completo; ROM v037 com fade-in/out, shake, flash, loader unificado e budget documentado; validado em BlastEm
**Proxima fase:** produzir assets autorais para substituir builder-generated (art direction no GDD); baseline comparativo opcional

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- FSM de branding v3 completa: Engine, Author, Project e teardown para boot em 480 frames NTSC.
- Dezesseis assets pixel-native v3: tres fundos, tres logos/placas, tres fontes e seis FX sprites.
- Cinco cues PCM XGM2 com reforco PSG, heat-wave, palette cycling, shimmer, impact shake e debris.
- Build wrapper, audio validation, grafo VRAM e evidencia BlastEm vinculados a ROM vigente.

### O que e placeholder

- A abertura v3 nao usa placeholder textual.
- Os assets sao autoria interna via builder deterministico e permanecem classificados como `needs_review` para entrega AAA.

### O que falta para o slice ser completo

- Promover ou manter em `needs_review` os assets individuais no `visual_delivery_gate`.
- Expandir o GDD apenas se o laboratorio for promovido para produto jogavel.

### Snapshot dos gates QA

- visual_lab_aprovado: false
- gameplay_rom_aprovada: false
- ready_for_aaa: false
- conceito_visual_humano: aprovado
- freshness_audit: ok; stale=0; missing_required=0
- scene_closeout_gate: blocked; cinco passos operacionais ok
- rom_mastering: `mastering_needs_fix`; header/checksum/region/hash BlastEm ok

### Blockers QA ativos

- `gdd_substantial_insufficient`
- `visual_gate_blocked`
- `final_engine_dedicated_capture_missing`
- `baseline_comparison_missing`
- `visual_vdp_dump_missing_for_aaa`

### Metricas de codigo

- Recursos: 21 declaracoes, 16 imagens/sprites, 5 WAV XGM2.
- VRAM: zero overlap; reserva de sprites 420 tiles.
- Runtime branding final: 151 frames observados, CPU medio/p95/max 6%, zero over-budget.
- Sprite pressure: picos de design 13/3/9 por slot; medicao SAT real ainda nao instrumentada.

### Estado de evidencia canonica

- ROM vigente: `be8a4d8459eb17b431cfc4051851b863ce82c426b7b24ddd462636963086ba76` (build_v037)
- `emulator_session.json`: boot=ok, gameplay=funcional, performance=estavel, audio=ok, launch=captured; BlastEm referencia
- `runtime_metrics.json`: stale (captura instrumentada nao executada para v037)
- `scene_regression_report.json`: nao requerido
- `audio_validation_report.json`: passed; 5 samples, 0 issues
- `res_graph_report.json`: ok; 21/21, zero overlap
- `visual_delivery_gate_report.json`: presente; conceito aprovado, `needs_review` para AAA
- `validation_report.json`: 0 errors, 6 warnings; blockers GDD/visual/runtime_metrics_stale/freshness/closeout
- `freshness_audit_report.json`: stale (precisa regenerar para ROM vigente)
- `scene_closeout_gate_report.json`: stale (precisa medir ROM vigente)
- `rom_mastering_report.json`: `mastering_needs_fix`; checks de ROM fisica/logica ok

---

## 2. O QUE ACABOU DE ACONTECER

**2026-06-04 - Branding v3 epico integrado e revisto em ROM**

- A abertura foi reestruturada em tres setpieces de 150/150/180 frames: forja, selo autoral e prensa de aprovacao.
- O builder `tools/image-tools/build_branding_v3_assets.py` gera 16 assets indexados 4-bit com PLTE <= 16 e lineage deterministico.
- O slot Author foi corrigido apos leitura em ROM: halo vazado, ordem SAT segura e monograma `MO` facetado legivel antes do nome.
- O slot Project ganhou colunas de prensa e deixou de repetir a linguagem de hazard/forja do slot Engine.
- A heuristica `Halo De Assinatura Apagando O Monograma` foi canonizada no feedback bank.
- Testes atuais: 3/3 contratos de assets/runtime e 12/12 contratos do build root sem espacos.
- ROM vigente `3bdb6ed7...c2dc8a6b` rodou no BlastEm com `scene_id=0`, SRAM fresca, CPU max 6% e zero over-budget.
- Conceito visual aprovado pelo usuario; o status maximo continua `technical_lab_validated`.

**2026-06-04 - Branding v2 restaurado e validado tecnicamente**

- Corrigido crash por uso de `SPR_setAnim` com indice de frame; runtime agora usa `SPR_setFrame`.
- Corrigido builder do escudo para gerar quatro celulas visiveis e PNGs 4-bit com 16 entradas PLTE.
- Restaurada a FSM completa e removida toda instrumentacao temporaria de pointer probe.
- Tres fontes bitmap passaram a ser desenhadas pelo runtime; spark, monograma, pena e escudo usam seus frames reais.
- Line scroll migrou para `DMA_QUEUE`; posicoes de sprites usam APIs publicas do SGDK.
- Runtime probe MDRT foi ligado no boot/loop, permitindo heartbeat SRAM e metricas rastreaveis.
- ROM vigente passou no wrapper, validacao, audio validation, res graph e BlastEm.
- O status maximo permanece `technical_ready_creative_blocked`; nenhum claim AAA foi feito.

**2026-06-04 - Gate de referencias externas ativas**

- O prompt local de assinatura deixou de conter hardcode para o workspace antigo.
- `validate_project_hygiene.ps1` agora bloqueia caminho absoluto para outro workspace em codigo, scripts, manifestos e documentacao ativa.
- `naming_policy=portable_descriptive_v1` foi materializada; o material ativo passou no gate de nomes portateis.
- Preflight resolveu o toolchain canonico local em `sdk/sgdk-2.11/`, ignorando `GDK` herdado de outro workspace.
- Closeout confirmou `project_hygiene_ready=true`, `technique_usage_ready=true` e `ready_for_aaa=false`.
- Logs historicos em `out/` permanecem preservados e nao contam como dependencia ativa.
- Nenhuma ROM foi rebuildada e nenhuma nova sessao BlastEm foi iniciada; o validator reutilizou evidencia vigente ja existente.

**2026-06-03 - Manifesto de tecnicas do projeto**

- Criado `doc/technique_usage_manifest.json` como contrato local para tecnicas catalogadas.
- O manifesto inicial esta vazio (`techniques=[]`) e marcado como `lab_not_delivery=true`; nenhuma tecnica foi promovida ou validada por esta mudanca.
- `doc/13-spec-cenas.md` passou a referenciar o contrato e a regra de bloqueio para tags/registry/status/evidencia fora do projeto.
- Status do projeto permanece bloqueado para entrega: sem gate BlastEm fechado, sem visual delivery e sem closeout.

**2026-05-24 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Branding intro AAA v1 com assets nativos e VDP**

- Criado builder deterministico `tools/image-tools/build_branding_intro_assets.py` para transformar fontes nativas em PNGs SGDK-safe: `brand_engine_logo`, `brand_author_logo`, `brand_project_logo`, `brand_presents_text` e `brand_fx_tiles`.
- `SCENE_branding` deixou de ser placeholder textual e passou a usar `IMAGE` real via `VDP_drawImageEx`, fundo de tiles FX, shimmer/pulse de paleta, PSG procedural e FSM engine/author/project.
- ROM direta SGDK buildada em `tools/sgdk_wrapper/modelo/out/rom.bin`; SHA256 `D012A842ADE368E25AE739F1DBB8A87F1DEAEDBE3799F407D24C2C4B170FD734`.
- Evidencia visual capturada no BlastEm para a mesma ROM final:
  - engine: `out/evidence/blastem_brand_intro_engine_final_rom/screenshot.png`
  - author: `out/evidence/blastem_brand_intro_author_final_rom/screenshot.png`
  - project/presents: `out/evidence/blastem_brand_intro_project_present_final/screenshot.png`
- `res_graph_audit.ps1` passou com status `warn` apenas por exigir evidencia VDP runtime para tiles carregados por codigo. O wrapper canonico ainda fica preso em `validate_resources.ps1`/gate `.agent` degradado; nao promover para closeout final ate corrigir esse gate.

**2026-06-05 - Remaster LAB Showcase: diagnostico historico e melhorias de runtime**

- Decisao humana: Rota A confirmada. Manter `kind=lab`, `lab_not_delivery=true`. Teto: `technical_lab_validated`.
- Diagnostico historico completo: identificadas 5 decisoes de resultado fraco (assets builder-generated, tiling como composicao, 34 builds iterativos, GDD minimo, classificacao LAB como ceiling).
- GDD expandido com fantasia do LAB, criterios visuais por slot, ambicao tecnica, regras sistemicas e criterios de qualidade.
- Adicionado screen shake ao runtime: `brandTriggerShake(4)` no impacto Engine (frame 2) e `brandTriggerShake(3)` na queda do escudo Project (frame 326).
- Adicionado impact flash: breve burst branco em PAL0 (4 entries) nos mesmos signature moments, com restore da paleta original nos 4 frames seguintes.
- Shake implementado via `brandGetShakeOffset()` aplicado ao `VDP_setVerticalScroll(BG_B)` dentro de `brandAnimateBackground()`.
- ROM v035 buildada com sucesso: 0 errors, 6 warnings. Warnings esperados: GDD/visual gate/emulator stale/freshness stale/closeout stale.
- Pendente: validacao BlastEm da nova ROM, art direction brief para substituicao futura dos assets builder-generated.
- BlastEm validado: ROM v035 bootou, 3 slots visiveis, shake no Engine e Project confirmados, skip funcional, audio ok, 60fps estavel.
- `emulator_session.json` atualizado para `captured` com todos os eixos QA ok/funcional/estavel.

---

## 3. DECISOES PENDENTES

- Validar ROM v035 no BlastEm com captura dedicada dos 3 slots.
- Decidir se baseline comparativo e VDP dump valem o custo para promover o LAB.
- Decidir se o branding v3 deve virar template canonico apos o visual delivery gate.
- Produzir assets autorais para substituir os builder-generated (art direction brief pendente).

---

## 4. DECISION LOG CONSERVADOR

Registre aqui escolhas que evitaram tentativa-e-erro ou mudanca de rota.

| Data | Contexto | Escolha | Alternativas recusadas | Evidencia | Proximo gate |
|------|----------|---------|------------------------|-----------|--------------|
| 2026-06-04 | branding/sprites | Usar `SPR_setFrame` para folhas com uma animacao e varios frames | `SPR_setAnim` por frame, escrita interna em `Sprite` | `src/scenes/scene_branding.c`, BlastEm | validado_budget |
| 2026-06-04 | branding/fontes | Fonte scene-local em tilemap `NONE` e base VRAM fixa | sistema font global, alocacao dinamica | `res/resources.res`, `doc/07-budget-vram-dma.md` | visual humano |
| 2026-06-04 | branding/v3 | Separar os slots em forja, selo autoral e prensa | repetir hazard stripes e brilho generico nos tres slots | `out/evidence/blastem_branding_v3_final/` | visual delivery |
| 2026-06-04 | branding/author | Halo vazado atras do monograma `MO` | glow opaco cobrindo a assinatura | `author_hold.png`, feedback bank | baseline |

---

## 5. ROTEIRO DE FECHAMENTO

- build/rebuild canonico: ok
- contratos recompilados: ok
- grafo de recursos: ok
- validator: ok
- captura BlastEm: ok
- regressao de cena: nao requerida
- freshness audit: ok
- closeout gate: blocked por GDD minimo e visual gate
- mastering: needs_fix apenas por gates de entrega, nao por header/checksum/region

---

## 6. REFERENCIAS RAPIDAS

- GDD: `doc/11-gdd.md`
- Spec cenas: `doc/13-spec-cenas.md`
- Diretrizes agente: `doc/00-diretrizes-agente.md`
- Plano de provas QA: `doc/14-plano-de-provas-qa.md`

## 7. ADOCAO METODOLOGICA 2026-06-04

- `project_methodology_manifest.json` adotado com lifecycle `existing`.
- `critical_motion`, `road_physics` e `modular_boss` sao `not_applicable` para este smoke estrutural.
- Identidade normalizada entre diretorio, `.mddev/project.json`, manifests e documentos; nenhum placeholder de template permanece.
- `freshness_audit` declarado como validacao metodologica obrigatoria.
- `doc/scene-contracts.json` recompilado a partir da spec para satisfazer o preflight de projeto antigo.
- Preflight final: passou sem avisos.
- Metodologia final: `passed`, zero blockers e nenhum falso claim de movimento critico, road physics ou boss modular.
- Closeout continua honestamente bloqueado por GDD, gate visual, audio e `scene_closeout_gate`; `ready_for_aaa=false`.
- Nenhuma tecnica foi promovida para `MESTRE_*`.

## 8. HIGIENE E SINCRONIZACAO DOCUMENTAL 2026-06-04

- `project_hygiene` foi adicionado as validacoes metodologicas obrigatorias.
- `doc/project_hygiene_manifest.json` e `rascunho/README.md` ja estavam presentes e foram preservados.
- `validate_project_methodology.ps1`: `passed`, zero blockers.
- `validate_project_hygiene.ps1`: `passed`, zero blockers.
- Nenhuma ROM foi rebuildada ou revalidada em BlastEm nesta alteracao.

### Closeout metodologico observado

- `validate_resources.ps1 -CloseoutGate`: `ready_for_aaa=false`.
- `project_hygiene_ready=true` e `technique_usage_ready=true`.
- Blockers vigentes: `gdd_substantial_insufficient`, `visual_gate_blocked`, `visual_delivery_gate_missing`, `audio_validation_missing`, `emulator_evidence_stale`, `freshness_audit_stale`, `scene_closeout_gate_missing`.
- `res_graph_report.json` e build/evidencias antigas ainda exigem regeneracao no fluxo proprio; nenhum status foi promovido.


































































































