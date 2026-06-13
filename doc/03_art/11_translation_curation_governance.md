# Translation Curation Governance

## Objetivo

Eliminar ambiguidade entre doutrina, few-shot pedagogico, corpus real e promocao para ROM.

## Hierarquia canonica

### 1. Doutrina

Arquivos que ensinam como o agente deve pensar e operar.

- `tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md`
- `doc/03_art/04_art_translation_curation_protocol.md`
- `doc/03_art/02_visual_feedback_bank.md`

### 2. Few-shot pedagogico

Casos destilados usados para consulta rapida do agente.

- `tools/sgdk_wrapper/.agent/lib_case/`

Regra:

- nao e codigo produtivo
- nao e backlog
- nao e corpus final

### 3. Corpus canonico

Casos reais com manifestos explicitos.

- `assets/reference/translation_curation/case_registry.json`
- `case_manifest.json`
- `collection_manifest.json`
- `corpus_manifest.json`

### 4. Promocao runtime / ROM

Quando a traducao sai do laboratorio e entra em `SGDK_projects/`.

Regra:

- so pode acontecer quando o caso estiver marcado como `runtime_candidate` ou `promoted_to_rom`

## Tipos de entrada

- `single_case`
  - caso real unitario
- `case_collection`
  - colecao com subcasos
- `training_corpus`
  - corpus pedagogico, nao competidor de caso final

## Regras de verdade

- `case_registry.json` e o indice mestre
- o manifest local e a verdade de cada pasta
- `reports/` guarda somente saidas geradas
- `truth/` guarda supervisao humana, quando existir
- `legacy` nunca compete com `canonical` sem declaracao explicita

## Consulta obrigatoria de agentes

1. skill e protocolo para o fluxo
2. `lib_case` para few-shot
3. `case_registry.json` para escolher o caso real correto

## Anti-ambiguidade

- backlog nunca substitui status de caso
- status de skill nunca substitui status de corpus
- prova offline nunca substitui prova em ROM
- few-shot nunca substitui caso real
