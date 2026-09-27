# 15 - Technical Design Document - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

O TDD descreve como o jogo sera construido. Ele nao substitui o GDD; traduz as escolhas de design em arquitetura, memoria, VDP, audio, input e validacao.

## 1. Contexto Tecnico

- Contexto do projeto: ver `doc/project_context_manifest.json`
- Teto de entrega tecnica: `technical_demo`; nenhum contrato eleva o projeto a AAA.
- Hardware alvo: Mega Drive
- SDK: SGDK 2.11
- Regiao de performance: NTSC, budget nominal16,667 ms/frame. PAL ainda precisa de execucao propria.
- Estado real do palco: pre-producao. A ROM principal observada (SHA `20034654...`) ainda tem fundo solido.

## 2. Arquitetura

- Modelo de cenas: sequencia branding -> front-end -> first_playable_slice -> resultado/retorno; ownership de VDP/CRAM/audio em transicoes ainda requer verificacao de ponta a ponta.
- Estrutura: C SGDK em `src/`/`inc/`; recursos `.res` ativos em `res/`; runtime do conversor e fonte canonica compartilhada em `tools/mugen2sgdk_forge/runtime/`.
- Estado global permitido: fight state do `mg_fight` e estado de cada cena; nao introduzir segundo owner de camera, scroll ou CRAM.
- Buffers estaticos: tabelas de flash ja existentes; futuros mapas de H-scroll e buffers `DMA_QUEUE` devem ter vida estatica/ate completar o VBlank.
- Proibicoes: sem `float/double`, `malloc/free`, APIs SGDK inventadas, DMA fora de VBlank ou pixel art final feita por primitivas.
- Contrato executavel: `doc/tdd_contract.json`; camera: `doc/camera_behavior_contract.json`.

## 3. Sistemas

### Input

- Latencia alvo: 1 quadro NTSC nominal (16,667 ms); input do menu, luta e comandos especiais precisa de prova observada.
- Mapeamento: snapshot SGDK por quadro; held/pressed/released devem permanecer separados para menu e parser de comandos MUGEN.
- Estados que consomem input: front-end, fight e resultado/rematch; intro, hitpause e super podem consumir comandos segundo as regras de gameplay.

### Gameplay

- Sistemas core: runtime convertido MUGEN para movimento, FSM, colisao, comandos, rounds, push e camera de midpoint.
- Sistemas secundarios: projeteis, explods, flash de CRAM, hitstop, shake e super-background; seus picos combinados ainda pedem captura sincronizada.
- Pools: dois fighters; `MG_MAX_PROJ=4` por fighter; `MG_MAX_EXPLOD=6`. O tamanho da reserva de VRAM de sprites nao sera reduzido com base em probe sem stage/audio.

### Render e VDP

- Planos usados: BG_A/BG_B para cenario, WINDOW para HUD fixo, sprites para fighters/FX. O palco Suzaku ainda nao esta integrado.
- Tecnicas selecionadas para medicao: `line_scrolling` (`LINE_SCROLL`, `PARALLAX`), `camera_scroll_management`, `advanced_tilemap_design`, `dma_transfer_safety` e `palette_state_transitions`; detalhes em `doc/technique_usage_manifest.json`.
- Budget VRAM: `fight_vram` mediu uma regiao hipotetica de446 tiles sob sprite pool600 e emprestimo do BGFX. Nao e valor de producao aprovado. Relatorio Suzaku anterior estimou ate845 padroes simultaneamente visiveis; novo inventario mede padroes fonte, nao ResComp nem viewport.
- Budget DMA por quadro: nao fechado. HSCROLL_LINE deve registrar bytes por tabela, frequencia de atualizacao e pico da fila VBlank; carga grande so no preload.
- Budget sprites/SAT: H40 limites20 sprites e320 pixels por scanline; super atual ja excedeu ambos em simulacao (28/832) e decomposicao de sheets ainda e pendente.
- Candidato de profundidade: no crop16, BG3/BG4a/BG4b alinham em faixas `[0,176)`, `[176,212)`, `[212,224)` com deltas0.671875/0.792410/1.102678. BG_B continua compromisso artistico por causa de camadas sobrepostas.
- Fallback: manter mundo640 e plano-level scroll; nao adicionar Mode7, terceira plane rolavel ou pool reduzido sem medicao e revisao.

### Audio

- Driver: XGM2 existente; nenhum driver PCM custom autorizado/necessario ate os testes mostrarem limitacao concreta.
- Canais e prioridade: prioridade de BGM, vozes, impacto, round e super pendente de decisao e medicao simultanea.
- SFX criticos: hit/guard, hadouken, super, KO e cues de transicao.
- Politica de mascaramento: musica de luta com loop, sem corte ao emitir cue; verificar canais YM2612/PSG, clipping, underrun e mix por escuta humana.
- Status: faixa final de luta e teste audiovisual no mesmo SHA ainda pendentes; audio nao aprovado.

### Save / Persistencia

- Escopo: none nesta demo de conversao.
- Checksum/duplicacao: nao aplicavel; SRAM continua usada apenas para evidencia de emulador/test harness, nao como progresso de usuario.

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

- Build canonico: wrapper SGDK 2.11 deste workspace; build do palco so apos relatorios estruturais e assets com proveniencia.
- BlastEm: obrigatorio por SHA exato; ainda nao existe captura da cena Suzaku integrada.
- Freshness audit: pendente para os artefatos novos depois da sincronizacao integral.
- Scene closeout: pendente; requires `scene_tilemap_conversion_report`, `per_tile_palette_conflict_report`, `tilemap_flag_report`, `res_graph`, `validation`, runtime, budget DMA/VRAM, regressao e emulator session.
- QA: 90 testes da suite do conversor passaram nesta rodada; isso valida tooling, nao o palco no hardware.

## 7. Atualizacao

Mudanca de arquitetura, tecnica, cena, budget ou pipeline exige atualizar:

- `doc/10-memory-bank.md`
- `doc/changelog/changelog.md`
- `doc/13-spec-cenas.md`
- `doc/technique_usage_manifest.json`
