# Production Diagnostic Triage

## Objetivo

Impedir que falhas de host, toolchain, ROM e qualidade criativa sejam
misturadas durante producao ou recuperacao de projetos.

## Entrada minima

- projeto alvo ou pedido de bootstrap;
- hierarquia de verdade do projeto, quando existir;
- ultimo binario e evidencia conhecidos;
- erro ou objetivo observavel.

## Procedimento

1. Leia `references/production_truth_protocol.md`.
2. Classifique `host_executor` antes de iniciar comandos destrutivos ou editar
   runtime.
3. Classifique `toolchain_wrapper` por estagio. Nao converta falha de
   pos-processamento em falha de compilacao.
4. Congele o ultimo binario comprovado e seu hash antes de investigar runtime.
5. Classifique `rom_runtime` somente com observacao da ROM, telemetria ou
   evidencia rastreavel.
6. Avalie `creative_quality` separadamente e apenas depois da verdade tecnica.
7. Para projeto existente, preserve worktree, baseline, historico e claims
   rebaixados. Nao renomeie legado automaticamente.
8. Para projeto novo, feche bootstrap, contexto, contratos, seed instrumentado,
   primeira rota vertical e budgets antes da producao definitiva.

## Saida minima

Um diagnostico curto contendo as quatro camadas, seus estados, evidencias,
blockers e a proxima acao causal.

## Passa quando

- nenhuma falha foi atribuida a uma camada sem evidencia;
- o hash da ROM usada na evidencia esta registrado;
- input publicado e input observado nao foram confundidos;
- estado tecnico e promocao criativa permanecem independentes;
- a correcao proposta ataca uma causa confirmada.

## Handoff para proxima etapa

- host bloqueado: manutencao do host, sem alterar runtime;
- toolchain bloqueada: `skills/operation/sgdk-build-wrapper-operator`;
- runtime bloqueado: `skills/code/sgdk-runtime-coder` e skill do subsistema;
- evidencia pendente: `skills/operation/emulator-vdp-evidence-curator`;
- qualidade criativa pendente: skill de arte/design aplicavel;
- claim AAA: `skills/governance/aaa-pipeline-guardian`.
