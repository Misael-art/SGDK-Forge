# Vibe Playable Loop V1 Design

## Objetivo

Implementar `vibe_playable_loop_v1` como uma rota canonica que transforma
pedidos naturais de jogo, fase, personagem, animacao, UI ou FX em producao
visualmente dirigida, jogavel e validada no BlastEm. O usuario nao precisa
nomear arte, AAA, sourcing, VDP, budget ou gates. A rota deve impedir que arte
procedural final seja confundida com entrega visual.

O criterio principal e:

> Se nao foi visto rodando no emulador, nao existe. Se foi visto, mas parece
> placeholder procedural, ainda nao e entrega visual.

## Decisoes de arquitetura

### Estender a espinha existente

O loop sera um pipeline e workflow de orquestracao sobre os owners e gates ja
existentes. Nao sera criado um segundo sistema visual paralelo.

O pipeline novo deve referenciar, nesta ordem causal:

1. roteamento deterministico da intencao;
2. `art-asset-diagnostic`;
3. direcao e gate arte + gameplay;
4. sourcing ou geracao bitmap quando faltar fonte aprovada;
5. congelamento da fonte premium e sua linhagem;
6. `visual-excellence-standards` antes da traducao definitiva;
7. `art-translation-to-vdp` ou conversao apropriada;
8. revisao estrutural e de animacao;
9. `megadrive-vdp-budget-analyst`;
10. admissao de runtime;
11. integracao SGDK, build e manifestos;
12. BlastEm, screenshot/dump e comparacao visual;
13. aprovacao humana para promocao visual final.

### Auditoria do owner `art-gameplay-direction-gate`

A auditoria encontrou cobertura operacional suficiente nos owners atuais:

- `art-direction-selector` escolhe e congela a linguagem visual, compara
  candidatos, registra risco de clone e entrega o `master_style_manifest`;
- `art-asset-diagnostic` classifica o estado real das fontes e escolhe a rota
  de conversao, revisao ou sourcing;
- `visual-excellence-standards` ja exige, avalia e emite o
  `art_gameplay_direction_gate_report`, incluindo contexto de game design,
  identidade, materiais, perspectiva, movimento e veto estetico.

Portanto, `art-gameplay-direction-gate` continuara sendo contrato e workflow
compartilhado. Nao sera criada uma nova skill nem um novo owner. O schema
existente sera endurecido e o pipeline declarara os owners acima. Um owner novo
so podera ser reconsiderado se uma futura auditoria demonstrar decisao,
artefato e fixture que nao pertençam aos tres owners atuais.

`art-direction-selector` preserva `allow_implicit_invocation=false`. O roteador
nao contorna essa politica: ele emite uma decisao explicita
`explicit_router_dispatch`, registra a rule id que exigiu direcao e inclui
`skills/art/art-direction-selector` em `required_owners`. O orquestrador
executa essa lista como handoff explicito antes do diagnostico/conversao.

Para tornar essa excecao auditavel sem criar skill duplicada, a implementacao
devera:

- registrar `art/art-direction-selector` como `active` no
  `skill_lifecycle_registry.json`, com `legacy_path=null`, sem replacement e
  com motivo de lifecycle;
- adicionar uma rota canonica explicita no
  `aaa_pipeline_curated_skill_map.json` para pedidos visuais naturais;
- manter o metadata `allow_implicit_invocation=false`;
- testar que somente o roteador/pipeline pode disparar essa invocacao sem uma
  chamada nominal do usuario.

## Roteador deterministico

### Limite epistemico

O roteador nao declara que compreendeu perfeitamente linguagem natural. Ele
executa regras versionadas sobre texto normalizado e registra exatamente o que
acionou. A mesma entrada, a mesma versao de regras e a mesma configuracao devem
produzir JSON semanticamente identico.

### Entrada e saida

O roteador recebe:

- texto original;
- idioma declarado ou `auto`;
- contexto do projeto quando disponivel;
- versao da tabela de regras.

Ele emite `vibe_playable_route_report.json` com:

- `schema_version` e `ruleset_version`;
- `request_text_sha256` e texto normalizado auditavel;
- `detected_language`;
- `detected_intents`: `game`, `scene`, `character`, `animation`, `ui`, `fx`,
  `visual_improvement` e `debug_lab`;
