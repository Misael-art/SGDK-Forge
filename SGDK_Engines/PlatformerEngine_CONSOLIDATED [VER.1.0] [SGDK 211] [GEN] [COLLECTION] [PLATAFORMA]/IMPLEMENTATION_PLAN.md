# 📋 Plano de Implementação: PlatformerEngine Consolidação

## Situação Atual (Fragmentado)

```
PlatformerEngine [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]/
  └─ Vazio (não tem conteúdo)

PlatformerEngine Toolkit [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]/
  ├─ upstream/
  │  ├─ PlatformerEngine/        ← VERSÃO ORIGINAL COM CÓDIGO
  │  ├─ ImageToGameMap/
  │  └─ Level/
  ├─ variants/
  │  └─ PlatformerEngine Core/   ← Minimalista (vazio)
  ├─ companions/
  │  └─ ImageToGameMap [HOST]/   ← Ferramenta host
  ├─ src/, inc/, res/            ← Estrutura toolkit base
  └─ doc/
```

## Novo estado (Consolidado)

```
PlatformerEngine_CONSOLIDATED [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]/
┌─ core/              ← LEVEL 1: Essencial
│  ├─ src/, inc/, res/
│  ├─ examples/
│  ├─ doc/
│  └─ build.bat, run.bat, clean.bat (delegam)
│
├─ standard/          ← LEVEL 2: Intermediário (cópia do upstream com docs)
│  ├─ src/            (upstream/PlatformerEngine/src/)
│  ├─ inc/
│  ├─ res/
│  ├─ examples/
│  ├─ doc/
│  └─ build.bat, run.bat, clean.bat
│
├─ advanced/          ← LEVEL 3: Compl
eto (variação otimizada)
│  ├─ src/, inc/, res/
│  ├─ examples/
│  ├─ doc/
│  └─ build.bat, run.bat, clean.bat
│
├─ utilities/
│  ├─ ImageToGameMap/  (do companions/ + upstream/)
│  └─ ...
│
├─ examples/          ← Exemplos multi-nível
│  ├─ simple/
│  └─ complex/
│
└─ reference/         ← Histórico
   ├─ UPSTREAM_INFO.md
   └─ PlatformerEngine_OriginalVersion/ (backup)
```

## Fases de Implementação

### Fase 1: ✅ Criação de Estrutura (COMPLETO)
- [x] Criar diretórios base (core/, standard/, advanced/, etc.)
- [x] Criar README.md pedagógico
- [x] Criar doc/00_QUICK_START.md

### Fase 2: 🔄 Migração de Código (PRÓXIMO)
- [ ] Copiar upstream/PlatformerEngine/src/ → standard/src/
- [ ] Copiar upstream/PlatformerEngine/inc/ → standard/inc/
- [ ] Copiar upstream/PlatformerEngine/res/ → standard/res/
- [ ] Criar core/ minimalista (subset de standard/)
- [ ] Criar advanced/ com optimizações

### Fase 3: 🔄 Documentação Específica por Nível
- [ ] doc/01_ARCHITECTURE.md (visão geral)
- [ ] standard/doc/README.md (guia STANDARD)
- [ ] standard/doc/CONCEPTS.md
- [ ] core/doc/README.md (guia CORE)
- [ ] advanced/doc/README.md (guia ADVANCED)

### Fase 4: 🔄 Scripts de Build
- [ ] Criar core/build.bat (delega a tools/sgdk_wrapper/)
- [ ] Criar standard/build.bat
- [ ] Criar advanced/build.bat
- [ ] Testar compilação em cada nível

### Fase 5: 🔄 Exemplos por Nível
- [ ] core/examples/01_hello_platformer/
- [ ] standard/examples/01_basic_level/, 02_with_enemies/, etc.
- [ ] advanced/examples/01_camera/, etc.

### Fase 6: 🔄 Consolidação de Utilidades
- [ ] Copiar ImageToGameMap de companions/ + upstream/ → utilities/
- [ ] Documentar uso em utilities/ImageToGameMap/USAGE.md

### Fase 7: 🔄 Backup de Originals
- [ ] Copiar upstream/ → reference/PlatformerEngine_OriginalVersion/
- [ ] Criar reference/UPSTREAM_INFO.md (changelog, origem, mudanças)

### Fase 8: ✅ Validação
- [ ] Compilar standard/ (deve gerar ROM)
- [ ] Testar em emulador (BlastEm)
- [ ] Validar recursos (validate_resources.ps1)
- [ ] Confirmar 60fps

### Fase 9: 📦 Archivamento
- [ ] Mover PlatformerEngine [VER.1.0] (standalone) → archives/
- [ ] Mover PlatformerEngine Toolkit (original) → archives/
- [ ] Mover variants/ → archives/ (opcional, se vazio)

### Fase 10: 📝 Documentação Final
- [ ] Atualizar memory-bank.md
- [ ] Criar MIGRATION_NOTES.md
- [ ] Gerar relatório de conclusão

---

## Recursos Necessários

- **Código-fonte original**: `upstream/PlatformerEngine/src/`
- **Headers**: `upstream/PlatformerEngine/inc/`
- **Recursos**: `upstream/PlatformerEngine/res/`
- **Build scripts**: `upstream/PlatformerEngine/build.bat`, `run.bat`, etc.
- **Ferramentas**: `companions/ImageToGameMap/`, `upstream/ImageToGameMap/`

---

## Benefícios Esperados

✅ Uma única pasta PlatformerEngine consolidada
✅ Progressão pedagógica clara (Core→Standard→Advanced)
✅ Documentação estruturada por nível
✅ Fácil para iniciantes encontrarem tudo
✅ Facilita manutenção e atualizações
✅ Versão original preservada em reference/

---

**Status**: Iniciado em 01/04/2026  
**Próxima etapa**: Fase 2 (Migração de Código)
