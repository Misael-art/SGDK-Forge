# Changelog de Curadoria Canonica - 2026-06-19

## Lifecycle e consolidacao de skills

Status: `validated_framework_no_rom`.

Decisoes:

- 13 aliases redundantes ou experimentais foram movidos integralmente para
  `tools/sgdk_wrapper/.agent/legacy/skills/`;
- hashes anteriores ao move foram preservados no
  `skill_lifecycle_registry.json`;
- scroll/raster/H-Int foi consolidado em `shadow-highlight-scroll-fx`;
- scanline budget foi mantido em `megadrive-vdp-budget-analyst`;
- conversao visual, tilemap, sprite e audio foram redirecionados aos owners
  especializados existentes;
- `software-tile-rasterizer` ficou `experimental`, sem invocacao automatica;
- 13 owners ativos foram reconstruidos com contrato curto e metadata valida;
- o framework validator passou a detectar pasta ativa sem `SKILL.md`, path
  stale no manifest, hash legado divergente e context budget excedido;
- o validator de curadoria AAA deixou de preservar a contagem historica de
  20 skills novas;
- o registry de generos agora mantem apenas seis especializacoes ativas com
  schema, validator, testes e opt-in; as outras 32 ficam `deferred`.

Limite factual:

- nenhuma ROM, runtime, tecnica ou claim AAA foi promovido;
- a verificacao executavel foi concluida em 2026-06-20;
- nenhuma ROM ou claim de runtime foi promovido.

## Fechamento de coesao da curadoria

- O mapa de rotas foi normalizado para o contrato `aaa_pipeline_curated_skill_map` v2 e passou a referenciar somente owners ativos.
- Rotas tecnicamente caras ou nao canonizadas exigem opt-in, budget e benchmark reproduzivel.
- Os testes antigos por genero agora delegam ao registro central e confirmam exatamente uma especializacao ativa por ID.
- Foi adicionado o gate agregado `tools/sgdk_wrapper/ci/test_canonical_skill_curation.ps1`.
- Estado: `validated_framework_no_rom`.

## Curadoria do aprendizado Celestial Chase Revive

- Promovida a separacao entre host, toolchain, ROM e qualidade criativa.
- Canonizadas as regras de autoridade RESCOMP, input observado, evidencia
  ligada ao hash, correcao causal e status tecnico independente do criativo.
- Sete automacoes candidatas ficaram em piloto com matriz de validacao.
- Rejeitados transporte de input local como regra universal e relaxamento de
  gates.
- Adicionados protocolo, workflow, registro, route e teste contratual.
- Estado: `validated_framework_no_rom`.
