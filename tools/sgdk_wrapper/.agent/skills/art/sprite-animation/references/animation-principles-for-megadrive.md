# Os 12 principios de animacao aplicados ao Mega Drive

Esta referencia e a autoridade artistica transversal da `sprite-animation`.
Os principios nao sao uma sequencia de producao e nao viram score numerico. Cada
acao demonstra como os aplica, ou justifica por que um principio condicional nao
se aplica. Medidas automaticas encontram contradicoes; leitura, acting e apelo
continuam sendo revisao visual humana vinculada ao SHA do strip.

## Contrato por acao

Declare `production_method` como `pose_to_pose`, `straight_ahead` ou `hybrid` e
registre os 12 IDs abaixo em `animation_principles_report`. Cada avaliacao usa:

- `status`: `passed`, `not_applicable`, `needs_review` ou `failed`;
- `observation`: evidencia observavel, sem elogio generico;
- `evidence_kinds`: `automated_measurement`, `human_visual_review`,
  `artifact_inspection` ou `runtime_evidence`;
- `evidence_refs`: caminhos relativos ou IDs de reports vinculados ao mesmo SHA;
- `not_applicable_reason`: obrigatorio quando o status for `not_applicable`.

`staging`, `timing`, `straight_ahead_and_pose_to_pose`, `solid_drawing` e
`appeal` nunca sao `not_applicable` para uma strip candidata a revisao humana.
`staging`, `exaggeration`, `solid_drawing` e `appeal` nao passam apenas por
medicao automatica: exigem `human_visual_review`.

Schema: `tools/sgdk_wrapper/schemas/animation_principles_report.schema.json`.
Exemplo: `tools/sgdk_wrapper/.agent/references/agentic_aaa_contracts/examples/animation_principles_report.example.json`.

## Principios e traducao operacional

1. `squash_and_stretch`
   - Somente pre-renderizado; conserva massa aparente, pivot e leitura.
   - Pode ser `not_applicable` para objeto rigido, com justificativa.
2. `anticipation`
   - Prepara ataque, salto, dash, esquiva, mudanca brusca ou impacto.
   - A duracao vive na tabela unica de VBlank.
3. `staging`
   - Acao, direcao e foco devem ser reconheciveis em 1x e na camera 320x224.
   - Silhueta, oclusao e FX nao podem esconder a informacao de gameplay.
4. `straight_ahead_and_pose_to_pose`
   - Declara o metodo. `pose_to_pose` favorece gameplay/key poses;
     `straight_ahead` favorece FX organico; `hybrid` combina ambos com fronteira
     explicita. Reordenar frames existentes nao e nenhum desses metodos.
5. `follow_through_and_overlapping_action`
   - Corpo lidera; cabelo, tecido, arma e extremidades respondem com atraso,
     damping e retorno coerentes.
6. `slow_in_and_slow_out`
   - Spacing e holds constroem aceleracao/desaceleracao. Nao duplicar PNG para
     simular hold; usar VBlank.
7. `arcs`
   - Maos, pes, cabeca, armas e centro de massa seguem trajetorias coerentes;
     movimento linear organico exige justificativa.
8. `secondary_action`
   - Reforca a acao principal sem competir com telegraph, hit ou locomocao.
   - Pode ser `not_applicable` quando escala/papel nao comportarem detalhe.
9. `timing`
   - Timing canonico e `frame_holds_vblank`; preview e runtime o consomem.
   - Comunica peso, intencao, impacto e responsividade.
10. `exaggeration`
    - Amplia leitura dentro de `extreme_pose_limits`; nao destrói identidade,
      hitbox justa nem volume.
11. `solid_drawing`
    - Em pixel art significa volume, proporcao, perspectiva, foreshortening,
      apoio, anatomia e materiais consistentes entre frames/direcoes.
12. `appeal`
    - Carisma, clareza, pose iconica e coerencia com a fantasia do personagem.
      Nao e sinonimo de detalhe, quantidade de frames ou conformidade tecnica.

## Regra de promocao

Para `human_review_candidate` ou claim superior, todas as acoes do candidato
devem aparecer uma unica vez no report, ligadas ao SHA do strip. O report precisa
estar `passed`; `needs_review` ou `failed` bloqueiam o gate humano. `not_applicable`
e permitido apenas nos principios condicionais e com razao especifica.

O report nao substitui pixel gate, fidelidade ao model sheet, budget, teste em
ROM ou decisao humana. Ele impede que esses gates sejam confundidos com oficio
de animacao.