- `detected_targets`, preservando cada entidade distinta encontrada;
- por intencao: `confidence`, `matched_rule_ids`, `matched_terms` e
  `decision_reason`;
- `ambiguity_status` e regras conflitantes;
- `fallback_decision`;
- `visual_route_required`;
- `required_owners` em ordem;
- `required_artifacts`;
- `runtime_admission`;
- `blocking_statuses`.

Cada item de `detected_targets` exige:

- `target_id` deterministico e estavel dentro do request;
- `target_type`;
- `role`;
- `criticality`;
- `requested_actions`;
- `animation_required` e motivo;
- `required_assets`;
- `required_owners`;
- `matched_rule_ids` que originaram o alvo.

O roteador nao funde entidades apenas porque compartilham o mesmo tipo. Heroi
e boss geram targets separados, com assets, animacoes, criticidade e owners
proprios. Deteccoes repetidas da mesma entidade nominal podem ser deduplicadas
somente por uma regra explicita registrada no report.

Confianca e discreta e determinada por regra, nao por palpite do modelo:

- `1.00`: termo e acao explicitamente mapeados;
- `0.80`: composicao verbo + substantivo mapeado;
- `0.60`: pedido amplo de criar/melhorar produto jogavel;
- `0.40`: fallback conservador por ambiguidade visual plausivel;
- `0.00`: regra nao acionada.

### Regras e fallback

A tabela cobre portugues e ingles, incluindo flexoes e frases que nao citam
arte, AAA ou qualidade visual. Exemplos obrigatorios incluem `crie um jogo`,
`faca uma fase`, `adicione um personagem`, `anime o golpe`, `melhore o
cenario`, `make a level`, `add a hero`, `animate the attack`, `build a boss
fight` e `improve the HUD`.

Pedidos que combinem verbo de criacao/alteracao com entidade visivel ou
jogavel acionam `visual_route_required=true`. Pedidos amplos de jogo ou fase
acionam no minimo `game|scene` e inferem os owners de direcao, sourcing,
traducao, budget e evidencia. Ambiguidade entre trabalho visual e tecnico usa
fallback conservador: a rota visual e obrigatoria ate classificacao posterior.

`debug_lab` so e aceito quando o pedido ou o contexto declara explicitamente
laboratorio, debug, smoke tecnico ou diagnostico. Ele nunca cancela uma
intencao visual detectada; apenas limita a saida a `lab_not_delivery`.

### Exemplo de aceitacao

Para `crie uma fase com um heroi enfrentando um boss`, a saida deve detectar:

- `game` ou `scene`;
- `character` para heroi;
- `character` e `fx`/setpiece para boss;
- animacao critica para heroi e boss;
- direcao visual e sourcing;
- traducao VDP;
- budget de planos, sprites, paleta, VRAM e DMA;
- evidencia BlastEm.

Ela tambem deve emitir, no minimo:

- `target_stage_1`, tipo `scene`, papel `playable_stage`;
- `target_hero_1`, tipo `character`, papel `player_hero`, criticidade
  `critical` e animacao obrigatoria;
- `target_boss_1`, tipo `character`, papel `boss`, criticidade `critical` e
  animacao/telegraph obrigatorios.

O contexto compacto deve incluir os owners visuais antes de qualquer owner de
runtime.

## Travas de admissao do runtime

O loop separa tres decisoes que nao se promovem entre si:

- `runtime_admitted`: runtime de producao visual;
- `technical_runtime_admitted`: correcao estritamente tecnica;
- `runtime_lab_admitted`: laboratorio, smoke ou diagnostico.

O caminho de producao usa estados monotônicos:

```text
request_routed
  -> visual_context_loaded
  -> direction_gate_passed
  -> premium_source_ready
  -> vdp_translation_ready
  -> structural_and_motion_review_passed
  -> vdp_budget_accepted
  -> runtime_admitted
  -> built
  -> blastem_captured
  -> visually_compared
  -> human_visual_approved
```

`sgdk-runtime-coder` nao pode receber handoff definitivo antes de
`runtime_admitted`. A admissao exige simultaneamente:

- `visual_route_required=true` resolvido;
- diagnostico de assets;
- direcao visual congelada;
- gate arte + gameplay aprovado;
- fonte premium valida para cada asset critico;
- traducao/conversao revisada;
- animacao revisada quando aplicavel;
- budget VDP aceito;
- ausencia de `blocked_image_tooling`, `blocked_no_premium_source`,
  `procedural_final_asset`, `unknown_authoring_method` ou
  `lab_not_delivery`.

`technical_runtime_admitted` exige um `technical_change_scope_report` que
prove, por inventario de arquivos e classificacao da mudanca, que o trabalho
nao altera:

- `data/`, `res/`, `data/source_art/` ou declaracoes `.res`;
- composicao de planos, camera visual, paleta ou apresentacao;
- sprites, animacao, HUD, menus, title, tipografia ou FX;
- baselines ou contratos visuais.

Essa rota pode corrigir logica, crash, input ou estado apenas quando a mudanca
nao produz alteracao visual intencional. Se o diff, o build ou a captura revelar
mudanca de apresentacao, a admissao tecnica e invalidada e o pedido volta para
a rota visual. `technical_runtime_admitted` nunca define `creative_ready`,
`visual_aprovado`, `elite_ready`, baseline visual ou aprovacao de asset.

`runtime_lab_admitted` exige `request_routed`, manifesto de laboratorio,
`lab_not_delivery=true` e `creative_ready=false`. Ele nao pode promover
baseline visual nem satisfazer as outras duas admissoes.

O build manifest deve registrar o SHA-256 do route report e da decisao de
admissao usada. `validate_resources.ps1` deve bloquear promocao quando houver
intencao visual ou recursos visuais sem `runtime_admitted`, e deve bloquear
qualquer status visual originado das rotas tecnica ou lab.

Assim, o roteador impede a abertura prematura de runtime por tres barreiras:

1. o pipeline nao oferece handoff de producao para `sgdk-runtime-coder` antes
   de `runtime_admitted`;
2. as rotas tecnica e lab carregam tetos de claim imutaveis;
3. o validator rejeita build/closeout de producao cujo manifest nao carregue a
   decisao de admissao vinculada ao route report.

## Extensao do `premium_source_manifest` canonico

Nao sera criado `premium_visual_source_manifest`. Cada asset critico deve
possuir o `premium_source_manifest` canonico antes da conversao ou promocao.
O wrapper passara a ter um unico
`schemas/premium_source_manifest.schema.json`, capaz de validar o formato novo
e reconhecer as formas legadas existentes.

A migracao e compativel:

- manifests `1.x` continuam legiveis como evidencia historica;
- um normalizador converte tanto o formato single-asset quanto o formato root
  com `assets[]` para uma representacao canonica;
- a migracao nunca inventa autoria, ferramenta, modelo ou licenca ausentes;
- campos ausentes viram `unknown`/blocker para promocao, nao valores
  presumidos;
- somente o contrato estendido pode autorizar nova producao visual;
- nenhum segundo schema ou nome de manifesto paralelo e permitido.

O contrato estendido registra:

- `asset_id`, papel e criticidade;
- `authoring_method`;
- `source_origin`;
- `source_classification`: `human_authored`, `generated_bitmap`,
  `licensed_source`, `procedural_debug` ou `unknown`;
- ferramenta, versao, modelo e canal utilizados;
- prompt/receipt ou referencia de licenca quando aplicavel;
- autor, titular, licenca e obrigacoes de atribuicao;
- todos os arquivos-fonte com caminho relativo, tamanho e SHA-256;
- transformacoes aplicadas em ordem;
- ferramenta/script, versao, parametros, input hash e output hash de cada
  transformacao;
- lineage parent/child;
- `basic` como controle diagnostico;
- `elite` como candidato de producao;
- aprovacao da direcao visual.

`procedural_debug` e `unknown` bloqueiam qualquer asset critico em producao,
mesmo quando existe PNG tecnicamente valido. Ausencia de informacao de autoria
produz `unknown_authoring_method`, nunca inferencia otimista.

## Politica procedural

Scripts e ferramentas procedurais podem somente:

