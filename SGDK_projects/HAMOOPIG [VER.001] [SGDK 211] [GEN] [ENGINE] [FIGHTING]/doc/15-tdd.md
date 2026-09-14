# 15 - Technical Design Document - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

O TDD descreve como o jogo sera construido. Ele nao substitui o GDD; traduz as escolhas de design em arquitetura, memoria, VDP, audio, input e validacao.

## 1. Contexto Tecnico

- Contexto do projeto: ver `doc/project_context_manifest.json`
- Teto de entrega tecnica: prototype
- Hardware alvo: Mega Drive
- SDK: SGDK 2.11
- Regiao alvo: NTSC para a prova atual; PAL ainda nao qualificado

## 2. Arquitetura

- Modelo de cenas: FSM global por `gRoom` (1 título/menu persistente, 2 seletor, 9 descompressao, 10 luta, 11 pos-partida)
- Estrutura de modulos: `main.c` orquestra; `init.c` possui reset; `select.c` possui seletor; `hud.c` possui WINDOW; `player.c` possui estado do lutador
- Estado global permitido: `P`, `GE`, `Spark`, clock, round/wins e camera em `globals.h`; cada cena limpa ou preserva explicitamente seus campos
- Buffers estaticos: `palette[64]`, scroll tables e arrays dentro de `PlayerDEF`; sem heap no gameplay
- Proibicoes: sem `float`, sem `malloc/free`, sem API SGDK inventada

## 3. Sistemas

### Input

- Latencia alvo: uma leitura por frame antes da FSM/animacao
- Mapeamento: dois pads de seis botoes; A confirma/revanche, START confirma/retorna ao seletor no pos-partida
- Estados que consomem input: seletor, luta e pos-partida

### Gameplay

- Sistemas core: luta 1v1, dano/KO, melhor de tres, time over, projetil, hit pause, HUD e camera
- Sistemas secundarios:
- Pool de atores/projeteis/particulas:

### Render e VDP

- Planos usados: BG_B palco, BG_A texto/transitorios, WINDOW barras/relogio, sprites lutadores/efeitos/KO
- Tecnicas escolhidas com registry ID/tag:
- Budget VRAM:
- Budget DMA por frame:
- Budget sprites/SAT:
- Fallbacks:

### Audio

- Driver: XGM1
- Canais e prioridade:
- SFX criticos:
- Politica de mascaramento:

### Save / Persistencia

- Escopo: [none/SRAM/etc]
- Checksum/duplicacao:

## 4. Contratos de Cena

Cada cena deve aparecer em `doc/13-spec-cenas.md` e declarar:

- `scene_id`
- tecnicas usadas com registry ID/tag
- owner skill
- budget
- fallback
- evidencia esperada

## 5. Riscos Tecnicos

| Risco | Impacto | Mitigacao | Evidencia |
|---|---|---|---|
| Sprite Safe retornar NULL | travamento ao posicionar/flipar | guards antes de APIs de Sprite | build + BlastEm |
| Sprites grandes | drop/flicker/VRAM | manter ceiling prototype e medir separadamente | ResComp + evidencia visual |
| Reset parcial | estado vaza entre rounds | reset integral, preservando somente ID/paleta/wins | prova de round |
| Tick de clock dependente da regiao | duracao divergente | constante arcade explicita; PAL nao qualificado | QA NTSC/PAL futura |

## 6. Validacao

- Build canonico: `tools/sgdk_wrapper/build_sgdk_wine_bridge.sh`
- BlastEm: captura deve usar `out/rom.bin` fresco e registrar hash/sessao
- Freshness audit:
- Scene closeout:
- QA:

## 7. Atualizacao

Mudanca de arquitetura, tecnica, cena, budget ou pipeline exige atualizar:

- `doc/10-memory-bank.md`
- `doc/changelog/changelog.md`
- `doc/13-spec-cenas.md`
- `doc/technique_usage_manifest.json`
