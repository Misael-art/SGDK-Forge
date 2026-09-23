# SGDK_Engines — Coleção de Engines e Samples para Mega Drive/Genesis

Estrutura organizada para estudo e reuso de engines open-source para Mega Drive/Genesis.

Última atualização: 2026-09-02.

Os repositórios externos listados abaixo são versionados como submódulos, com
revisão exata preservada pelo monorepo. Depois de clonar o SGDK Forge, materialize-os
com:

```bash
git submodule update --init --recursive
```

`SGDK-examples/` continua sendo uma coleção local versionada; não é submódulo.

---

## Diretórios

### SGDK-source
Fonte completa do **SGDK** (Sega Genesis Development Kit) — versão `Stephane-D/SGDK` (2.11, April 2025).

**O que tem:**
- `src/` — código fonte da biblioteca SGDK (bmp.c, dma.c, joy.c, map.c, sprite_eng.c, vdp.c, vdp_spr.c, etc.)
- `inc/` — headers públicos da API SGDK (36 arquivos .h)
- `lib/` — bibliotecas pré-compiladas (libgcc.a, libmd.a, libmd_debug.a)
- `sample/` — exemplos didáticos do SGDK (ver abaixo)
- `tools/` — ferramentas auxiliares (rescomp, sizebnd, lz4w, bintos, convsym, xgm2tool, apj, sjasm, etc.)
- `doc/` — documentação
- `bin/` — binários da toolchain (Windows) / scripts para Linux
- `ext/` — extensões (link cable, flash save, EverDrive, SD card, etc.)
- `inc/snd/` — submódulos de áudio (XGM2, XGM, PCM, SMP)
- `inc/ext/` — submódulos de extensão (link cable, flash save, EverDrive, mw, etc.)

**Ferramentas em tools/:**
- `rescomp` — Compiler de resources (SPR, MAP, etc.) para SGDK
- `sizebnd` — Analizador de tamanho de código
- `lz4w` — Compressão LZ4 para ROM
- `bintos` — Conversor binário
- `convsym` — Conversor de símbolos
- `xgm2tool` — Ferramenta XGM2
- `apj` — Apple II joystick converter
- `sjasm` — Assembler SJASMPlus
- `xgm2tool` — Ferramenta de música XGM2

**Como usar:**
1. Definir `export SGDK_HOME=/caminho/para/SGDK_Engines/SGDK-source`
2. Toolchain `m68k-elf-gcc` no PATH
3. Compilar samples individualmente.

### SGDK-examples
Amostras selecionadas do SGDK-source/sample/ para estudo focado:

| Exemplo | Conteúdo | Relevância para estudo |
|---|---|---|
| `basics/` | Inicialização básica, VDP, sprites, entrada | **Primeiro contato** com SGDK |
| `game/` | Exemplo de jogo completo com loop principal | Estrutura de jogo |
| `bitmap/` | Modos bitmap, manipulação de tela | Gráficos avançados |
| `demo/` | Demostrações visuais | Referência visual |
| `fx/` | Efeitos especiais (scroll, zoom, etc.) | Técnicas de apresentação |
| `joy-test/` | Leitura de controle | Input handling |
| `snd/` | Áudio (YM2612 FM + PSG) | Sistema de som |
| `sys/` | Sistema — timers, interrupções, DMA | Infraestrutura |
| `tiled/` | Tilemaps, backgrounds | Fundamentos de cenário |
| `advanced/` | Técnicas avançadas | Referência avançada |
| `benchmark/` | Medição de desempenho | Otimização |
| `flash-save/` | Flash save (cartridge) | Persistência |
| `linkcable/` | Comunicação link cable | Multijejo |
| `megawifi/` | MegaWiFi cart | Hardware adicional |
| `serial/` | Serial communication | Debug/comms |

### SGDK-source/sample/ (todos os 15 exemplos)
ALl exemplos didáticos do SGDK estão em `SGDK-source/sample/`:

