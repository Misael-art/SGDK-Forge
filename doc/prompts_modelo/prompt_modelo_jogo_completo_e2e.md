# Prompt Modelo — Jogo Completo E2E Multi-Agente

**versao:** 1.0.0
**ultima_incrementacao:** 2026-09-05
**natureza:** via OPCIONAL de utilizacao do framework `.agent` — nao altera modos de sessao, rotas existentes nem o foco canonico do agente
**fontes canonicas:** `AGENTS.md` (raiz) · `doc/prompts_modelo/prompt_modelo_direcionamento_projeto.md` · `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json` · `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json` · `tools/sgdk_wrapper/.agent/pipelines/quality_review_v1.json` · `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` (§16, §29, §30, §34, §38) · `tools/sgdk_wrapper/.agent/workflows/production-loop.md` · `tools/sgdk_wrapper/.agent/skills/operation/harness-orchestration/SKILL.md`

---

## 0. Natureza e escopo deste documento (via opcional)

Este arquivo define **uma via de ativacao** entre as varias que o framework
ja oferece (menu de sessao com 5 modos, `vibe-playable-loop`, direcionamento
externo via `prompt_modelo_direcionamento_projeto.md`, curadoria, laboratorio,
treino). Ele existe para o caso especifico: **um humano quer encomendar, em
uma unica mensagem, um jogo de Mega Drive real do zero, ponta a ponta, com
orquestracao multi-perspectiva e loop persistente ate o pacote de aceitacao.**

Regras de conviverio:

1. Nada aqui cria gate novo, script novo, tooling novo ou modo de sessao novo.
   Tudo o que este contrato manda fazer ja existe no framework; este documento
   apenas **ordena e pre-autoriza** a execucao continua.
2. Este contrato so entra em vigor quando um humano cola a Mensagem de
   Ativacao (Bloco 7) em uma sessao de agente. Sem essa mensagem, ele e apenas
   documentacao consultiva — o agente NAO deve inicia-lo por conta propria.
3. Ele nao restringe o agente: fora de uma sessao ativada por ele, todas as
   demais vias, modos e rotas do framework permanecem identicos.
4. Onde este documento e silencioso, valem `AGENTS.md` + `SGDK_GLOBAL.md` +
   `tools/sgdk_wrapper/.agent/` na hierarquia normal.

---

## 1. Bloco 0 — Pre-autorizacao humana (consentimento registrado)

A Mensagem de Ativacao carrega, de uma vez, o consentimento que o framework
exige ponto a ponto:

### 1.1 Modo de sessao

- `create_new_project` autorizado. O agente NAO precisa renderizar o menu de
  sessao; registra a abertura em `doc/agent_session_state.json` conforme
  `tools/sgdk_wrapper/.agent/workflows/agent-session-bootstrap.md`.

### 1.2 Trocas de perspectiva

- As 10 lentes (`director, architect, artist, hardware, coder, audio, qa,
  learner, curator, lab_operator`) sao autorizadas DENTRO deste projeto,
  sempre via `tools/sgdk_wrapper/.agent/workflows/perspective-switch-gate.md`
  com registro da transicao em `doc/agent_session_state.json`.
- A autorizacao NAO se estende a outros projetos nem a curadoria canonica
  (`tools/sgdk_wrapper/.agent/`, `tools/sgdk_wrapper/`, `doc/` do workspace).

### 1.3 Conceito autonomo

- Nome, genero e fantasia do jogo sao propostos pelo proprio agente na Fase 0
  via `planning/game-design-planning` (registry ids de genero opt-in respeitados)
  e registrados no GDD. **A execucao segue sem esperar aprovacao do conceito.**
- O humano pode vetar ou redirecionar a qualquer momento; veto humano vence
  este bloco.

### 1.4 Orcamento

- Preenchido na Mensagem de Ativacao (`{{BUDGET}}`) ANTES de iniciar
  (correcao 8 do `prompt_modelo_direcionamento_projeto.md`). Ao esgotar o
  orcamento, o agente para com estado honesto e handoff conforme
  `tools/sgdk_wrapper/.agent/workflows/handoff.md` — nunca com claim verde.

### 1.5 Pontos de PARADA obrigatoria (os unicos)

O loop roda sem perguntar, EXCETO nestes tres pontos, onde o agente para,
monta um pacote e aciona o humano:

