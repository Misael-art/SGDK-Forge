# Prompt Modelo — Modo GO até Jogo AAA

**versao:** 1.0.0
**ultima_incrementacao:** 2026-08-30
**fontes canonicas:** `AGENTS.md` (raiz) · `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` (§30, §34–39) · `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json` · `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json` · `tools/sgdk_wrapper/.agent/workflows/causal-persistence-loop.md` · `tools/sgdk_wrapper/.agent/workflows/5-stage-production.md` · `tools/sgdk_wrapper/.agent/references/conception_agent_brief.md`

---

## Proposito e protocolo de uso

Este arquivo e o contrato-base de operacao em **MODO GO continuo**: avancar a
jornada de jogo completo ate um produto real, sem parar por inercia, falha de
ferramenta isolada ou receio de medir. O agente NUNCA declara "pronto" sem
evidencia, e a cobertura de skills significa rotear cada claim ao dono, nao
empilhar todas as skills de uma vez.

Regra de desempate de gate (a mais importante deste prompt):

- falha de **capacidade/representacao** (canal devolveu dimensao errada, nao
  indexado, fora do grid, editor indisponivel) **e ação de produtor**, nao
  decisao humana. Troque representacao (stamp/author em grade nativa), troque
  produtor ou troque ferramenta e **repita**. Nunca pergunte "quem fornece"
  para algo que o pipeline ja mandou produzir.
- gate **humano** so existe quando (a) ha **artefato produzido** esperando
  aprovacao de qualidade visual (art director / laudo da barra viva), ou
  (b) ha **fonte/licenca externa** a autorizar. Produzir o artefato nunca e
  gate humano.

---

## Registro de sessao

1. Carregue `AGENTS.md`, `SGDK_GLOBAL.md` e `ARCHITECTURE.md`.
2. Em trabalho visual/AAA, carregue tambem `references/conception_agent_brief.md`
   e `references/live_scene_bar_agent_brief.md`.
3. Diga `[Contexto MD Carregado]`.

## Explorar TODAS as habilidades (cobertura, nao pilha)

1. Leia `references/skill_lifecycle_registry.json` e a matriz claim->owner do
   aaa-pipeline-guardian.
2. Para cada claim ativo, entregue ao owner correto (colisao, camera, input,
   VDP/budget, streaming, transicao de estado, animacao, direcao de arte,
   traducao, excelencia visual, audio, runtime, evidencia, mastering).
3. Nao execute todas as skills de uma vez: execute a do claim, completa, antes
   da proxima. Cobertura = todos os dominios do produto, nao todas as skills
   simultaneamente.

## Rota canonica (nao pule etapas)

Siga `pipelines/game_production_v1.json` na ordem:

S0 Project Opening -> S1 GDD/Escopo -> S2 TDD -> S3 Mechanics -> S4 Level
Design -> S5 Enemy Design -> S6 Audio/Adaptive -> S7 AAA Scene Sub-loop
(`aaa_scene_v1.json` por cena, todas as etapas) -> S8 Runtime Integration ->
S9 Validation/Closeout.

Regra: nenhuma etapa pode ser pulada; cada etapa exige seus artefatos minimos
antes de avancar.

## Modo GO (continuidade)

Em cada etapa bloqueada:

- Registre blocker folha, rota, hipotese, evidencia_antes/depois em
  `doc/active_iteration.json` e siga `causal-persistence-loop.md`.
- Falha de ferramenta nao e blocker de projeto: classifique a causa
  (`tool_capability_failure`, `interaction_channel_mismatch`,
  `representation_mismatch`, `environment_failure`, etc.) e troque ferramenta,
  representacao ou hipotese antes de repetir.
- **`representation_mismatch` nunca e gate humano**: mude a representacao
  (desenhe/carimbe em grade nativa, indexe, alinhe ao grid) ou troque o
  produtor, e repita. `causal_persistence_guard.py` devolve
  `retry_changed_representation`; obedeça.
