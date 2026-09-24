# 14 - Plano de Provas QA Canonicas - TAIKETSU ULTRA HERO GENESIS [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

**Objetivo:** tornar explicito como este projeto pretende provar os gates finais do wrapper sem depender de memoria implicita.

**Regra:** se um eixo ainda nao tem evidencia minima definida, ele deve permanecer `nao_testado` e o blocker precisa ficar documentado aqui e no `doc/10-memory-bank.md`.

## Eixos e provas proporcionais ao contexto (technical_demo / ceiling prototype)

| Eixo | Prova minima | Status 2026-09-10 |
|------|--------------|-------------------|
| build | `out/rom.bin` existe + `out/logs/linux_wine_build_report.json` com wine_bridge_status=buildado | **provido** |
| boot_emulador | sessao BlastEm em `out/emulator_evidence/` com screenshot.png + save.sram + blastem.log | **provido** (boot + interativo, apos fix do crash — ver memory bank) |
| gameplay_basico | sessao de input no emulador exercitando golpe/movimento/HUD | **provido (parcial)** — movimento ate engajar a IA e animacoes provadas por input real em `out/emulator_evidence/interactive-20260910T200010Z/`; dano/HUD e fim de round ainda nao exercitados |
| performance | leitura de fps do titulo da janela BlastEm (60 fps) por sessao | **observado** (60 fps sustentados durante a sequencia interativa) |
| audio | substituir PCM silenciosos por samples reais e provar via captura de audio | bloqueado por asset ausente (upstream e repo original tem sound.res vazio) — placeholder declarado |
| sprites placeholder | substituir as 28 entradas placeholder do sprite.res pelos assets reais | bloqueado por asset ausente (snapshot upstream fora de sincronia) |
| memoria canonica | `doc/10-memory-bank.md` + changelog refletindo a verdade | **provido** |

## Nota de captura

O wrapper canonico de captura nao retem a janela desta ROM (kdebug no boot + flatpak sem x-terminal-emulator → re-exec falha). Sessoes manuais sob pty reproduzem os mesmos artefatos; motivo registrado em cada `session_runtime.json`.

## Nao-metas de prova neste contexto

- validado_budget (VRAM/DMA/scanline): nao e meta desta porta; o validador reporta o erro conhecido de tiles carregados em runtime (design da engine upstream).
- barra viva da cena AAA: nao se aplica a ceiling prototype.
