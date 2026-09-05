# Changelog — GOTHAM_OVERDRIVE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

## [0.2.0] - 2026-08-29
### Adicionado
- Síntese e injeção de 11 assets gráficos padrão AAA em pixel art autêntica dos anos 90 no estilo Dark Deco (Gotham Skyline BGB, Perspective Roadway BGA, Batmóvel 4 frames, Chassi Two-Face, Torre giratória 8 direções, Esteiras animadas, Pod lançador, Drones de ataque, Atlas de projéteis e Atlas de partículas).
- Quantização rigorosa em espaço de cores 9-bit RGB do Mega Drive e paletas indexadas a 4 bits por plano (`PAL0` a `PAL3`).
- Geração e registro da cadeia de proveniência autoral em `doc/asset_provenance_manifest.json` e armazenamento das fontes em `data/source_art/`.
- Aprovação integral de todos os gates de auditoria estética (`audit_procedural_asset_provenance.py` e `validate_brand_comprehension_gate.py`).
- Recompilação e validação do binário da ROM (`out/rom.bin`) via toolchain SGDK 2.11 GCC m68000.

## [0.1.0] - 2026-08-15
### Adicionado
- Criação e estruturação canônica do projeto de laboratório/tech demo `GOTHAM_OVERDRIVE`.
- Implementação da engine de raster scroll multi-eixo pseudo-3D com 224 scanlines de `HSCROLL_LINE` e 20 colunas de `VSCROLL_COLUMN` (`gotham_raster.c`).
- Implementação do Batmóvel do jogador com canhões Vulcan duplos, mísseis Batarang e turbo afterburner com física em ponto fixo (`gotham_player.c`).
- Implementação do Chefe Colossal Modular "Two-Face Siege Dreadnought" composto por 5 sprites de hardware articulados e máquina de estados de combate (`gotham_boss.c`).
- Implementação de esquadrão de drones de escolta biônicos com trajetória senoidal (`gotham_enemies.c`).
- Implementação de pool estático de partículas e projéteis com zero alocação dinâmica (`gotham_particles.c`).
- Implementação de sistema de telemetria com HUD de monitoramento de carga de CPU, contagem de hardware sprites e taxa de 60 FPS ao vivo (`telemetry.c`).
- Compilação limpa da ROM `out/rom.bin` no SGDK 2.11 com compilador GCC m68k.
