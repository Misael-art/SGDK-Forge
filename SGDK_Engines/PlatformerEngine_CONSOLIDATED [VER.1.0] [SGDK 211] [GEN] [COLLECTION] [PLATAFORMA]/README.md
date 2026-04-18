# PlatformerEngine [VER.1.0] [SGDK 211] [GEN] [COLLECTION] [PLATAFORMA]

## 🎮 Bem-vindo à Coleção Educacional de PlatformerEngine

Este é um **projeto de aprendizado estruturado em níveis de complexidade** para dominar desenvolvimento de plataformers para Sega Mega Drive usando SGDK 2.11.

### 📋 Estrutura Pedagógica

O projeto é dividido em **3 níveis de progressão**:

#### **Level 1: CORE** 📍 (Essencial)
- **Foco**: Conceitos fundamentais mínimos
- **Você aprende**: 
  - Sprite rendering básico
  - Detecção de colisão essencial
  - Entrada de controle
  - Game loop fundamental
- **Complexidade**: Mínima
- **Tempo estimado**: 2-4 horas para compreender
- **👉 Comece aqui** se é iniciante

#### **Level 2: STANDARD** 📍 (Intermediário)
- **Foco**: Prototipagem de jogo completo
- **Você aprende**:
  - Física de plataforma (gravity, jump)
  - Inimigos com IA básica
  - Sistema de vidas/pontuação
  - Mapas de nível completos
  - Animações de sprite
- **Complexidade**: Média
- **Tempo estimado**: 8-16 horas
- **👉 Progresse aqui** após dominar CORE

#### **Level 3: ADVANCED** 📍 (Completo)
- **Foco**: Jogo polido e otimizado
- **Você aprende**:
  - Sistema de câmera avançado
  - Efeitos visuais (parallax, screen transitions)
  - Boss fights com padrões complexos
  - Áudio XGM2 integrado
  - Otimizações de performance (DMA, VRAM budgeting)
- **Complexidade**: Alta
- **Tempo estimado**: 20+ horas
- **👉 Maître** após STANDARD

---

### 📁 Estrutura de Pastas

```
.
├── README.md                          ← Você está aqui
├── doc/
│   ├── 00_QUICK_START.md             (comece por aqui)
│   ├── 01_ARCHITECTURE.md            (visão geral técnica)
│   ├── 02_LEVEL_DESCRIPTIONS.md      (explicação core→adv)
│   ├── 03_EXAMPLES_GUIDE.md          (como usar exemplos)
│   ├── HISTORY.md                    (evolução do projeto)
│   └── TROUBLESHOOTING.md            (FAQs e erros comuns)
│
├── core/                              ← LEVEL 1
│   ├── build.bat, run.bat, clean.bat (scripts delegam a tools/sgdk_wrapper/)
│   ├── doc/
│   │   ├── README.md                 (guia CORE específico)
│   │   ├── CONCEPTS.md               (conceitos-chave)
│   │   └── TODO_NEXT.md              (próximos passos → STANDARD)
│   ├── src/, inc/, res/              (código didático comentado)
│   └── examples/
│       └── 01_hello_platformer/      (exemplo mais simples)
│
├── standard/                          ← LEVEL 2
│   ├── build.bat, run.bat, clean.bat
│   ├── doc/
│   │   ├── README.md                 (guia STANDARD específico)
│   │   ├── CONCEPTS.md
│   │   └── TODO_NEXT.md              (próximos passos → ADVANCED)
│   ├── src/, inc/, res/              (código completo)
│   └── examples/
│       ├── 01_basic_level/
│       ├── 02_with_enemies/
│       ├── 03_full_game/
│       └── 04_animations/
│
├── advanced/                          ← LEVEL 3
│   ├── build.bat, run.bat, clean.bat
│   ├── doc/
│   │   ├── README.md                 (guia ADVANCED específico)
│   │   ├── CONCEPTS.md
│   │   └── OPTIMIZATION_TIPS.md
│   ├── src/, inc/, res/              (código otimizado)
│   └── examples/
│       ├── 01_camera_system/
│       ├── 02_parallax_scrolling/
│       ├── 03_boss_fight/
│       └── 04_full_game_optimized/
│
├── utilities/                         ← Ferramentas Host
│   ├── ImageToGameMap/               (conversor de imagens → mapa de nível)
│   │   └── USAGE.md
│   ├── LevelEditor/                  (editor de níveis - futuro)
│   └── AssetValidator/               (validador de assets)
│
├── examples/                          ← Showcases Multi-nivelo
│   ├── simple_platformer/            (combina conceitos core)
│   ├── complex_platformer/           (combina conceitos standard)
│   └── full_game_showcase/           (e combina advanced)
│
└── reference/                         ← Histórico e Origem
    ├── UPSTREAM_INFO.md              (origem, versão original, mudanças)
    └── PlatformerEngine_OriginalVersion/ (backup intacto da versão original)
```

