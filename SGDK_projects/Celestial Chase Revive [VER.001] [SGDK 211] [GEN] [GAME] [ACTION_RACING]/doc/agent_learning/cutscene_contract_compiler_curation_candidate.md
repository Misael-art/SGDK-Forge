# Cutscene Contract Compiler Curation Candidate

Status: `implemented_locally_after_human_proceed`.

Data: 2026-06-27

Este arquivo registra um candidato local para o agente canonico avaliar. A mudanca foi aplicada no wrapper canonico apos aceite humano explicito nesta sessao, mas ainda precisa de curadoria posterior para consolidar a regra como padrao de futuros projetos.

## Problema observado

O projeto agora possui contratos estruturados para:

- `opening_catalyst_cutscene`;
- `race_start_handoff`.

Mesmo assim, `scene_contract_compiler.ps1 -Mode production` continua gerando
`doc/scene-contracts.json` sem `cutscene_contract`, e o lint emite `SC100`.

## Evidencia local

- `doc/contracts/opening_cutscene_contract.json`
- `doc/contracts/opening_cinematic_storyboard_contract.json`
- `doc/contracts/race_start_handoff_contract.json`
- `doc/contracts/race_start_handoff_cinematic_storyboard_contract.json`
- `out/logs/scene_contract_overlay_probe.json`
- `out/logs/scene_contract_report.json`
- `tools/sgdk_wrapper/ci/test_scene_contract_compiler.ps1`
- `tools/sgdk_wrapper/ci/test_cutscene_contract_lint.ps1`

O overlay probe removeu `SC100`/`SC107` para abertura e handoff quando os campos
foram injetados no contrato compilado. Naquele momento o artefato canonico real
permanecia limitado pelo compilador.

Atualizacao: `tools/sgdk_wrapper/scene_contract_compiler.ps1` agora descobre contratos de cutscene em `doc/contracts/*_contract.json` e projeta `cutscene_contract` no artefato canonico por `scene_id`. A regressao de compilador passou 8/8 e o lint especifico de cutscene passou 7/7.

## Mudanca proposta

Adicionar ao wrapper uma fonte estruturada para contratos de cutscene, com uma
das rotas abaixo:

1. O compilador reconhece blocos `Contrato de cutscene` em `doc/13-spec-cenas.md`.
2. O compilador mescla campos de `doc/scene-contract-overrides.json`.
3. O compilador descobre `doc/contracts/*_contract.json` quando
   `scene_role=cutscene`.

Rota aplicada: opcao 3, com chaveamento por `scene_id` declarado no JSON para tolerar nomes de arquivo historicos como `opening_cutscene_contract.json`.

## Gate de aceitacao

- `scene_contract_compiler.ps1 -Mode production` preserva `cutscene_contract`.
- `lint_scene_contract.ps1 -Mode production` nao emite `SC100` para cutscenes com contrato.
- `lint_scene_contract.ps1 -Mode aaa_gate` valida `cinematic_storyboard_contract`.
- Teste CI cobre abertura com storyboard e handoff curto sem texto.

## Limites

- Nao promover cenas futuras para `supported` sem rota real no runtime.
- Nao transformar contrato planejado em evidencia de emulador.
- Nao alterar wrapper canonico sem aprovacao humana explicita.
