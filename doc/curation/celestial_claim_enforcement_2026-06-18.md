# Curadoria canonica — claim/evidencia/ROM

Data: 2026-06-18
Caso: `Celestial Chase Revive [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_RACING]`
ROM auditada: `167d4f6937099b542e84f0d64dc6ddf258ba32091c9e874988e01c45a760eafd`

## Resultado

Foi adicionado um gate executavel que impede promocao por inventario, build
isolado, screenshot, score automatico, relatorio manual ou evidencia de outra
ROM. O gate e obrigatorio no `scene_closeout_gate.ps1`.

## Causa raiz por falha

| Falha | Causa sistemica | Enforcement |
|---|---|---|
| Modulo existente tratado como funcional | Estado binario presente/ausente | Estados `module_present` → `integrated` → `reachable` → `runtime_proven` |
| Screenshot de ROM antiga | Evidencia sem identidade selada | SHA-256 deve coincidir com `out/rom.bin` |
| Boot extrapolado | Ausencia de escopo observado | `claim_scope` separa gameplay/audio/performance |
| Warning impossivel aceito | Build usava apenas exit code | `critical_compiler_warning` |
| Corrupcao visual promovida | Gate tecnico sem teto visual | `visual_corruption_observed` |
| Pillow vendido como premium | Validade tecnica confundida com arte | Quarentena procedural |
| Score automatico vendido como arte | Um unico eixo de aprovacao | `technical_score_not_artistic_approval` |
| Closeout manual aceito | Declaracao confundida com execucao | Exige gate report executado |
| MTR vendido como MDRT | Proveniencia ausente | `mdrt_performance_evidence_missing` |
| Enum/asset vendido como feature | Reachability nao observada | `runtime_feature_not_proven` |
| Paralelismo sem integrador | Sem owner final | `integration_owner_missing` |
| Relatorios divergentes | Escolha do mais otimista | Menor status consistente |
| Captura atribuia tres eixos | Defaults permissivos | Claims separados por escopo |
| Sector 02 apos crash | Avanco sem gate corrente | `phase_advance_blocked` |

## Mapa de mudancas

| Tipo | Artefato |
|---|---|
| Script | `tools/sgdk_wrapper/audit_promotion_claims.ps1` |
| Schemas | `promotion_claim_manifest.schema.json`, `promotion_claim_audit_report.schema.json` |
| CI | `tools/sgdk_wrapper/ci/test_promotion_claim_enforcement.ps1` |
| Closeout | `tools/sgdk_wrapper/scene_closeout_gate.ps1` |
| Framework | `ARCHITECTURE.md`, `SGDK_GLOBAL.md`, `production-loop.md` |
| Skills | `aaa-pipeline-guardian`, `sgdk-build-wrapper-operator` |

## RED → GREEN

RED: a suite falhou porque o auditor canonico nao existia.

| Pressao | Blocker esperado | Resultado |
|---|---|---|
| Screenshot de hash antigo | `claim_rom_hash_mismatch` | bloqueado |
| Title screenshot → gameplay | `claim_scope_not_observed` | bloqueado |
| Warning impossivel | `critical_compiler_warning` | bloqueado |
| Procedural com score alto | dois blockers de arte | bloqueado |
| Modulos inalcançaveis | `runtime_feature_not_proven` | bloqueado |
| Closeout manual | `executed_closeout_gate_missing` | bloqueado |
| MTR → performance | `mdrt_performance_evidence_missing` | bloqueado |
| Crash antes do resultado | dois blockers de rota | bloqueado |
| Relatorios divergentes | conflito + ceiling | bloqueado |
| Proxima fase apos crash | `phase_advance_blocked` | bloqueado |

GREEN: `10/10`, `0` falhas.

## Compatibilidade

- Projeto antigo sem promocao formal recebe `status=not_applicable`.
- Build exploratorio continua permitido.
- Claims fortes novos exigem manifesto ou campos equivalentes explicitos.
- Artefatos antigos continuam legiveis, mas nao concedem claims por omissao.

## Riscos remanescentes

- Warnings estruturados ainda dependem do manifesto; classificacao direta de
  todos os logs de compilador e expansao futura.
- Deteccao de corrupcao visual continua dependendo de review dedicado.
- Reachability profunda em C/68000 exige probes runtime para prova positiva.

## Propostas de aprendizado

Todas permanecem `not_applied`:

- ampliar taxonomia de warnings por toolchain;
- extrair matriz de reachability de probes MDRT;
- adicionar detector visual assistido como evidencia auxiliar;
- migrar projetos antigos apenas com aprovacao humana por projeto.

## Claim ceiling desta curadoria

`implementado_validado_sem_rom_nova`.

Nenhuma correcao de gameplay foi feita no Celestial Chase. Nenhuma ROM foi
promovida.
