# Framework Conformance Recovery Checkpoint - 2026-08-02

Status: `checkpoint_recovered_framework_partial` -- **superado em 2026-08-04**.

> Este documento tem duas partes. O corpo abaixo preserva o estado factual de
> 2026-08-02, quando o trabalho estava interrompido, e permanece intacto como
> registro historico. A secao final, `Resolucao - 2026-08-04`, tem precedencia:
> os quatro blockers P0 foram fechados e o status corrente e
> `framework_conformance_validated`. Nao leia os blockers do corpo como abertos
> sem conferir a tabela de resolucao no fim.

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

---

# Resolucao - 2026-08-04

Status: `framework_conformance_validated`.

Esta secao substitui as expectativas da parte acima. O checkpoint de 2026-08-02
descrevia trabalho interrompido; os quatro blockers P0 agora estao fechados.

## Correcao factual do checkpoint

O blocker 5 acima afirma que a implementacao Python embutida no teste "nao
reproduz a normalizacao CRLF/LF existente em `validate_skill_framework.py`".
Isso estava errado: **nenhuma** das tres implementacoes normalizava fim de linha
-- todas hasheavam bytes crus. Nao havia normalizacao a reproduzir. O contrato
CRLF/LF foi introduzido em 2026-08-04, nao apenas replicado.

## Commits

| Commit | Escopo | Validacao |
|---|---|---|
| `6e7bd223` | executores do host em vez de `powershell` literal | 12/12, 192 scripts varridos |
| `a4882e98` | dependencias Python dos gates hermeticas | 18/18 |
| `62fb7484` | hash de payload identico em qualquer host | 34/34 paridade |

## Blockers do checkpoint, um a um

| # | Blocker de 2026-08-02 | Estado |
|---|---|---|
| 1 | `assert_agent_environment.ps1` chama `powershell` literal | resolvido em `6e7bd223`; guard termina exit 0 no Linux |
| 2 | `USERPROFILE` nulo em `Refresh-ProcessPath` | resolvido em `6e7bd223` |
| 3 | consumidores chamando `powershell.exe` literal | resolvido; varredura de 192 scripts nao encontra executor literal |
| 4 | `host_executors.psm1` sem lock/cache Python | resolvido em `a4882e98`; lock unico com hashes, cache do workspace, versao divergente bloqueia |
| 5 | paridade sem CRLF e sem motor canonico unico | resolvido em `62fb7484` |
| 6 | 13 owners no lifecycle versus 47 skills active | **aberto**; fora do escopo desta remediacao |
| 7 | checkout cru com `core.symlinks=false` | resolvido pelo guard funcional; gate de materializacao precede o validador |

## Algoritmo final de hash

Dono unico por linguagem, nenhuma copia:

- `tools/sgdk_wrapper/lib/skill_payload_hash.psm1`;
- `tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`.

Contrato: chave relativa POSIX com case preservado; ordenacao explicita ordinal
pela chave (nunca objetos de caminho, nunca `Sort-Object`); chaves restritas a
ASCII imprimivel sem `\`, porque `StringComparer.Ordinal` compara unidades UTF-16
e o `sorted()` do Python compara code points e as ordens divergem fora do BMP;
CRLF e CR colapsam para LF apenas em extensoes textuais declaradas; binarios
byte-exatos; agregado = chave UTF-8 + `0x00` + sha256 hex + `0x0A`; hash final =
sha256 do agregado.

Nenhum hash regenerado: os 25 arquivos legacy ja eram LF, a normalizacao e
idempotente e o registry ficou byte-identico. O contrato foi provado antes de
tocar em qualquer valor.

## Fixtures multiplataforma

`ci/test_skill_hash_engine_parity.ps1` importa as duas implementacoes reais em
vez de embutir copia simplificada. 34 verificacoes cobrindo: 13 payloads legacy;
LF, CRLF e CR convergindo para o mesmo hash; `.bin` com bytes CRLF distinto do
gemeo LF; arquivo na raiz e em subdiretorio; diferenca de caixa; chave
convergente entre caminho nativo, com `/` e com componente `.`; rejeicao de chave
nao-ASCII nos dois lados; igualdade dos conjuntos de extensoes textuais;
proibicao de `Get-DirectoryContentHash` ressurgir em qualquer `.ps1`/`.psm1`.

Mutantes que fazem o gate falhar, como exigido: `Sort-Object FullName`,
`sorted(Path)` e remocao da normalizacao CRLF.

## Suite integral no Linux

| Gate | Resultado | Exit |
|---|---|---|
| `assert_agent_environment.ps1` | `agent_environment_status=ready` | 0 |
| `test_host_executor_resolution.ps1` | 12/12, 192 scripts | 0 |
| `test_python_dependency_hermeticity.ps1` | 18/18 | 0 |
| `test_skill_hash_engine_parity.ps1` | 34/34, pwsh == python | 0 |
| `validate_skill_framework.py` | 47 active, 13 legacy | 0 |
| `test_canonical_skill_curation.ps1` | 21 gates, 64 PASS | 0 |

O blocker `restoration fixture hash mismatch` nao reaparece e nenhum gate foi
saltado.

## Blockers remanescentes

1. `run_framework_conformance.sh/.bat` deterministas: `not_started`.
2. Golden obrigatorio com registry de referencias: `not_started`.
3. `FORGE_REFERENCE` canonico: `not_started`.
4. Reconciliacao 13 owners no lifecycle versus 47 skills active: `not_started`.
5. Execucao real em Windows nao foi feita. As fixtures cobrem a divergencia de
   ordenacao e de chave por construcao, o que e prova de contrato, nao execucao
   no host.

## Claim ceiling

`framework_conformance_validated` cobre a infraestrutura de conformance:
resolucao de executores, hermeticidade de dependencias Python, hash determinista
multiplataforma e suite canonica completa.

Nao use `ready_for_aaa`. Esta remediacao nao prova ROM, gameplay, audio, budget
VDP nem execucao no BlastEm.