| # | Parada | Gatilho | Pacote minimo |
|---|--------|---------|---------------|
| P1 | Aprovacao visual | laudo `out/logs/live_scene_bar_report.json` fechado para a primeira cena jogavel/signature | screenshot BlastEm + GIF de animacao + laudo + status honesto |
| P2 | Escuta de audio | banco de audio final integrado na ROM | WAVs/XGM2 fonte + evidencia de audio vivo na ROM (gate RMS da barra viva) |
| P3 | Promocao final | criterio de conclusao (Bloco 5) atingido | pacote de aceitacao completo do Bloco 5 |

Promocao de claim visual/sonoro/`ready_for_aaa` e sempre humana; aprovacao
humana de P1/P2 desbloqueia a continuacao, e P3 encerra a via.

### 1.6 Nao-retrocesso

- Vale para UM projeto novo por mensagem. Reusar em outro projeto exige nova
  Mensagem de Ativacao. Escopo-alvo travado: **micro-jogo completo VER.001** —
  titulo → 1 fase completa → boss → game over/continue.

---

## 2. Contrato do loop

### 2.1 Pipelines

- **Pipeline mestre do jogo:** `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json`
  (S0 abertura → S1 GDD/escopo → S2 TDD → S3 mecanica → S4 level → S5 enemy →
  S6 audio adaptativo → S7 `pipeline_call` da cena → S8 integracao → S9 closeout).
- **Pipeline por cena:** `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`
  (S0 escopo → S0b direcao de arte → S1 diagnostico → S1a/s1b/s1c sourcing,
  autoria e visual gate antecipado → S2 composicao → S2b direcao de cena →
  S3 traducao VDP → S4 excelencia → S5 budget → S6 runtime → S7 validacao →
  S8 QA/evidencia).
- Ordem dentro de cada cena:
  `tools/sgdk_wrapper/.agent/workflows/scene-direction-first.md` — roteiro →
  storyboard → coreografia → **medicao** → orcamento → contrato de asset →
  model sheet → assets → runtime → evidencia.

### 2.2 Persistencia e iteracao

- Loop de producao: `tools/sgdk_wrapper/.agent/workflows/production-loop.md`
  (etapas 0–5, nenhuma pulada).
- Continuidade ate entrega: `tools/sgdk_wrapper/.agent/workflows/causal-persistence-loop.md`.

### 2.3 Anti-thrash (SGDK_GLOBAL §16)

- Iteracao sem mudanca mensuravel em gate, artefato ou metrica e bloqueada
  pelo meaningful-change gate. "Trabalhei no problema" nao e mudanca.
- Toda falha passa por
  `tools/sgdk_wrapper/.agent/workflows/production-diagnostic-triage.md`
  (4 camadas independentes: host_executor, toolchain_wrapper, rom_runtime,
  creative_quality) ANTES de atribuir causa ou alterar codigo.

### 2.4 Escalada honesta

- O mesmo gate bloqueado **3 iteracoes seguidas** → blocker declarado com
  causa classificada, teto de claim rebaixado (SGDK_GLOBAL §29) e o trabalho
  continua nos ramos paralelizaveis. Blocker acumulado entra no pacote de
  aceitacao. **Nunca fingir verde para destravar o loop.**

### 2.5 Fechamento de iteracao

Toda iteracao termina com: build via wrapper → evidencia BlastEm selada por
hash da ROM → `doc/changelog/changelog.md` e `doc/10-memory-bank.md`
atualizados. Commit local a cada cena fechada.

---

## 3. Orquestracao multi-agente

### 3.1 Coordenador unico

- A lente `director` (persona `game-director-sgdk`) coordena: dono de escopo,
  claims, promocao, integracao Git e resposta humana. Nao existe segundo
  coordenador.

### 3.2 Ramos paralelos

- Tarefa com ≥2 ramos independentes (ex.: dois assets, level design e audio,
  arte e coreografia) passa pela skill `operation/harness-orchestration` via
  `python3 tools/sgdk_wrapper/harness_orchestration.py probe|plan` →
  `execution_mode` obrigatorio (`local` | `subagente_read_only` |
  `produtor_isolado`), com capsula de worker e resultado hash-bound conforme
  a skill.

### 3.3 Revisao independente

