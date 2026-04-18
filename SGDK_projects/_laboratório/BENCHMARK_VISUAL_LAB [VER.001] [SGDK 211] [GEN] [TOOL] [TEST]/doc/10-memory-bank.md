# 10 - Memory Bank & Context Tracker — BENCHMARK_VISUAL_LAB [VER.001] [SGDK 211] [GEN] [TOOL] [TEST]

**Ultima atualizacao:** 2026-04-03
**Fase atual:** benchmark side-by-side capturado com evidencia rastreavel e quicksave nativo automatizado
**Proxima fase:** ampliar telemetria de runtime e endurecer a automacao de captura sem reabrir o gate de evidencia

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- projeto-ferramenta criado com bootstrap canonico da `.agent`
- arena com 3 provas fixas definida em documentacao
- integracao prevista com o eixo visual do `validation_report.json`
- benchmark side-by-side com BGs e sentinels `basic` vs `elite`
- `main.c` estavel em BlastEm a 59.9 fps no slice atual, sem fatal de CPU durante janela de validacao
- score composto do caso visual confirmando delta `elite > basic`
- `validation_report.json` limpo, com `boot_emulador=ok` e `testado_em_emulador=true`
- captura dedicada preservada em `out/captures/benchmark_visual.png`
- quicksave nativo do BlastEm preservado em `out/captures/benchmark_quicksave.state`
- dump visual extraido de SRAM em `out/captures/visual_vdp_dump.bin`

### O que e placeholder

- telemetria de runtime forte (`runtime_metrics.json`)
- fallback externo via AutoHotkey / AutoIt nao foi exercitado nesta maquina porque essas ferramentas nao estao instaladas

### O que falta para o slice ser completo

- medir `frame_stability`, `sprite_pressure`, `fx_load` e `perceptual_quality`
- endurecer a camada de fallback externa para `ui.save_state` sem depender apenas do helper nativo

### Metricas de codigo

- foco inicial: boot limpo, navegacao entre provas e leitura textual em 320x224
- foco atual: preservar estabilidade do loop enquanto a captura SRAM/VDP e acionada

## 2. O QUE ACABOU DE ACONTECER

**2026-04-03 — fundacao do BENCHMARK_VISUAL_LAB**

- projeto criado como ferramenta canonica de benchmark visual
- docs iniciais escritos para governar a prova de heuristicas

**2026-04-03 — causa raiz do crash em BlastEm isolada e resolvida**

- o fatal `M68K attempted to execute code at unmapped or I/O address ...` nao vinha de VDP dump nem de sprites
- a origem real era o uso de `VDP_drawTextBGFill()` com `len` menor que o tamanho de strings do overlay
- em SGDK 2.11 isso corrompe a stack e mascara a causa real como salto ilegal do 68000
- o benchmark passou a usar um wrapper local que trunca o texto antes de desenhar
- depois da correcao, o ROM voltou a rodar de forma estavel no BlastEm

**2026-04-03 — captura ferro fechada sem `session_not_captured`**

- o script `run_visual_capture.ps1` passou a usar screenshot dedicado da janela do BlastEm em vez de hotkey interna
- o encerramento da sessao agora e gracioso via `CloseMainWindow()`, permitindo flush confiavel de `save.sram`
- o bloco `VLAB` foi extraido com sucesso para `visual_vdp_dump.bin`
- `validation_report.json` ficou com `emulator_evidence_reason = ok` e sem warnings

**2026-04-03 — quicksave nativo do BlastEm automatizado**

- `invoke_blastem_hotkey.ps1` passou a acionar `ui.save_state` no `SDL_app` do BlastEm via `PostMessage`
- a captura oficial agora preserva `benchmark_visual.png`, `benchmark_quicksave.state`, `save.sram` e `visual_vdp_dump.bin`
- `emulator_session.json`, `validation_report.json` e `visual_aesthetic_report.case.json` passaram a marcar `quicksave_captured = true`
- o metodo registrado e `native-postmessage`
- `blastem_hotkey_fallback.ahk` e `blastem_hotkey_fallback.au3` ficam como caminhos externos de contingencia; nesta maquina eles nao foram executados porque AutoHotkey e AutoIt nao estao instalados

## 3. DECISOES PENDENTES

- consolidar o primeiro pacote de capturas que vira baseline visual canonica do laboratorio
- transformar o helper nativo + fallbacks externos no pacote padrao reutilizavel para outros projetos do workspace
