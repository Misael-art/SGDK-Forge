# Build and Emulator Gate

## Objetivo

Garantir que a skill feche o ciclo ate ROM + evidencia, sem declarar sucesso so porque o codigo compila.

## 1. Build

Passos minimos:

1. resolver o projeto alvo
2. buildar pelo wrapper canonico
3. verificar `out/rom.bin`
4. registrar hash, tamanho e timestamp
5. ler `validation_report.json`

## 2. Evidencia de emulador

Gate canonico:

- BlastEm obrigatorio
- BizHawk so complementa

Evidencia minima aceita:

- screenshot dedicada da janela do BlastEm
- quando existir no projeto: `save.sram` + `visual_vdp_dump.bin`
- sessao de emulador coerente com a ROM buildada
- log JSONL da automacao (`out/logs/*_blastem.log`)

Contrato operacional:

- usar a lib canonica `tools/sgdk_wrapper/lib/blastem_automation.psm1`
- heartbeat canonico: ROM escreve `READY` em SRAM `0x100` em rolling (re-assinado pos-warmup), nao em emissao unica; referencia canonica em `tools/sgdk_wrapper/modelo/src/system/runtime_probe.c`
- wrapper detecta readiness com duas camadas: `FileSystemWatcher` como fast-path e polling como backstop
- `press_until_ready:key[,timeout_ms=,interval_ms=,hold=,max_presses=,flush_every=,rotate_key=]` e o unico passo oficial para chegar em cena antes de captura
- `flush_every=K` forca ciclo ESC pause/resume a cada K presses sem READY, disparando flush de SRAM do BlastEm
- `rotate_key=<tecla>` faz tentativa extra com tecla alternativa em timeout do primeiro laco
- todo candidato de SRAM precisa passar por `Test-FreshSramCandidate` (sandbox-root + `processStartedAt`)
- `fresh_sram_confirmed=true` e obrigatorio para promover evidencia de runtime BlastEm
- manter `save.sram`, screenshots e artefatos auxiliares apenas dentro de `out/blastem_env_*`
- tratar qualquer evidencia fora do sandbox ou anterior ao boot do processo como `stale`
- fechar o BlastEm via `ESC -> WM_CLOSE -> Alt+F4 -> kill`
- GDB stub `Z2`/`Z3`/`Z4` (watchpoints) NAO existe como rota no contrato: stub do BlastEm responde pacote vazio; so `Z0` e `m addr,len` (CPU parada) sao validos, uteis apenas para debug humano offline

## 3. O que nao vale

- compilar sem rodar
- rodar ROM antiga sem ancorar hash/timestamp
- screenshot de desktop inteiro como evidencia primaria
- declarar `testado_em_emulador` sem artefato rastreavel

## 4. Saida da skill

A skill deve sempre explicitar:

- status de `buildado`
- status de `testado_em_emulador`
- status de `validado_budget` quando aplicavel
- o que ainda e `parcial`, `placeholder` ou `nao_testado`
