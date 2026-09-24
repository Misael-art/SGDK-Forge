<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: bootstrap de projeto novo
- Ultima sincronizacao: 2026-09-10T17:13:51.8127400Z
- Ultimo build versionado: nenhum
- ROM vigente: inexistente
- Evidencia de emulador: inexistente
- Gate visual: blocked_no_premium_source
- Gate gameplay: nao provado
- Gate AAA: ready_for_aaa=false
<!-- SGDK GENERATED STATUS END -->

# 10 - Memory Bank & Context Tracker - TAIKETSU ULTRA HERO GENESIS [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

**Ultima atualizacao:** 2026-09-10
**Fase atual:** porta SGDK 2.11 buildada e bootada no BlastEm (ceiling prototype)
**Proxima fase:** substituir placeholders de audio/sprites; portar header de ROM upstream

## 1. Origem e proveniencia

- Engine origem: `SGDK_Engines/TaiketsuUltraHeroGenesis/src` (upstream `https://github.com/guilhermesousa03/TaiketsuUltraHeroGenesis`, 9 commits, licenca GPL-3.0).
- Fork da engine HAMOOPIG (by GameDevBoss / Daniel Moura, 2015-2022).
- **Creditos obrigatorios a GameDevBoss (Daniel Moura)** — cabecalho de src/main.c exige creditos. GPL-3.0 copiado em `rascunho/upstream_reference/LICENSE`.
- Copia de referencia do material upstream (nao-fonte: README, PDF, LICENSE, bats, icones) em `rascunho/upstream_reference/`; hashes dos assets importados em `imported_assets_sha256.json`.
- `src/main.c` (5.586 linhas, 234 KB) copiado byte-a-byte (cmp) do upstream.

## 2. Estado operacional

- portado: sim
- documentado: sim
- implementado: sim
- buildado: **sim** — `tools/sgdk_wrapper/build.sh`, rota Wine flatpak, `out/rom.bin` (917.504 bytes), `wine_bridge_status=buildado`
- testado_em_emulador: **sim (boot + gameplay basico por input)** — BlastEm 0.6.2 flatpak NTSC: arena de luta renderizada a 60 fps com lutadores/cenario/paletas; evidencia em `out/emulator_evidence/blastem-linux-manual-20260910T193902Z/` (screenshot.png, save.sram, blastem.log, session_runtime.json). **Sessao interativa 2026-09-10** (`out/emulator_evidence/interactive-20260910T200010Z/`): input real por teclado — P1 anda do spawn ate engajar a IA P2, animacoes executam, 60 fps sustentados; fix do crash se mantem estavel sob input.
- validado_budget: nao (fora do escopo da porta; validador reporta erro conhecido de tiles carregados em runtime — design da engine)
- audio: **placeholder** — sound.res upstream vazio (0 bytes, idem no repo upstream); 17 simbolos snd_* ativos via XGM_setPCM recebem PCM silenciosos de 800 amostras @16kHz (`res/snd/`, registro em `rascunho/upstream_reference/sound_placeholder_manifest.json`)
- sprites: **28 placeholder** — main.c referencia 28 simbolos spr_* ausentes do sprite.res upstream E do ultimo sprite.h valido (snapshot fora de sincronia): paletas gillius/haohmaru (truque sprite 1-tile), digitos spr_n0..n9, spr_raiden_100, spr_sombra. Entradas marcadas no proprio `res/sprite.res`
- ready_for_aaa: false

## 3. Decisoes e incidentes da porta (2026-09-10)

1. Boot files: template SGDK 2.11 (modelo) mantidos como base; **header portado em 2026-09-10** — domestic/overseas "TAIKETSU ULTRA HERO GENESIS", copyright "(C)GAMEDEVBOSS26" (antes SAMPLE PROGRAM). ROM sha256: 3967996af4efe197284dd80e48a3b457aa381f8e0ba098851b5dbb59fc42bc7c
2. fix_migration_issues.ps1 aplicou 4 reescritas em main.c; 2 revertidas por falso-positivo (sprite.h/sound.h sao headers de RECURSO rescomp, nao de engine). As 2 mudancas de SPR_init na linha 336 caem dentro de comentario (inocuas).
3. **CRASH DE BOOT CORRIGIDO**: ROM original da porta morria com ILLEGAL INSTRUCTION logo apos "Room Tela Hamoopig". Causa raiz: `memcpy(&palette[48], ..., 18*2)` escreve indices 48..65 em `u16 palette[64]` — stack overflow de 2 u16 que o GCC da era 2.01 tolerava por layout de pilha, mas o GCC -O3 do SGDK 2.11 corrompia o endereco de retorno. Fix minimo: `u16 palette[66]` (linha ~5355), comportamento de escrita preservado. Evidencia do crash pre-fix: `out/emulator_evidence/blastem-linux-manual-20260910T193317Z/screenshot.png`.
4. Captura de evidencia: o wrapper canonico `capture_blastem_evidence_linux.sh` nao captura esta ROM (window_timeout): o jogo imprime kdebug no boot e o BlastEm flatpak, com stdout redirecionado, tenta re-executar num x-terminal-emulator inexistente no sandbox. Sessoes manuais sob pty (script -qec) reproduzem os mesmos artefatos (screenshot/sram/log/manifest).

## 4. Bloqueios

- Nenhum bloqueio de metodo. Placeholders de audio/sprites e header SAMPLE PROGRAM sao estado documentado, nao bloqueio.

## 5. Regra de continuidade

Atualize este arquivo, o changelog e os manifests sempre que a verdade
operacional mudar. Nunca copie hashes, builds, aprovacao ou evidencia do modelo.
