# Plano de Provas — FORGE_REFERENCE

## Ordem

1. validar contexto, metodologia, higiene e recursos;
2. executar `test_canonical_fixture_contracts.py`;
3. executar `test_project_learning_loop.py` no ambiente Python hermético;
4. buildar com o wrapper central e registrar SHA-256 da ROM;
5. iniciar a ROM no BlastEm e aguardar ao menos 240 frames de cena;
6. capturar screenshot e SRAM da mesma sessão;
7. parsear `FREF` com `canonical_fixture_gate.py --fref-sram`;
8. selar bundle e reavaliar identidade com manifesto e relatório ligados ao
   mesmo SHA-256;
9. atualizar memory bank e changelog.

## Resultado esperado

- gate amostrado: denominador maior que zero, violações zero;
- telemetria: versão e comprimento válidos; campo opcional ausente vira aviso;
- playtest: `requested=0x0003`, `observed=required=0x0007`, `completed=1`;
  o terceiro bit e observado pelo contrato de elisao, nao pedido como input;
- tabela estática: hashes iguais, rebuild/upload estático zero;
- CRAM: 16 usadas, zero ilegais; screenshot não substitui dump;
- escopo: `runtime_observation`, sem extrapolação;
- identidade: bundle e gate com a mesma ROM.

## Falha fechada

Qualquer ausência de amostra, campo obrigatório, bit observado, hash de ROM ou
evidência BlastEm mantém o item como `not_run`, `warning`, `blocked` ou
`failed`; nunca como aprovação implícita.
