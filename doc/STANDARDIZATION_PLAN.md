# Plano de Padronização de Nomenclatura de Diretórios

**Data:** 2026-04-02  
**Status:** Identificado (executar em próxima sessão com VS Code fechado)  
**Prioridade:** ALTA - Garante consistência com padrão Unix/Linux

---

## Problema Identificado

Inconsistência nos nomes de diretórios raiz:

### Atual (Inconsistente):
```
f:\Projects\MegaDrive_DEV\
├── SGDK_Engines/       ❌ Maiúsculo + underscore
├── SGDK_projects/      ❌ Maiúsculo + underscore  
├── SGDK_templates/     ❌ Maiúsculo + underscore
├── assets/             ✅ Minúsculo
├── scripts/            ✅ Minúsculo
├── tools/              ✅ Minúsculo
├── doc/                ✅ Minúsculo
├── sdk/                ✅ Minúsculo
├── archives/           ✅ Minúsculo
└── .tmp/               ✅ Minúsculo (hidden)
```

### Padrão Objetivo (Consistente):
```
f:\Projects\MegaDrive_DEV\
├── sgdk_engines/       ✅ Minúsculo + underscore (ao invés de hyphen)
├── sgdk_projects/      ✅ Minúsculo + underscore
├── sgdk_templates/     ✅ Minúsculo + underscore
├── assets/             ✅ Consistente
├── scripts/            ✅ Consistente
├── tools/              ✅ Consistente
├── doc/                ✅ Consistente
├── sdk/                ✅ Consistente
├── archives/           ✅ Consistente
└── .tmp/               ✅ Consistente
```

---

## Motivação

1. **Convenção Unix/Linux:** Diretórios devem ser minúsculos
2. **Consistência:** Todos os diretórios raiz seguem este padrão menos SGDK_*
3. **Compatibilidade:** Sistemas case-sensitive e paths em scripts
4. **Manutenibilidade:** Facilita automação e scripts futuros

---

## Passos de Implementação

### Pré-Requisitos:
- ✅ Fechar VS Code
- ✅ Fechar exploradores de arquivo com as pastas abertas
- ✅ Desativar antivírus temporariamente se necessário

### Execução (via cmd com privilégios elevados):

```batch
cd /d f:\Projects\MegaDrive_DEV
ren SGDK_Engines sgdk_engines
ren SGDK_projects sgdk_projects
ren SGDK_templates sgdk_templates
```

### Validação Pós-Rename:

```batch
dir /b
```

Verificar que aparecem `sgdk_engines/`, `sgdk_projects/`, `sgdk_templates/` (lowercase).

### Busca-e-Replace em Documentação:

Após renomear diretórios, atualizar referências em:
- [x] `README.md` (raiz)
- [x] `doc/README.md`
- [x] Arquivos .bat em `scripts/`
- [x] AGENTS.md
- [x] CLAUDE.md

---

## Impacto em Projetos Existentes

**Nenhum:** Scripts em cada projeto delegam para `tools/sgdk_wrapper/` via paths relativos (`../../../tools/...`), não referem diretórios raiz nomeados.

**Verificação rápida:**
- PlatformerEngine_CONSOLIDATED: ✅ Usa paths relativos
- Todos os projetos: ✅ Builds não dependem de nomes absolutos de raiz

---

## Próximos Passos

1. ✅ Identificado plano
2. ⏳ Executar renomes (próxima sessão, VS Code fechado)
3. ⏳ Atualizar documentação com novos paths
4. ⏳ Revalidar builds após padronização
5. ⏳ Atualizar memory-bank

---

## Referência Rápida

| Antes | Depois | Tipo |
|-------|--------|------|
| `SGDK_Engines/` | `sgdk_engines/` | Engines, templates pedagógicos |
| `SGDK_projects/` | `sgdk_projects/` | Jogos autorais em desenvolvimento |
| `SGDK_templates/` | `sgdk_templates/` | Templates base (Golden Template) |