- `advanced/` — Técnicas avançadas
- `basics/` — Inicialização básica, VDP, sprites, entrada
- `benchmark/` — Medição de desempenho
- `bitmap/` — Modos bitmap, manipulação de tela
- `demo/` — Demostrações visuais
- `flash-save/` — Flash save (cartridge)
- `fx/` — Efeitos especiais (scroll, zoom, etc.)
- `game/` — Exemplo de jogo completo com loop principal
- `joy-test/` — Leitura de controle
- `linkcable/` — Comunicação link cable
- `megawifi/` — MegaWiFi cart
- `serial/` — Serial communication
- `snd/` — Áudio (YM2612 FM + PSG)
- `sys/` — Sistema — timers, interrupções, DMA
- `tiled/` — Tilemaps, backgrounds

---

## Engines adicionais clonadas

### TaiketsuUltraHeroGenesis
Projeto de engine de luta baseado em HAMOOPI, com código completo em `src/main.c` (5.600 linhas), sprites, resources, build scripts e ROM pronta em `out/rom.bin`.

**Ver README.md próprio** para detalhes de compilação e estudo.

### HAMOOPIG-SGDK
**Engine de luta para Mega Drive com SGDK** (humbertodias/sgdk-HAMOOPIG).

Derivada do HAMOOPI (Dan Moura / GameDevBoss). Features: FSM de combate, hitboxes, física, animação sprites, sistema de câmera, comemorações/derrotas, Docker, documentação, WebAssembly build.

### Blast-Engine
**Engine de desenvolvimento para Genesis baseada em SGDK** (kubilus1/blast).

Inclui: examples, incs, libs, tests, tools, Makefile, mkfiles.

### SGDK_PlatformerEngine
**Engine de platformers para Mega Drive com SGDK** (GerardGascon/PlatformerEngine).

Features: física de platform, coyote time, jump buffer, conversor LDtk → mapa de colisão.

### UltraDrive
**Projeto de estudo: engine de jogo para Mega Drive do zero** (jvisser/UltraDrive).

GPLv3, código aberto, focado em aprendizado de arquitetura de engine.

### SGDK_MegaDriving
**Exemplos pseudo-3D com SGDK** (radioation/MegaDriving).

Técnicas pseudo-3D (estilo OutRun, Hang-On), scrolls, perspectivas.

### MDSDRV
**Driver de som para Mega Drive** (superctr/MDSDRV).

FM + PSG + PCM pitchável, 16 tracks, efeitos avançados. Alternativa ao driver padrão do SGDK.

### Awesome_MegaDrive
**Catálogo curado** de ferramentas, tutoriais, jogos com código fonte, snippets (And-0/awesome-megadrive).

Referência para encontrar mais projetos e recursos.

---

## Extra: MegaDrive_DEV/SGDK_Engines

Ver `MegaDrive_DEV/SGDK_Engines/README.md` para a coleção completa de 1137 projetos SGDK (empacotados, engines, jogos, estudos).

Inclui:
- HAMOOPIG completo (HAMOOPIG [VER.1.0 CPU6.2], HAMOOPIG BASIC, HAMOOPIG KOF94 MINIMALIST)
- BLAZE_ENGINE
- PlatformerEngine + PlatformerEngine Toolkit + PlatformerEngine CONSOLIDATED
- RaycastingEngine + Raycasting Anael
- MDSDRV + XGM2 Driver Samples
- MegaDriving + variants/upstream
- Shadow Dancer Hamoopig
- SGDK LizarDrive
- Jogo completo: Mega Tetris, Mega Snake, Mega Pong, FireBrawl, Goblin SGDK, Mega Metroid, Penguin World, etc.

---

## Referências

- SGDK oficial: https://github.com/Stephane-D/SGDK
- Canal GameDevBoss: https://www.youtube.com/c/GameDevBoss
- Vídeo instalação: https://youtu.be/H0XNUe4wY7E
- Awesome MegaDrive: https://github.com/And-0/awesome-megadrive

---

**Documento gerado como contexto da coleção. Atualizado 2026-09-02.**