- converter formato;
- quantizar e remapear paleta;
- recortar;
- montar tiles, mapas e atlas;
- gerar collision masks, hitboxes e mascaras auxiliares;
- calcular metricas e diagnosticos;
- montar grids, overlays, contact sheets e previews de revisao.

Eles nao podem criar a estetica final por retangulos, poligonos, primitivas,
texto, gradientes sinteticos, padroes matematicos ou desenho programatico de
pixels. Pillow, SVG, Canvas, C e equivalentes sao avaliados pelo papel da
operacao, nao apenas pelo nome da ferramenta.

Cada transformacao declara `operation_class`. Classes de processamento
permitidas exigem input de fonte aprovada e output descendente desse input.
Classes `visual_authoring_procedural`, `procedural_debug` ou nao classificadas
rebaixam personagem, inimigo, boss, cenario, foreground, HUD, logo, menu,
title, particula, impacto ou FX heroico para `lab_not_delivery`.

## Cadeia de rastreabilidade

A cadeia canonica e:

```text
fonte premium + SHA-256
  -> asset convertido + SHA-256
  -> declaracao exata em .res
  -> metadata/saida ResComp e build manifest
  -> ROM SHA-256
  -> sessao BlastEm
  -> screenshot + SRAM + dump aplicavel
  -> comparacao visual e aprovacao
```

O contrato nao presume que o hash bruto do PNG seja recuperavel da ROM apos
ResComp. A prova usa elos distintos:

- manifest de transformacao liga fonte ao asset convertido;
- auditor `.res` liga o asset convertido a uma declaracao e recurso;
- build manifest liga entradas `.res` e metadata ResComp a uma ROM;
- evidence seal liga a sessao e os artefatos ao SHA-256 da ROM;
- mapa source-to-runtime liga o asset esperado, a cena, a regiao observada e o
  dump/captura.

Qualquer elo ausente, stale ou com hash divergente bloqueia promocao visual.

## Controle `basic` e candidato `elite`

`basic` existe apenas como controle diagnostico e nunca satisfaz fonte premium
ou runtime de entrega. `elite` deve demonstrar ganho perceptivel sobre `basic`
e preservar identidade, materiais, silhueta, profundidade e movimento.

O contrato exige:

- hashes diferentes e lineage comum;
- metricas estruturais por variante;
- criterios e limiares declarados antes da comparacao;
- painel lado a lado em escala nativa e ampliada;
- parecer de `visual-excellence-standards`;
- ausencia de regressao em identidade/material/silhueta/profundidade/movimento;
- aprovacao humana explicita da variante elite.

Duas variantes quase iguais, ou elite que melhora apenas score tecnico, nao
satisfazem o contrato. O validator emite `elite_perceptual_delta_missing` ou
`elite_identity_regression`.

## Animacao premium

Animacao critica exige:

- model sheet ou visual DNA travado;
- key poses;
- fases `anticipation`, `active`, `follow_through` e `recovery`, com excecoes
  explicitamente justificadas;
- timing, spacing e holds;
- pivots por frame;
- pontos de contato e foot-contact quando aplicavel;
- coerencia de volume, escala e silhueta;
- motion GIF ou WebP gerado do output final;
- leitura sob movimento, FX, hitstop e gameplay;
- parecer estetico e aprovacao humana.

Sem motion preview ou pivots medidos, o asset fica `needs_review` e nao pode
ser promovido.

## Comparacao visual e aprovacao

Comparacao mensurada e necessaria, mas nunca substitui julgamento estetico. A
promocao visual final exige simultaneamente:

1. metricas estruturais e perceptivas rastreaveis;
2. painel lado a lado `source + basic + elite + BlastEm`;
3. parecer `passed` de `visual-excellence-standards`;
4. aprovacao humana apontando para os hashes atuais da fonte e convertido;
5. evidencia runtime fresca para o SHA-256 da ROM atual.

O painel deve identificar ROM SHA-256, scene id, asset ids, source hashes e
timestamp da sessao.

A aprovacao e dividida em dois contratos independentes:

### Aprovacao humana do asset

O `doc/human_approval_record.md` canonico ganha uma entrada
`approval_scope=asset` que aponta para:

