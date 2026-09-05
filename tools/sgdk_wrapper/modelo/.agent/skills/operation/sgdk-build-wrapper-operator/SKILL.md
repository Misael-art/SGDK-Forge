---
name: sgdk-build-wrapper-operator
description: Operacao segura do wrapper central SGDK, layouts de projeto, bootstrap da .agent e continuidade entre build, changelog e memoria operacional.
---

# SGDK Build Wrapper Operator

Use esta skill ao tocar qualquer arquivo em `tools/sgdk_wrapper/` ou ao diagnosticar build, run, clean ou rebuild.

## Principios

- o wrapper central e a fonte unica de logica compartilhada
- wrappers locais dos projetos devem continuar finos
- o manifesto resolve layout e policy
- UGDM/build significa o fluxo real `.res`/ResComp/wrapper/validate/evidencia; build limpo nao substitui budget de residencia e DMA
- a `.agent` local nao pode ser tratada como saudavel se faltar contexto canonico critico
- `doc/changelog` e parte do fluxo operacional, nao pos-processo opcional
- freshness de evidencia e parte do fluxo operacional: depois de nova ROM, captura ou contrato, rode `freshness_audit.ps1`
- fechamento de cena deve preferir `scene_closeout_gate.ps1` para evitar sequencias manuais incompletas
- `ci_gate_report` ou `local_ci_gate_report` e parte do fechamento AAA/stable/release; ausencia de GitHub Actions nao bloqueia prototipo, mas bloqueia declarar pipeline AAA-grade sem substituto local
- `prd_readiness_report` e o preflight de autonomia: ele diz se o agente tem autoridade documentada antes de produzir arte/runtime
- a rota de build e escolhida pelo host e pela proveniencia LTO, nunca pelo nome
  do projeto nem por tentativa e erro no link

## Roteamento obrigatorio por host

Antes do primeiro build da sessao, execute:

```text
python tools/sgdk_wrapper/select_sgdk_build_route.py \
  --repo-root <workspace> \
  --project-root <projeto> \
  --output <projeto>/out/logs/sgdk_build_route_report.json
```

O report e a autoridade para escolher a rota:

| Host | Rota canonica | Regra |
|---|---|---|
| Linux | `build_sgdk_wine_bridge.sh --project-root <projeto>` | usa staging isolado do SDK, wrappers Wine e `libmd.a` reconstruida sem LTO; nunca altera a biblioteca canonica de origem |
| Windows | `build.bat <projeto>` | usa o wrapper batch e o SDK canonico; bloqueia antes do build se `gcc.exe` e `libmd.a` LTO tiverem majors diferentes |

Regras de ferro:

- se o seletor retornar `blocked`, nao editar C, `.res` ou assets para
  "consertar" toolchain;
- no Linux, nao chamar o `.bat` do projeto, nao usar PowerShell sob Wine e nao
  linkar diretamente a `libmd.a` canonica quando
  `direct_link_compatible=false`;
- no Windows, nao usar a bridge Linux como atalho: restaurar ou reconstruir a
  `libmd.a` com o mesmo compilador empacotado no SDK;
- ResComp e compilacao C aprovados seguidos de falha no link classificam o
  incidente como `toolchain_wrapper` ate prova contraria;
- sucesso do build limita o status a `buildado_emulator_pending`; somente
  evidencia nova da ROM no BlastEm permite `testado_em_emulador`.

## Jornada AAA cena (ordem obrigatoria)

1. `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`
2. `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`
3. `tools/sgdk_wrapper/.agent/workflows/production-loop.md`

Nao declarar barra AAA nem tile budget `cabe` sem passar por `skills/hardware/megadrive-vdp-budget-analyst` depois da arte definida.

## Contrato Operacional

### Entrada minima

- raiz do projeto
- manifesto resolvido
- wrapper central disponivel

### Saida minima

