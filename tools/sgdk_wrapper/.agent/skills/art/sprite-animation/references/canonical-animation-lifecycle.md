# Lifecycle canonico de animacao SGDK

Este e o unico ciclo global de producao. Os 12 principios atravessam as etapas;
eles nao sao etapas. Os passes P0-P5 de sprite nativa e os antigos 11 passes de
producao sao subrotinas mapeadas aqui, nao workflows concorrentes.

1. `gameplay_scene_brief`
   - papel, camera, oponente, alcance, contato, estados e prioridades do GDD/spec.
2. `source_identity_audit`
   - autoridade visual, proveniencia, model sheet limpo e `must_preserve`.
3. `scale_pivot_collision_budget_lock`
   - escala, canvas, pivot, ground line, boxes e budget preliminar.
4. `native_pose_construction`
   - volumes, turnaround, lineart, materiais, paleta e pose nativa vencedora.
   - Owner: `native-sprite-production`; aqui vivem seus passes P0-P5.
5. `state_roster_motion_language`
   - estados P0/P1, fantasia, perfil de movimento e transicoes.
6. `method_and_key_poses`
   - `pose_to_pose`, `straight_ahead` ou `hybrid`; extremos e breakdowns.
7. `staging_silhouette_appeal_gate`
   - 1x, silhueta, 320x224, identidade, acting e apelo por revisao humana.
   - em forward-test continuo, use `agent_curated_diagnostic_review` para
     rework em staging e mantenha a revisao humana pendente; nunca simule o gate.
8. `timing_spacing_physics`
   - VBlank, arcos, centro de massa, apoio, overlap e secondary action.
9. `native_frame_authorship`
   - inbetweens, line cleaning, clusters, shading e consistencia de materiais.
10. `strip_sheet_metasprite_assembly`
    - uma acao por strip; sheet final so com strips aceitas; layout de hardware
      unico. Sheet de personagem usa `SPRITE`, nao `TILEMAP`, por padrao.
11. `artifact_motion_principles_budget_qa`
    - pixel/celula, semantica, 12 principios, visual cego, tiles/VRAM/DMA/scanline.
12. `runtime_canonization`
    - `res/`, SGDK, timing runtime, ROM, BlastEm, evidencia e decisao final.

## Mapeamento legado

- Os antigos 11 production passes mapeiam principalmente para as etapas 2, 4,
  6-11. Eles nao definem uma segunda ordem.
- P0-P5 de `generation-and-scale-protocol.md` ficam dentro da etapa 4.
- O antigo fluxo de 12 itens em `07_sprite_animation_standards.md` e substituido
  por este lifecycle.

## Roteamento para tilemap e planos

Nao crie tilemap para uma sheet comum. Faça handoff somente quando houver:

- Tiled JSON, tileset, flip flags, colisao/oclusao ou parallax modular:
  `tiled-hybrid-parallax-curator`;
- BG_A/B, WINDOW, composicao em profundidade ou boss tomado por plano:
  `multi-plane-composition`;
- tiles animados, dirty regions, mundo grande ou uploads por janela:
  `vram-streaming-dma-queue`;
- sprites/metasprites comuns: `megadrive-vdp-budget-analyst` e
  `sgdk-runtime-coder`.

O handoff deve registrar por que `SPRITE`, `TILESET`/`TILEMAP`, `IMAGE` ou `MAP`
e a representacao correta. A escolha e de arquitetura visual/hardware, nao uma
preferencia de ferramenta.
