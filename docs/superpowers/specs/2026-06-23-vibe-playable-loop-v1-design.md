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
- por intencao: `confidence`, `matched_rule_ids`, `matched_terms` e
  `decision_reason`;
- `ambiguity_status` e regras conflitantes;
- `fallback_decision`;
- `visual_route_required`;
- `required_owners` em ordem;
- `required_artifacts`;
- `runtime_admission`;
- `blocking_statuses`.

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

O contexto compacto deve incluir os owners visuais antes de qualquer owner de
runtime.

## Trava de admissao do runtime

O loop usa estados monotônicos:

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

O build manifest deve registrar o SHA-256 do route report e dos gates usados
na admissao. `validate_resources.ps1` deve bloquear promocao quando houver
intencao visual ou recursos visuais sem route report/admission correspondente.
Runtime tecnico ainda pode ser aberto em `debug_lab`, mas somente depois de
`request_routed`, em caminho e manifesto de laboratorio, por uma decisao
separada `runtime_lab_admitted`. Essa decisao exige `lab_not_delivery=true`,
`creative_ready=false` e nao pode promover baseline visual nem satisfazer
`runtime_admitted` de producao.

Assim, o roteador impede a abertura prematura de runtime por duas barreiras:

1. o pipeline nao oferece handoff para `sgdk-runtime-coder` antes de
   `runtime_admitted`;
2. o validator rejeita build/closeout de producao cujo manifest nao carregue a
   decisao de admissao vinculada ao route report.

## Manifesto de autoria e fonte visual

Cada asset critico deve possuir um `premium_visual_source_manifest` antes da
conversao ou promocao. Ele registra:

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
4. aprovacao humana apontando para hashes e evidencia atuais.

O painel deve identificar ROM SHA-256, scene id, asset ids, source hashes e
timestamp da sessao. Um novo build invalida a aprovacao de runtime anterior.

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
- primeiro preparo com `graph_missing` usa timeout maior, alvo de 300 segundos;
- updates incrementais usam timeout menor e o cache existente;
- somente mudancas nos tracked roots marcam stale;
- uma sessao nao repete build do grafo para cada roteamento;
- falha consultiva e reportada separadamente e nao autoriza relaxar gates
  visuais.

## Schemas, workflows e validators

O plano de implementacao devera cobrir, sem duplicar owners:

- pipeline `vibe_playable_loop_v1`;
- workflow de entrada natural e admissao de runtime;
- schema e roteador do `vibe_playable_route_report`;
- endurecimento do `art_gameplay_direction_gate` existente;
- schema do `premium_visual_source_manifest`;
- schema da cadeia source-to-runtime/build/evidence;
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
4. sprite procedural critico e bloqueado;
5. scripts de conversao, quantizacao, corte, tiles/atlas, mascaras e
   diagnosticos permanecem permitidos quando descendem de fonte aprovada;
6. ausencia de image tooling/fonte premium produz blocker, nao arte inferior;
7. animacao sem motion preview ou pivots nao e promovida;
8. build verde com placeholder permanece `lab_not_delivery`;
9. build manifest seleciona a variante `elite` aprovada, nunca `basic`;
10. screenshot/dump e sessao BlastEm pertencem a ROM e asset chain atuais;
11. tentativa adversarial de entregar personagem, cenario, HUD ou FX desenhado
    por Pillow, SVG, Canvas ou primitivas C e rebaixada para
    `lab_not_delivery`;
12. variantes `basic` e `elite` quase iguais falham o delta perceptivo;
13. metricas sem painel, parecer estetico ou aprovacao humana nao promovem;
14. route report ausente impede `runtime_admitted` para pedido visual;
15. fixture visual end-to-end usa fonte premium bitmap nao procedural,
    conversao VDP, animacao com motion preview, ROM real, BlastEm, screenshot,
    SRAM/dump aplicavel, cadeia completa e aprovacao visual.

A fixture end-to-end deve persistir uma fonte `human_authored`,
`generated_bitmap` ou `licensed_source` com autoria/licenca e hash. Seu setup
nao pode desenhar a arte por script. Scripts podem apenas processar a fonte
persistida e montar os artefatos de diagnostico.

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
