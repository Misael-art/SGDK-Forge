# Arquitetura de validacao de animacao ligada ao artefato

Use esta referencia ao produzir, revisar ou promover strips. Ela fecha os falsos
verdes que metadados, contact sheets e previews auto-declarados nao conseguem
fechar sozinhos.

## Autoridades

1. O PNG indexado e o artefato medido.
2. `animation_strip_contract` v3 passa no schema embutido e vincula PNG,
   fonte autoral, produtor, lineart, timing, perfil e layout.
3. Os validators rederivam medidas do arquivo; reports nao provam a si mesmos.
4. Revisao visual humana decide leitura, identidade, acting e apelo.
5. ROM + BlastEm decide runtime. Nenhuma etapa inferior herda esse claim.
6. `animation_principles_report` demonstra os 12 principios por acao; nao cria score artistico.

## Pipeline minimo

```text
lineart/topologia -> strip/celulas -> semantica temporal -> agregado de claims
                 -> 12 principios + revisao visual cega -> budget -> res -> ROM/BlastEm
```

Comandos canonicos:

```bash
python3 tools/sgdk_wrapper/.agent/scripts/validate_lineart_topology.py \
  --input <lineart.png> --output <lineart_report.json>

python3 tools/sgdk_wrapper/.agent/scripts/validate_animation_strip_artifact.py \
  --project-root <projeto> --input <strip_contract.json> \
  --output <strip_validation_report.json>

python3 tools/sgdk_wrapper/.agent/scripts/validate_motion_semantics.py \
  --project-root <projeto> --contract <strip_contract.json> \
  --output <motion_semantics_report.json>

python3 tools/sgdk_wrapper/.agent/scripts/render_animation_evidence.py \
  --project-root <projeto> --contract <strip_contract.json> \
  --output <preview.gif> --scale 1

python3 tools/sgdk_wrapper/.agent/scripts/validate_animation_candidate.py \
  --project-root <projeto> --manifest <animation_candidate_manifest.json> \
  --output <animation_candidate_gate_report.json>
```

## O que o contrato v3 precisa vincular

- `artifact.path` e SHA-256 do strip real;
- celulas horizontais exatas e contatos de borda por frame/edge;
- `state_lineart_lineage.source_path` e SHA-256, quando o asset declara lineart;
- autoria, derivacao e aprovacao hash-bound da lineart; contorno procedural e probe;
- lineage por frame e tipo de transformacao;
- contato de apoio medido no PNG ou anotado por evidencia hash-bound;
- `motion_profile_id` do registry, sem perfil codificado por personagem;
- uma unica tabela `timing_contract.frame_holds_vblank`;
- preview opcional vinculado por hash; se existir, seus delays devem coincidir;
- um unico `metasprite_layout` compartilhado por reports de budget/runtime.
- `production_provenance` com bitmap autoral persistido e record do produtor.
  Raster criado por ASCII, spans, primitivas ou codigo e probe procedural,
  independentemente do nome do PNG ou da declaracao escrita pelo produtor.

Uma grade inteira replicada exatamente 2x/3x/4x revela resolucao efetiva menor;
nao passa como autoria nativa no canvas maior. O schema e validado pelo proprio
validator, sem depender de pacote opcional do host.

`fixed_cell` nao autoriza clipping. Contato legitimo com borda precisa de entrada
coordenada em `allowed_boundary_contacts`; fragmentos alinhados entre a borda
direita de uma celula e a esquerda da proxima continuam bloqueados.

## Perfis de movimento

O registry em `motion_profile_registry.json` define fases e limites proporcionais
para familias de acao. Ele serve para detectar contradicoes grosseiras, nao para
transformar animacao em score unico. Adicione um perfil somente quando uma nova
familia de movimento nao couber nas existentes; nao crie perfil por personagem.

Frame duplicado nao representa tempo. Segure o frame por VBlank. Reuso identico
entre acoes exige justificativa explicita no agregado; reordenar celulas-fonte e
rotula-las como outra acao e blocker.

Variacoes por resize, deslocamento, crop ou paleta da mesma pose tambem nao
representam autoria temporal. `source_frame_id` e unico por key pose/inbetween;
`mechanical_affine_probe` pode comparar uma hipotese, mas nao prova movimento.

## Gate visual cego

Depois dos gates automaticos, apresente a animacao sem o nome da acao e registre:

- qual acao revisores reconheceram;
- leitura em 1x e em camera 320x224;
- fidelidade ao model sheet e direcao;
- foot slide, pivot, peso, arco, anticipation e recovery observados;
- status `passed`, `needs_review` ou `failed` vinculado ao SHA do strip.

O agregado exige `blind_visual_review=passed`, `fidelity=passed` e
`art_direction=passed` antes de `human_review_candidate`. Um
`sprite_artifact_report.visual_pass=true` nao pode sobrepor qualquer um deles.
Sem reconhecimento cego da acao, o teto e `technical_candidate`, ainda que
perfil, delta, timing e integridade estrutural tenham passado.

Tambem exige `animation_principles_report=passed`, ligado ao SHA de cada strip e
com os 12 IDs exatos. `staging`, `exaggeration`, `solid_drawing` e `appeal`
precisam de evidencia `human_visual_review`; medicao automatica apenas apoia a
decisao. O metodo `pose_to_pose`, `straight_ahead` ou `hybrid` e declarado por
acao. Cobertura incompleta, falso `not_applicable` ou `needs_review` bloqueiam o
gate humano.

## Teto de claim

```text
technical_candidate
  -> motion_semantic_candidate
  -> human_review_candidate
  -> ready_for_res
  -> runtime_candidate
  -> ready_for_aaa (somente guardian completo)
```

Cada seta depende de reports hash-bound. Divergencia de timing, layout de
metasprite ou status visual rebaixa o claim; nao se arredonda para cima.

## Blockers permanentes

- `neighbor_cell_fragment_detected`
- `unexpected_frame_boundary_contact`
- `lineart_fill_masquerading_as_contour`
- `lineart_stroke_over_1px`
- `action_is_reordered_source_cells`
- `undeclared_duplicate_frame`
- `cross_action_frame_reuse`
- `motion_profile_mismatch`
- `gif_delay_contract_mismatch`
- `metasprite_layout_conflict`
- `visual_pass_self_asserted`
- `claim_dependency_violation`
- `human_gate_opened_on_failed_candidate`
- `animation_principles_incomplete`
- `animation_principle_illegal_not_applicable`
- `animation_principle_human_review_missing`
- `single_pose_affine_animation_masquerade`
- `mechanical_probe_cannot_prove_motion`
- `procedural_contour_declared_native_lineart`
- `support_contact_not_artifact_bound`
- `motion_semantic_report_outdated`
- `strip_contract_has_unresolved_motion_blocker`
- `animation_principles_evidence_kind_invalid`
- `animation_strip_schema_invalid`
- `native_lineart_approval_status_invalid`
- `native_pixel_integer_scale_masquerade`
- `animation_production_provenance_missing`
- `code_authored_character_pixels`

As fixtures adversariais vivem em
`tools/sgdk_wrapper/ci/fixtures/animation_validation/fixture_manifest.json` e
sao exercitadas por `tools/sgdk_wrapper/test_animation_validation.py`.
