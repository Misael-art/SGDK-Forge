# Changelog de curadoria - 2026-09-02

## Escopo

Curadoria canonica da validacao de animacoes SGDK. Nenhum projeto, `res/`, ROM
ou asset de jogo foi promovido ou alterado.

## Mudancas

- `sprite-animation` agora exige gate ligado ao arquivo antes do gate humano.
- `animation_strip_contract` v3 ganhou binding do strip/lineart, lineage por
  frame, suporte de solo, timing unico, motion profile e metasprite layout.
- Foram adicionados:
  - `validate_animation_strip_artifact.py` (entrypoint canonico);
  - `validate_lineart_topology.py`;
  - `validate_motion_semantics.py`;
  - `validate_animation_candidate.py`;
  - `render_animation_evidence.py`;
  - registry/schema de perfis de movimento;
  - schema do manifesto agregado;
  - arquitetura operacional e exemplo v3;
  - corpus adversarial machine-readable e runner dedicado.
- `aaa-pipeline-guardian` passou a consumir o gate agregado para claims de
  animacao, sem duplicar a logica dos validators.
- O meta-gate de ferramentas mede os quatro entrypoints canonicos novos.

## Falsos verdes encerrados

- fragmento de celula vizinha apesar de `fixed_cell`;
- silhueta preenchida ou stroke grosso rotulado como lineart 1 px;
- frame-fonte reordenado/duplicado e anunciado como acao nova;
- reuso de frame identico entre acoes sem justificativa;
- foot slide e deriva do contato declarado;
- duas autoridades de timing ou GIF divergente do VBlank;
- reports com decomposicoes incompativeis de metasprite;
- `visual_pass=true` quando fidelity, art direction ou blind review nao passam;
- report nao vinculado ao hash do sujeito;
- claim ou gate humano acima das dependencias provadas.

## Validacao

- `python3 tools/sgdk_wrapper/test_animation_validation.py`: 9/9.
- fixtures adversariais declaradas: 14/14 blockers.
- meta-gate isolado dos quatro validadores: 4/4, `verdict=OK`.
- `test_art_pipeline.py`: 128/128.
- `forge_art self-check`: 126/126.
- schemas Draft-07 e registry validados com `jsonschema` 4.25.1 do runtime
  controlado do workspace.
- skill `sprite-animation`: `quick_validate.py` passou.

## Limites honestos

- Medidas automaticas detectam contradicoes; nao provam apelo, carisma ou
  acting. Isso permanece no blind visual review vinculado ao SHA.
- Nenhuma ROM foi gerada; nao existe claim de runtime, performance ou AAA.
- O auditor global permaneceu bloqueado por dividas preexistentes fora desta
  curadoria: `validate_native_sprite_production.py` sem self-check reconhecido,
  copias antigas de `vdp_scanline_simulator` e `runtime_probe` em projetos.

## Complemento — princípios e lifecycle

- Formalizados os 12 princípios de animação para pixel art/VDP, com estados
  auditáveis e sem score artístico inventado.
- Criado lifecycle canônico de 12 etapas; os 11 passes e P0-P5 agora são
  explicitamente subpasses mapeados.
- Adicionado `animation_principles_report.schema.json` e integrado o report ao
  manifesto/agregador de candidato.
- O gate reprova princípio obrigatório como `not_applicable`, cobertura menor
  que 12, método de produção ausente e appeal/staging/exaggeration/solid drawing
  aprovados sem revisão visual humana.
- Handoff de representação corrigido: personagem comum usa `SPRITE`; tilemap,
  planos e streaming entram apenas pelos owners especializados.
- Validação final desta extensão: animation validation `10/10`, blockers
  adversariais `18/18`, exemplo/schema Draft-07 válidos, measurement gate
  isolado `4/4`, art pipeline `128/128`, forge-art `126/126` e três skills em
  `quick_validate`.
- O meta-gate global terminou `17/18`, `BLOCKED` por dívida preexistente:
  `validate_native_sprite_production.py` ainda não é reconhecido com self-check,
  além de cópias locais antigas de `vdp_scanline_simulator` e `runtime_probe`.
  Os quatro validadores canônicos de animação passaram; o blocker não foi
  causado nem mascarado por esta curadoria.

## Complemento — autoria temporal e continuidade sem falso gate humano

- Fechado o caso observado no forward-test Kirby r1: resize/deslocamento da
  mesma pose nao pode provar idle, run ou inhale, ainda que hashes, fases e
  deltas sejam diferentes.
- Lineart nativa agora exige autoria/derivacao/aprovacao rastreavel; contorno de
  mascara, spans e primitivas permanecem probes. Contato de pe precisa ser
  medido no PNG ou anotado por evidencia hash-bound.
- Reports de movimento anteriores ao gate vigente deixam de comprar claim no
  agregado; tipos de evidencia dos 12 principios fora do schema falham fechado.
- Adicionada politica de forward-test continuo: revisao do agente pode conduzir
  rework e prototipos em staging, mas nunca se chama revisao humana nem autoriza
  `res/`, runtime ou AAA.
- O pacote Kirby v03 r1 foi usado apenas como fixture observacional: agora e
  reprovado pelos quatro blockers causais esperados. Nenhum arquivo do projeto
  foi alterado.
- Validacao: animation validation `10/10`, corpus adversarial `25/25`, skills
  `3/3`, measurement tools modificadas `1/1` cada, art pipeline `128/128` e
  forge-art `126/126`.

## Complemento — proveniência raster, escala efetiva e semântica reconhecida

- Schema v3 passou a ser executado pelos próprios validadores e ganhou
  `production_provenance` com fonte bitmap e produtor hash-bound.
- ASCII, spans, primitivas e raster criado por código não podem ser declarados
  `hand_authored_pixel`; expansão inteira do grid não mascara resolução efetiva.
- Approval record `pending/needs_review/failed` não aprova lineart, ainda que o
  contrato escreva `approved_for_strip_authoring`.
- `motion_semantic_candidate` passou a exigir `blind_visual_review=passed`;
  nomes de fases e deltas automáticos sustentam apenas claim técnico.
- O Kirby Cloude v04 foi reexecutado como fixture negativa, sem mutação: idle
  detectado como 2x exato, schema inválido, aprovação pendente e proveniência
  ausente. O agregado não preservou o falso claim anterior.
- Validação: self-checks `3/3`, animation validation `10/10`, blockers `30/30`,
  exemplo v3 sem erro de schema, `quick_validate` aprovado e art pipeline
  `128/128`.
