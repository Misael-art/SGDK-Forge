# 15 - Technical Design Document - HYBRIDO_MUAY_THAI [VER.001] [SGDK 211] [GEN] [ESTUDO] [LUTA]

O TDD descreve como o jogo sera construido. Ele nao substitui o GDD; traduz as escolhas de design em arquitetura, memoria, VDP, audio, input e validacao.

## 1. Contexto Tecnico

- Contexto do projeto: ver `doc/project_context_manifest.json`
- Teto de entrega tecnica: [prototype/technical_demo/vertical_slice/ready_for_aaa]
- Hardware alvo: Mega Drive
- SDK: SGDK 2.11
- Regiao alvo: [NTSC/PAL/ambas]

## 2. Arquitetura

- Modelo de cenas: [FSM/scene manager/etc]
- Estrutura de modulos: [src/inc/res/data]
- Estado global permitido: [listar]
- Buffers estaticos: [listar]
- Proibicoes: sem `float`, sem `malloc/free`, sem API SGDK inventada

## 3. Sistemas

### Input

- Latencia alvo:
- Mapeamento:
- Estados que consomem input:

### Gameplay

- Sistemas core:
- Sistemas secundarios:
- Pool de atores/projeteis/particulas:

### Render e VDP

- Planos usados: [BG_A/BG_B/WINDOW/sprites]
- Tecnicas escolhidas com registry ID/tag:
- Budget VRAM:
- Budget DMA por frame:
- Budget sprites/SAT:
- Fallbacks:

### Audio

- Driver:
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
| [risco] | [impacto] | [acao] | [report] |

## 6. Validacao

- Build canonico:
- BlastEm:
- Freshness audit:
- Scene closeout:
- QA:

## 7. Atualizacao

Mudanca de arquitetura, tecnica, cena, budget ou pipeline exige atualizar:

- `doc/10-memory-bank.md`
- `doc/changelog/changelog.md`
- `doc/13-spec-cenas.md`
- `doc/technique_usage_manifest.json`
