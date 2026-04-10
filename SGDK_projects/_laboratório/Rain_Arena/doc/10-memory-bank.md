# 10 - Memory Bank & Context Tracker — Rain_Arena

**Ultima atualizacao:** 2026-04-03
**Fase atual:** C6 - loop jogavel minimo
**Proxima fase:** decidir expansao do slice apos validacao dedicada no emulador

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- build limpo no wrapper SGDK 2.11 com geracao valida de `out/rom.bin`
- boot confirmado no BlastEm com ROM reconhecida corretamente
- cena de chuva com scroll de fundo, hit-pause, flash de paleta e cooldown funcionando
- input em `A/B/C` agora sustenta um loop jogavel de timing com acerto, erro e reinicio
- sprites de chuva renderizam sem vazamento magenta nas amostras validadas
- audio fechado como silencio intencional: nenhuma rotina XGM/PCM/PSG e nenhum asset sonoro declarado no slice
- budget tecnico consolidado com 853 tiles de VRAM operacional, 40 entradas SAT e 800/1488 words de DMA por frame
- HUD textual em window plane mostra score, erros, tempo e estado do ciclo sem exigir asset novo

### O que e placeholder

- hardware real ainda nao testado fora do emulador

### O que falta para o slice ser completo

- decidir se a base vira prototipo expandido ou apenas vertical slice fechado

### Metricas de codigo

- codigo principal observado em `src/main.c` com loop jogavel minimo, HUD e reinicio de round
- 3 recursos validados no pipeline (`rain_sprite.png`, `sky.png`, `temple.png`)
- 3 paletas ativas no slice (`PAL0`, `PAL1`, `PAL2`)
- 40 sprites de chuva (`MAX_RAINDROPS = 40`)

---

## 2. O QUE ACABOU DE ACONTECER

**2026-04-03 — fechamento de C2 a C6 validado**

- a causa raiz do erro no BlastEm foi identificada: `out/rom.out` era ELF e nao ROM executavel
- o build foi refeito de forma limpa, regenerando `out/rom.bin` com header `SEGA MEGA DRIVE`
- o boot foi validado no BlastEm e a evidencia foi salva em `out/logs/c2_valid_rom_blastem_window.png`
- a cena foi observada por aproximadamente 10 segundos no BlastEm, com resposta visual ao input e sem glitch evidente
- o hit-pause/flash foi capturado em `out/logs/c3_burst_01.png`
- o movimento continuo foi evidenciado em `out/logs/c3_t02.png` e `out/logs/c3_t10.png`
- `out/logs/emulator_session.json` e `out/logs/validation_report.json` foram atualizados para refletir o estado real do QA
- a auditoria de audio confirmou ausencia total de trilha e SFX no slice; o comportamento esperado em BlastEm e silencio
- a ROM atual foi medida em budget tecnico real: `bg_sky = 474 tiles`, `bg_temple = 283 tiles`, `sprite_rain = 2 tiles maximos por gota`, totalizando `853` tiles operacionais com base de sistema
- a pressao maxima de sprite ficou em `40` entradas SAT e o perfil de DMA foi consolidado em `800` words/frame tipico e `1488` words/frame no pico
- a cena deixou de ser apenas demonstrativa e passou a ter objetivo explicito: fazer `6` acertos em `30s` antes de `3` erros
- o HUD foi movido para `WINDOW`, preservando os backgrounds existentes e evitando necessidade de arte adicional
- o round agora reinicia por `START`, mantendo o slice copiavel e testavel sem menu extra
- a validacao dedicada do C6 foi registrada no BlastEm com capturas em `out/logs/c6_gameplay_blastem.png` e `out/logs/c6_round_restart_blastem.png`
- o boot, o loop basico, a estabilidade observada e o silencio intencional foram sincronizados em `out/logs/emulator_session.json` e `out/logs/validation_report.json`

**2026-04-03 — revalidacao do gate BlastEm apos rebuild**

- o wrapper marcou corretamente a evidencia anterior como stale depois do rebuild da ROM
- a ROM atual foi reaberta no BlastEm e a janela foi capturada novamente com evidencia dedicada em `out/logs/c6_gameplay_blastem_refresh.png` e `out/logs/c6_round_restart_blastem_refresh.png`
- `out/logs/emulator_session.json` foi ressincronizado com `rom_path` canonico, identidade da ROM e timestamp da nova sessao capturada
- `out/logs/validation_report.json` voltou a reportar `boot_emulador = ok`, `gameplay_basico = funcional`, `blastem_gate = true` e `emulator_evidence_stale = false`

---

## 3. DECISOES PENDENTES

- decidir se o proximo passo e avatar jogavel, audio real ou migracao para estrutura multi-cena
- reforcar no framework canonico a automacao de captura dedicada, fechamento de sessao e sincronizacao de QA para novos projetos

---

## 4. REFERENCIAS RAPIDAS

- GDD: `doc/11-gdd.md`
- Spec cenas: `doc/13-spec-cenas.md`
- Diretrizes agente: `doc/00-diretrizes-agente.md`
