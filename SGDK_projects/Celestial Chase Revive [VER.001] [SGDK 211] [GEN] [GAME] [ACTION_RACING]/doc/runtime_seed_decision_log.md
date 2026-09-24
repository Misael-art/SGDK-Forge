# Runtime Seed Decision Log

Data: 2026-06-16

## Escopo

Fase A apenas: ROM bootavel, tela visivel, header Mega Drive, loop VBlank e heartbeat `READY` em SRAM `0x100`.

Fora do seed:

- scene manager;
- title menu interativo;
- opening cutscene;
- Sector 01;
- player, track data, collision, HUD e audio;
- assets finais ou pixel art premium.

## Modelo de Runtime

- `src/main.c` e autocontido para reduzir acoplamento antes do scene manager.
- `src/boot/sega.s` foi copiado do modelo canonico do wrapper.
- `src/boot/rom_head.c` declara header proprio do Revive.
- `res/resources.res` existe como seed auditavel sem declaracoes de asset.
- `inc/project_config.h` centraliza labels e offset do probe.

## API Reality Check

Headers SGDK 2.11 consultados:

- `sdk/sgdk-2.11/inc/pal.h`: `PAL_setColor`, `RGB24_TO_VDPCOLOR`.
- `sdk/sgdk-2.11/inc/vdp.h`: `VDP_setScreenWidth320`, `VDP_setPlaneSize`, `VDP_setBackgroundColor`.
- `sdk/sgdk-2.11/inc/vdp_bg.h`: `VDP_clearPlane`, `VDP_setTextPlane`, `VDP_drawText`.
- `sdk/sgdk-2.11/inc/sram.h`: `SRAM_enable`, `SRAM_writeByte`, `SRAM_disable`.

Nenhuma API migrada/antiga foi usada.

## Decisao de Qualidade

Esta ROM pode provar `buildado` e, se capturada no BlastEm, `boot_emulador=ok`.
Ela nao prova gameplay, arte final, audio, performance de jogo, budget visual AAA ou Sector 01.
