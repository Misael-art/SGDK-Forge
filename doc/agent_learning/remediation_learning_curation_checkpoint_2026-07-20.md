# Checkpoint De Curadoria Do Aprendizado - 2026-07-20

Status: `captured_validated_pending_maturity`

## Autorizacao E Limites

O responsavel humano autorizou registrar os aprendizados maduros da jornada de
remediacao e manter os demais pontos em uma fila retomavel conforme novas
evidencias se tornarem maduras.

Esta autorizacao cobre captura, triagem, deduplicacao, definicao de owner,
criterios de maturidade e retomada do processo. Ela nao promove automaticamente
ROM, tecnica, skill, `MESTRE_*`, `stable`, `release` ou `ready_for_aaa`.
Qualquer patch canonico deve continuar possuindo evidencia, limite de escopo,
teste de generalizacao e regressao proporcional ao risco.

## Estado Consolidado

| Item | Aprendizado reutilizavel | Maturidade de curadoria | O que ja foi assimilado | O que ainda nao foi feito | Gatilho de retomada |
|---|---|---|---|---|---|
| P0-001 | Arquivo de screenshot existente nao prova conteudo visual util | `integrado_verificado` | Gate semantico, schema, fixtures negativas e consumo no closeout/validator | Monitoramento de novos formatos | Nova classe de falso positivo visual |
| P0-002 | O menor status comprovado vence claims narrativos | `integrado_verificado` | Reconciliador por status, ROM, sessao e conflitos | Incluir futuros tipos de report | Novo report forte nao reconhecido pelo reconciliador |
| P0-003 | Dependencia ausente nao pode virar skip silencioso | `integrado_verificado` | Provisionamento Linux fixado, hashes e runner canonico | Validar em hosts adicionais quando disponiveis | Novo host ou atualizacao controlada das dependencias |
| P0-004 | Divergencia de hash exige diagnostico historico antes de regravar registry | `integrado_verificado` | Algoritmo deterministico e auditoria de payload legado | Nenhuma promocao tecnica nasce desse reparo | Nova divergencia lifecycle ou mudanca do algoritmo |
| P0-005 | ROM, screenshot, SRAM, dump e metricas precisam da mesma sessao | `integrado_verificado` | Bundle selado, identidade e auditoria de freshness/tamper | Reexecutar depois de toda ROM relevante | Rebuild, nova captura ou mudanca do contrato de evidencia |
| P1-001 | Laboratorio aninhado nao deve ser classificado como ausencia de arte | `integrado_verificado` | Discovery confinado ao projeto e ownership por classe de arte | Ampliar apenas com fixtures de novos layouts | Novo layout real nao reconhecido sem atravessar isolamento |
| P1-002 | Prova tecnica de FM/PSG/XGM2 nao substitui avaliacao auditiva humana | `tecnico_completo_bloqueado_externo` | Ownership de canais, telemetria, analise WAV e gate conservador | Revisao auditiva humana | Registro humano de audio com decisao e escopo |
| P1-003 | Performance exige janela completa, regiao e conclusao explicita | `comprovado_localmente` | Probe 900/750, parser, serie/agregados, NTSC/PAL e bundle BlastEm | Generalizacao cross-project e contrato parametrico | Segunda cena/projeto reproduzir fixtures completa e parcial |
| P1-004 | BlastEm nao prova console real ou FPGA | `gate_implementado_bloqueado_externo` | Schema, protocolo, validador e mastering conservador | Sessao real, video/captura e atestacao | Evidencia externa vinculada a mesma ROM |
| P1-005 | Autonomia deve ser calculada de eventos, nao estimada narrativamente | `instrumentacao_verificada_amostra_limitada` | Schema, recorder, derivador, privacidade e regressao | Amostra longitudinal e mais sessoes | Volume suficiente para comparar rework e first-attempt ao longo do tempo |
| P1-006 | Infraestrutura corrigida nao equivale a jogo curto completo | `nao_iniciado_bloqueado` | Dependencias e acceptance checks documentados | Conteudo completo, audio humano, hardware aplicavel e todos os gates | Dependencias externas e tecnicas fechadas |
| P2-001 | Memoria, changelog e reports precisam de uma unica identidade/status ativo | `implementacao_iniciada_nao_fechada` | Auditor e regressao inicial existem | Executar report real, reconciliar contradicoes e fechar backlog | `doc_sync_report` real sem contradicao forte |
| P2-002 | Continuidade precisa ser medida por uma sessao independente | `nao_executado` | Handoff, memory bank e backlog existem | Independent session log e context recovery report | P2-001 concluido |
| P2-003 | Tecnica so pode subir com fixture, ROM, BlastEm, budget, fallback e aprovacao | `nao_executado` | Politica e acceptance checks existem | Technique promotion report e runtime bundle de escopo elegivel | Tecnica candidata cumprir todos os checks sem inferencia documental |

## Aprendizados Que Ja Devem Orientar Novas Construcoes

1. Separar planejamento, implementacao, build, emulador, budget, audio humano,
   hardware e qualidade criativa em eixos independentes.
2. Nunca promover claim pela mera existencia de arquivo, hash, codigo ou
   screenshot.
3. Exigir identidade de ROM e sessao em todo artefato de evidencia ativo.
4. Rejeitar captura parcial quando o claim exigir estabilidade sustentada.
5. Medir DMA e sprites no ponto correto do frame e preservar o payload selado.
6. Tratar aprovacao humana externa como blocker real, nao como campo a ser
   preenchido pelo agente.
7. Converter erros recorrentes em validator, schema, workflow ou regressao;
   uma nota isolada nao fecha a curadoria.
8. Parametrizar invariantes comprovadas; nao universalizar offsets, contagens
   ou layouts especificos de um unico projeto.

## Fila De Retomada

Ordem conservadora atual:

1. fechar P2-001 e gerar `doc_sync_report` real;
2. testar P2-002 em contexto independente;
3. reclassificar P2-003 apenas quando houver tecnica elegivel com prova completa;
4. retomar P1-002 quando houver review humano de audio;
5. retomar P1-004 quando houver console/FPGA e captura externa;
6. considerar P1-006 somente depois dos bloqueios acima.

Fonte machine-readable:
`doc/agent_learning/remediation_learning_curation_checkpoint_2026-07-20.json`.

## Resultado Da Captura

- `learning_context_status=learning_context_present`;
- 15 licoes extraidas e 10 entradas no indice de candidatos;
- 6 propostas roteadas para owners canonicos existentes e 9 licoes mantidas
  sem proposta de patch;
- todas as propostas permanecem `not_applied`;
- `canonical_promotion_performed=false`;
- schema do ledger: `passed`;
- Audit posterior: read-only, zero warnings e hashes preservados;
- regressao do ciclo de aprendizado: 34/34 checks.
