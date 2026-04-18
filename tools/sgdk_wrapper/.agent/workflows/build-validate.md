# Workflow: Build Validate

Use este fluxo para build, rebuild e validacao operacional.

## Entrada

- raiz do projeto
- contexto resolvido pelo wrapper
- `.agent` local nao degradada ou explicitamente tratada como invalida

## Passos

1. Resolver contexto do projeto e manifesto.
2. Auditar bootstrap local da `.agent`.
   - se faltar manifesto, tentar heal seguro
   - se faltarem `pipelines`, skills de arte ou workflows criticos, tratar como `agent_context_degraded`
3. Rodar `preflight_host.ps1` quando a sessao ainda nao foi saneada.
4. Rodar build pelo wrapper canonico.
5. Registrar identidade da ROM:
   - caminho
   - tamanho
   - hash
   - timestamp
6. Marcar evidencia antiga como `stale` quando a ROM mudar.
7. Atualizar `doc/changelog/` via script canonico:
   - snapshot de assets alterados
   - snapshot da ROM quando o hash mudar
   - atualizacao de `build_meta.json`
   - atualizacao do bloco derivado em `doc/10-memory-bank.md`
8. Executar `validate_resources.ps1 -CloseoutGate` no fechamento de QA; durante iteracao, o wrapper pode usar o modo normal apenas para manter o relatorio coerente sem bloquear o build.
9. Conferir blockers de fechamento:
   - `agent_context_degraded`
   - `budget_doc_mismatch`
   - `visual_gate_blocked`
   - `emulator_evidence_stale`
   - `changelog_missing`
10. Rodar BlastEm para gate de entrega.
11. Consolidar:
   - `emulator_session.json`
   - `validation_report.json`
   - `doc/changelog/changelog.md`
   - `doc/10-memory-bank.md`
12. Se houver novo build depois disso, rebaixar a evidencia anterior para `stale`.

## Semantica do Gate Final

- `visual_lab_aprovado` pode fechar o laboratorio visual, mas nao autoriza entrega AAA sozinho.
- `gameplay_rom_aprovada` exige gameplay real, `performance`, `audio` e `hardware_real` fora de `nao_testado`.
- `ready_for_aaa` so pode ser verdadeiro quando a ROM jogavel estiver aprovada e o budget/runtime estiverem validados.

## Saida minima esperada

- `out/rom.bin` com identidade registrada
- `out/logs/validation_report.json`
- `out/logs/emulator_session.json`
- `doc/changelog/changelog.md`
- `doc/10-memory-bank.md` coerente com a ROM vigente

## Regras de Fechamento

- `summary.errors == 0` continua obrigatorio
- nenhum blocker de fechamento pode permanecer ativo
- BlastEm e obrigatorio para `testado_em_emulador`
- `doc/changelog` nao e opcional
- memoria operacional nao pode contradizer a ultima ROM validada