- `tools/sgdk_wrapper/.agent/pipelines/quality_review_v1.json` nos quatro
  checkpoints: **Q1** pos-GDD, **Q2** pos-audio, **Q3** vertical slice,
  **Q4** release candidate — ate 3 revisores read-only por checkpoint.
- Invariantes inegociaveis: `producer_cannot_approve_own_work`,
  `reviewers_are_read_only`, `quality_review_never_promotes_claims`.

### 3.4 Handoff

- Toda troca de lente registra handoff no schema minimo de
  `tools/sgdk_wrapper/.agent/workflows/handoff.md` (de, para, objetivo,
  entradas, saidas, status_por_eixo, bloqueios, proximo_gate).

---

## 4. Cobertura de capacidade — o "100%" mensuravel

"Usar 100% das capacidades" so e honesto como **cobertura de 100% das
capacidades aplicaveis, com exclusao declarada.** Antes de abrir arte/runtime
(Fase 0/1), o coordenador emite `doc/capability_coverage_plan.json` no projeto:

```json
{
  "schema": "capability_coverage_plan.v1",
  "project": "NOME [VER.001] [SGDK 211] [GEN] [GAME] [GENERO]",
  "skills": [
    {"skill_path": "planning/game-design-planning", "status": "planned", "phase": "F0", "note": ""},
    {"skill_path": "planning/fighting-game-design", "status": "not_applicable", "phase": "-", "note": "opt-in de outro genero"}
  ],
  "agents": [
    {"agent": "qa-hardware-tester", "status": "planned", "phase": "F2", "note": ""}
  ],
  "gates_and_tools": [
    {"tool": "tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py", "status": "planned", "phase": "F2", "note": ""}
  ]
}
```

Regras:

1. Toda skill ativa de `tools/sgdk_wrapper/.agent/skills/` aparece com status
   `planned` | `used` | `not_applicable`. `not_applicable` exige justificativa:
   opt-in de genero diverso do escolhido, gatilho da skill nao disparado pelo
   escopo, ou legado (`legacy/skills/`, `discoverable: false` — fora por regra
   do framework, nunca reativado aqui).
2. Os 10 agentes de `.agent/agents/` e os gates/ferramentas de medicao do
   wrapper tambem sao mapeados nas secoes `agents` e `gates_and_tools`.
3. No fechamento, skill `planned` que terminou sem `used` e sem justificativa
   atualizada = defeito de closeout declarado no pacote de aceitacao.
4. A auditoria do arquivo e do coordenador + revisor Q4 ( nao ha gate mecanico
   novo — gates novos sao proibidos nesta via, correcao 3 do prompt modelo).

---

## 5. Esqueleto de execucao E2E

### FASE -1 — Preparo do host (antes de qualquer projeto)

1. Preflight do host (`tools/sgdk_wrapper/preflight_host.ps1`; rota Linux:
   `tools/sgdk_wrapper/build.sh` com wine bridge).
2. Meta-gate de medicao: `python3 tools/sgdk_wrapper/validate_measurement_tools.py`.
3. Estado conhecido deste workspace: **17/18** (`validate_native_sprite_production.py`
   sem self-check + copias antigas de `runtime_probe`). Declarar o gap e o teto
   de claim decorrente — nenhum `ready_for_aaa` enquanto nao fechar. A remedicao
   e curadoria separada com aprovacao humana explicita e NAO faz parte desta via.
4. Ferramenta de medicao quebrada nao gera leitura em claim (SGDK_GLOBAL §34).

### FASE 0 — Abertura e contrato

1. `tools/sgdk_wrapper/new_project.sh "<nome>"` — nome conforme
   `doc/PADRAO_NOMENCLATURA.md`, validado por `validate_project_name.ps1`.
2. Classificar `doc/project_context_manifest.json` como `aaa_game`;
   `validate_project_context.ps1`; `validate_project_methodology.ps1`;
   `validate_project_hygiene.ps1`.
3. Conceito autonomo via `planning/game-design-planning` → GDD com escopo
   micro-jogo (titulo → 1 fase → boss → game over/continue), Route Decision
   Record, Identidade de Front-End; TDD (`planning/tdd-authoring`), `doc/13-spec-cenas.md`.
4. Emitir `doc/capability_coverage_plan.json` (Bloco 4).
5. Revisao Q1.

### FASE 1 — Chain de producao (production-loop etapa 1a)

