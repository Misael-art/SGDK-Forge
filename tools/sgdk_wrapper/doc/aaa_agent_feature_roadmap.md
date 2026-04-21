# Roadmap Tecnico de Expansao do Ecossistema de Agentes AAA

**Data:** 2026-04-21  
**Alvo:** `F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper`  
**Publico:** agente de IA responsavel por implementar novas capacidades no ecossistema do wrapper  
**Status:** especificacao de handoff para implementacao incremental e segura

---

## 1. Objetivo

Este documento registra um plano tecnico para implementar cinco capacidades novas no ecossistema do `sgdk_wrapper`, sem regressao no comportamento atual do workspace.

Capacidades propostas:

1. capturador canonico de evidencia BlastEm
2. auditor de budget por frame/cena
3. runner deterministico de regressao por cena
4. inspector visual de VRAM/paleta/sprites
5. linter de contrato de cena

O foco nao e reescrever o wrapper atual. O foco e adicionar camadas novas de observabilidade, validacao e reproducibilidade sem degradar os fluxos existentes.

---

## 2. Regra Maxima de Preservacao

Esta regra e obrigatoria durante toda a implementacao:

- nenhuma feature nova pode quebrar, substituir ou alterar silenciosamente o comportamento atual de `build.bat`, `build_inner.bat`, `run.bat`, `validate_resources.ps1`, `run_runtime_capture.ps1`, `run_visual_capture.ps1` e `generate_scene_regression_report.ps1`
- nenhum gate novo entra como bloqueante por default
- nenhum formato antigo de artefato pode mudar sem compatibilidade explicita
- nenhum script novo pode editar `src/`, `res/`, `doc/` ou `out/rom.bin` sem o usuario pedir isso explicitamente
- toda feature nova deve comecar em modo observacao, depois `warn_only`, depois `opt_in_gate`, e so no fim considerar `required`
- se houver duvida entre avancar rapido e preservar estabilidade, preservar estabilidade vence

Se uma implementacao exigir mudar um contrato atual do wrapper, a implementacao deve parar e registrar a dependencia como decisao arquitetural pendente.

---

## 3. Estado Atual Confirmado

O ecossistema ja possui base forte nas areas abaixo:

- bootstrap e build resiliente
- migracao SGDK e correcoes operacionais
- validacao de recursos
- captura de runtime e evidencia parcial
- automacao basica de emulador
- governanca da `.agent`

Arquivos centrais que devem ser preservados:

- `tools/sgdk_wrapper/build.bat`
- `tools/sgdk_wrapper/build_inner.bat`
- `tools/sgdk_wrapper/run.bat`
- `tools/sgdk_wrapper/validate_resources.ps1`
- `tools/sgdk_wrapper/run_runtime_capture.ps1`
- `tools/sgdk_wrapper/run_visual_capture.ps1`
- `tools/sgdk_wrapper/generate_scene_regression_report.ps1`
- `tools/sgdk_wrapper/lib/blastem_automation.psm1`
- `tools/sgdk_wrapper/ensure_project_agent.ps1`

As features novas devem ser desenhadas para ampliar esse conjunto, nunca para substituir de imediato o que ja existe.

---

## 4. Estrategia Canonica de Implantacao

Toda feature nova deve seguir esta estrategia:

### 4.1 Fase 1 - Observacao

- implementa script novo
- gera artefato novo versionado
- nao bloqueia build nem validacao
- falha degrada para warning

### 4.2 Fase 2 - Integracao Opt-In

- script continua separado
- feature pode ser ligada por flag `SGDK_*`
- status vai para `out/logs`
- ainda sem bloquear por default

### 4.3 Fase 3 - Warning Operacional

- wrapper principal pode consumir o artefato
- problemas novos aparecem como warning
- ainda sem impedir entrega

### 4.4 Fase 4 - Gate Opt-In

- projetos laboratorio podem habilitar gate
- somente com evidencia de repetibilidade

