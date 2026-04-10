# Informações sobre Versão Original (Upstream)

## O Que Contém Aqui

Este diretório `reference/` preserva a **versão original** do PlatformerEngine, antes de consolidação em níveis pedagógicos.

---

## Mudanças Aplicadas em Consolidação

### De
```
PlatformerEngine Toolkit [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]
└── upstream/PlatformerEngine/     ← Versão original
```

### Para
```
PlatformerEngine_CONSOLIDATED [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]
├── standard/                       ← Cópia da versão original
├── core/                          ← Subset minimalista
├── advanced/                      ← Versão otimizada
└── reference/                     ← Backup histórico
    └── PlatformerEngine_OriginalVersion/  ← Versão original intacta
```

---

## Por Que Consolidar?

| Problema | Solução |
|----------|---------|
| 3 cópias de PlatformerEngine espalhadas | Uma única pasta consolidada |
| Difícil encontrar código correto | Estrutura pedagógica clara (core→standard→advanced) |
| Ferramentas (ImageToGameMap) misturadas | `/utilities/` separado e organizado |
| Versão original não documentada | `reference/` preserva histórico |

---

## Histórico

| Data | Versão | Descrição |
|------|--------|-----------|
| 2024 | 1.0.0 | Versão original desenvolvida |
| 2026 (antes) | Fragmentado | Distribuído em upstream/, variants/, companions/ |
| 2026-04-01 | Consolidado | Reorganização pedagógica em níveis |

---

## Como Usar Esta Referência

### Se encontrar bug em STANDARD
1. Compare com `reference/PlatformerEngine_OriginalVersion/src/`
2. Veja se bug também existe lá
3. Caso sim → bug original; case não → introduzido em consolidação

### Se precisar entender código original
1. Leia comentários em `reference/`
2. Compare com versão STANDARD (devem ser idênticas)
3. Veja evolução até ADVANCED

### Se precisar reverter
```bash
cp -r reference/PlatformerEngine_OriginalVersion/* standard/
cd standard
rebuild.bat
```

---

## Versão Original Attributions

- **Autor**: [Verificar em PlatformerEngine_OriginalVersion/README.md]
- **Base**: SGDK 2.11 templates
- **Plataforma**: Sega Mega Drive / Genesis
- **Data Original**: ~2024

---

**Status**: Intacto como referência histórica e debug.

**Próxima ação**: Use `/core`, `/standard` ou `/advanced` para desenvolvimento!
