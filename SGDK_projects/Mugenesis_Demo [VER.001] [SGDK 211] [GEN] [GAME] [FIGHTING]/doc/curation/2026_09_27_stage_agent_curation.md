# Curadoria do agente canonico — Suzaku — 2026-09-27

Autorizacao: pedido explicito do usuario para curar o que a rodada ensinou.
Alcance: metodo reutilizavel. O cenario do jogo permanece incompleto.

| Ponto | Estado anterior | Decisao | Owner |
|---|---|---|---|
| Reuso H/V | Ja previsto genericamente | Acrescentar grade original, uniao do plano, compartilhamento entre pecas e custo compilado. Recorte nao e economia nova. | `art/multi-plane-composition` |
| Budget VRAM | `TILE_MAX_NUM` descrito como teto geral seguro | Distinguir alocacao automatica de bancos fisicos explicitamente reclamados; intervalos por fase e restauracao obrigatorios. | `hardware/megadrive-vdp-budget-analyst` |
| Falha de init | Triagem ja separava host/build/runtime | Acrescentar primeira guarda e seus operandos; nova triagem apos destravar etapa. | `workflows/production-diagnostic-triage` |
| Paleta de atlas | Regra de indices e quantizacao ja existia | Exigir igualdade dos indices usados em palavras CRAM compiladas entre atlas e paleta carregada. | `art/multi-plane-composition` |
| Bundle rejeitado | Claims ja separados | Captura rejeitada pode dar diagnostico local sem liberar gate. | `operation/emulator-vdp-evidence-curator` |

Fonte e limite de cada observacao: `tools/sgdk_wrapper/.agent/references/mugen_suzaku_vram_diagnostic_2026_09_27.md`.
Evidencia local: `doc/mugen/suzaku_piece_reuse_baseline.json`, ROMs
`bef4dba9...` e `8bf3b933...` e respectivas sessoes de BlastEm. O segundo
bundle foi rejeitado; sua screenshot sustenta apenas que a tela foi renderizada
com cores/artefatos incorretos. A capacidade de 920 tiles e contrato do
alocador host na configuracao medida, sem aprovacao do runtime completo.

Nao promovidos: fidelidade de arte, piso com perspectiva, paleta corrigida,
streaming, desempenho, SUPER no HUD, audio, aceite AAA ou capacidade de
converter todo MUGEN. O experimento de redesenho modular ainda nao ocorreu.

Mudancas canonicas: duas skills, um workflow e a skill de evidencia citados
na tabela; referencia de caso adicionada e indice MUGEN atualizado. Nenhuma
skill, status de mastery, schema ou tecnica de hardware nova foi criada.

Validacao: `git diff --check` passou; quatro testes direcionados de allocator
e contagem de tiles passaram. `validate_skill_framework.py` continua bloqueado
por falhas em skills nao alteradas (music-composition, reviewers,
harness-orchestration e limite de contexto). `test_schema_contract_gates.py`
nao iniciou porque o Python do host carece de `jsonschema`. Nenhum desses
resultados deve ser relatado como regressao aprovada do framework inteiro.
