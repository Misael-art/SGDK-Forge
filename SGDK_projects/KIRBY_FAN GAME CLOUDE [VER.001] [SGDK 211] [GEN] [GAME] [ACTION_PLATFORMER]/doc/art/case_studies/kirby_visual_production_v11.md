# Estudo de caso congelado — producao visual Kirby v11

## Decisao

`freeze_visual_production_as_case_study`

Este projeto nao recebera novas poses, frames, strips ou versoes visuais nesta
linha de trabalho. V04-v11, outputs de runtime, staging e arte em `res/` sao
evidencia historica ou tecnica; nenhum deles e fonte autorizada de novos pixels.

Estado honesto no congelamento:

```text
project_stage=technical_runtime_creative_blocked
visual_assets=procedural_code_probe
native_authorship=false
animation_candidate=false
visual_pass=false
res_promotion=false
ready_for_aaa=false
```

## Evidencia que continua valida

- a autoridade R1 foi preservada por SHA-256;
- os gates de PNG P/4bpp, PLTE, index 0 e alpha binario detectam erros reais;
- strips por acao, timing unico, pivot/contato, GIF/strip e fixtures adversariais
  sao controles tecnicos reutilizaveis;
- ROM e BlastEm provaram a rota de runtime para o material medido, nao sua
  qualidade artistica;
- os tetos de claim impediram que o pacote fosse chamado de AAA.

## Evidencia negativa que nao pode virar fonte

- V04-v10 e os outputs V11 produzidos por canvas vazio + `pencil_run`, spans,
  coordenadas ou `putpixel`;
- linearts aprovadas apenas por espessura/topologia;
- strips aprovadas apenas por delta, fases ou timing;
- placeholders e `visual_lab_control` ainda alcançaveis pelo runtime;
- arquivos de `out/`, `data/staging/`, `data/archive/` e `res/` usados como
  underlay, baseline de geracao ou fonte de pixels.

## Causa da regressao

O produtor deterministico representava personagens como runs e patches sobre
canvas vazio. A otimizacao passou a favorecer formas faceis de codificar, nao
silhueta, identidade, acting ou appeal. Validadores comprovaram estrutura e
formato, mas seus nomes permitiram interpretar essas medidas como autoria ou
semantica visual.

## Licoes canonizadas

1. Fonte elegivel vem do workset ativo por caminho e SHA; busca ou proximidade
   no diretorio nao concede autoridade.
2. Arquivo so esta arquivado quando fica inalcançavel pelo grafo de producao e
   runtime, nao quando recebe um rotulo textual.
3. Canvas vazio + pixels definidos por codigo e `procedural_code_probe`, mesmo
   com log detalhado e PNG tecnicamente perfeito.
4. `lineart_topology_pass` nao e aprovacao artistica.
5. Deltas e fases provam `motion_structure_pass`; reconhecimento da acao,
   fidelidade, acting e appeal possuem gates separados.
6. Duas iteracoes sem ganho observavel encerram o produtor/representacao; mais
   reports, builds ou versões nao contam como delta artistico.
7. Specs essenciais vivem em arvore versionada; staging e regeneravel.
8. Build/ROM/BlastEm nao elevam um asset visual reprovado.

## Fechamento executavel

- `forge-art workset-validate` confirma `frozen_case_study` e zero fontes de
  producao;
- `native-edit`, `convert` e `route-shootout` falham com
  `visual_production_frozen` antes de criar saída;
- `spr_native_run_contact_v11` e `spr_native_run_cycle_v11` estão declarados
  como `procedural_primitive` + `visual_lab_control` no manifesto de
  proveniência;
- auditoria de proveniência passa porque os 25 símbolos ativos estão
  classificados honestamente. Isso não concede `visual_pass`.

## Reativacao

Somente uma decisao humana explicita pode descongelar o projeto. Ela deve criar
novo `active_epoch`, novo workset e identificar um produtor visual capaz de
autoria independente. Reusar V04-v11, alterar apenas status ou abrir uma pasta
`v12` nao satisfaz a reativacao.
