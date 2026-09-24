# 15 - Technical Design Document - BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BEAT_EM_UP]

O TDD descreve como o jogo sera construido. Ele nao substitui o GDD; traduz as escolhas de design em arquitetura, memoria, VDP, audio, input e validacao.

## 1. Contexto Tecnico

- Contexto do projeto: ver `doc/project_context_manifest.json`
- Teto de entrega técnica: `prototype`
- Hardware alvo: Mega Drive
- SDK: SGDK 2.11
- Região alvo: NTSC primeiro; PAL fica como validação posterior.

## 2. Arquitetura

- Modelo de cenas: máquina de estados legada por `room`, preservada nesta porta.
- Estrutura de módulos: `src/main.c` legado + `src/boot`, `res/`, `doc/` e wrappers centrais.
- Estado global permitido: estado legado da engine, sem expansão de escopo nesta iteração.
- Buffers estáticos: structs `P[3]`, `E[MAX_ENEMYS]`, arrays de input e strings existentes.
- Proibicoes: sem `float`, sem `malloc/free`, sem API SGDK inventada

## 3. Sistemas

### Input

- Latência alvo: até 1 frame para o polling no início do loop.
- Mapeamento: JOY1/JOY2, direções, A/B/C/X/Y/Z, START e MODE.
- Estados que consomem input: créditos, menu principal, seleção e gameplay.

### Gameplay

- Sistemas core:
- Sistemas secundarios:
- Pool de atores/projeteis/particulas:

### Render e VDP

- Planos usados: BG_A, BG_B e sprites; WINDOW não é usado na fonte.
- Técnicas escolhidas com registry ID/tag: `full_resident` para o smoke; sem técnica experimental promovida.
- Budget VRAM: medir após ResComp; não declarar `cabe` antes do laudo.
- Budget DMA por frame: apenas filas SGDK/VBlank; uploads de sprites seguem a política do sprite engine.
- Budget sprites/SAT: medir a cena carregada, com atenção a 20 sprites/320 pixels por scanline em H40.
- Fallbacks: `fallback_reduced_residency` se o conjunto original não couber.

### Audio

- Driver: XGM PCM já usado pela fonte.
- Canais e prioridade: canais PCM definidos pelos IDs legados 64–67.
- SFX críticos: confirmação, voz de seleção, impacto e eventos de combate.
- Política de mascaramento: não alterar até existir evidência de áudio no emulador.

### Save / Persistencia

- Escopo: `none` nesta porta técnica.
- Checksum/duplicação: não aplicável.

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
