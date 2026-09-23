# TAINA resampling route lab — gate humano

## Escopo

Este painel compara a fonte de identidade, a fonte direcional 56×80, a v04 rejeitada, vinte probes geométricos brutos, quatro probes de paleta e duas guias de retrabalho nativo. Nenhum item do laboratório é autorizado para `res/`.

## Decisão humana necessária

1. Qual rota preserva melhor anatomia, silhueta, pose e identidade em 1×?
2. Qual rota mantém a guarda diagonal e a separação ombro–braço/quadril–perna?
3. Alguma das duas guias nativas é suficientemente séria para continuar como guia de reautoria?
4. O custo de limpeza parece localizado ou equivalente a começar do zero?

## Regras do gate

- Não escolher por soma numérica.
- `mechanical_geometry_probe` não é `native_candidate`.
- Probes de paleta são `technical_palette_probe` somente.
- As guias nativas não são v05, não são final e não podem ser usadas como fonte de novos pixels.
- A decisão deve preservar 56×80, pivot, linha de chão e identidade do model sheet.

## Estado

`status=resampling_route_lab_evidence`

`human_gate_status=pending_human_decision`

`claim_ceiling=mechanical_geometry_probe | technical_palette_probe | native_authoring_guide_candidate`

`normal_taina_production=paused_until_lab_gate`

## Registro de entrada do gate

A entrada humana que abriu este laboratório foi:

`decision=rejected_requires_route_lab`

`asset_id=taina_idle_guard_56x80_native_authoring_v04`

`sha256=0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`

Para liberar uma próxima etapa, responder explicitamente com uma decisão de rota,
por exemplo `decision=approve_route_for_native_reauthoring` e um ou mais
`route_id`/`guide_id`, ou `decision=reject_all_routes`. A aprovação, se houver,
será somente para reautoria nativa em staging 56×80; não autoriza `res/`, animação,
runtime, ROM, `visual_pass` ou AAA.
