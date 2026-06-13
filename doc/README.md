# Documentação MegaDrive_DEV

Documentação centralizada do projeto MegaDrive_DEV – engines e jogos para Mega Drive/Genesis com SGDK.

---

## Índice

### Diretrizes e Arquitetura

| Documento | Descrição |
|-----------|-----------|
| [AGENTS.md](AGENTS.md) | Diretrizes para agentes de IA – propósitos, métodos, regras e checklist de migração |
| [06_AI_MEMORY_BANK.md](06_AI_MEMORY_BANK.md) | Memory Bank global – estado do repositório, sessões recentes, decisões |
| [QA_CHECKLIST_ROTEIRO.md](QA_CHECKLIST_ROTEIRO.md) | Roteiro QA passo-a-passo e checklist de evidências para promoção RC |
| [PADRAO_NOMENCLATURA.md](PADRAO_NOMENCLATURA.md) | Padrão de nomenclatura de projetos e engines |
| [CANONICAL_WORKTREE.md](CANONICAL_WORKTREE.md) | Estrutura canonica de projeto, manifesto `.mddev` e política de arquivamento |
| [HIERARQUIA_TEMPLATES.md](HIERARQUIA_TEMPLATES.md) | Papel de cada template (project-template, base-elite, SimpleGameStates_Elite, nested) |
| [AVALIACAO_PROJETOS_SGDK_PROJECTS.md](AVALIACAO_PROJETOS_SGDK_PROJECTS.md) | Avaliação de teste e ELITE_TEST_PROJECT (2026-03-19) |
| [VALIDACAO_BAT_WRAPPER.md](VALIDACAO_BAT_WRAPPER.md) | Validação de coesão dos .bat com o wrapper (2026-03-19) |
| [FAXINA_EXECUTADA_20260314.md](FAXINA_EXECUTADA_20260314.md) | Registro da limpeza, isolamento do Git e arquivamento do legado |
| [INTEGRACAO_IMPORTS_20260314.md](INTEGRACAO_IMPORTS_20260314.md) | Registro da incorporacao dos imports e canonicalizacao do lote SGDK 211 |
| [INTEGRACAO_IMPORTS_20260314_LOTE2.md](INTEGRACAO_IMPORTS_20260314_LOTE2.md) | Status final do segundo lote de imports, com projetos validados, pendentes e colecoes |

### Migrações SGDK 160 → 211

| Documento | Projeto | Status |
|-----------|---------|--------|
| [BLAZE_ENGINE_FIX_REPORT.md](migrations/BLAZE_ENGINE_FIX_REPORT.md) | BLAZE_ENGINE [SGDK 211] | Concluido |
| [MIGRATION_SHADOW_DANCER_HAMOOPIG.md](migrations/MIGRATION_SHADOW_DANCER_HAMOOPIG.md) | Shadow Dancer Hamoopig [SGDK 211] [PLATAFORMA] | Concluido |
| [MIGRATION_MSU_EXAMPLE.md](migrations/MIGRATION_MSU_EXAMPLE.md) | msu-example, mega genius | Scripts padronizados |
| [MIGRATION_BATCH_211.md](migrations/MIGRATION_BATCH_211.md) | 9 projetos (HAMOOPIG, KOF94, MUSIC, etc.) | Migrados em lote |

### Wrapper e Build

| Documento | Localização |
|-----------|-------------|
| Wrapper README | [tools/sgdk_wrapper/README.md](../tools/sgdk_wrapper/README.md) |
| Resiliência | [tools/sgdk_wrapper/RESILIENCE.md](../tools/sgdk_wrapper/RESILIENCE.md) |
| Worktree Canônico | [CANONICAL_WORKTREE.md](CANONICAL_WORKTREE.md) |
| Catalogo de Engines | [SGDK_Engines/README.md](../SGDK_Engines/README.md) |

---

## Estrutura de Pastas

```
doc/
├── README.md           # Este indice
├── AGENTS.md           # Diretrizes para agentes de IA
├── 06_AI_MEMORY_BANK.md    # Memory Bank global (workspace)
├── QA_CHECKLIST_ROTEIRO.md # Roteiro QA e checklist evidências RC
├── PADRAO_NOMENCLATURA.md
└── migrations/         # Relatorios de migracao por projeto
    ├── BLAZE_ENGINE_FIX_REPORT.md
    ├── MIGRATION_SHADOW_DANCER_HAMOOPIG.md
    ├── MIGRATION_MSU_EXAMPLE.md
    └── MIGRATION_BATCH_211.md
```