TDD (`tdd_contract.json`) → mecanica (`design/systems-mechanics-validator`) →
level (`design/level-design-canonical`) → enemy roster
(`design/enemy-design-canonical`) → audio adaptativo
(`code/xgm2-audio-director`; `code/z80-pcm-custom-driver` se disparado).
**A etapa de arte so abre com o chain completo.**

### FASE 2 — Loop de cena (coracao da via)

Ordem de cenas do micro-jogo: `branding_sequence` → `front_end_main_menu` →
`first_playable_slice` (fase completa) → boss → `game_over/continue`.

Para cada cena, `aaa_scene_v1.json` S0–S8 na ordem `scene-direction-first`:

1. Storyboard com coordenadas em pixel; coreografia; **medicao antes da arte**:
   `vdp_scanline_simulator.py` (2 limites por scanline) +
   `audit_tile_residency.py` (residencia de tiles no asset).
2. Arte com proveniencia obrigatoria (`doc/asset_provenance_manifest.json`,
   `audit_procedural_asset_provenance.py`); protocolo de insatisfacao do
   `prompt_modelo_direcionamento_projeto.md` Bloco 3 (pisos numericos,
   minimo 3 rounds, crítico cego ≥ 8.5/10).
3. Runtime via `code/sgdk-runtime-coder`; build via wrapper;
   `validate_resources.ps1`.
4. Evidencia: `tools/sgdk_wrapper/capture_blastem_evidence_linux.sh` +
   `finalize_emulator_evidence.ps1` (selo por hash); `scene_closeout_gate.ps1`
   + `freshness_audit.ps1`.
5. **PARADA P1** ao fechar o laudo da primeira cena jogavel
   (`out/logs/live_scene_bar_report.json` conforme `doc/03_art/18_live_scene_bar.md`).
6. Reviews Q2/Q3 nos checkpoints; doutrina de audacia §30: medir o degrau
   seguinte antes de fechar budget; `unexploited_headroom` exige
   `headroom_justification`.

### FASE 3 — Fechamento

1. Integracao S8/S9 do pipeline mestre; audio final integrado → **PARADA P2**
   (escuta humana).
2. `tools/sgdk_wrapper/ci/run_golden_validate.ps1`;
   `tools/sgdk_wrapper/audit_promotion_claims.ps1`; freshness global.
3. `audit_project_learning.ps1 -Mode Capture`; changelog + memory bank;
   review Q4; auditoria do `capability_coverage_plan.json`.
4. Criterio de conclusao (Bloco 5) → **PARADA P3**.

---

## 6. Criterio de conclusao (definition of done do loop)

O loop declara trabalho concluido — e so para em P3 — quando TODOS os itens
sao verdadeiros:

1. Todas as cenas do escopo em `validado_budget` com evidencia BlastEm fresh
   (hash da ROM vigente confere; freshness sem drift).
2. Gate de entrega de 7 eixos verde (build, validation_report, boot BlastEm,
   gameplay basico, 60fps, audio, memory bank atualizado).
3. `doc/capability_coverage_plan.json` auditado: nenhuma skill `planned` sem
   `used` sem justificativa.
4. Q1–Q4 executados com reports hash-bound; revisor nunca foi o produtor.
5. Golden CI passa; `audit_promotion_claims.ps1` reconciliado; zero blockers
   nao-declarados.
6. Changelog, memory bank e aprendizado capturado.

Insatisfeito em qualquer item → o loop continua (ou para com handoff honesto
se o orcamento acabou). **`ready_for_aaa` nunca e auto-declarado**; e sempre
decisao do humano em P3, dentro do teto provado.

---

## 7. Gates anti-fraude e registro por iteracao

- Vocabulario de status do `AGENTS.md`; regra de ferro: "se nao foi visto
  rodando no emulador, nao existe".
- Claim ceiling (§29), self-check de medicao (§34), capacidade com prova (§38),
  adjetivo com piso numerico (§36), producao por degraus (§21).
- Proibido criar gate/harness artesanal dentro do projeto (correcao 3).
- Proibições de codigo do `AGENTS.md` (float, malloc, DMA fora do VBlank,
  API 1.60, pixel procedural em entrega) valem integralmente.
- Toda iteracao grava changelog + memory bank; aprendizado via
  `audit_project_learning.ps1 -Mode Capture` no fechamento.

---

