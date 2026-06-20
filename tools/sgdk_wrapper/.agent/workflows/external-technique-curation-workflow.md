# External Technique Curation Workflow

Status: `workflow_candidate`

Use este workflow quando o usuario trouxer videos, transcricoes, entrevistas,
postagens tecnicas ou pareceres de outra IA para melhorar o agente canonico.

## Objetivo

Transformar material externo em melhoria real do ecossistema sem inflar skills,
sem duplicar owners e sem aceitar relato textual como prova operacional.

## 1. Separar fonte de interpretacao

Classifique cada entrada:

- `direct_transcript`: texto do video ou transcricao esta disponivel;
- `direct_user_summary`: usuario resumiu tecnicas especificas;
- `agent_aggregate_summary`: outro agente trouxe contagem/conclusao agregada;
- `project_evidence`: ha fixture, build, screenshot, dump ou report local;
- `unknown`: fonte insuficiente.

Resumo agregado pode orientar backlog, mas nao justifica skill nova sozinho.

## 2. Criar `external_technique_curation_record`

Para cada tecnica aproveitavel, preencha:

- fonte e disponibilidade;
- tecnica e dominio de risco;
- classificacao: criar skill, aprimorar existente, ja coberto, descartar,
  case study, pipeline update ou backlog;
- owner canonico;
- evidencia atual e minima necessaria;
- decisao de promocao e status.

Schema:

`tools/sgdk_wrapper/schemas/external_technique_curation_record.schema.json`

Exemplo:

`tools/sgdk_wrapper/doc/05_technical/examples/external_technique_curation_record.min.json`

## 3. Regras de decisao

- Crie skill nova apenas se houver ciclo operacional proprio: trigger, entradas,
  saidas, gates e anti-padroes que nao cabem em owner existente.
- Aprimore skill existente quando a tecnica e um refinamento de arte, VDP,
  budget, audio, runtime, pipeline ou governanca ja coberto.
- Marque `already_covered` quando o framework ja exige o gate correto.
- Marque `discard_as_default` quando a tecnica for hack, exploit, historica ou
  util somente em cena especial.
- Use `case_study` quando a tecnica ensina mentalidade ou tradeoff, mas nao
  vira procedimento direto.
- Use `pipeline_update` quando o ganho e de ordem, handoff ou status, nao de
  uma habilidade isolada.
- Use `backlog_pending_evidence` quando a fonte agregada nao sustenta regra.

## 4. Evidencia minima

- `E1_text`: suficiente para case study ou backlog.
- `E2_artifact`: suficiente para proposta candidata.
- `E3_runtime`: necessario para claims de runtime/visual em emulador.
- `E4_vdp_or_hardware`: necessario para claims de H-Int, CRAM mid-frame,
  Shadow/Highlight, scroll tables ou comportamento sensivel do VDP.

## 5. Fechamento

Atualize:

- `video_curation_evidence_backlog.json` para fonte ainda incompleta;
- `aaa_video_curation_manifest.json` para pacote aplicado;
- changelog de curadoria;
- validador, se novos schemas/docs forem adicionados.

Nunca marque `canonical_ready` enquanto houver apenas resumo textual.