- contexto do projeto resolvido
- bootstrap da `.agent` auditado
- build e validacao executados no wrapper central
- `doc/changelog` atualizado quando houver novo asset ou nova ROM
- `out/logs/freshness_audit_report.json` quando houver evidencia previa ou fechamento
- `out/logs/scene_closeout_gate_report.json` quando uma cena for declarada fechada
- `ci_gate_report` ou `local_ci_gate_report` quando houver alegacao AAA/stable/release
- `out/logs/prd_readiness_report.json` antes de arte/runtime em projeto novo ou escopo reseed
- `qa_emulator_report.json`, `softlock_detection_report.json` e `runtime_fuzz_report.json` quando houver QA de entrega ou gate operacional novo
- input de emulador em JSON validavel por `tools/sgdk_wrapper/schemas/blastem_input_script.schema.json` quando a navegacao for roteirizada

### Passa quando

- o projeto nao esta em contexto degradado silencioso
- a ROM, o changelog e a memoria operacional apontam para o mesmo estado
- para AAA/stable/release, preflight, testes CI locais/host, validator, mastering e code review foram registrados; se GitHub Actions/pre-commit/make paralelo/debug symbols nao existirem, status de pipeline fica `pipeline_gate_partial`
- a automacao BlastEm usa exclusivamente `tools/sgdk_wrapper/lib/blastem_automation.psm1`
- logs do emulador ficam em JSONL sob `out/logs/*_blastem.log`
- artefatos de SRAM/screenshot ficam confinados a `out/blastem_env_*`
- no Windows, o sandbox BlastEm precisa espelhar `Home/AppData/Local` e o `blastem.cfg` efetivo deve nascer nesse ramo
- `qa_emulator_report.rom_sha256` aponta para a ROM testada e fica stale se houver rebuild posterior
- scripts de entrada BlastEm usam `press_until_ready` quando o heartbeat `READY` existir

### Handoff para proxima etapa

- entregar `validation_report.json`, `doc/changelog` e `doc/10-memory-bank.md` coerentes para o fechamento de QA
- em fechamento de cena, entregar tambem `scene_closeout_gate_report.json` e `freshness_audit_report.json`

## Checklist

- executar `tools/sgdk_wrapper/preflight_host.ps1` antes do primeiro build da sessao
- executar `tools/sgdk_wrapper/select_sgdk_build_route.py` e obedecer
  `selected_route`, `blockers` e `source_library.direct_link_compatible`
- executar `tools/sgdk_wrapper/check_prd_readiness.ps1` apos bootstrap/reseed de escopo; para AAA/stable/release, blocker nesse report impede fechar entrega
- quando o objetivo for AAA/stable/release, gerar `local_ci_gate_report` conforme `tools/sgdk_wrapper/schemas/local_ci_gate_report.schema.json`, com preflight, testes `ci/*.ps1` relevantes, validadores, code review e mastering; nao tratar build manual como CI
- confirmar `MD_ROOT`, `GDK` e `SGDK_EMULATOR_PATH`
- resolver contexto do projeto via manifesto ou heuristica controlada
- em projeto novo, garantir que `doc/11-gdd.md` ou `doc/13-spec-cenas.md` declarem `ui_decision_card` para qualquer UI formal antes do runtime
- em projeto novo, garantir que `doc/13-spec-cenas.md` declare `scene_transition_card` para qualquer transicao formal antes de arte/runtime
- em projeto novo, tratar menu e title screen como cenas formais desde o bootstrap, usando `profile_kind=front_end_profile` e seguindo `doc/03_art/12_menu_visual_language.md` + `doc/03_art/13_hud_ui_fx_decision_system.md`
- verificar `build_policy`
- ao operar UGDM/build, preservar a separacao entre ROM/compressao, VRAM residente, DMA de preload, DMA por frame e pior scanline
- nunca tratar `FAST`, `BEST` ou `NONE` em `.res` como reducao automatica de VRAM residente
- preservar compatibilidade com projetos antigos
- evitar sobrescrita de `.agent` local
- apos build com validacao, garantir `validation_report.json`, `doc/changelog` e memoria operacional coerentes
- apos qualquer nova ROM, regressao, captura ou baseline, rodar `freshness_audit.ps1` e corrigir drift antes de promover status
- ao encerrar uma cena, rodar `scene_closeout_gate.ps1`; se usar fluxo manual, registrar a justificativa no `runtime_decision_log`
- quando usar BlastEm, preferir `press_until_ready:*` apoiado em heartbeat `READY` em SRAM `0x100` com rolling write pos-warmup (ROM-side) + FileSystemWatcher fast-path (wrapper-side)
- `press_until_ready` aceita knobs canonicas: `timeout_ms`, `interval_ms`, `hold`, `max_presses`, `flush_every` (forca ciclo ESC pause/resume para flushar SRAM), `rotate_key` (tentativa extra com tecla alternativa em timeout)
- quando o input for persistido, usar `tools/sgdk_wrapper/schemas/blastem_input_script.schema.json` e exemplo `tools/sgdk_wrapper/.agent/references/agentic_aaa_contracts/examples/blastem_input_script.example.json`
- `save_path` e `screenshot_path` do BlastEm devem ser reescritos dentro do bloco `ui {}`; no topo do cfg a opcao pode ser ignorada
- tratar `outside_sandbox_candidate`, `stale_sandbox_candidate` e `fresh_sram_confirmed=false` como evidencia invalida
- fechar o BlastEm pelo contrato `ESC -> WM_CLOSE -> Alt+F4 -> kill`
- se o build falhar antes do emulador por blockers do projeto, registrar isso como falha do smoke integrado, nao como sucesso parcial de QA
- nao construir rota de heartbeat live via GDB watchpoint: stub do BlastEm nao suporta `Z2`/`Z3`/`Z4`, retorna pacote vazio
- `make -j`, debug symbols, hooks e GitHub Actions sao melhorias de pipeline; ate existirem e serem provadas, registrar gap em vez de vender como resolvido