## 8. Mensagem de ativacao (unico input humano obrigatorio)

Template — o humano preenche `{{BUDGET}}` e cola em uma sessao nova:

```
[Contexto MD Carregado] Ative a via opcional
doc/prompts_modelo/prompt_modelo_jogo_completo_e2e.md como contrato
operacional desta sessao, integralmente e sem pular etapas. Ele e uma via
entre varias; fora dele, o framework segue canonico.

PRE-AUTORIZACAO (Bloco 0 do contrato, concedida agora):
- Modo create_new_project autorizado; nao renderize o menu de sessao.
- Trocas de perspectiva entre as 10 lentes autorizadas dentro deste projeto,
  sempre via perspective-switch-gate com registro em doc/agent_session_state.json.
- Conceito do jogo (nome, genero, fantasia) proposto por voce na Fase 0 via
  planning/game-design-planning e registrado no GDD; NAO espere aprovacao
  para seguir. Veto humano pode chegar a qualquer momento.
- Orcamento: {{BUDGET}}
- Pontos de parada obrigatoria (os UNICOS em que voce para e me aciona):
  P1 aprovacao visual do laudo live_scene_bar da primeira cena jogavel;
  P2 escuta do audio final; P3 pacote de aceitacao no fechamento.
  Todo o resto roda em loop sem me perguntar.

ESCOPO-ALVO: micro-jogo completo VER.001 — titulo → 1 fase completa →
boss → game over/continue. Reconciliacao obrigatoria com
doc/prompts_modelo/prompt_modelo_direcionamento_projeto.md (8 correcoes +
prompt magico com pisos numericos).

INICIO IMEDIATO: Fase -1 (preflight + validate_measurement_tools.py; declare
o gap 17/18 e o teto de claim decorrente) → Fase 0 (new_project.sh,
classificacao aaa_game, validators, conceito, capability_coverage_plan.json)
→ Fase 1 (chain de producao) → Fase 2 (loop de cena) → Fase 3 (fechamento).
Pipeline mestre: tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json;
por cena: aaa_scene_v1.json. Multi-agente conforme Bloco 3 do contrato
(coordenador director + harness-orchestration + revisores read-only Q1-Q4).

REGRA DE FERRO: se nao foi visto rodando no emulador, nao existe. Cada
iteracao termina com build via wrapper, evidencia BlastEm selada por hash,
changelog e memory bank atualizados. ready_for_aaa nunca e auto-declarado.
```

Sugestao de `{{BUDGET}}` para sessao Codex continua:
`loop continuo ate o criterio de conclusao, commit local a cada cena fechada;
limite duro de 30 iteracoes sem fechar nenhuma cena = parada honesta com handoff`.

---

## 9. Anti-padroes

- iniciar esta via sem Mensagem de Ativacao explicita de um humano
- auto-aprovar conceito, arte, audio ou promocao de claim (P1–P3 existem para isso)
- pular Fase -1 ou rodar producao com ferramenta de medicao sem self-check declarado
- tratar "100% das capacidades" como usar tudo de uma vez; e cobertura com exclusao justificada
- gate/harness artesanal dentro do projeto
- loop que gira sem mudanca mensuravel (§16) ou que "finge verde" para avancar
- escopo maior que micro-jogo antes do primeiro fechamento completo (§30: degrau medido)
- alterar foco, modos ou curadoria canonica do framework em nome desta via

---

## 10. REGISTRO DE INCREMENTOS

Regras identicas ao `prompt_modelo_direcionamento_projeto.md` Bloco 5:
licao medida com fonte citada; +0.0.1 linha, +0.1.0 regra, +1.0.0 reescrita
aprovada por humano.

| Data | Fonte | Incremento | Evidencia |
|---|---|---|---|
| 2026-09-05 | auditoria de harmonizacao do workspace + inventario completo do framework `.agent` (48 skills ativas, 10 agentes, 46 workflows, 4 pipelines) | criacao do arquivo: via opcional E2E com pre-autorizacao P1–P3, loop game_production_v1 + aaa_scene_v1, orquestracao harness-orchestration + quality_review_v1, capability_coverage_plan.v1 | `tools/sgdk_wrapper/.agent/framework_manifest.json`; `doc/prompts_modelo/prompt_modelo_direcionamento_projeto.md`; estado 17/18 de `validate_measurement_tools.py` |