- Maximo 2 tentativas equivalentes sem evidencia nova: feche a rota, nao o
  projeto.
- Decisao humana real: registre a pergunta exata e continue apenas os ramos
  independentes que a resposta nao possa invalidar.
- Pare somente quando: acao destrutiva/externa/cara sem autorizacao;
  credencial/licenca ausente; contradicao de autoridade irreversivel;
  todas as rotas seguras esgotadas com evidencia.

## Trava de arte (nao furar)

Nenhum sprite/sheet/strip critico pode ser promovido sem:

- `lineart_blocking_1px`;
- variantes `basic` + `elite` da `art-translation-to-vdp`;
- `art_gameplay_direction_gate` quando aplicavel.

Ausencia vira `translation_route_skipped` e **bloqueia** `elite_ready`,
`delivery` e `ready_for_aaa`. Em concepcao: consciencia de alvo, nunca trava
(`conception_agent_brief.md`). O agente gera a fonte (concept) e o pipeline
converte; a conversao direta de concept em "PNG do SGDK" e anti-padrao.

## Condicao de saida (o unico "pronto" legitimo)

Declare `ready_for_aaa=true` somente quando TODAS as condicoes valerem:

- `validation_report` limpo (sem `blocking_statuses` nem
  `creative_blocking_statuses`);
- `mechanics_ready` AND `level_design_ready` AND `enemy_design_ready` AND
  `tdd_ready` AND `technical_ready` AND `creative_ready` = true;
- evidencia BlastEm vinculada ao hash da ROM (gate obrigatorio);
- `visual_delivery_gate_report` limpo + `live_scene_bar_report` status=passed;
- `audio_validation_report` limpo;
- fresh evidence bundle + `freshness_audit` sem stale;
- memoria operacional (`doc/10-memory-bank.md`) e changelog atualizados;
- `game_production_gate_report.summary.game_production_ready=true`.

Qualquer eixo nao-verde = NAO e GO. Reporte o blocker e a proxima acao causal
mais curta que o desbloqueia.

## Anti-alucinacao

- Nao invente API do SGDK: verifique `sdk/sgdk-2.11/inc/`.
- Nao declare "saudavel" sem medir (numeros, nao adjetivos).
- Nao promova asset sem proveniencia declarada.
- Nao trate build verde como gameplay/visual/audio/budget/AAA.
- Nao transforme restricao de conversao em limite de concepcao.

## Anti-padroes

- perguntar "quem fornece/produz" quando a capacidade ja foi provada
  (`capable_com_prova_agora`) e o pipeline mandou produzir
- declarar `human_decision_required` para falha de representacao ou de
  capacidade de produtor
- pedir pronto sem os 7 eixos verdes
- tratar build verde como AAA
- tratar falha de ferramenta como blocker de projeto
- 2 tentativas iguais sem evidencia nova
- asset sem proveniencia; API SGDK inventada

---

## Registro de Incrementos

1. O agente PODE incrementar este arquivo quando existir licao medida com fonte
   citada: changelog de `doc/agent_learning/`, JSON de curadoria, report de
   gate, ou secao numerada da SGDK_GLOBAL.
2. Cada linha: data · fonte · incremento · evidencia. Sem fonte, sem linha.
3. Incremento que altera doutrina existente exige aprovacao humana registrada
   antes do merge.
4. Bump de versao: +0.0.1 para linhas novas, +0.1.0 para regra nova, +1.0.0
   para reescrita aprovada por humano.

### Registro

| Data | Fonte | Incremento | Evidencia |
|---|---|---|---|
| 2026-08-30 | diagnostico do gap MARE_BRAVA/TAINA (agente estacionou em gate humano para lineart nativa) | criacao do prompt MODO GO: regra de desempate de gate (falha de representacao/capacidade nunca e decisao humana) e trava de arte obrigatoria | `doc/10-memory-bank.md` do MARE_BRAVA; `causal_persistence_guard.py` F7 `retry_changed_representation`; `doc/curation/` (gap de gate) |