### 4.5 Fase 5 - Gate Default

- so permitido apos validacao em varios projetos
- requer decisao explicita de manutencao do wrapper

---

## 5. Convencoes Obrigatorias para Novas Ferramentas

### 5.1 Versionamento de artefatos

Todo artefato novo deve conter:

- `schema_version`
- `generated_at`
- `tool_name`
- `tool_version`
- `project_root`
- `rom_sha256` quando houver relacao com runtime

### 5.2 Diretorios de saida

Usar apenas:

- `out/logs/` para JSON, TXT e relatarios tecnicos
- `out/evidence/` para capturas, dumps e derivados binarios
- `out/reports/` para HTML e relatorios humanos consolidados

### 5.3 Feature flags

Nao integrar comportamento novo sem flag explicita. Flags iniciais recomendadas:

- `SGDK_CAPTURE_CANONICAL_EVIDENCE=0|1`
- `SGDK_SCENE_CONTRACT_LINT=off|warn|error`
- `SGDK_SCENE_REGRESSION_RUNNER=0|1`
- `SGDK_SCENE_BUDGET_AUDIT=0|1`
- `SGDK_VDP_INSPECTOR=0|1`
- `SGDK_EXPERIMENTAL_TOOLS=0|1`

### 5.4 Politica de erro

- por default, falha em feature nova nao pode falhar o build principal
- erro bloqueante so pode existir se o projeto habilitar o gate correspondente
- toda falha deve registrar `failure_reason` detalhado no artefato JSON

---

## 6. Ordem Recomendada de Implementacao

Apesar da prioridade funcional pedida ser `1, 2, 3, 4, 5`, a ordem tecnica mais segura para codificacao e:

1. Prioridade 1 - capturador canonico de evidencia BlastEm
2. Prioridade 5 - linter de contrato de cena
3. Prioridade 3 - runner deterministico de regressao por cena
4. Prioridade 2 - auditor de budget por frame/cena
5. Prioridade 4 - inspector visual de VRAM/paleta/sprites

Justificativa:

- sem evidencia canonica confiavel, a regressao por cena continua fraca
- sem contrato de cena, o runner fica ambiguo
- sem runner e baseline, o auditor de budget perde contexto operacional
- sem dump e telemetria confiavel, o inspector VDP vira apenas estimativa superficial

---

## 7. Prioridade 1 - Capturador Canonico de Evidencia BlastEm

### 7.1 Objetivo

Gerar um pacote canonico, reproduzivel e validavel de evidencia de emulador para uma ROM especifica.

### 7.2 Problema atual

Existem evidencias parciais e dependencia de estado externo do sandbox, o que produz bloqueios como `missing_sandbox_root`, `session_not_captured` e `rom_identity_mismatch`.

### 7.3 Entregas novas

Arquivos sugeridos:

- `tools/sgdk_wrapper/capture_blastem_evidence.ps1`
- `tools/sgdk_wrapper/lib/blastem_evidence.psm1`
- `tools/sgdk_wrapper/schemas/blastem_evidence.schema.json`

Artefatos gerados:

- `out/logs/blastem_evidence.json`
- `out/evidence/blastem/screenshot.png`
- `out/evidence/blastem/save.sram`
- `out/evidence/blastem/visual_vdp_dump.bin`
- `out/evidence/blastem/session_manifest.json`

### 7.4 Contrato de entrada

- ROM em `out/rom.bin`
- caminho do BlastEm resolvido via `env.bat`
- parametros opcionais de timeout, warmup e destino de evidencia

### 7.5 Contrato de saida

Campos minimos do JSON:

- `schema_version`
- `generated_at`
- `project_root`
- `rom_path`
- `rom_sha256`
- `emulator_path`
- `capture_mode`
- `session_started`
- `session_completed`
- `screenshot_present`
- `sram_present`
- `vdp_dump_present`
- `evidence_status`
- `failure_reason`

