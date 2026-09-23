# Changelog Canonico - TAIKETSU ULTRA HERO GENESIS [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

## 2026-09-10T17:13:51.8127400Z - bootstrap

- projeto criado a partir da estrutura canonica
- historico de ROM, hashes e evidencia do modelo removido
- status inicial: documentado; nao buildado; nao testado em emulador
- proximo gate: classificar contexto e metodologia

## 2026-09-10 - porta SGDK 2.11 (porta direta de SGDK_Engines/TaiketsuUltraHeroGenesis)

- materializado new_project.sh (estrutura canonica completa) e classificado como technical_demo com ceiling prototype
- src/main.c upstream (5.586 linhas) copiado byte-a-byte (cmp)
- assets upstream portados: gfx.res (5 IMAGE), sprite.res (63 SPRITE) + 65 pngs; hashes em rascunho/upstream_reference/imported_assets_sha256.json
- sound.res upstream vazio: criados 17 PCM silenciosos XGM (res/snd/) para os simbolos snd_* ativos; status placeholder documentado
- sprite.res: 28 entradas placeholder para simbolos spr_* que o snapshot upstream nao declara (paletas gillius/haohmaru, digitos n0-n9, raiden_100, sombra); status placeholder documentado
- fix_migration_issues.ps1: 4 reescritas; 2 revertidas como falso-positivo (sprite.h/sound.h sao headers de RECURSO rescomp)
- FIX DE CRASH DE BOOT: memcpy(&palette[48],...,18*2) estourava u16 palette[64] em 2 indices; GCC -O3 do 2.11 corrompia endereco de retorno (ILLEGAL INSTRUCTION apos "Room Tela Hamoopig"). Fix minimo: u16 palette[66]; comportamento de escrita preservado. Evidencia pre-fix em out/emulator_evidence/blastem-linux-manual-20260910T193317Z/
- build: tools/sgdk_wrapper/build.sh (Wine flatpak, sdk/sgdk-2.11) → out/rom.bin 917.504 bytes, wine_bridge_status=buildado
- boot BlastEm 0.6.2 NTSC: arena de luta a 60 fps (evidencia em out/emulator_evidence/blastem-linux-manual-20260910T193902Z/ — screenshot, save.sram, log, manifest; captura manual sob pty porque o wrapper canonico nao captura ROMs que imprimem kdebug neste flatpak)
- status: buildado e bootado em emulador (boot only; input nao exercitado; audio e sprites placeholders declarados)

## 2026-09-10 (2) - header de ROM real + gameplay basico provado

- src/boot/rom_head.c: domestic/overseas "TAIKETSU ULTRA HERO GENESIS" e copyright "(C)GAMEDEVBOSS26" (antes SAMPLE PROGRAM); rebuild limpo (ROM sha256 3967996a...)
- sessao interativa de input (out/emulator_evidence/interactive-20260910T200010Z/): xdotool -> gamepad 1; P1 anda do spawn ate engajar a IA P2, animacoes executam, 60 fps sustentados, fix do crash estavel; manifest com sequencia de inputs e limites de claim
- status: gameplay basico provido (movimento/engajamento); dano/HUD, fim de round e audio continuam nao provados