## Reconciliacao de status apos build

Regra generalizada de reconciliacao entre ROM, relatorios e documentacao ativa.

Depois de uma ROM, captura ou refresh de validacao, o agente deve comparar, no
mesmo escopo:

- `out/rom.bin` e hash/tamanho registrado
- `doc/changelog/roms/*/build_meta.json`
- `doc/10-memory-bank.md`
- `doc/changelog/changelog.md`
- `doc/rom_mastering_report.json`
- `doc/local_ci_gate_report.json` quando existir
- evidencia de BlastEm/SRAM/screenshot e sua frescura em relacao a ROM
- `validation_report.blocking_statuses`

Se estes artefatos discordarem, o status maximo e o menor status consistente por
escopo. Exemplo: um boot seed com screenshot/SRAM pode ser
`testado_em_emulador` somente para o seed, enquanto `gameplay`, `visual AAA`,
`budget`, `audio` e `first playable` continuam nao provados. Relatorio antigo
`not_started`, `sem_sessao` ou `report_older_than_rom` deve virar drift a
reconciliar, nao argumento para promover ou descartar a evidencia sem analise.

Quando a mudanca for apenas reconciliacao de relatorio/status, preferir
atualizacao status-only e freshness audit; nao criar build snapshot artificial.

## Gate de progresso antes de novo build

Regra operacional sustentada pelo historico canonico de
`doc/changelog/roms/build_v*/build_meta.json`.

- O detector de loop deve preferir `build_meta.json` ao arquivo mutavel
  `out/logs/validation_report.json`; um relatorio atual isolado nao representa
  historico.
- Dois builds consecutivos com blocker comum geram `progress_warning`.
- Sob `progress_warning`, o proximo build exige:
  - `SGDK_TARGET_BLOCKER`: blocker vigente que a mudanca pretende remover;
  - `SGDK_CHANGE_CATEGORY`: `runtime`, `visual`, `art`, `infra`, `docs`,
    `wrapper`, `log`, `schema` ou `other`;
  - `SGDK_CHANGE_SUMMARY`: mudanca concreta, com informacao suficiente para
    auditoria.
- O alvo precisa existir em `validation_report.blocking_statuses`, e a categoria
  precisa atacar o tipo do blocker. Rebuild sem alvo explicito e bloqueado.
- Tres builds consecutivos com blocker comum continuam exigindo
  `doc/operational_loop_decision.json` valido.
- Numero de build, nova captura ou refresh de relatorio nao contam como
  progresso quando `blockers_removed=0`.
