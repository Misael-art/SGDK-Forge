# Workflow: Route Decision Gate

Use este gate antes da primeira implementacao de um projeto novo, reseed ou cena ainda sem familia tecnica definida.

Objetivo:

- escolher a rota de skill/ferramenta antes de tentar converter, codar ou depurar
- evitar que o agente trate sintoma como causa raiz
- preservar a filosofia maximalista sem transformar uma tecnica especifica em dogma

Este gate e curto. Ele nao substitui GDD, budget, arte ou runtime. Ele decide por onde a execucao deve comecar.

---

## Quando abrir

Abrir este gate quando houver qualquer sinal abaixo:

- projeto novo ou reseed
- first playable slice ainda nao materializado
- cena com arte forte, pack externo, spritesheet, parallax ou tilemap grande
- menu/title/front-end que precisa parecer produto final
- HUD/UI, texto expressivo, transicao, audio senior, boss/setpiece ou FX formal
- erro visual/runtime ainda sem causa raiz provada

Se o pedido for uma correcao pontual em contrato ja medido e validado, registrar `route_decision_record: reutilizar_rota_existente` e seguir.

---

## Ordem de decisao

Responder nesta ordem, sem pular:

1. Qual e o tipo de contexto?
2. Qual skill e dona da primeira decisao?
3. Existe builder, manifest, source case ou referencia interna ja curada?
4. Qual e a familia tecnica dominante?
5. Qual ferramenta deve ser rodada primeiro?
6. Qual evidencia decide se a rota esta certa?
7. Quais atalhos ficam proibidos ate essa evidencia existir?

---

## `route_decision_record`

```md
route_decision_record:
  context_type: "projeto_novo | reseed | projeto_existente | cena_nova | bug_visual | bug_runtime"
  affected_surface: "<projeto | cena | menu | HUD | audio | asset | runtime>"
  user_goal: "<objetivo em uma frase>"
  dominant_route: "planning | art_diagnostic | curated_builder | source_translation | conversion_batch | scene_architecture | budget | runtime | validation"
  first_skill: "<skill canonica que deve agir primeiro>"
  supporting_skills:
    - "<skill complementar>"
  first_tool:
    command: "<comando ou none>"
    reason: "<por que esta ferramenta vem antes>"
  existing_curation:
    builder: "<tools/image-tools/build_*.py | none>"
    source_case_manifest: "<doc/source_cases/**/case_manifest.json | none>"
    reference_implementation: "<engine/sample interno | none>"
  technical_family:
    resource_loading_model: "full_resident | scene_local_preload | camera_guided_streaming | tilemap_streaming | animation_window_streaming | fallback_reduced_residency | not_applicable"
    plane_model: "<BG_A/BG_B/WINDOW/SPRITES em uma frase>"
    asset_strategy: "<IMAGE | MAP | panels | metatiles | spritesheet window | procedural | mixed>"
  evidence_required:
    - "<relatorio, build, captura ou medicao que fecha a decisao>"
  forbidden_shortcuts_until_evidence:
    - "<atalho que nao pode ser usado ainda>"
  handoff_next: "<workflow/skill seguinte>"
```

---

## Matriz de rota

| Sinal | Primeira rota |
|-------|---------------|
| projeto novo, fantasia, genero e escopo ainda abertos | `planning/game-design-planning` |
| assets desconhecidos em `data/` ou `res/` | `art/art-asset-diagnostic` |
| pack visual forte, concept, source grande ou spritesheet | `art/art-translation-to-vdp` depois do diagnostico |
| builder dedicado em `tools/image-tools/build_*.py` | rodar builder curado antes de OCR/crop/lote generico |
| `doc/source_cases/**/case_manifest.json` existe | consumir manifest como fonte de verdade antes de inferir |
| cena com base + foreground/oclusao + sprite/cenario | `workflows/scene-architecture-triage.md` |
| cenario largo, parallax, metatile, stage ou mundo maior que a janela | `camera_guided_streaming` ou `tilemap_streaming` devem ser avaliados antes de `full_resident` |
| sheet de personagem grande | `animation_window_streaming` ou SGDK auto VRAM alloc antes de reprovar por sheet completa |
| HUD/menu/title/texto expressivo | `ui_decision_card` e anexos antes de runtime |
| transicao formal | `scene_transition_card` antes de runtime |
| audio com stinger/ambience/PCM/voz | `audio_architecture_card` e skills de audio antes de runtime |

---

## Debug visual/runtime: escada obrigatoria

Quando a ROM builda mas a cena falha visualmente, investigar nesta ordem:

1. objeto existe e foi criado?
2. posicao real esta on-screen?
3. coordenadas usam o contrato correto da API?
4. camera/scroll/plane transformam a posicao?
5. prioridade e oclusao entre BG_A, BG_B, WINDOW e SPRITES estao corretas?
6. paleta, index 0, transparencia e PLTE estao corretos?
7. tiles unicos e VRAM residente cabem no budget real?
8. `rescomp`, compressao, DMA e streaming estao coerentes?

Regra SGDK importante:

- `SpriteDefinition.w` e `SpriteDefinition.h` devem ser tratados como pixels no runtime gerado, nao como contagem de tiles.

---

## Regras anti-tentativa

- Nao usar OCR, thumbnails ou crop manual se existir builder ou manifest curado.
- Nao usar `WINDOW` para simular foreground/oclusao de cenario; `WINDOW` e HUD/interface fixa salvo justificativa formal.
- Nao carregar prancha grande inteira como `IMAGE` quando a cena pede streaming, paineis, metatiles ou camera.
- Nao mexer em `resources.res` para "ver se aparece" antes de provar posicao, plano e budget.
- Nao declarar `testado_em_emulador` por build ou por `READY`; precisa evidencia semantica da cena correta.

---

## Passa quando

- a rota dominante ficou clara
- a primeira skill/ferramenta foi escolhida por contrato, nao por tentativa
- atalhos perigosos ficaram bloqueados ate a evidencia certa existir
- a proxima etapa sabe exatamente qual artefato consumir