### 7.6 Integracao segura

- primeira versao deve rodar manualmente, sem tocar em `run.bat`
- segunda versao pode ser chamada por flag em `run.bat`
- consumo por `validation_report` so depois de repetibilidade comprovada

### 7.7 Riscos

- automacao de foco de janela no Windows
- tempo de boot nao deterministico
- variacao de sandbox do BlastEm
- arquivo SRAM vindo de sessao anterior

### 7.8 Mitigacoes

- usar pasta canonica isolada para evidencia
- validar `rom_sha256`
- usar retries e timeout configuravel
- sempre escrever manifesto da sessao

### 7.9 Criterio de aceite

- 10 execucoes sequenciais no mesmo projeto produzem o mesmo conjunto de artefatos esperados
- a feature desligada nao altera o comportamento de `run.bat`

### 7.10 Viabilidade honesta

Alta. Esta e a feature com melhor relacao entre valor e risco, desde que reaproveite a automacao BlastEm ja existente.

---

## 8. Prioridade 5 - Linter de Contrato de Cena

### 8.1 Objetivo

Formalizar o contrato declarativo de cada cena para reduzir ambiguidade entre docs, codigo, captura e gates.

### 8.2 Entregas novas

Arquivos sugeridos:

- `tools/sgdk_wrapper/lint_scene_contract.ps1`
- `tools/sgdk_wrapper/schemas/scene_contract.schema.json`
- `tools/sgdk_wrapper/schemas/scene_contract_report.schema.json`

Manifesto por projeto:

- `doc/scene-contracts.json`

Artefato:

- `out/logs/scene_contract_report.json`

### 8.3 Campos minimos por cena

- `scene_id`
- `scene_role`
- `boot_mode`
- `capture_frame`
- `warmup_frames`
- `required_assets`
- `visual_priority`
- `palette_policy`
- `budget_profile`
- `effects_active`
- `cleanup_required`
- `regression_required`

### 8.4 Regras do linter

- manifesto precisa ser valido contra schema
- cenas criticas precisam declarar baseline de regressao
- cena com FX temporal precisa declarar `warmup_frames`
- cena que altera estado visual precisa declarar cleanup
- assets declarados precisam existir

### 8.5 Integracao segura

- iniciar em modo `warn`
- nao obrigar retroativamente todos os projetos
- permitir perfis `lab`, `production` e `aaa_gate`

### 8.6 Criterio de aceite

- o manifesto e simples o bastante para ser mantido
- o relatorio ajuda o runner de regressao e o auditor de budget

### 8.7 Viabilidade honesta

Alta. E a feature mais barata e ajuda a estabilizar as demais.

---

## 9. Prioridade 3 - Runner Deterministico de Regressao por Cena

### 9.1 Objetivo

Executar cenas declaradas, capturar evidencia e comparar com baseline de forma repetivel.

### 9.2 Entregas novas

Arquivos sugeridos:

- `tools/sgdk_wrapper/run_scene_regression.ps1`
- `tools/sgdk_wrapper/lib/scene_regression.psm1`
- `tools/sgdk_wrapper/schemas/scene_regression.schema.json`

Manifesto por projeto:

- `doc/scene-regression.json`

Artefatos:

- `out/logs/scene_regression_report.json`
- `out/logs/scene_regression_matrix.json`
- `out/evidence/scenes/<scene_id>/...`

### 9.3 Dependencia tecnica critica

O jogo precisa oferecer entrada deterministica para a cena. Sem isso, o runner host nao sera realmente confiavel.

Contratos aceitos de bootstrap:

- menu debug
- `scene_id` persistido em SRAM
- build variant de laboratorio
- bootstrap por flag de runtime

### 9.4 Comparadores necessarios

- hash exato
- diff tolerante de imagem
- diff de dump VDP
- diff de paleta

### 9.5 Integracao segura