- asset id e variante aprovada;
- SHA-256 da fonte premium;
- SHA-256 do asset convertido;
- parecer vigente de `visual-excellence-standards`;
- painel lado a lado usado na decisao;
- aprovador humano, timestamp e decisao;
- SHA-256 do proprio registro imutavel, fixado no manifest/closeout que o
  consome.

Um novo build nao invalida essa aprovacao quando fonte, convertido, lineage,
parecer e painel mantêm os mesmos hashes. Qualquer mudanca nessa cadeia invalida
a aprovacao do asset e exige nova decisao humana.

### Evidencia runtime

Nao sera criado um registro runtime paralelo. `emulator_session.json` e
`evidence_closeout_report.json` continuam sendo os contratos canonicos e sao
estendidos para apontar para:

- SHA-256 da ROM;
- build manifest;
- scene id e target ids observados;
- sessao BlastEm;
- screenshot, SRAM e dump aplicavel;
- mapa source-to-runtime e comparacao contra o asset aprovado.

Qualquer novo build com ROM SHA-256 diferente invalida a evidencia runtime,
mesmo quando a aprovacao do asset continua fresca. Aprovar o asset nao prova que
a ROM o exibiu; capturar a ROM nao aprova esteticamente o asset.

Testes automaticos nao podem criar, assinar, simular ou promover aprovacao
humana. Fixtures automatizadas podem apenas validar um
`doc/human_approval_record.md` previamente aprovado, imutavel e cujo hash
esteja fixado no manifest da fixture. A aceitacao visual final end-to-end
permanece uma acao humana real fora do resultado automatico.

## Falha honesta

Se nenhum canal de imagem bitmap ou fonte licenciada/premium estiver
disponivel:

- emitir `blocked_image_tooling` quando nao houver canal capaz de produzir ou
  persistir fonte bitmap adequada;
- emitir `blocked_no_premium_source` quando houver tooling, mas nenhuma fonte
  valida foi obtida/aprovada;
- nao criar substituto procedural final;
- permitir somente smoke tecnico com `lab_not_delivery=true`.

## Graphify

Graphify permanece indice consultivo e nao entra no caminho quente de cada
pedido.

- `status=fresh` usa cache e nao reconstrói o grafo;
- cold start faz uma tentativa curta e limitada de status/update consultivo;
- timeout ou grafo ausente degrada para `consultive_index_unavailable` e a rota
  continua lendo os arquivos canonicos;
- rebuild completo fica restrito a manutencao explicita fora do caminho do
  pedido, nunca a uma espera de 300 segundos no loop;
- updates incrementais reutilizam o cache existente;
- somente mudancas nos tracked roots marcam stale;
- uma sessao nao repete build do grafo para cada roteamento;
- falha consultiva e reportada separadamente e nao autoriza relaxar gates
  visuais.

O timeout exato sera configuravel e coberto por teste, mas o contrato de
corretude depende de numero de tentativas e fallback, nao de aguardar o grafo.

## Cache, reuso e contexto compacto

Cada etapa registra `input_fingerprint`, `cache_decision` e os artefatos
reutilizados. Reuso so ocorre quando todos os inputs autoritativos daquela
etapa conservam os mesmos hashes.

Chaves de reuso minimas:

- roteamento: request hash + ruleset version + project context fingerprint;
- diagnostico: inventario de `data/`, `res/` e `.res` + versao do diagnostico;
- direcao: GDD/spec + catalogo + decision record + style manifest;
- fonte: `premium_source_manifest` + arquivos-fonte e hashes;
- aprovacao do asset: fonte + convertido + parecer + painel + entrada
  asset-scoped de `human_approval_record.md`;
- evidencia runtime: build manifest + ROM SHA-256 + sessao/capturas.

Mudanca em um elo invalida apenas os descendentes. Por exemplo, rebuild com
assets identicos invalida evidencia runtime, mas preserva direcao, fonte e
aprovacao de asset. Mudanca de source hash invalida conversao, aprovacao de
asset e toda evidencia runtime dependente.

O route report completo permanece em disco. O agente recebe um
`vibe_playable_compact_context` contendo somente:

- intents e targets;
- owners unicos em ordem;
- blockers e proxima etapa;
- referencias aos arquivos canonicos necessarios;
- fingerprints e decisoes de cache.

