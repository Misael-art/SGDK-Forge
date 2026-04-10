# 94 - 16-bit Hardware Mastery Roadmap

Status: `implementation_backlog`

---

## Objetivo

Dar a outra IA um roteiro fechado para elevar o agente de dominio parcial para pericia senior absoluta nas tecnicas hardware-level relevantes para Mega Drive.

Este roadmap assume:

- `93_16bit_hardware_mastery_matrix.md` como mapa humano
- `93_16bit_hardware_mastery_registry.json` como indice machine-readable
- `BENCHMARK_VISUAL_LAB` como unico laboratorio oficial

## Regra de progresso

Nenhuma tecnica sobe de estado sem passar por:

1. skill owner explicito
2. regra ou doc clara
3. artefato reproduzivel
4. build no laboratorio
5. evidence bundle em BlastEm
6. aprovacao humana

## Wave 0 - Auditoria canonica

Entregas:

- manter `93_matrix` e `93_registry` sincronizados
- confirmar dono de skill para cada tecnica
- ligar cada entrada a `lib_case`, `registry_ids` e `benchmark_scene`

Saida esperada:

- nenhuma tecnica relevante fica sem `owner_skills`
- nenhum gap puro fica escondido como se fosse competencia madura

## Wave 1 - Consolidacao do que ja existe

Entregas:

- expandir skills atuais com secao `Senior Competencies`
- unificar linguagem de pericia em:
  - `sgdk-runtime-coder`
  - `megadrive-vdp-budget-analyst`
  - `multi-plane-composition`
  - `visual-excellence-standards`
  - `sprite-animation`
  - `character-design`
- declarar DMA safety e worst-frame budget como checklist obrigatorio

Gate:

- nenhuma tecnica parcialmente coberta continua invisivel dentro da skill dona

## Wave 2 - Raster e iluminacao

Scenes obrigatorias no `BENCHMARK_VISUAL_LAB`:

- `fx_line_scroll_lab`
- `fx_column_scroll_lab`
- `fx_hint_palette_split_lab`
- `fx_shadow_highlight_lab`
- `fx_palette_cycling_lab`

Entregas:

- budget lines em `doc/13-spec-cenas.md`
- validation axes preenchidos
- evidence bundle por scene

Gate:

- linha, coluna, split e cycling rodam sem glitch e com budget declarado

## Wave 3 - Sprite engineering pesado

Scenes obrigatorias:

- `fx_sprite_multiplex_lab`
- `boss_bg_b_bypass_lab`
- `priority_split_foreground_lab`

Entregas:

- regra binaria por tecnica:
  - `permitida`
  - `proibida`
  - `fallback`
- worst-frame budget para scanline pressure

Gate:

- nenhuma tecnica de sprite pesado fica como truque sem governanca

## Wave 4 - Pseudo-3D e articulacao

Scenes obrigatorias:

- `pseudo3d_road_lab`
- `boss_kinematics_lab`

Entregas:

- promover o stack pseudo-3D para `blastem_proven`
- criar skill `forward-kinematics-rigging`
- benchmark minimo de tentaculo, corrente ou braco articulado

Gate:

- articulacao em `fix16` estavel
- prova em ROM sem queda perceptivel de desempenho

## Wave 5 - Audio senior

Scene obrigatoria:

- `audio_xgm2_lab`

Entregas:

- criar skill `xgm2-audio-director`
- provar BGM + 2 SFX + 1 ambiente
- provar `pause`, `resume`, `loop` e ownership de canal

Gate:

- audio deixa de ser categoria ausente do framework

## Wave 6 - Certificacao senior absoluta

Para cada tecnica:

- `lib_case` existe
- scene dedicada existe
- `validation_report` confirma `blastem_gate = true`
- budget esta aprovado
- aprovacao humana esta registrada

Somente entao o `current_status` pode virar `senior_default`.

## Ordem obrigatoria de implementacao

1. consolidar skill owners
2. consolidar benchmark contract
3. promover tecnicas candidatas fortes
4. abrir skills novas para gaps puros
5. certificar por BlastEm e regressao

## Regressao obrigatoria

Toda wave deve reexecutar:

- checklist das tecnicas ja promovidas
- evidence bundle das scenes correlatas
- leitura do `validation_report`

Falha de regressao:

- rebaixa a tecnica para `candidate_with_evidence` ou `partial`
- nunca manter `senior_default` com falha escondida