- fase 1 com uma unica cena piloto
- suportar status `passed`, `failed`, `missing`, `stale`, `unsupported`
- nao bloquear projetos que ainda nao tenham bootstrap deterministico

### 9.6 Riscos

- cenas dependentes de input humano
- random nao seedado
- animacao nao estabilizada no frame de captura

### 9.7 Mitigacoes

- seed fixa quando possivel
- `warmup_frames`
- checkpoints declarados por cena

### 9.8 Criterio de aceite

- mesma ROM e mesma cena geram evidencia equivalente em repeticoes controladas

### 9.9 Viabilidade honesta

Alta, desde que seja aceito um contrato de bootstrap deterministico de cena no runtime.

---

## 10. Prioridade 2 - Auditor de Budget por Frame/Cena

### 10.1 Objetivo

Consolidar metrica real ou explicitamente inferida de custo por frame e por cena.

### 10.2 Entregas novas

Arquivos sugeridos:

- `tools/sgdk_wrapper/audit_scene_budget.ps1`
- `tools/sgdk_wrapper/merge_scene_budget_metrics.ps1`
- `tools/sgdk_wrapper/schemas/scene_budget.schema.json`

Artefatos:

- `out/logs/scene_budget_report.json`
- `out/logs/scene_budget_summary.md`

### 10.3 Metricas desejadas

- `scene_id`
- `frame_number`
- `dma_bytes_requested`
- `dma_ops`
- `sprite_count`
- `max_sprites_per_scanline`
- `pal_changes`
- `tile_stream_updates`
- `vram_usage_estimate`
- `cpu_frame_overrun_flag`
- `measurement_origin`

### 10.4 Dependencia tecnica critica

Se o runtime nao emitir dados suficientes, o auditor sera parcial. Nao fingir precisao que ainda nao existe.

Classificar cada campo como:

- `measured`
- `estimated`
- `inferred`

### 10.5 Estrategia segura

- fase 1: consolidar `runtime_metrics.json` atual
- fase 2: desenhar schema de telemetria in-game
- fase 3: instrumentar projeto laboratorio com `#ifdef SGDK_TELEMETRY`
- fase 4: calibrar thresholds por cena

### 10.6 Restricoes de runtime

- nada de `malloc`
- buffers estaticos
- impacto minimo no frame
- telemetria desligada por default

### 10.7 Criterio de aceite

- overhead da telemetria e conhecido
- o relatorio deixa claro o que foi medido e o que foi inferido

### 10.8 Viabilidade honesta

Media-alta. E viavel, mas depende de instrumentacao leve no codigo do jogo e disciplina de schema.

---

## 11. Prioridade 4 - Inspector Visual de VRAM/Paleta/Sprites

### 11.1 Objetivo

Gerar um relatorio visual e tecnico do uso do VDP por cena.

### 11.2 Entregas novas

Arquivos sugeridos:

- `tools/sgdk_wrapper/inspect_vdp_scene_state.ps1`
- `tools/sgdk_wrapper/render_vdp_inspection_report.py`
- `tools/sgdk_wrapper/schemas/vdp_inspection.schema.json`

Artefatos:

- `out/logs/vdp_inspection.json`
- `out/reports/vdp_inspection.html`
- `out/evidence/vdp/*.png`

### 11.3 Dados alvo

- ocupacao de tiles
- distribuicao de paletas
- sprites ativos
- hotspots por scanline
- separacao entre `BG_A`, `BG_B` e `WINDOW`
- reuse e duplicacao de tiles

### 11.4 Dependencias tecnicas

- dump VDP confiavel da prioridade 1
- idealmente contexto de runtime da prioridade 2

### 11.5 Integracao segura

- comecar como ferramenta read-only
- sem gate no build
- relatorio humano antes de qualquer politica automatica

### 11.6 Riscos

- dump VDP dificil de interpretar
- alto custo de transformar dado bruto em relatorio util

### 11.7 Criterio de aceite