O contexto compacto tem teto inicial de 32 KiB serializados. Se a lista de
targets ultrapassar o teto, o roteador cria referencias para contextos
per-target; ele nao trunca targets, owners ou blockers. O report registra
`compact_context_bytes`, `owners_loaded`, `files_loaded`, cache hits/misses e
numero de execucoes por diagnostico.

Cold start pode fazer no maximo uma tentativa consultiva Graphify e uma leitura
de cada arquivo canonico necessario. Warm start com fingerprints frescos deve
reutilizar roteamento, diagnostico, direcao, fontes e aprovacoes sem reexecutar
os respectivos owners. Um cache hit nunca reutiliza evidencia stale.

## Schemas, workflows e validators

O plano de implementacao devera cobrir, sem duplicar owners:

- pipeline `vibe_playable_loop_v1`;
- workflow de entrada natural e admissao de runtime;
- schema e roteador do `vibe_playable_route_report`;
- endurecimento do `art_gameplay_direction_gate` existente;
- extensao e schema unico do `premium_source_manifest` canonico, com
  normalizacao/migracao compativel;
- schema da cadeia source-to-runtime/build/evidence;
- extensao asset-scoped de `human_approval_record.md` e extensao runtime de
  `emulator_session.json`/`evidence_closeout_report.json`, sem registros
  concorrentes;
- extensoes do contrato de animacao;
- extensoes do `visual_delivery_gate_report`;
- validator de autoria/operacao procedural;
- integracao com `validate_resources.ps1`, build manifest, evidence closeout,
  pipeline AAA, routing map e framework manifest;
- atualizacao da memoria operacional e changelog canonicos.

## Fixtures de aceitacao

As fixtures devem ser test-first e cobrir:

1. pedidos naturais em portugues, incluindo `crie um jogo` e `crie uma fase
   com um heroi enfrentando um boss`, ativam a rota visual completa;
2. pedidos naturais equivalentes em ingles ativam a mesma rota;
3. pedidos sem as palavras arte, AAA ou qualidade visual ainda ativam direcao,
   sourcing, animacao, VDP, budget e evidencia;
4. heroi e boss produzem `detected_targets` distintos, sem colapso de
   multiplicidade;
5. sprite procedural critico e bloqueado;
6. scripts de conversao, quantizacao, corte, tiles/atlas, mascaras e
   diagnosticos permanecem permitidos quando descendem de fonte aprovada;
7. ausencia de image tooling/fonte premium produz blocker, nao arte inferior;
8. animacao sem motion preview ou pivots nao e promovida;
9. build verde com placeholder permanece `lab_not_delivery`;
10. build manifest seleciona a variante `elite` aprovada, nunca `basic`;
11. screenshot/dump e sessao BlastEm pertencem a ROM e asset chain atuais;
12. tentativa adversarial de entregar personagem, cenario, HUD ou FX desenhado
    por Pillow, SVG, Canvas ou primitivas C e rebaixada para
    `lab_not_delivery`;
13. variantes `basic` e `elite` quase iguais falham o delta perceptivo;
14. metricas sem painel, parecer estetico ou aprovacao humana nao promovem;
15. route report ausente impede `runtime_admitted` para pedido visual;
16. `technical_runtime_admitted` rejeita mudanca em asset, composicao ou
    apresentacao e nunca promove status visual;
17. `runtime_lab_admitted` conserva `lab_not_delivery`;
18. novo build invalida evidencia runtime, mas preserva aprovacao do asset
    quando a cadeia fonte/convertido/parecer/painel nao mudou;
19. testes automaticos rejeitam approval record criado durante o proprio teste
    e aceitam somente o registro preaprovado cujo hash esta fixado na fixture;
20. `art-direction-selector` permanece implicitamente desabilitado e e
    despachado explicitamente pelo roteador registrado;
21. fixture visual end-to-end usa fonte premium bitmap nao procedural,
    conversao VDP, animacao com motion preview, ROM real, BlastEm, screenshot,
    SRAM/dump aplicavel, cadeia completa e aprovacao visual.

