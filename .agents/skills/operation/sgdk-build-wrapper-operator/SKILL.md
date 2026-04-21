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
- a `.agent` local nao pode ser tratada como saudavel se faltar contexto canonico critico
- `doc/changelog` e parte do fluxo operacional, nao pos-processo opcional

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

### Passa quando

- o projeto nao esta em contexto degradado silencioso
- a ROM, o changelog e a memoria operacional apontam para o mesmo estado
- a automacao BlastEm usa exclusivamente `tools/sgdk_wrapper/lib/blastem_automation.psm1`
- logs do emulador ficam em JSONL sob `out/logs/*_blastem.log`
- artefatos de SRAM/screenshot ficam confinados a `out/blastem_env_*`
- no Windows, o sandbox BlastEm precisa espelhar `Home/AppData/Local` e o `blastem.cfg` efetivo deve nascer nesse ramo

### Handoff para proxima etapa

- entregar `validation_report.json`, `doc/changelog` e `doc/10-memory-bank.md` coerentes para o fechamento de QA

## Checklist

- executar `tools/sgdk_wrapper/preflight_host.ps1` antes do primeiro build da sessao
- confirmar `MD_ROOT`, `GDK` e `SGDK_EMULATOR_PATH`
- resolver contexto do projeto via manifesto ou heuristica controlada
- em projeto novo, garantir que `doc/11-gdd.md` ou `doc/13-spec-cenas.md` declarem `ui_decision_card` para qualquer UI formal antes do runtime
- em projeto novo, garantir que `doc/13-spec-cenas.md` declare `scene_transition_card` para qualquer transicao formal antes de arte/runtime
- em projeto novo, tratar menu e title screen como cenas formais desde o bootstrap, usando `profile_kind=front_end_profile` e seguindo `doc/03_art/12_menu_visual_language.md` + `doc/03_art/13_hud_ui_fx_decision_system.md`
- verificar `build_policy`
- preservar compatibilidade com projetos antigos
- evitar sobrescrita de `.agent` local
- apos build com validacao, garantir `validation_report.json`, `doc/changelog` e memoria operacional coerentes
- quando usar BlastEm, preferir `press_until_ready:*` apoiado em heartbeat `READY` em SRAM `0x100` com rolling write pos-warmup (ROM-side) + FileSystemWatcher fast-path (wrapper-side)
- `press_until_ready` aceita knobs canonicas: `timeout_ms`, `interval_ms`, `hold`, `max_presses`, `flush_every` (forca ciclo ESC pause/resume para flushar SRAM), `rotate_key` (tentativa extra com tecla alternativa em timeout)
- `save_path` e `screenshot_path` do BlastEm devem ser reescritos dentro do bloco `ui {}`; no topo do cfg a opcao pode ser ignorada
- tratar `outside_sandbox_candidate`, `stale_sandbox_candidate` e `fresh_sram_confirmed=false` como evidencia invalida
- fechar o BlastEm pelo contrato `ESC -> WM_CLOSE -> Alt+F4 -> kill`
- se o build falhar antes do emulador por blockers do projeto, registrar isso como falha do smoke integrado, nao como sucesso parcial de QA
- nao construir rota de heartbeat live via GDB watchpoint: stub do BlastEm nao suporta `Z2`/`Z3`/`Z4`, retorna pacote vazio

## Proibido

- duplicar regras de copia da `.agent` em varios arquivos sem helper comum
- depender de um unico layout de projeto
- tratar changelog, budget e evidencia como assuntos separados
- reintroduzir fallback para `LocalAppData\\blastem\\rom` fora do sandbox do projeto
- bootstrapar projeto novo sem declarar que papel a UI cumpre na fantasia, no fluxo e no `ui_decision_card`
- bootstrapar projeto novo com transicoes dramaticas, de zona ou de menu sem `scene_transition_card`, teardown e fallback
