# Sgdk Forge

Root canônico limpo para o ecossistema SGDK + agentes AAA. Este workspace contém apenas o núcleo necessário para o framework funcionar — sem projetos, sem assets, sem outputs de build.

## O que é isto?

Uma reconstrução cirúrgica do workspace SGDK a partir de `F:\Projects\MegaDrive_DEV`, mantendo:

- **Wrapper de build** (`tools/sgdk_wrapper/`) com o framework `.agent/` completo
- **SDK SGDK 2.11** real (`sdk/sgdk-2.11/`)
- **Emuladores** de Mega Drive (`tools/emuladores/`)
- **Ferramentas internas** essenciais (ai_imagegen, image-tools, photo2sgdk, vscode-template, maintenance, gen-scripts)
- **Documentação operacional** mínima
- **Ponte de skills** `.agents/skills` → `tools/sgdk_wrapper/.agent/skills`

O workspace original `F:\Projects\MegaDrive_DEV` permanece intocado para arquivamento. Este novo root é onde novos projetos nascem.

## Estrutura

```
Sgdk Forge/
├── AGENTS.md                   ← regras canônicas para agentes de IA
├── CLAUDE.md                   ← contexto para Claude
├── README.md                   ← este arquivo
├── .gitignore
├── .agents/                    ← ponte para skills (junction)
├── .cursor/rules/              ← regras Cursor (megadrive-sgdk-aaa-pipeline.mdc)
├── doc/                        ← documentação operacional
│   ├── 06_AI_MEMORY_BANK.md
│   ├── AGENTS.md
│   ├── CANONICAL_BOOTSTRAP_STATUS.md
│   ├── PADRAO_NOMENCLATURA.md
│   ├── TEMPLATE_REGISTRY.md
│   ├── WORKSPACE_STRUCTURE.md
│   ├── template_registry.json
│   ├── agent_learning/
│   ├── migrations/
│   ├── 05_technical/
│   ├── 03_art/
│   └── migration/
│       ├── canonical_copy_manifest.json
│       ├── canonical_copy_report.md
│       ├── dry_run.log
│       └── real_copy.log
├── sdk/
│   └── sgdk-2.11/              ← toolchain SGDK (~136 MB)
├── SGDK_projects/              ← vazio: destino de novos projetos
├── SGDK_Engines/               ← vazio: destino de engines portadas
└── tools/
    ├── sgdk_wrapper/           ← wrapper de build + framework .agent
    ├── ai_imagegen/            ← geração de assets via IA (workflows, sem runtime)
    ├── emuladores/             ← BlastEm, BizHawk, Exodus, GensKMod
    ├── image-tools/            ← ferramentas de análise de imagem
    ├── photo2sgdk/             ← conversor foto → SGDK
    ├── vscode-template/        ← template de configuração VSCode
    ├── maintenance/            ← placeholder para scripts de manutenção
    └── gen-scripts/            ← scripts auxiliares de geração
```

## Como criar novo projeto

```powershell
# Opção 1: via wrapper
.\tools\sgdk_wrapper\new_project.bat

# Opção 2: cópia manual do template
Copy-Item -Recurse .\tools\sgdk_wrapper\modelo .\SGDK_projects\"MEU_PROJETO [VER.001] [SGDK 211] [GEN] [GAME] [ACAO]"
```

Convenção de nomenclatura: `NOME [VER.XXX] [SGDK 211] [GENERO] [TIPO]`. Ver `doc/PADRAO_NOMENCLATURA.md`.

## Como validar ambiente

```powershell
# Preflight do host (Java, make, ImageMagick)
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\sgdk_wrapper\preflight_host.ps1

# Validação do framework .agent
python .\tools\sgdk_wrapper\.agent\scripts\validate_skill_framework.py
python .\tools\sgdk_wrapper\.agent\scripts\self_check_agentic_aaa_contracts.py
python .\tools\sgdk_wrapper\.agent\scripts\validate_template_registry.py

# Contratos de game design
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\sgdk_wrapper\ci\test_game_design_contract_gates.ps1
```

## Pipeline AAA

Ordem canônica: ver `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md` e `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`.

Gate de entrega exige os 7 eixos:

1. ✅ build sucesso
2. ✅ validation_report limpo
3. ✅ boot em BlastEm (gate obrigatório; BizHawk só complementa)
4. ✅ gameplay básico funcional
5. ✅ performance 60fps estáveis
6. ✅ áudio ok
7. ✅ memória operacional canônica atualizada

**"Se não foi visto rodando no emulador, não existe."**

## Notas de migração

Este root foi populado a partir de `F:\Projects\MegaDrive_DEV` em 2026-06-02. Detalhes completos em `doc/migration/canonical_copy_report.md`.

- **Não** há projetos aqui. Eles nascem em `SGDK_projects/`.
- **Não** há assets, outputs de build ou arquivos experimentais.
- **Não** há `sgdk_templates/` antigo nem `_archive`.
- A pasta `tools/ai_imagegen/runtime/` (1.5 GB) e `tools/ai_imagegen/models/` (4 GB) foram **propositalmente excluídas** — reconfigure sob demanda.
