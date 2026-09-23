# AAA Skill Canonization Protocol

Ultima atualizacao: 2026-04-10

## Objetivo

Este documento rege a canonizacao de skills artisticas e tecnicas do workspace em nivel de meta-governanca.

Ele existe para:

- separar `doutrina incorporada` de `prova em ROM`
- impedir que pesquisa forte seja promovida cedo demais
- absorver novos aprendizados sem sobrescrever silenciosamente a malha atual

Este protocolo NAO substitui protocolos especializados.

Permanece especializado e obrigatorio para traducao artistica:

- `doc/03_art/04_art_translation_curation_protocol.md`

## Hierarquia de governanca

1. Este protocolo-meta rege promocao e versionamento de skills
2. Protocolos especializados regem o fluxo interno de cada dominio
3. Status doutrinario vive em `doc/03_art/AAA_SKILL_CURATION_STATUS.md`
4. Estado operacional real vive em memory banks, manifests e provas de emulador

## Regra suprema

Se nao foi provado em ROM e aprovado pelo humano, nao existe como canon runtime.

Consequencia:

- skill pode estar `INCORPORADA` como doutrina
- skill so vira referencia de runtime depois de BlastEm + evidencia + aprovacao humana

## Modelo de status obrigatorio

Toda skill deve ser lida em dois eixos:

- `doctrine_status`
  - `PENDENTE`
  - `PROPOSTO`
  - `RASCUNHO`
  - `DRAFT_APROVADO`
  - `INCORPORADO`
- `runtime_proof_status`
  - `NAO_INICIADA`
  - `POC_PENDENTE_ROM`
  - `VALIDADA_EM_ROM`
  - `APROVADA_PELO_HUMANO`

Regra:

- `doctrine_status` nunca substitui `runtime_proof_status`
- `runtime_proof_status` nunca reescreve o historico doutrinario

## Gate em 5 fases

### Fase 1 - Pesquisa e draft

Obrigatorio:

- estudar referencias reais do workspace
- definir regras binarias com linguagem `DEVE`, `NAO DEVE`, `PROIBIDO`, `OBRIGATORIO`
- definir metricas com corte numerico ou criterio visual inequivoco
- nomear benchmarks comerciais
- listar checklist de validacao
- listar anti-padroes proibidos

Gate:

- aprovacao humana do draft

### Fase 2 - Prova de conceito em codigo

Obrigatorio:

- implementacao real em `SGDK_projects/BENCHMARK_VISUAL_LAB`
- codigo C SGDK 2.11 valido
- assets minimos, mas representativos
- build bem-sucedido com ROM gerada

Gate:

- humano compila, roda e aprova o POC como candidato a prova runtime

### Fase 3 - Validacao de eficacia

Obrigatorio:

- captura dedicada no BlastEm
- screenshot rastreavel
- comparacao com benchmark nomeado
- estabilidade observavel
- budget de VDP respeitado

Gate:

- humano aprova ou reprova explicitamente

### Fase 4 - Canonizacao

Obrigatorio apos aprovacao humana:

- promover ou versionar documento canonico
- promover ou versionar skill correspondente
- preservar o codigo de referencia no laboratorio
- registrar heuristicas aprovadas no feedback bank ou memoria apropriada

Gate:

- confirmacao humana de que a canonizacao ficou completa

### Fase 5 - Curadoria continua

Obrigatorio:

- cada uso real devolve aprendizado para memory bank e feedback bank
- heuristica nova so entra com aprovacao humana
- mudanca relevante gera nova versao, nunca edicao silenciosa de criterio canonico

## Clausula anti-ambiguidade

- regra deve ser binaria
- metrica deve ter threshold ou benchmark de comparacao
- checklist deve ser respondido com `SIM` ou `NAO`
- excecao so existe se estiver explicitamente listada com condicao de ativacao
- backlog nao substitui status
- appendix nao substitui front door
- prova offline nao substitui prova em ROM
- few-shot nao substitui caso real

## Clausula anti-retrocesso

- nenhuma skill nova pode degradar skill ja incorporada sem aprovacao humana explicita
- toda alteracao relevante gera nova versao da skill
- entradas do feedback bank nao sao removidas; podem apenas ser marcadas como superseded
- codigo de referencia do laboratorio nao e deletado; pode ser arquivado com motivo registrado
- antes de canonizar nova skill, o checklist das skills impactadas deve ser reexecutado no laboratorio

## Regra 9 - Citacao obrigatoria do conhecimento de engines

Todo draft de Sprint 2+ DEVE citar, nesta ordem:

1. `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md`
2. `doc/05_technical/92_sgdk_engine_pattern_registry.json`
3. `doc/05_technical/99_sgdk_engines_scan_appendix.md`

Regra de uso:

- `92_frontdoor` define a leitura canonica
- `92_registry` define a classificacao automatizavel
- `99_appendix` entra apenas como evidencia bruta e log de extracao

Draft que ignorar essa ordem e automaticamente reprovado em Fase 1.

## Regras de integracao com a malha atual

- `S1.1`, `S1.2` e `S1.3` permanecem competencias incorporadas; este protocolo NAO as rebaixa
- documentos ja existentes devem ser revisados in place quando voltarem ao fluxo
- skills ja existentes devem evoluir nos diretorios atuais; nao duplicar por renomeacao cosmetica
- identificadores canonicos do roadmap sao `S1.1` ate `S5.2`
- nome final de documento futuro so e reservado quando a skill entrar formalmente em Fase 1

## Backlog oficial futuro

Fica aceito como backlog oficial futuro:

- `S5.1` Forward Kinematics
- `S5.2` XGM2 Audio Architecture

Regra:

- backlog oficial futuro NAO equivale a draft ativo
- skill final, doc final e POC continuam bloqueados ate a entrada formal em Fase 1
