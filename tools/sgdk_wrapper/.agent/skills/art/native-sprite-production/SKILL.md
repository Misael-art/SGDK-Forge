---
name: native-sprite-production
description: Use quando personagem, inimigo, boss, objeto ou FX autoral precisar sair de concept, arte de IA ou raster high-res e chegar a sprite nativa SGDK, com escala, clusters, paleta, validacao, budget, animacao e evidencia. Nao use para background/tilemap, asset ja nativo que pede apenas conversao, ou timing de animacao isolado.
---

# Native Sprite Production

Orquestra a producao completa de sprites nativas sem confundir uma boa imagem-fonte com o asset que entra no jogo.

## Owners especializados

Coordene `character-design`, sourcing/geracao, `art-translation-to-vdp`,
`sprite-animation`, conversao/pixel-strict, `visual-excellence-standards`, budget
VDP e runtime/evidencia. Esta skill organiza os handoffs; nao substitui os owners.

## Ler antes de agir

1. `tools/sgdk_wrapper/.agent/workflows/native-sprite-production-loop.md`
2. `references/source-route-triage-protocol.md` quando a entrada nao for pixel art nativa limpa
3. `references/generation-and-scale-protocol.md` quando houver geracao por IA, fonte high-res ou duvida de escala
4. `../sprite-animation/SKILL.md` e seus contratos quando o alvo incluir key poses, strips ou sheet
   - nesse caso, `../sprite-animation/references/canonical-animation-lifecycle.md` e a ordem global; P0-P5 desta skill ocupam somente `native_pose_construction`
5. `doc/03_art/02_visual_feedback_bank.md` e a barra visual do projeto
6. `doc/11-gdd.md`, `doc/13-spec-cenas.md` e o contrato de escala do personagem
7. `../sprite-animation/references/uninterrupted-forward-production-policy.md` quando o usuario pedir forward-test sem gates humanos intermediarios

## Contrato operacional

### Entrada minima

- projeto/papel de gameplay/camera, fonte aprovada com hash, `must_preserve`,
  escala `locked`/`provisional`, materiais e `native_sprite_production_record`

### Saida minima

- `native_sprite_production_record` validado
- fonte visual persistida e classificada
- shape-block nativo: `silhouette_mask`, `semantic_region_map`,
  `contour_overlay`, regioes obrigatorias, ocupacao e bbox
- depois do color blocking, `material_region_contract` independente da anatomia:
  `material_region_map`, `material_boundary_overlay`, indices permitidos por
  material, outline compartilhado e fronteiras criticas. `torso` nao prova onde
  roupa termina e pele comeca
- `lineart_blocking_1px`
- `palette_role_map` com no maximo 15 cores visiveis
- candidata nativa e `pixel_compliance_report`
- `foreground_matte_report` quando o alpha nao for confiavel
- 1x, nearest e fundos claro/escuro/chroma, distintos e do mesmo hash
- decisao de escala (scale report) e budget
- `incumbent` e `methodology_reference` com hash, apenas comparativos

Validacao semantica executavel:

```bash
python3 tools/sgdk_wrapper/validate_native_sprite_production.py \
  --project-root "<projeto>" \
  --record "<projeto>/doc/art/<asset>/native_sprite_production_record.json"
```

Veredito `passed` e requisito de promocao; veredito `failed` e consumido pelo
`aaa-pipeline-guardian` como `native_sprite_semantic_gate_failed`.

### Passa quando

- produtor visual e autor nativo sao papeis separados
- fonte high-res passa por `source-audit`; sombra de chao, poeira, fumaça,
  nuvem, particula, checkerboard, texto ou oclusao nao podem ser confundidos
  com corpo, cabelo, roupa ou pe. Fonte contaminada fica reference-only e pede
  model sheet limpo
- quando houver mais de uma rota mecanica aplicavel, `route-shootout` produz o
  painel causal antes da autoria cara; prior historico ordena a busca, nunca
  escolhe vencedor nem transforma filtro em arte nativa
- imagem RGB/high-res, fake pixel art ou checkerboard assado fica `visual_source`; nunca `native_candidate`
- `forge-art convert` sozinho produz controle/probe; traducao assistida ainda
  exige fidelidade, 1x, escala, budget e humano
- escala travada nunca muda por resize silencioso
- os passes P0-P5 de `generation-and-scale-protocol.md` e o validator fecham
  grid, alpha, paleta, silhueta, semantica, metasprite e budget sem confiar no report
- rosto, maos, pes, assinatura, contato e pose sobrevivem em 1x
- `material_topology` independente passa antes de shading; indice cruzado,
  rampa sem dono ou AA entre materiais reprova
- `technical_pass`, `visual_pass`, `scale_pass`, `budget_pass` e `emulator_pass` permanecem independentes
- promocao exige todos os gates aplicaveis e decisao humana registrada
- aprovacao humana cita o SHA-256 exato; preview ou fundo sem derivacao
  deterministica falha fechado

### Handoff

- para animacao somente depois de pose, escala, paleta e budget passarem
- o handoff de animacao inicia no estagio 5 do lifecycle canonico e deve preservar SHA, identidade, escala, pivot, materiais e paleta aprovados
- para `res/` somente depois de visual + pixel + budget + aprovacao humana
- para claim de runtime somente depois de SGDK + BlastEm vinculados ao hash da ROM

## Persistencia causal

- falha visual nao encerra o projeto; classifique e mude produtor, representacao, escala de probe ou hipotese
- duas tentativas equivalentes encerram a rota, nao o asset
- cor vazando entre materiais pede patch causal sobre a candidata em rework, nao
  regeneracao integral: registre sintoma, material dono, fronteira esperada,
  indices permitidos e pixels/segmentos alterados
- GUI/ponteiro para operacao deterministica e `interaction_channel_mismatch`
- operacao mecanica usa CLI/headless; decisao de forma usa produtor visual ou autoria nativa
- enquanto uma decisao humana estiver pendente, continue apenas ramos realmente independentes
- sob autorizacao explicita de forward-test continuo, mantenha o gate humano
  pendente e produza rework/prototipos downstream somente em staging, marcados
  `agent_curated_diagnostic_review` ou `speculative_downstream`; nao simule
  aprovacao nem use esses artefatos para `res/` ou elevacao de claim

## Teto de claim

Concept e fonte high-res nao passam de `visual_source`; conversao/probe nao passa
de `technical_candidate`; nativa sem todos os gates nao passa de
`native_candidate`. `ready_for_res` exige pixel, visual, escala, budget e humano;
runtime exige ROM no BlastEm. A tabela completa vive no workflow.

## Proibicoes

- gerar sheet completa antes de uma pose nativa vencer
- rotular uma imagem como Lanczos/Mitchell/qualquer rota quando essa rota nao
  participou causalmente dos pixels registrados
- chamar mascara preenchida, spans hardcoded ou recolor semantico de
  `lineart_blocking_1px`
- abrir gate humano entre opcoes que ja falham fonte, silhueta ou identidade
- usar uma sheet reprovada como nova fonte de geracao
- desenhar personagem final por primitivas ou script procedural
- declarar numero de cores por inspecao visual; medir PNG/PLTE
- resolver perda de rosto/maos/pes adicionando detalhe high-res
- trocar 48x64 por 64x96 sem gate de camera, gameplay e budget
- promover probe mecanica, screenshot ou preview ampliada para `res/`
- remover fundo por threshold global e depois esconder halo com quantizacao
- inventar score estetico numerico, hitbox ou recomendacao sem medicao/decisao