- o relatorio ajuda decisoes de arquitetura visual de verdade
- nao apenas exibe bytes e tabelas incompreensiveis

### 11.8 Viabilidade honesta

Media. E possivel, mas depende mais de engenharia de introspecao e UX tecnica do que de script puro.

---

## 12. Cronograma Recomendado

### Sprint 0 - Fundacao

- criar schemas JSON base
- criar convencao de flags
- criar helper de validacao de artefatos
- nao tocar em gates existentes

### Sprint 1 - Prioridade 1 Base

- manifesto de evidencia BlastEm
- captura de screenshot
- captura de SRAM
- status padronizado de sessao

### Sprint 2 - Prioridade 1 Consolidada + Prioridade 5

- dump VDP
- validacao de repetibilidade
- schema e linter de contrato de cena

### Sprint 3 - Prioridade 3 Piloto

- manifesto de regressao por cena
- runner de 1 cena
- comparador basico

### Sprint 4 - Prioridade 3 Consolidada + Prioridade 2 Fase 1

- runner multi-cena
- consolidacao de metrica existente
- relatorio inicial de budget

### Sprint 5 - Prioridade 2 Fase 2

- instrumentacao runtime opt-in
- thresholds de cena
- classificacao `measured/estimated/inferred`

### Sprint 6 - Prioridade 4 Fase 1

- parser de dump VDP
- relatorio visual basico
- visualizacao de paleta e tiles

---

## 13. Matriz de Risco

| Risco | Severidade | Probabilidade | Mitigacao |
|---|---|---:|---|
| gate novo bloquear projeto antigo | alta | media | manter `warn_only` por default |
| evidencia BlastEm nao deterministica | alta | media | seed, warmup, timeout, sandbox isolado |
| telemetria runtime afetar performance | alta | media | `#ifdef`, buffers estaticos, counters minimos |
| schema de cena burocratico demais | media | media | campos minimos + perfis de rigidez |
| inspector VDP entregar pouca utilidade pratica | media | media | comecar pequeno e validar com casos reais |

---

## 14. Definicao de Pronto

### 14.1 Pronto por feature

Uma feature so pode ser considerada pronta quando:

- possui schema versionado
- possui artefato de saida estavel
- possui modo desligado sem impacto no fluxo atual
- possui teste em pelo menos um projeto laboratorio
- nao introduz regressao nos wrappers atuais

### 14.2 Pronto para integracao no wrapper principal

Uma feature nova so entra no wrapper principal quando:

- repetibilidade foi confirmada
- falhas conhecidas estao documentadas
- existe flag de desligamento
- passou por pelo menos um projeto simples e um projeto complexo

---

## 15. Instrucao Final ao Agente Implementador

Ao implementar qualquer item deste roadmap:

1. nao altere o comportamento atual por default
2. crie a nova ferramenta como script isolado primeiro
3. gere artefato novo e versionado
4. integre por flag
5. trate falhas novas como warning nas fases iniciais
6. so proponha gate depois de provar repetibilidade

Se surgir qualquer necessidade de quebrar um contrato atual do wrapper, pare e registre isso como decisao arquitetural pendente, em vez de improvisar.

---

## 16. Veredito Tecnico

E possivel implementar as cinco propostas com seguranca, mas nao todas ao mesmo tempo e nao como gates obrigatorios desde o inicio.

Julgamento honesto:

- capturador canonico de evidencia BlastEm: viabilidade alta
- linter de contrato de cena: viabilidade alta
- runner deterministico de regressao por cena: viabilidade alta com bootstrap de cena
- auditor de budget por frame/cena: viabilidade media-alta com telemetria leve
- inspector visual de VRAM/paleta/sprites: viabilidade media

O ponto critico para dar certo nao e ambicao tecnica. O ponto critico e disciplina de preservacao.

Se a regra maxima de preservacao for respeitada, o roadmap e seguro e realista.
