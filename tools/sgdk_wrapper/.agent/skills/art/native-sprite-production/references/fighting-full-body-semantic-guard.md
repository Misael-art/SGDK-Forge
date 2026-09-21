# Fighting full-body semantic guard

Use antes de produzir ou redimensionar um lutador. O objetivo e impedir que
um retrato, icon, thumbnail, XPM ou probe pequeno reduza silenciosamente a
escala corporal do jogo.

## Perfil obrigatorio

O record usa `schema_version=1.5.0`,
`asset_profile=fighting_full_body_sprite` e aponta
`semantic_guard_contract` para um contrato conforme
`tools/sgdk_wrapper/schemas/fighting_sprite_semantic_contract.schema.json`.

Somente `fighter_full_body_frame_or_strip` com
`allowed_use=scale_reference` pode participar da formula de escala. Retrato,
icon e HUD podem orientar identidade ou UI, nunca altura do lutador. XPM e
outra matriz textual sao `procedural_code_probe`, `diagnostic_only` e
`promotable=false`.

## Escala derivada, nao escolhida por intuicao

Declare no GDD a formula e preserve no contrato o caminho, SHA, `rule_id` e o
marcador canonico exato:

```text
<rule_id>:minimum_visible_height=ceil(<multiplier>*max(full_body_reference_visible_height))
```

O validator confirma o hash e o marcador no GDD, abre os PNGs, separa as
celulas declaradas, mede o bbox alpha/index 0 de cada frame e recalcula o
minimo. Ele tambem mede o bbox real da candidata; canvas grande com figura
minuscula nao passa.

Execute o contrato ainda com `candidate=null` para fechar identidade, fontes e
escala antes da arte; execute novamente com a candidata vinculada por SHA:

```bash
python3 tools/sgdk_wrapper/validate_fighting_sprite_semantics.py validate \
  --project-root "<projeto>" \
  --contract "<projeto>/doc/art/<fighter>/fighting_sprite_semantic_contract.json"
```

## Identidade do projeto

O gate compara o nome canonico e normaliza tags. Uma raiz irma com a mesma
identidade bloqueia a producao mesmo vazia. Primeiro reconcilie qual raiz e a
canonica; nunca escolha pela que apareceu primeiro numa busca.

## Ordem de decisao visual

1. escala relativa aos lutadores reais do engine;
2. silhueta e pose em 1x;
3. identidade, rosto, maos e pes;
4. paleta/contraste e materiais;
5. somente depois tiles, DMA e scanline.

Compliance ou budget nao compram legibilidade. Uma candidata pequena demais e
rejeitada antes de route shootout, refinamento ou animacao.
