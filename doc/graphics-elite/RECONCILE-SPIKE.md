# WI-00 — Spike de reconciliação: GRAPHICS-ELITE-DIRECTIVE v2 × framework existente

- **Data:** 2026-08-07
- **Escopo:** somente WI-00. Nenhuma skill criada, nenhuma regra editada, nenhum schema alterado.
- **Branch:** `codex/canonical-skill-curation` (ver Seção 4, premissa P1).
- **Entrada:** GRAPHICS-ELITE-DIRECTIVE v2 (fornecida pelo operador) e
  `doc/curation/GRAPHICS_CAPABILITY_REPORT_2026-08-06.md`.
- **Saída:** este documento. Ele **decide o quê fazer**, não faz.

## Por que este spike existe

A diretiva propõe 8 work items para canonizar um sistema de produção e veto visual.
A própria diretiva manda parar e registrar se uma premissa se revelar falsa. Ao medir o
framework antes de escrever qualquer coisa, **a maior parte do que ela propõe criar já existe
e é aplicada por schema e por CI**. Executar WI-01…WI-05 como escritos produziria duplicação —
exatamente o que a política de skills proíbe (`.agent/skills/README.md`: "Nao duplique nem
edite skills em dois lugares").

O resultado prático tem **duas camadas**, e a segunda inverte a primeira:

1. Medido **neste worktree**, dos 8 itens sugeridos pelo relatório (§11), 7 já existem
   como schema/CI e 1 é lacuna real.
2. Medido contra **`origin/main`**, quase nada disso está lá. Ver Seção 0.

---

## 0. Grau de canonicidade — a medição que muda a resposta

`tools/sgdk_wrapper/schemas/` tem **132 arquivos no disco**, **124 rastreados no HEAD deste
branch** e **0 em `origin/main`**. Os artefatos que sustentam os itens 1 e 2 — a base
inteira de WI-01 e WI-05 — não estão rastreados em lugar nenhum.

| Camada | O que significa | Artefatos citados neste spike |
|---|---|---|
| **UNTRACKED** | existe só no disco; não está em nenhum commit, nem neste branch | `schemas/sprite_artifact_report.schema.json`, `tools/image-tools/sprite_artifact_audit.py`, `ci/test_sprite_artifact_report.py` |
| **TRACKED, ausente em `main`** | commitado nos 36 commits à frente deste branch; não mergeado | `visual_source_of_truth`, `visual_dna_manifest`, `animation_strip_contract`, `blastem_evidence`, `art_gameplay_direction_gate`, `model_sheet_to_sprite_fidelity_report`, `art_quality_report`, `composition_scope_contract`, `ci/test_visual_source_of_truth_gate.ps1`, `tools/ai_imagegen/imagegen_circuit.py` |
| **TRACKED + em `main`** | canônico no sentido pleno | `tools/sgdk_wrapper/art_diagnostic.py`; as skills de arte (9 em `main`, **14 aqui**) |

**Consequência direta:** onde este spike diz "já canônico", leia **"já canônico neste
worktree, pendente de commit e/ou merge"**. Nenhuma das colunas `Decisão` da Seção 1 pode
ser executada antes de resolver isso — senão o WI seguinte vai "criar" algo que já existe
no disco de um agente e em mais lugar nenhum, ou vai declarar `nada a fazer` apoiado em
arquivo que ninguém mais tem.

**Isto é a premissa P1 falsa deixando de ser burocracia e virando causa raiz.** A diretiva
mandava partir do tip de `main` justamente para que "o que já existe" fosse uma pergunta
com resposta única. Aqui ela tem três respostas diferentes conforme a camada.

---

## 1. Tabela de reconciliação

Os 8 itens são citados literalmente de `GRAPHICS_CAPABILITY_REPORT_2026-08-06.md:498-505`.
As 4 skills são as propostas pela diretiva.

> **Ler junto com a Seção 0.** A coluna `Estado` descreve o **disco deste worktree**.
> Itens 1, 2 e 7 apoiam-se em arquivos **untracked**; os demais em arquivos rastreados
> mas **ausentes de `origin/main`**. Todas as citações `arquivo:linha` referem-se à árvore
> local e devem ser reconferidas contra `main` antes de qualquer canonização.

| # | Item | Onde vive hoje | Estado | Decisão | Justificativa |
|---|---|---|---|---|---|
| 1 | `technical_pass_visual_fail` | `tools/sgdk_wrapper/schemas/sprite_artifact_report.schema.json:31` (enum); `tools/image-tools/sprite_artifact_audit.py:393`; `tools/sgdk_wrapper/ci/test_sprite_artifact_report.py:96,113,126` | já canônico | **nada a fazer** | É valor de enum com 3 testes de CI. Não é "prática de projeto" |
| 2 | `sprite_artifact_report.v2` | schema `schemas/sprite_artifact_report.schema.json`; gerador `tools/image-tools/sprite_artifact_audit.py`; CI `ci/test_sprite_artifact_report.py` | já canônico | **nada a fazer** | Os 7 `required_checks` são `"const": true` — não há como alegar conformidade pulando check |
| 3 | `visual_source_of_truth` | `schemas/visual_source_of_truth.schema.json` (10 campos required); CI `ci/test_visual_source_of_truth_gate.ps1` | já canônico | **nada a fazer** | `negative_evidence` (schema:147) e `obsolete_for_generation_source` (schema:140, `const`) já são enum |
| 4 | model sheet com scale / turnaround / material lock | `schemas/visual_dna_manifest.schema.json` → `material_rules`, `scale_contract`, `key_pose` (todos em `required`); `schemas/animation_strip_contract.schema.json` → `turnaround` | já canônico, **disperso** | **aditivo documental** | As 3 travas existem, mas em 2 schemas diferentes. Falta um ponteiro; não falta contrato |
| 5 | lineart nativo por estado e key poses | `lineart`: `schemas/art_quality_report.schema.json`, `schemas/visual_source_of_truth.schema.json`. `key_pose`: 5 schemas, incl. `art_gameplay_direction_gate` e `model_sheet_to_sprite_fidelity_report` | parcial | **aditivo em skill existente** (`sprite-animation`) | Ambos os termos existem. O que não existe é a exigência de **um lineart por estado** encadeada ao strip |
| 6 | **scene kit + multi-plane + semantic parse** | `scene_kit`, `semantic_parse`, `multi_plane`: **0 ocorrências nos 132 schemas**. Adjacências: `layer_plan` (`composition_scope_contract`, `art_gameplay_direction_gate`), `depth_role` (`art_gameplay_direction_gate`), `parallax` (`parallax_camera_contract`) | **ausente** | **skill nova ou schema novo** — a única do lote | Única lacuna genuína. Ver Seção 4b: MARE_BRAVA também nunca decompôs o kit, então não há nem contrato nem precedente completo |
| 7 | contact sheet VDP e comparação source/runtime | `schemas/sprite_artifact_report.schema.json:145` exige `contact_sheet` + `animated_captures` no bloco `evidence`; também em `model_sheet_to_sprite_fidelity_report:38` e `art_gameplay_direction_gate:65` | já canônico | **nada a fazer** | Contact sheet é evidência obrigatória, não sugestão |
| 8 | BlastEm vinculado ao hash da ROM | `schemas/blastem_evidence.schema.json` — `rom_sha256` está em `required`, junto de `vdp_dump_present` e `sram_present` | já canônico | **nada a fazer** | O vínculo é obrigatório no schema de evidência |
| A | skill `visual-lineage-and-veto` | `art/megadrive-pixel-strict-rules/SKILL.md:158-163` (`### Limite do gate pixel-strict`); `art/visual-excellence-standards/SKILL.md:356`; `art/art-translation-to-vdp/SKILL.md:59`; `art/character-design/SKILL.md:70` | já canônico | **não criar** | A regra de veto já existe e já faz handoff do veto semântico para `visual-excellence-standards`. Criar a skill duplicaria 4 arquivos |
| B | skill `character-visual-first-route` | `art/character-design` (200L), `art/sprite-animation` (385L), `art/art-direction-selector` (245L), `art/art-translation-to-vdp` (817L) | parcial | **aditivo, não skill nova** | O território está ocupado por 4 skills. O que falta é a **ordem** entre elas — isso é workflow, não skill |
| C | skill `scene-kit-multiplane-route` | `art/multi-plane-composition` (267L), `art/scene-direction-curator` (209L), `art/tiled-hybrid-parallax-curator` (66L) | parcial → item 6 é a lacuna | **candidata única a skill nova** | Se alguma skill nova se justificar, é esta — mas só depois de resolver a Seção 4b |
| D | skill `elite-perceptual-benchmark` | `art/visual-excellence-standards` (994L, a maior do framework); eixo perceptivo em `hardware/megadrive-vdp-budget-analyst` | já canônico | **não criar** | `visual-excellence-standards` é declaradamente "o cerebro estetico do workspace" |

**Leitura da tabela:** 6 linhas `nada a fazer`, 4 `aditivo`, 1 lacuna real (item 6),
1 candidata a skill nova (C) subordinada a ela.

**Mas nenhum `nada a fazer` é executável hoje.** Os itens 1, 2 e 7 dependem de
`sprite_artifact_report.schema.json` + `sprite_artifact_audit.py` + `test_sprite_artifact_report.py`,
que estão **untracked**. Antes de fechar WI-01/WI-05, esses três precisam ser commitados —
caso contrário "já é canônico" é uma afirmação sobre o disco de uma máquina.
Essa é a ação de maior valor e menor custo saída deste spike.

---

## 2. Mapa de propriedade — as 14 skills de arte

Existem 14 skills em `.agent/skills/art/`. Nenhuma skill nova pode nascer sem
explicar por que não cabe em nenhuma destas (`.agent/skills/README.md`,
`## Crescimento da arvore`: "skill nova so nasce quando o gap for puro").

| Skill | Linhas | Implícita | Território que a diretiva queria ocupar |
|---|---|---|---|
| `visual-excellence-standards` | 994 | sim | **Todo o WI-04.** Julgamento estético, legibilidade, contraste de plano, dithering funcional, leitura CRT, canonização de feedback visual |
| `art-translation-to-vdp` | 817 | sim | Reinterpretação de fonte forte como recurso MD; trata a imagem como matéria-prima, não como asset final |
| `art-conversion-pipeline` | 552 | sim | Conversão mecânica; delega tradução interpretativa |
| `art-creation-sourcing` | 472 | **não** | Sourcing por IA/fontes livres; dona do `context_pack_manifest` |
| `sprite-animation` | 385 | **não** | Sheets, ciclos, continuidade de pose, pivôs, strips. **Dona natural do item 5** |
| `cutscene-cinematic-direction` | 313 | sim | Cutscene como FSM |
| `multi-plane-composition` | 267 | sim | BG_A/BG_B/foreground, parallax, `scene_slice`. **Dona natural do item 6** |
| `megadrive-pixel-strict-rules` | 255 | sim | **Todo o veto sintático + `### Limite do gate pixel-strict`.** Dona de `technical_pass_visual_fail` e `obsolete_for_generation_source` |
| `art-direction-selector` | 245 | **não** | Impede avanço com "pixel art generico" por falta de decisão estética |
| `image-generation-routing` | 239 | **não** | Escolhe canal de geração; emite `BLOCKED_IMAGE_TOOLING` |
| `art-asset-diagnostic` | 226 | sim | Primeira etapa; roteia para o workflow correto |
| `scene-direction-curator` | 209 | **não** | `minimal / competente / monumental / signature-only` |
| `character-design` | 200 | **não** | Escala canônica, silhueta, código funcional de cor. **Dona natural do item B** |
| `tiled-hybrid-parallax-curator` | 66 | sim | Tiled JSON + plates → cena MD |

---

## 3. Termos já tomados — não redefinir

Cada um já tem dono. Redefinir qualquer um cria um segundo eixo paralelo de status,
que é o defeito que a Seção 7 do relatório aponta.

| Termo | Definido em |
|---|---|
| `technical_pass_visual_fail` | `schemas/sprite_artifact_report.schema.json:31` |
| `obsolete_for_generation_source` | `schemas/visual_source_of_truth.schema.json:140` (`const`) |
| `negative_evidence` | `schemas/visual_source_of_truth.schema.json:147` |
| `source_candidate` | `tools/ai_imagegen/imagegen_circuit.py:185,199` |
| `active_res_art` | `tools/sgdk_wrapper/art_diagnostic.py:394,410` |
| `visual_aprovado` / `_com_recuo` / `=false` | `skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`, tabela de veredito de 2 eixos |
| `visual_direction_failed`, `artistic_gate_failed` | `rules/SGDK_GLOBAL.md` §8.2, §18 |
| `visual_gate_blocked` | `rules/SGDK_GLOBAL.md`; `schemas/visual_delivery_gate_report.schema.json` |
| `asset_lineage_record`, `premium_source_manifest` | `workflows/production-loop.md` §2; `schemas/premium_source_manifest.schema.json` |
| `source_validity_report`, `authoriality_gate_report`, `clone_risk_report` | `workflows/production-loop.md` §0 |
| `art_gameplay_direction_gate` | `schemas/art_gameplay_direction_gate.schema.json` |
| `S1c_visual_gate_early` | `rules/SGDK_GLOBAL.md` §22 |

Vocabulários de status **paralelos** que já coexistem (quatro, além do de `AGENTS.md`):
o de `AGENTS.md:116-127` (8 termos); o eixo perceptivo do budget analyst; o de
proficiência em `SGDK_GLOBAL.md` §1.0.2 (`LABORATORIO`…`MESTRE_PRIORITARIA`);
e os verdictos pixel-strict (`aprovado / aprovado_com_ajustes / rejeitado`).
**Qualquer termo novo precisa declarar qual destes estende — não criar um quinto.**

---

## 4. Premissas falsas e bloqueios

| # | Premissa da diretiva | Realidade medida | Efeito |
|---|---|---|---|
| P1 | Partir do tip de `main` com PR#3 e PR#4 | `origin/main` tem ambos, mas a árvore está em `codex/canonical-skill-curation`, 10 commits atrás, 36 à frente, com 378 arquivos não commitados incluindo o projeto Kirby inteiro. **E `origin/main` não tem nenhum dos 132 schemas nem 5 das 14 skills de arte** | **Não é desvio de bookkeeping — é causa raiz.** Ver Seção 0. Aceito para escrever este spike (que só cria arquivo novo), mas bloqueia WI-01 e WI-05 até o WI-00b |
| P2 | Escrever em `doc/logs/WORKLOG.md` | Não existe | Bloqueia WI-07 |
| P3 | Registrar decisões como ADR | Não existe diretório nem processo de ADR | Bloqueia WI-01…WI-05 como escritos |
| P4 | Ser "aditivo ao FAILURE-MODES" | Documento não existe | O aditivo não tem destino |
| P5 | Ser "aditivo ao DATA-FLOW" | Documento não existe | Idem |
| P6 | WI-05 "promover `sprite_artifact_report` v2 ao central" | Já é central desde antes: schema + gerador + CI | WI-05 fecha como `nada a fazer` |
| P7 | WI-01 criar o veto visual canônico | Já canônico em schema, CI e 4 skills | WI-01 fecha como `nada a fazer` |

**Recomendação sobre P2–P5:** não criar `WORKLOG.md`, ADR, `FAILURE-MODES` e `DATA-FLOW`
do zero. O workspace já tem os equivalentes funcionais, e criar paralelos repetiria o
defeito dos vocabulários duplicados:

- histórico por projeto → `doc/changelog/changelog.md` + `doc/10-memory-bank.md`
- decisão registrada → `art_direction_decision_record`, `route_decision_record`,
  `runtime_decision_log.json`
- modos de falha → `doc/agent_learning/failure_patterns.md` por projeto
- fluxo de dados → `.agent/pipelines/aaa_scene_v1.json` + `workflows/production-loop.md`

**Decisão do operador necessária** antes de WI-07.

### Dois defeitos de integridade encontrados de passagem

Registrados, **não corrigidos** (mexer neles é alterar árvore canônica sem aprovação):

1. `doc/curation/graphics_capability_inventory_2026-08-06.json` tem `scope` apontando
   para `/mnt/sdcard/SGDKForge/` (o symlink) em vez de `/mnt/sdcard/Projects/Sgdk Forge/`.
2. Os strips reprovados v002/v009 do HYBRIDO continuam em `res/sprites/hibrido/` sem
   quarentena. A disciplina de arquivamento que o relatório elogia vale para o Kirby,
   não para o Híbrido.

---

## 4b. Livro-razão de atribuição

**Este é o achado que impede WI-02 e WI-03.**

A diretiva descreve as duas rotas como "PROVEN in the field". O relatório de onde ela
tirou a tabela (§5, "Genealogia dos métodos") usa a palavra **`incumbente`** — melhor
rota conhecida — e declara em §13 que "não houve aprovação humana dos 700 arquivos" e
que "o status de cada projeto continua subordinado ao memory bank e evidência".

**Nenhum dos cinco projetos está visualmente aprovado.**

### Atribuições incorretas

| Alegação da diretiva | Dono real | Artefato que decide | Teto honesto |
|---|---|---|---|
| Híbrido v010 estabelece o redraw nativo | Híbrido, mas **superado** | `out/logs/visual_delivery_gate_report_v011.json` e `_v012.json` — ambos `ready_for_aaa=false`, `visual_route_status=visual_gate_blocked`. **v012 tem `generation_source_policy=advanced_ai_source_to_vdp_candidate`**, enquanto v011 tem `locked_to_approved_model_sheet_only` | v010 é `runtime_candidate_not_aaa_not_source`, `visual_aprovado=false`. A variante mais recente é rota **de fonte IA**, o oposto da alegação |
| "morphing de frames gerados por IA" é lição do Híbrido | **MARE_BRAVA / TAÍNA** | `doc/agent_learning/failure_patterns.md:112` — "L12 gerar todos os frames por IA produz morphing em vez de animação" (2026-07-29) | Contra-regra promovida: `success_patterns.md:49` "L13 pose-mestre aprovada e edicao de clusters preservam autoria na animacao" |
| MARE_BRAVA estabelece "scene kit" | MARE_BRAVA, **mas o kit não existe** | `doc/contracts/dock_scene_kit_inventory.json` → `"status": "dock_scene_kit_source_board_present_not_decomposed"`, com `unblock_condition` exigindo decomposição em 7 famílias que **nunca ocorreu** | O que existe é *semantic parse → layer plan → montagem modular nativa* (`success_patterns.md:82`, L16) |
| BLUE_CIRCUIT tem visual DNA / material lock / turnaround | Ninguém | Nenhum dos três existe no projeto. `doc/08-bible-artistica.md` é stub de 56 linhas | O gate do Blue é `sprite_artifact_report.v2` — cite-o por isso e pela sequência de 3 gates humanos |
| Celestial Chase estabelece "scene kit" | Ninguém | Nenhum artefato de kit no projeto | Cite-o por *semantic parse → builder tile-aware → split basic/elite → gate de screenshot* |
| MUGEN tem comparação basic/elite | Ninguém | Não existe | O eixo do MUGEN é *viewport da fonte → preview de export → BlastEm* |

### Teto real de cada projeto citado

| Projeto | Status literal do memory bank |
|---|---|
| BLUE_CIRCUIT | `technical_ready_creative_blocked`; `visual_pass` vale **só** para player v002 estático; `ready_for_aaa=false` |
| MARE_BRAVA | `buildado_runtime_observed_partial`; selos rejeitados por `vlab_block_missing`, `artifact_missing:vdp_dump`, `artifact_missing:runtime_metrics` |
| Celestial Chase | `validado_budget_tecnico_v011`, porém metodologia presa em `perceptual_motion_unvalidated` |
| MUGEN SFF Showdown | `route_a_runtime_reworked_emulator_seen_budget_dump_pending`; `documented_not_validated_budget` |
| HYBRIDO_MUAY_THAI | `visual_gate_blocked` em v010, v011 **e** v012 |

### O que pode ser citado com honestidade

- **BLUE_CIRCUIT** — a sequência de 3 gates humanos (`doc/contracts/human_visual_gate_plan.json`)
  e a disciplina de retratação formal (`sprite_strip_rejection_report_20260723.json`).
- **HYBRIDO** — o *vocabulário de contrato*: visual DNA, turnaround, `visual_source_of_truth`
  como trava anti-polimento — e as 6 falhas arquivadas nomeadas (terceiro braço, mão ilegível,
  rosto estático, spray→tile-noise, sprite 48x64 sem anatomia, escala instável).
- **MARE_BRAVA / TAÍNA** — a **única corrida ponta-a-ponta que chegou ao runtime com direção
  visual aprovada**: pose-mestre + edição de clusters (L13), contra morphing de frames (L12).
- **CAIS_01** — a separação custo-de-ROM × set residente de VRAM
  (`cais01_vdp_budget_report_v04.json`, bloco `resource_budget_semantics`), decisão `cabe com recuo`.
- **MUGEN rota A** — as três lições que a diretiva cita são literalmente títulos de seção
  do `failure_patterns.md` dele: crop ≠ conversão; tiles da ROM ≠ budget residente;
  HUD não sobrescreve paleta do stage.

---

## 5. Custo de entrada de uma skill nova

`.agent/scripts/validate_skill_framework.py` impõe o seguinte como **erro duro**. A diretiva
não menciona nenhum destes:

1. Frontmatter com **exatamente** as chaves `name` e `description`, nessa ordem. Qualquer
   chave extra é erro.
2. `name` deve ser igual ao nome da pasta.
3. `agents/openai.yaml` **obrigatório**.
4. `short_description` entre **25 e 64 caracteres**.
5. `default_prompt` deve conter literalmente `$<nome-da-pasta>`.
6. `allow_implicit_invocation` deve estar presente. Política do README: skills de
   governança, auditoria, roteamento ou sourcing externo usam `false`.
7. `SKILL.md` deve conter os 4 blocos de contrato: `entrada minima`, `saida minima`,
   `passa quando`, `handoff`.
8. A pasta deve estar em `framework_manifest.json > tracked_paths` como
   `skills/<categoria>/<nome>`.
9. Termos proibidos: `megadrive-elite`, `blaze_applicability`.

Além disso, de `ARCHITECTURE.md` (`### Acoplamento por skill_path`): pipelines referenciam
skills por `skill_path`, então **mover ou renomear skill exige curadoria simultânea de
`pipelines/`** — "mover ou renomear skill sem revisar pipelines e workflows e regressao de
governanca, nao 'refactor cosmetico'".

`framework_manifest.json` está em `framework_version: "2026.06.19"`; alterar `tracked_paths`
deveria vir com bump.

---

## 6. Sequência revisada de WIs

| WI | Diretiva original | Decisão do spike |
|---|---|---|
| WI-00 | spike de reconciliação | **feito** — este documento |
| **WI-00b** | *(não previsto pela diretiva)* | **novo e prioritário: commitar os 3 arquivos untracked** (`schemas/sprite_artifact_report.schema.json`, `tools/image-tools/sprite_artifact_audit.py`, `ci/test_sprite_artifact_report.py`) e decidir o destino dos 36 commits deste branch. Sem isso, todo `nada a fazer` abaixo é vácuo |
| WI-01 | canonizar veto visual + skill `visual-lineage-and-veto` | **fechar como `nada a fazer` — depois do WI-00b.** A regra já existe em 4 skills (linha A), mas o schema que a aplica está untracked |
| WI-02 | skill `character-visual-first-route` | **não executar como escrito.** Canonizaria as atribuições erradas da Seção 4b. Reespecificar como *aditivo de ordenação* em `sprite-animation` + `character-design`, citando TAÍNA L12/L13 — não Híbrido v010 |
| WI-03 | skill `scene-kit-multiplane-route` + catálogo de evidência negativa | **não executar como escrito.** "Scene kit" não existe em lugar nenhum: 0 ocorrências em 132 schemas e o kit do MARE_BRAVA nunca foi decomposto. Reespecificar em duas partes: (a) o catálogo de evidência negativa — barato e útil; (b) decidir se *scene kit* vira contrato novo ou se o alvo real é `semantic_parse` + `layer_plan`, que têm precedente |
| WI-04 | skill `elite-perceptual-benchmark` | **fechar como `nada a fazer`.** `visual-excellence-standards` (994L) já é isso |
| WI-05 | promover `sprite_artifact_report` v2 ao central | **reespecificar.** O v2 está em `tools/sgdk_wrapper/schemas/`, o lugar central certo — mas **untracked**. "Promover ao central" vira, literalmente, `git add`. A diretiva estava certa pelo motivo errado |
| WI-06 | cena-prova com `visual_pass` humano | **mantém, e é o único que ataca o problema real do Kirby.** Exige revisor humano — não pode ser fechado por agente |
| WI-07 | consolidação em `AGENTS.md` / WORKLOG / catálogo de erros | **bloqueado** por P2–P5 até o operador decidir se cria infra nova ou reusa a existente |

**Recomendação, em ordem:**

1. **WI-00b** — commitar os 3 untracked e decidir o destino dos 36 commits. Custo: minutos.
   Sem isso, metade das conclusões deste spike não é verificável por outra pessoa.
2. **WI-06** — a cena-prova. O gargalo do Kirby não é falta de framework: é que quatro
   rotas de arte foram reprovadas e **nenhuma quinta foi tentada com a rota que chegou ao
   runtime no MARE_BRAVA** (pose-mestre + edição de clusters). Não depende de nenhum outro WI.
3. WI-01, WI-04 — fecháveis sem escrever código, depois do WI-00b.
4. WI-02, WI-03 — só após reespecificação (Seção 4b).
5. WI-07 — bloqueado até o operador decidir sobre P2–P5.

---

## 7. Colisão de nomenclatura

`SGDK_projects/KIRBY_FAN GAME CLOUDE …/doc/art/PRODUCTION_ASSET_PACK.md` rotula sua rodada
como **"P1"**, com IDs de asset `A1..E3`.

`P1` agora é também o identificador da evidência negativa arquivada em
`data/source_art/archive/p1_2026-08-06_visual_rejected/`. As duas coisas são
indistinguíveis por nome, e o pack ainda descreve um **pedido**, não um resultado.

**Recomendação:** renomear a próxima rodada para `NATIVE-01` (ou `P5`), e marcar o
`PRODUCTION_ASSET_PACK.md` atual com o desfecho — ele produziu a rota P1, que foi
reprovada. Sem isso, uma auditoria futura pode reusar o pack achando que é pedido pendente.

---

## 8. Erro de método a registrar

O `PRODUCTION_ASSET_PACK.md` pediu 16 assets finais de uma vez. A rota incumbente do
MARE_BRAVA gasta a metade dianteira do esforço antes de pedir qualquer asset final:
art bible → style manifest → model sheet → lineart → key poses → só então strips.

O pack pulou essa metade. Os checks mecânicos passaram (`active_technical_ok: 22,
blockers: 0`) e o resultado foi reprovado por tradução procedural — o padrão
`technical_pass_visual_fail` exato que o framework já sabe nomear.

**A lição não é "o Codex falhou".** É que um pedido de asset final sem model sheet
aprovado a montante não tem como acertar, independente do modelo que o atende.

---

## Verificação executada

| # | Verificação | Resultado |
|---|---|---|
| 1 | Todos os caminhos citados existem | 28/28 confirmados por script |
| 2 | Tabela da Seção 1 cobre 8 itens do §11 + 4 skills | 12 linhas |
| 3 | Nenhuma linha recomenda usar evidência negativa como fonte | confirmado |
| 4 | Nenhum uso de "provado/entregue/field-proven" fora de citação | ver Seção 4b, que usa `incumbente`/`candidato`/`parcial` |
| 5 | Seção 4b cita status literal, não paráfrase | valores extraídos por `json.load` dos próprios artefatos |
| 6 | `validate_skill_framework.py` | passa — `47 active, 13 legacy`, exit 0 |
| 7 | Nada em `tools/sgdk_wrapper/.agent/` foi tocado por este spike | confirmado: `find .agent -newermt "2026-08-07"` retorna vazio. **Ressalva:** `git status` mostra 31 arquivos modificados sob `.agent/` — eles são trabalho não commitado **anterior** a esta sessão, no branch `codex/canonical-skill-curation`, e não foram alterados aqui |

### Ressalva sobre a árvore de trabalho

Este spike foi escrito sobre um worktree com 378 arquivos não commitados, dos quais 31
estão sob `tools/sgdk_wrapper/.agent/` — incluindo `SGDK_GLOBAL.md`, `production-loop.md`,
`framework_manifest.json`, `skill_lifecycle_registry.json` e 8 SKILL.md de arte.

Nenhum deles foi alterado aqui, mas todos são anteriores e não commitados. Somado à
Seção 0, isto significa que **as citações `arquivo:linha` das Seções 1 e 3 descrevem uma
árvore que só existe nesta máquina.** A correção está registrada na Seção 0 e
endereçada pelo WI-00b da Seção 6.
