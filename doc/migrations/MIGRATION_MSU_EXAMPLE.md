# Migração msu-example [SGDK 160] → SGDK 211

**Data:** 2026-03-09  
**Projeto:** msu-example [VER.001] [SGDK 160] [GEN] [ENGINE] [AUDIO]  
**Status:** Em andamento

---

## 1. Alterações Realizadas

### 1.1 Scripts de Build (padronização)

Criados scripts canônicos que delegam ao wrapper:

- **build.bat** – Compila via `tools/sgdk_wrapper/build.bat`
- **clean.bat** – Limpa artefatos via `tools/sgdk_wrapper/clean.bat`
- **run.bat** – Já existia, delega ao wrapper

Caminho relativo: `..\..\..\tools\sgdk_wrapper` (3 níveis: msu-example → pasta projeto → SGDK_Engines → raiz)

### 1.2 Pré-requisitos para Migração Completa

O projeto **não possui** `[SGDK 211]` no nome; o `env.bat` do wrapper usa SGDK 2.11 para todos os builds. Para migração completa:

1. **fix_migration_issues.ps1** – Migrar APIs deprecadas (VDP_* → PAL_*) no código C
2. **validate_resources.ps1** – Validar recursos (bg.res, sound.res, bt.res)
3. **Build** – Executar `build.bat` no diretório `msu-example/msu-example/`

---

## 2. Estrutura do Projeto

```
msu-example [VER.001] [SGDK 160] [GEN] [ENGINE] [AUDIO]/
└── msu-example/
    ├── build.bat    (novo)
    ├── clean.bat   (novo)
    ├── run.bat
    ├── src/
    ├── res/
    │   ├── bg.res
    │   ├── bt.res
    │   └── sound.res
    └── out/
```

---

## 3. Projetos Padronizados na Fila

Scripts canônicos (build.bat, clean.bat, rebuild.bat) adicionados a:

- **msu-example** [SGDK 160] – Áudio
- **mega genius** [SGDK 160] – Puzzle

Ambos usam `..\..\..\tools\sgdk_wrapper` (3 níveis de profundidade).

## 4. Próximos Passos

1. Executar build em cada projeto e verificar erros de compilação
2. Aplicar correções de API (fix_migration_issues.ps1) se necessário
3. Documentar resultado final

## 5. Notas de Build (2026-03-09)

- **msu-example:** O wrapper processa `bg.res`, `bt.res`, `sound.res`. O `bt.res` referencia recursos (kaizer2, krauzer, krauzer0) que podem estar ausentes – o autofix comenta linhas faltantes.
- **Build manual:** Para projetos em caminhos com colchetes, executar `make -f "%GDK%\makefile.gen"` diretamente no diretório do projeto (após `call env.bat`).
- **Documentação:** Ver [doc/README.md](../README.md) para índice completo.
