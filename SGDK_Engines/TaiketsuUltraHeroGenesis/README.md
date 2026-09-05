# TaiketsuUltraHeroGenesis — Engine de Luta SGDK (Mega Drive/Genesis)

Engine de fighting baseada em **HAMOOPIG** de GameDevBoss (Daniel Moura), adaptada como projeto open-source para estudo de:
- Sistemas de sprites / tilemaps (SGDK)
- FSM de movimento e combate (idle, walk, jump, attack ligh/medium/heavy, guard, hit reaction)
- Sistema de hitboxes e física de combate (body space, gravidade, furious timer)
- Geração de sons (SFX banks)
- Menu, tela de logo, descompressão, round system, placar energético

## Origem
- Autor original: GameDevBoss (Daniel Moura) 2015–2022
- Repo: https://github.com/guilhermesousa03/TaiketsuUltraHeroGenesis.git
- Canal: https://www.youtube.com/c/GameDevBoss
- Licença: ver `LICENSE` no repositório (HAMOOPIG é gratuito e open-source; manter créditos ao criador original)

## Estrutura
```
TaiketsuUltraHeroGenesis/
├── src/
│   ├── main.c            (5.600 linhas — engine de luta completa)
│   ├── sprite.h          (definições de sprites, estados, frames)
│   ├── gfx.h             (fontes, paletas, tiles)
│   ├── sound.h           (definições de SFX)
│   ├── res/
│   │   ├── gfx/          (graficos tileset)
│   │   │   └── gfx.res   (resource file)
│   │   ├── sprite/       (sprites dos personagens jack/ryo + efeitos)
│   │   │   ├── jack/     (sprites player 1)
│   │   │   └── ryo/      (sprites player 2)
│   │   │   ├── spr_rect_*.png
│   │   │   └── spr_spark*.png
│   │   ├── gfx.res
│   │   ├── sprite.h (sprites definitions)
│   │   ├── sprite.res
│   │   └── sound.res
│   ├── out/              (build artifacts — rom.bin, rom.out, .o, .d)
│   │   ├── rom.bin       (ROM compilada — 917 KB)
│   │   ├── rom.out
│   │   ├── main.o
│   │   ├── main.d
│   │   ├── symbol.txt
│   │   └── src/ + res/
│   ├── src/              (código fonte boot)
│   │   └── boot/
│   ├── COMPILAR.bat      (script Windows — compila código apenas)
│   ├── COMPILAR_E_ATUALIZAR_ASSETS.bat (compila + atualiza assets)
│   ├── LEIA-ME.txt       (instruções de compilação para Windows)
│   ├── READ-ME.txt
│   ├── HAMOOPIG_1.0_DOC.pdf (documentação do engine)
│   ├── HAMOOPIG_color.png
│   ├── HAMOOPIG_icon.png
│   ├── HAMOOPIG_lineart.png
│   └── LICENSE
```

## Dependências de build
- **SGDK** (Sega Genesis Development Kit) — instalado em `C:\SGDK\` no Windows do autor. No Linux, o SGDK deve estar no PATH ou definido via `SMSGDK_HOME`.
- **Java** (usado pelo SGDK em alguns scripts)
- **m68k cross-compiler** (m68k-elf-gcc) — parte do SGDK
- **Emulador**: BizHawk (autor usa) ou BlastEm, Fusion, Gens K-Mod para testar a ROM

## Como compilar (Linux)

### Pré-requisitos
1. Instalar SGDK no sistema (ex: `~/.sgdk` ou `/opt/sgdk`)
2. Exportar `export SGDK_HOME=/caminho/para/sgdk`
3. Garantir que `m68k-elf-gcc` está no PATH

### Makefile
```makefile
# Makefile para Linux — TaiketsuUltraHeroGenesis
# Requer SGDK instalado com m68k-elf-gcc no PATH

SGDK_HOME ?= $(HOME)/.sgdk
M68K := $(SGDK_HOME)/bin/m68k-elf-gcc
PYTHON := python3

# Diretório de output
OUT_DIR := out
RES_DIR := res

# Fontes
C_SRCS := src/main.c
RES_SRCS := $(wildcard res/*.res)

# Objetos
OBJS := $(C_SRCS:src/%.c=out/%.o)

# Alvo principal
rom.bin: $(OBJS) $(RES_SRCS)
	@mkdir -p $(OUT_DIR)
	$(M68K) -o $(OUT_DIR)/rom.bin $(OBJS) -lgcc -lres -I$(SGDK_HOME)/include
	@echo "ROM gerada: $(OUT_DIR)/rom.bin"

# Compilar fonte
out/%.o: src/%.c
	@mkdir -p $(dir $@)
	$(M68K) -c $< -o $@ -I$(SGDK_HOME)/include -Ires -O2

# Resource files (.res) — usa o resource compiler do SGDK
%.res: %.png
	$(SGDK_HOME)/bin/rescomp $< $@

clean:
	rm -rf out/

.PHONY: clean
```

## Como estudar o código

1. **Engine de FSM**: `FUNCAO_FSM()` — máquina de estados do personagem (idle, walk, jump, attack, guard, hit, etc.)
2. **Hitboxes**: `FUNCAO_FSM_HITBOXES()` — hitbox generation per state
3. **Física**: `FUNCAO_PHYSICS()` — movimento, gravidade, body space (BODYSPACE 15), furious timer (RAGETIMER 600)
4. **Sprites**: `sprite.h` — definições de sprites, frames, animações
5. **SGDK API**: consultar headers em `sdk/` ou documentação oficial do SGDK

## Pontos de atenção para Portugual learning

- `VRAM_SIZE 600` no main.c parece ser **bytes** reservados para sprites em VRAM — verificar se é 600 bytes ou se há relação com VRAM total do Genesis (64KB VRAM). Pode ser um valor de prova de conceito.
- O projeto usa **6 botões** (LP/MP/HP/LK/MK/HK) — compatível com controlador 6-button Genesis
- Sistema de rosters: rooms enum `R_TELA_HAMOOPIG`, `R_TELA_LOGO`, `R_MAIN_MENU`, `R_DESCOMPRESSION`, `R_IN_GAME`, `R_AFTER_MATCH` — fluxo completo de jogo
- Veja `sprite.h` para entender como os sprites de jack/ryo são definidos e animados

## Links úteis
- SGDK oficial: https://github.com/Stephane-D/SGDK
- Canal GameDevBoss: https://www.youtube.com/c/GameDevBoss
- Vídeo de instalação SGDK: https://youtu.be/H0XNUe4wY7E
