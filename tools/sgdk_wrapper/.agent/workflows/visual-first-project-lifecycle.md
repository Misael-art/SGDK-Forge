# Workflow: Visual-first Project Lifecycle

Use este workflow quando um projeto `aaa_game`, vertical slice, reseed ou
retomada de projeto estiver travando em qualidade visual, assets procedurais,
runtime seed repetido ou diagnostico caro.

Este workflow nao substitui `production-loop.md`; ele e um gate de rota para
decidir quando o agente pode sair de planejamento/arte e entrar em runtime.

## 1. Iniciar

Antes de qualquer runtime de entrega:

- validar `doc/project_context_manifest.json`;
- validar `doc/project_methodology_manifest.json`;
- validar `doc/project_hygiene_manifest.json`;
- ler `doc/10-memory-bank.md`, `doc/11-gdd.md` e `doc/13-spec-cenas.md`;
- executar `audit_project_learning.ps1 -Mode Audit` e consultar apenas o indice
  compacto;
- emitir ou atualizar `route_decision_record` com modo `visual_first` quando a
  entrega depender de arte, front-end, personagem, cena assinatura, cutscene,
  HUD heroico ou identidade de marca.
- ler `tools/sgdk_wrapper/.agent/references/production_visual_quality_contract.md`; para qualquer arte de
  producao, exigir uma `quality_reference_board` local e aprovada para os papeis
  que serao promovidos.

Passa quando:

- o projeto sabe se e jogo, demo, treino, laboratorio ou smoke;
- a primeira fatia jogavel tem promessa visual, mecanica, audio, risco,
  evidencia e bloqueios declarados;
- nenhum benchmark, mockup, PNG procedural ou tela textual esta sendo tratado
  como fonte final.
- a referencia de qualidade foi definida sem virar fonte para copia, e nenhum
  asset recebe avaliacao positiva apenas por ser melhor que um placeholder.

## 2. Analisar

Classifique o estado real antes de propor trabalho:

- `visual_first_ready_for_translation`: fonte premium, aprovacao humana e gate
  de direcao existem, mas falta conversao VDP/budget/runtime;
- `technical_runtime_creative_blocked`: ROM ou rota existe, mas arte, identidade,
  animacao, audio ou direcao visual seguem bloqueados;
- `lab_evidence_not_delivery`: demo ou treino provou tecnica, mas nao entrega;
- `smoke_only`: build/boot existe para validar estrutura, nao qualidade;
- `unclassified_or_degraded`: faltam contexto, metodologia, higiene ou memoria.

Regra:

- O padrao positivo de rota visual-first exige direcao, fonte e bloqueio de
  runtime antes do build final.
- Runtime tecnico com placeholder pode ser valioso como smoke, mas nao deve
  continuar consumindo ciclos se o blocker dominante e `visual_gate_blocked`.

## 3. Amadurecer

Quando o blocker dominante for visual, a proxima acao deve atacar exatamente
um destes pontos:

- fonte premium local em `data/source_art/` com manifesto, autoria, licenca,
  hash e papel no jogo;
- `human_approval_record.md` ou painel de aprovacao visual imutavel;
- `art_gameplay_direction_gate` com GDD/spec, camera, interacoes, identidade e
  `must_preserve`;
- `premium_source_manifest` com `production_source_ready=true`;
- conversao VDP real para `res/` com diagnostico de asset, budget e match;
- `visual_delivery_gate_report` medido;
- evidencia BlastEm da mesma ROM quando a arte ja entrou no runtime.

Nao passa quando:

- a mudanca e apenas novo build, novo screenshot, novo texto ou refresh de
  report sem remover blocker visual;
- o asset critico e `procedural_renderer`, `debug_lab`, `placeholder`,
  `needs_review`, `rework`, `benchmark-derived` ou `perceptual_quality=nao_medido`;
- o runtime usa `VDP_drawText`, painel ASCII, nomes de efeito ou fallback
  generico como experiencia final.

## 4. Revisar

Revise por eixos separados:

- `technical_runtime`: build, cena, input, performance e crash;
- `visual_direction`: identidade, fonte, gate humano, coesao e assinatura;
- `vdp_budget`: VRAM, CRAM, DMA, sprites/scanline e fallback;
- `game_design`: loop, risco, agencia, feedback, level design e telegraph;
- `animation`: timing, spacing, pivots, contato, motion GIF/WebP e leitura;
- `evidence`: BlastEm, SRAM, screenshot, VDP dump, freshness e scene closeout.

O menor eixo define o status maximo do projeto.

## 5. Concluir

Antes de declarar `pronto`, `AAA`, `stable`, `release`, `validado_budget` ou
`ready_for_aaa`:

- `validation_report.blocking_statuses` deve estar vazio para o escopo;
- `scene_closeout_gate_report.json` e `freshness_audit_report.json` devem estar
  frescos;
- `visual_delivery_gate_report.json` deve ser canonico e medido;
- a evidencia BlastEm deve apontar para a mesma ROM e cena;
- `doc/10-memory-bank.md` e `doc/changelog/changelog.md` devem refletir o mesmo
  estado;
- o projeto nao pode estar em `lab_not_delivery`, `smoke_only` ou
  `technical_runtime_creative_blocked`.

Se qualquer eixo falhar, conclua com o status honesto e volte para a etapa dona
do blocker.

## Handoff

- Para fonte/arte: `art/visual-excellence-standards` e
  `art/art-translation-to-vdp`.
- Para composicao: `art/multi-plane-composition`.
- Para budget: `hardware/megadrive-vdp-budget-analyst`.
- Para runtime: `code/sgdk-runtime-coder` somente depois de rota visual
  suficiente.
- Para evidencia: `operation/emulator-vdp-evidence-curator`.