A fixture end-to-end deve persistir uma fonte `human_authored`,
`generated_bitmap` ou `licensed_source` com autoria/licenca e hash. Seu setup
nao pode desenhar a arte por script. Scripts podem apenas processar a fonte
persistida e montar os artefatos de diagnostico.

### Fixtures de eficiencia

O pacote tambem deve provar:

- cold start: no maximo uma tentativa Graphify, nenhuma espera longa e fallback
  canonico quando o indice nao responde;
- warm start: zero rebuilds Graphify quando `fresh`;
- diagnostico de assets executa uma vez por inventory fingerprint e zero vezes
  no warm start inalterado;
- `vibe_playable_compact_context` permanece dentro de 32 KiB ou se divide por
  target sem perda semantica;
- `owners_loaded` e `files_loaded` correspondem exatamente aos targets e gates
  requeridos, sem carregar a arvore inteira;
- direcao, fontes e aprovacoes frescas sao reutilizadas;
- mudanca seletiva invalida apenas os descendentes corretos;
- contadores de operacao e fingerprints, e nao apenas tempo de parede sujeito
  a ruido de CI, sustentam o teste deterministico de eficiencia.

## Autorrevisao da especificacao

### Duplicidade

- nenhum novo owner ou skill duplica `art-direction-selector`,
  `art-asset-diagnostic` ou `visual-excellence-standards`;
- `art-gameplay-direction-gate` permanece contrato/workflow compartilhado;
- existe somente `premium_source_manifest` e um unico schema;
- aprovacao humana continua em `doc/human_approval_record.md`;
- evidencia runtime continua em `emulator_session.json` e
  `evidence_closeout_report.json`.

### Compatibilidade

- manifests premium `1.x` sao normalizados e preservados como historico;
- migracao nao inventa campos ausentes;
- projetos legados podem executar investigacao tecnica, mas campos desconhecidos
  nao promovem visual;
- as tres admissoes de runtime possuem tetos independentes e nao convertem
  status tecnico/lab em status visual.

### Falsificacao de aprovacao

- testes nao criam nem promovem aprovacao humana;
- o hash do approval record preexistente e fixado pela fixture/closeout;
- a aprovacao cita hashes de fonte e convertido;
- evidencia runtime cita ROM SHA-256 e fica stale apos rebuild;
- asset approval e runtime evidence nao substituem um ao outro;
- qualquer alteracao no approval record, fonte, convertido, parecer ou painel
  quebra o fingerprint e exige nova aprovacao humana.

### Custo de contexto

- Graphify nao bloqueia o caminho do pedido e pode degradar consultivamente;
- contextos completos ficam em disco; o agente recebe no maximo 32 KiB por
  contexto compacto ou referencias per-target;
- owners e arquivos sao carregados sob demanda e registrados;
- diagnostico, direcao, fontes e aprovacoes sao reutilizados por fingerprint;
- warm start nao repete Graphify, diagnostico ou owner ainda fresco.

### Riscos residuais e respostas

- falsa classificacao de mudanca tecnica: diff/inventario e captura que revelem
  mudanca visual invalidam `technical_runtime_admitted`;
- cache incorreto: qualquer hash autoritativo divergente invalida descendentes;
- excesso de targets: dividir contexto por target sem truncar multiplicidade;
- approval record adulterado: comparar com o hash fixado antes de aceitar.

## Compatibilidade e teto de claims

Projetos legados podem continuar builds tecnicos, mas nao recebem nova
promocao visual sem adotar os contratos. Ausencia de rota ou autoria nao quebra
investigacao controlada; limita o teto a `technical_lab_validated` e
`lab_not_delivery`.

Build verde prova compilacao. Somente a cadeia completa, o julgamento
estetico, a aprovacao humana e o BlastEm podem provar entrega visual.

## Criterio final de aceitacao

Um usuario pede somente `crie uma fase com um heroi enfrentando um boss`. O
framework registra as regras e confiancas acionadas, carrega os owners visuais,
fecha direcao e sourcing, exige animacao, traduz para VDP, valida budget, so
entao admite runtime, constrói a ROM, captura no BlastEm e fecha comparacao e
aprovacao. Em nenhum ponto Pillow, SVG, Canvas, C ou outra ferramenta
procedural pode fabricar a estetica final e atravessar o gate como entrega.
