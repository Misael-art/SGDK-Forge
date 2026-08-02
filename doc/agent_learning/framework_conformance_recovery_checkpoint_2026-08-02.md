# Framework Conformance Recovery Checkpoint - 2026-08-02

Status: `checkpoint_recovered_framework_partial`

Claim ceiling: infraestrutura de conformance parcialmente implementada. Este
registro nao prova framework funcional completo, pipeline AAA, build de jogo,
ROM, runtime ou evidencia em emulador.

## Motivo do registro

O agente anterior foi interrompido por limite diario de tokens enquanto atuava
no worktree isolado `/tmp/forge_remediation_wt`. Este documento preserva o
estado factual encontrado, os testes reexecutados e o ponto seguro de retomada.

## Estado Git recuperado

- branch: `remediation/framework-conformance`
- base original: `b345c6ab`
- commit ja concluido pelo agente: `96de9154`
- titulo do commit: `fix: make the skill bridge portable across checkouts`
- worktree principal nao foi resetado, limpo nem misturado ao checkpoint

O commit `96de9154` preserva:

- `.agents/skills` com alvo relativo
  `../tools/sgdk_wrapper/.agent/skills`;
- reconciliacao de 13 hashes legacy;
- `test_skill_bridge_materialization.py`;
- recuperacao de stub de checkout em `prepare_agent_environment.ps1`;
- integracao do gate de materializacao antes do validador de framework.

## Delta interrompido recuperado

| Arquivo | Estado recuperado | SHA-256 antes do checkpoint |
|---|---|---|
| `tools/sgdk_wrapper/audit_skill_lifecycle.ps1` | ordenacao por caminho relativo POSIX com `StringComparer.Ordinal` | `919bcd524972010813ceef4e956f8f2d0858213276bdfa41fbbb4eb5d60134e8` |
| `tools/sgdk_wrapper/ci/test_skill_hash_engine_parity.ps1` | gate novo; compara fixture sintetica e 13 payloads legacy | `a7254e4f53fcd150d16bdf2db23750f5f584c63810ce1a4c9d9d832eeeedcdba` |
| `tools/sgdk_wrapper/ci/test_canonical_skill_curation.ps1` | gate de paridade conectado a suite agregada | `07fa973840d08f57218b8d44b18ccb24207a1319f9a5f0739fb9d6b76e4a6f22` |
| `tools/sgdk_wrapper/lib/host_executors.psm1` | helper central com resolucao de pwsh/Python/Java e validacao do cache Python | `1e9cb382caa0bc01eea0887fb42f264fc9b00e28b41e0ddfb03516682afa51a3` |

## Validacao reexecutada em 2026-08-02

| Verificacao | Resultado | Observacao |
|---|---|---|
| hash engine parity | passou | 14/14 payloads no Linux |
| lifecycle audit | passou | 13 active registrados, 13 legacy, 0 erros |
| bridge gate em checkout cru | falhou | `core.symlinks=false` materializou arquivo-texto |
| framework validator em checkout cru | falhou | bridge mismatch |
| preparo direto do ambiente | parcial | rematerializou a ponte; depois falhou com `USERPROFILE` nulo |
| bridge gate apos rematerializacao | passou | 6/6, 47 skills visiveis |
| framework validator apos rematerializacao | passou | 47 active, 13 legacy |
| guard `assert_agent_environment.ps1` | falhou | chama `powershell` literal no Linux |
| suite canonical skill curation | parcial | passou bridge, framework, paridade, lifecycle e route validator; parou em `powershell.exe` literal no teste de lifecycle |

## Blockers e riscos conhecidos

1. `assert_agent_environment.ps1` ainda chama `powershell` literalmente. No
   Linux o guard falha antes de executar a preparacao.
2. `prepare_agent_environment.ps1` consegue recuperar o stub da ponte, mas
   `Refresh-ProcessPath` usa `USERPROFILE` sem fallback Linux e falha depois da
   rematerializacao.
3. A suite agregada ainda encontra consumidores que chamam
   `powershell.exe` literalmente. O helper central nao esta integrado.
4. `host_executors.psm1` depende de
   `linux_python_requirements.lock`, `ensure_linux_python_deps.sh` e do cache
   `out/host_tools/python/site-packages`; esses itens nao existem nesta branch
   isolada neste checkpoint. O helper esta preservado, mas nao e autonomo nem
   concluido.
5. O gate de paridade novo cobre a ordem ordinal, mas a implementacao Python
   embutida no teste nao reproduz a normalizacao CRLF/LF existente em
   `validate_skill_framework.py`. A paridade Windows ainda precisa de fixture
   CRLF e de uma unica implementacao canonica ou contrato compartilhado.
6. O lifecycle audit reporta 13 owners active registrados, enquanto o framework
   validator descobre 47 skills active. A reconciliacao de cobertura entre
   lifecycle registry, framework manifest e descoberta permanece tarefa aberta.
7. O commit `96de9154` e correto como material e recuperacao, mas a frase
   "clean worktree now reports" pressupoe preparacao previa. Checkout cru com
   `core.symlinks=false` continua bloqueado ate o guard funcionar.

## Estado das tarefas deixadas na interface

| Tarefa | Estado factual |
|---|---|
| helpers compartilhados de executores | `in_progress_checkpointed`, nao integrado |
| entradas `run_framework_conformance.sh/.bat` | `not_started` |
| reconciliar `framework_manifest.json` e estender validador | `not_started` |
| golden obrigatorio com registry de referencias | `not_started` |
| criar `FORGE_REFERENCE` canonico | `not_started` |
| sexta tarefa exibida de forma truncada | `unknown_not_inferred` |

## Ordem segura de retomada

1. Integrar `host_executors.psm1` primeiro em
   `assert_agent_environment.ps1`, `prepare_agent_environment.ps1` e nos testes
   que ainda chamam `powershell`/`powershell.exe`.
2. Corrigir `USERPROFILE` nulo no preparo Linux e provar o guard completo em
   checkout cru com `core.symlinks=false`.
3. Trazer para a branch, de forma cirurgica, o lock/bootstrap Python canonico;
   gates nao podem baixar da rede nem aceitar dependencia global.
4. Completar o gate de paridade com CRLF e verificar o motor real usado pelo
   validador Python.
5. Reexecutar `test_canonical_skill_curation.ps1` ate o final.
6. Somente depois iniciar entrypoints deterministas, manifest, golden registry e
   `FORGE_REFERENCE`.

## Criterio para promover o checkpoint

Nao promover este commit como remediacao concluida ate existir worktree limpo
com guard de ambiente, suite canonica e conformance runner completos, sem
dependencia global e sem zero-golden falso verde.