---

### 🚀 Como Começar

#### 1️⃣ **Primeiro Timer? Comece com QUICK START**
```bash
cd doc
cat 00_QUICK_START.md  # ou abra no editor
```

#### 2️⃣ **Escolha seu Nível**
- **Não sabe nada?** → `core/`
- **Entende conceitos básicos?** → `standard/`
- **Quer otimização?** → `advanced/`

#### 3️⃣ **Compile e Teste o Seu Nível**
```bash
cd standard              # ou core, ou advanced
build.bat               # Compila (delega a tools/sgdk_wrapper/)
run.bat                 # Testa no emulador
```

#### 4️⃣ **Leia o README do Seu Nível**
```bash
cd standard/doc
cat README.md
```

#### 5️⃣ **Execute Exemplos**
```bash
cd standard/examples/01_basic_level
build.bat && run.bat
```

#### 6️⃣ **Leia o Código Comentado**
- Código didático: `src/` com comentários explicativos
- Compare entre níveis para entender progresso

---

### 📚 Documentação Principal

| Arquivo | Propósito |
|---------|-----------|
| `doc/00_QUICK_START.md` | Guia 5 minutos para startup |
| `doc/01_ARCHITECTURE.md` | Visão geral técnica do motor |
| `doc/02_LEVEL_DESCRIPTIONS.md` | Por que 3 níveis? Diferenças entre eles |
| `doc/03_EXAMPLES_GUIDE.md` | Como rodar e aprender com exemplos |
| `HISTORY.md` | Evolução do projeto, changelog |
| `TROUBLESHOOTING.md` | Erros comuns e soluções |

---

### 🎯 Roadmap de Aprendizado (Recomendado)

```
┌─────────────────────────────────┐
│  1. Read: 00_QUICK_START.md     │
│  2. Read: 01_ARCHITECTURE.md    │
└──────────────┬──────────────────┘
               │
       ┌───────┴───────┐
       │               │
   Choose Level:   Choose Level:
    BEGINNER       ADVANCED
       │               │
       v               v
   core/          standard/ → advanced/
   └─ Examples    └─ Examples
   └─ Doc         └─ Doc
   └─ Code        └─ Code
   └─ Build       └─ Build
   └─ Next: STANDARD   └─ Next: ADVANCED
```

---

### 🔧 Requisitos

- **SGDK 2.11** instalado (`sdk/sgdk-2.11/`)
- **Java** (para ResComp, compilador de recursos)
- **Emulador**: BlastEm, BizHawk ou Gens (inclusos em `tools/emuladores/`)
- **Conhecimento**: C básico, conceitos de game loop

---

### ⚙️ Scripts de Build

Cada nível tem scripts que **delegam ao sistema centralizado**:

```bat
build.bat      # Compila (chama tools/sgdk_wrapper/build.bat)
run.bat        # Testa no emulador
clean.bat      # Remove build artifacts
rebuild.bat    # clean + build
```

---

### ✅ Validação e QA

Após cada build, o projeto passa por:
- ✅ Compilação sem erros
- ✅ Validação de recursos (sprites, paletas, tiles)
- ✅ Boot no emulador (BlastEm obrigatório)
- ✅ Performance 60fps estável
- ✅ Áudio funcional

---

### 📞 Precisa de Ajuda?

1. **Erro durante build?** → `TROUBLESHOOTING.md`
2. **Não entende um conceito?** → Leia `doc/` do seu nível
3. **Quer copiar um exemplo?** → Veja `examples/`
4. **Quer ver versão original?** → Veja `reference/UPSTREAM_INFO.md`

---

### 🎓 Status de Aprendizado

Use este checklist para acompanhar seu progresso:

- [ ] Lembrei de `00_QUICK_START.md`
- [ ] Entendi `01_ARCHITECTURE.md`
- [ ] Compilei e rodei `core/examples/01_hello_platformer/`
- [ ] Compreendi conceitos do `core/doc/CONCEPTS.md`
- [ ] Compilei `standard/`
- [ ] Executei todos os exemplos em `standard/examples/`
- [ ] Entendi código em `standard/src/`
- [ ] Compilei `advanced/`
- [ ] Customizei um exemplo do `advanced/`

Parabéns! 🎉 Agora você domina development de plataformers no Mega Drive.

---

**Última atualização**: Abril 2026  
**Versão do SGDK**: 2.11  
**Status**: [CONSOLIDADO - Em Implementação]
