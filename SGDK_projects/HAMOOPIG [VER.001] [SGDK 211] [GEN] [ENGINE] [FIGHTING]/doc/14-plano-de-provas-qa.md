# 14 - Plano de Provas QA Canonicas - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

**Objetivo:** tornar explicito como este projeto pretende provar os gates finais do wrapper sem depender de memoria implicita.

**Regra:** se um eixo ainda nao tem evidencia minima definida, ele deve permanecer `nao_testado` e o blocker precisa ficar documentado aqui e no `doc/10-memory-bank.md`.

## Continuacao vigente — 2026-09-13

Mesma ROM `532d44539809e40ad3ae8150532f27c91d7f638ee12d6b194cd53897f294a953`, sem rebuild.
Fechamento: `doc/curation/2026_09_13/qa_continuation_closeout.md`.

- P2 vence e START retorna ao seletor: NTSC `visual_ko_20260913T114321Z`, PAL `visual_ko_20260913T114702Z`.
- Empate e reset: `visual_ko_20260913T114914Z`; vencedor por tempo com vida desigual e reset: `visual_ko_20260913T193905Z`.
- Audio isolado com sinal, sem clipping digital: `visual_ko_20260913T115242Z/audio_signal_report.json`. Nao equivale a audicao ou SFX sob carga; audio da sessao PAL foi rejeitado.
- Host: 9.216 pares no contrato de time-over, 192 transicoes letais, paleta/hashes e self-check do auditor PCM passaram.
- Identidade/integridade: finalizador canonico e gate semantico; relatorio `out/logs/evidence_closeout_report.json`. Nao e selo completo VLAB/VDP/runtime.
- Pendentes: especial/projetil apos reset, variantes PAL restantes, audicao/SFX, FPS do loop, DMA/SAT/fragmentacao e instrumentacao canonica.

## Historico visual/KO — 2026-09-12 (pendencias atualizadas acima)

ROM `532d44539809e40ad3ae8150532f27c91d7f638ee12d6b194cd53897f294a953`.
Build exit 0 em `out/logs/visual_ko_verified_build.log`.
Sessoes finais `visual_ko_20260912T162753Z` (Ken x Musgo) e
`visual_ko_20260912T162933Z` (Musgo x Musgo), ambas em `out/emulator_evidence/`.

- Provado visualmente nesta ROM: HUD limpo, P2 zero em dois KOs, round seguinte restaurado, Musgo cai e fica deitado, pose de vitoria, texto do atlas legivel, revanche A e cenario sem buracos pretos de transparencia.
- Tests host PASS: `test_health_contract.py` e `test_stage_palette.py` em `rascunho/temporario/`.
- Videos 640x480/60 quadros/s, sem audio; isto nao prova FPS sustentado da ROM.
- Pendentes na vigente: P2 vencedor, empate/time-over, START, especial/projetil apos reset, PAL, audio isolado, pior DMA/SAT/scanline e bundle VLAB/VDP/runtime.
- Residencia estatica 1018/1020 nao equivale a budget dinamico validado.
- Fechamento e limites: `doc/curation/2026_09_12/visual_ko_closeout.md`.

## Historico anterior — nao certifica a ROM vigente

| Eixo | Prova minima | Status 2026-09-12 |
|------|--------------|-------------------|
| build | `out/rom.bin` existe + `out/logs/linux_wine_build_report.json` com wine_bridge_status=buildado | **provido** |
| boot_emulador | sessao BlastEm em `out/emulator_evidence/` com screenshot.png + save.sram + blastem.log | **provido** (boot + interativo); captura canônica `blastem-linux-20260912T125335Z-2562833` passou o gate semântico, mas não sela sem VLAB/VDP/runtime |
| gameplay_basico | sessao de input no emulador exercitando golpe/movimento/HUD | **provido (parcial)** — idle, movimento H, pulo/camera V e hit em `interactive-showdown-20260911T225648Z`; round fresco em `interactive-round-integrity-20260912T124213Z` usa a ROM pós-patch |
| round_loop | KO dos dois lados, time over/empate, reset simetrico, segunda vitoria, tela pos-partida e retorno/revanche | **provido parcialmente** — P1 venceu dois rounds por KO natural, houve reset, tela pós-luta e retorno por START no bundle `interactive-round-integrity-20260912T064603Z`; time-over/empate foi provado no binário imediatamente anterior em `interactive-round-integrity-20260912T063457Z`; faltam P2 vencedor e revanche por A |
| performance | leitura de fps do titulo da janela BlastEm (60 fps) por sessao | **observado** — 60.2 fps ao fim do round completo no bundle final |
| audio | BGM e SFX reais ligados; captura de audio nao silenciosa e audicao | **implementado; prova parcial** — o round novo ainda nao foi capturado com audio |
| memoria canonica | `doc/10-memory-bank.md` + changelog refletindo a verdade | **provido** — hash vigente `363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f` |

## Nao-metas de prova neste contexto

- validado_budget (VRAM/DMA/scanline): nao e claim desta porta; qualquer medicao futura deve continuar separada do simples build/boot.
- barra viva da cena AAA: nao se aplica a ceiling prototype.