- Quando o blocker dominante for `visual_gate_blocked`,
  `visual_direction_failed`, `blocked_no_premium_source`,
  `blocked_no_human_asset_approval`, `blocked_no_vdp_conversion` ou
  `perceptual_motion_unvalidated`, o proximo build so e progresso se
  `SGDK_CHANGE_CATEGORY` for `art`, `visual` ou `runtime` com resumo que ataque
  diretamente fonte, aprovacao, conversao VDP, match visual, motion evidence ou
  `visual_delivery_gate_report`. Build tecnico, screenshot novo ou revalidacao
  sem remover blocker visual deve ser classificado como `smoke_only` ou
  `technical_runtime_creative_blocked`.

Exemplo de sessao PowerShell antes do build:

```powershell
$env:SGDK_TARGET_BLOCKER = "visual_gate_blocked"
$env:SGDK_CHANGE_CATEGORY = "art"
$env:SGDK_CHANGE_SUMMARY = "Produzir a fixture visual real do primeiro setor."
```

## Evidencia de input no BlastEm por observacao da ROM

Regra generalizada de evidencia de input observada pela ROM.

- Input enviado pelo host nao e evidencia por si so.
- Para navegacao roteirizada, exigir confirmacao ROM-side quando disponivel:
  campos SRAM/metricas para `raw_input`, `observed_input`, `input_locked` e
  `scene_id`.
- Se `SendInput` reporta envio mas `observed_input` permanece `0`, nao contar a
  navegacao como sucesso.
- `wm_key_message_to_sdl_window` e transporte experimental; nao promover a
  transporte universal ate o wrapper ter suporte canonico e teste proprio.
- Relatorios de navegacao devem registrar `input_transport`, `observed_input`,
  `raw_input`, cena esperada, cena observada e hash da ROM.
- Preferir scripts JSON e `press_until_ready`, mas qualquer transporte de input
  precisa ser validado por estado observado pela ROM quando a alegacao for
  transicao de cena.

## Setup SGDK/VS Code candidato

Origem: item `SGDK Setup + VS Code` do lote `curation_batch_2026_06_16`,
evidência `E1_text`, expansão candidata. Reusa o checklist e o contrato
operacional existentes (manifesto, `assert_agent_environment.ps1`,
`preflight_host.ps1`); não cria schema novo e não promete build/runtime de
projeto.

- setup e build pertencem ao **wrapper central**, não à lógica dentro do
  projeto; configurar SGDK/VS Code é operação de wrapper.
- a toolchain canônica é sempre o `sdk/sgdk-2.11/` deste workspace; build sempre
  resolve por ele.
- `GDK` herdado de outro workspace **não é dependência canônica**; não tratar um
  GDK externo como toolchain oficial.
- antes de diagnosticar ambiente, o ambiente deve passar por
  `assert_agent_environment.ps1`.
- erros de PATH, shell, PowerShell, Make, Java/rescomp ou VS Code viram
  **diagnóstico explícito**, nunca workaround silencioso.
- não editar um projeto para "consertar setup" sem manifesto/higiene resolvidos;
  ambiente não conserta projeto por atalho.
- a expansão continua candidata: produção real ainda exige os validators do
  projeto, build real e evidência de emulador quando houver entrega de ROM.

## Proibido

- duplicar regras de copia da `.agent` em varios arquivos sem helper comum
- depender de um unico layout de projeto
- tratar changelog, budget e evidencia como assuntos separados
- reintroduzir fallback para `LocalAppData\\blastem\\rom` fora do sandbox do projeto
- bootstrapar projeto novo sem declarar que papel a UI cumpre na fantasia, no fluxo e no `ui_decision_card`
- bootstrapar projeto novo com transicoes dramaticas, de zona ou de menu sem `scene_transition_card`, teardown e fallback
- declarar pipeline AAA-grade sem `ci_gate_report`/`local_ci_gate_report`, `code_review_report` e `rom_mastering_report`
- tratar `doc/prd_index.json` ausente, PRD obrigatorio em `seed` ou `prd_readiness_report.status=blocked` como detalhe menor quando o objetivo for AAA/stable/release
- tratar screenshot, SRAM ou boot como prova automatica de gameplay, audio ou
  performance sem `claim_scope` correspondente
- tratar MTR de estatistica de corrida como MDRT de desempenho
- aceitar closeout manual sem `scene_closeout_gate_report.json` executado
- ignorar `sgdk_build_route_report.json`, misturar rota Linux/Windows ou
  classificar mismatch LTO de link como defeito do codigo do jogo
