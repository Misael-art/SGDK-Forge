# Workflow: Scene Architecture Triage

Use este template antes de arte/runtime quando a cena tiver chance honesta de ser `aaa_layered`.

Objetivo:

- evitar reinvencao local precoce
- comparar cedo a cena com o melhor baseline interno disponivel
- nomear a tecnica pelo seu tipo real, nao pelo nome de uma engine
- permitir divergencia sem engessar a solucao
- empurrar bugs residuais para depois da decisao arquitetural
- transformar referencia interna em principio tecnico, nao em copia literal

---

## Quando abrir este template

Abra a triagem quando a cena tiver um ou mais sinais abaixo:

- composicao em camadas com base + foreground/oclusao
- staging visual forte
- relacao importante entre sprite e cenario
- parallax, streaming, priority foreground ou tilemap regional
- risco de workaround precoce com `WINDOW`, VRAM, paleta ou sprite runtime

Se a cena for simples, single-plane ou HUD-first, responda honestamente `scene_profile` como outro tipo e siga adiante sem forcar a BLAZE.

Antes de preencher, consulte `workflows/route-decision-gate.md` se a tarefa ainda nao declarou skill/ferramenta/familia tecnica.

---

## Template canonico

```md
scene_architecture_triage:
  scene_name: "<nome da cena>"
  scene_profile: "aaa_layered | single_plane | hud_heavy | boss_arena | cutscene | fx_driven | outro"
  baseline_technique: "tilemap streaming guiado pela camera"
  baseline_technique_applicability: "sim | parcial | nao"
  reference_implementation: "SGDK_Engines/BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BRIGA DE RUA] | outra | nenhuma"
  baseline_contract:
    base_foreground_split: "<como BG_B/BG_A/base/foreground se dividem>"
    plane_roles: "<papel de BG_A, BG_B, WINDOW e sprites>"
    staging_visual: "<como a cena entra, segura leitura e cria profundidade>"
    tilemap_strategy: "<full resident, preload local, streaming, cache de janela, etc>"
    occlusion_model: "<como a oclusao acontece e em qual plano>"
    sprite_scenery_relation: "<como o heroi/inimigo interage visualmente com o cenario>"
  resource_topology_measurement:
    source_extent: "<tamanho do mundo/imagem total>"
    visible_window: "<janela vista por frame>"
    motion_path: "<camera/scroll previstos>"
    panel_candidates: ["<ex: 160x224: max/p90 tiles unicos>", "<ex: 128x224: max/p90>"]
    resident_window_unique_tiles: "<estimativa simultanea BG_A+BG_B+sprites+fonte/HUD>"
    streaming_boundary: "<onde entram colunas, blocos, paineis ou metatiles>"
    detail_priority: "<onde preservar detalhe maximo e onde simplificar>"
  baseline_decision: "adotar | adaptar | divergir"
  adopted_from_blaze:
    - "<item 1>"
  adapted_locally:
    - "<item 1>"
  rejected_from_blaze:
    - "<item 1>"
  divergence_reason: "<obrigatorio se baseline_decision = divergir>"
  primary_risk_if_skipped: "<qual erro caro tende a acontecer se a triagem for ignorada>"
  residual_debugs_blocked_until_here:
    - "VRAM fina"
    - "paleta"
    - "rescomp"
    - "WINDOW workaround"
    - "sprite runtime visibility"
```

---

## Regra de leitura

Interpretacao esperada:

- `sim`: `tilemap streaming guiado pela camera` serve como baseline principal e a cena deve nascer dessa familia tecnica
- `parcial`: a tecnica cobre parte da arquitetura, mas a cena tem constraints locais relevantes
- `nao`: a cena pertence a outra familia estrutural e a justificativa deve deixar isso claro

Se houver implementacao interna madura, registre-a em `reference_implementation`, mas nao use esse nome como substituto da tecnica.

---

## Passa quando

- o perfil da cena foi nomeado honestamente
- a aplicabilidade da tecnica ficou declarada
- o contrato estrutural foi extraido em linguagem concreta
- mundo total, janela visivel e custo de paineis/janela ativa foram separados quando a cena tiver assets grandes
- ficou claro o que sera adotado, adaptado ou rejeitado
- qualquer divergencia ficou justificada antes de depuracao residual

---

## Nao permitido

- abrir depuracao de VRAM, paleta, `rescomp`, `WINDOW` ou upload de sprite como primeira linha em cena `aaa_layered` sem preencher a triagem
- usar uma engine como dogma quando a cena claramente pertence a outra familia
- dizer que "nao se aplica" sem declarar qual baseline local substitui `tilemap streaming guiado pela camera`
- copiar `IMAGE` ou tamanho de painel de uma referencia interna sem medir a janela real da cena atual
- usar `WINDOW` como mascara de cenario para resolver problema de foreground que deveria pertencer a BG_A, sprite graft ou rota declarada

---

## Handoff

- `workflows/aaa-scene-pipeline.md`
- `workflows/production-loop.md`
- `skills/art/multi-plane-composition`
