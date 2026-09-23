# Workflow: Independent Quality Review

Use nos checkpoints `foundation`, `pre_growth`, `vertical_slice` e
`release_candidate`, nunca em toda pequena edição.

1. Materialize `quality_review_request.json` com artefatos hash-bound, estágio,
   domínios alterados, riscos e intenção comercial/narrativa/sonora.
2. Execute `quality_review_router.py plan`; aceite no máximo três reviews.
3. Quando houver dois ou mais ramos longos, passe o taskset para
   `harness-orchestration`; reviewers permanecem read-only e independentes.
4. Consolide `independent_quality_review.json` sem expor raciocínio interno.
5. Execute `validate-report` e descarte parecer stale, autoaprovado ou
   contraditório.
6. Corrija somente as três prioridades, pelos owner skills indicados.
7. Reavalie o delta. Claims, escopo, promoção e Git continuam com o coordenador.

`defect`/`risk` demonstrado pode produzir `revise_before_growth`.
`opportunity`/`taste` não bloqueia. Mudança de escopo abre decisão humana.
