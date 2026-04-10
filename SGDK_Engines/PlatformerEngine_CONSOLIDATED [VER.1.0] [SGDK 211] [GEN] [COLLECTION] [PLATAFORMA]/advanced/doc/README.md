# 📍 ADVANCED Level - Completo (Nível 3)

## O Que é ADVANCED?

ADVANCED é a **versão polida e otimizada** de um plataformador AAA-like. Contém:
- Sistema de câmera com prediction/easing
- Parallax scrolling (múltiplos planos)
- Efeitos visuais (transições, VFX de partículas)
- Boss fights com padrões complexos
- Áudio XGM2 integrado (música + SFX)
- Otimizações de performance (VRAM budgeting, DMA)
- Tela de menu, pausa, game over
- Salvar/carregar progresso

**Objetivo**: Jogo comercialmente viável, pronto para entrega.

---

## Conceitos-Chave Ensinados

1. **Advanced Camera** — Prediction, easing, limited scrolling
2. **Parallax Scrolling** — Múltiplos backgrounds, scroll lag
3. **VFX System** — Partículas, screen shake, fade transitions
4. **Boss AI** — Padrões, fases, ataques coordenados
5. **XGM2 Audio** — Música dinâmica, SFX em tempo real
6. **VRAM Optimization** — Budget de VRAM, streaming de sprites
7. **DMA Scheduling** — Timing de DMA no VBlank
8. **Save System** — Salvar estado do jogo em SRAM
9. **UI System** — Menus, HUD, estados de tela

---

## Estrutura

```
advanced/
├── src/
│   ├── main.c         ← Game loop + menu/pause/gameover
│   ├── player.c       ← Versão otimizada
│   ├── enemy.c        ← Inimigos avançados
│   ├── boss.c         ← Boss fights com IA
│   ├── camera.c       ← Sistema de câmera com prediction
│   ├── physics.c      ← Physics otimizado
│   ├── collision.c    ← Detecção pixel-perfect
│   ├── map.c          ← Tilemap streaming
│   ├── vfx.c          ← Partículas, efeitos
│   ├── audio.c        ← XGM2 driver integration
│   ├── save.c         ← Save/load system
│   └── ui.c           ← Menu, HUD, transições
├── inc/
│   ├── types.h
│   ├── .../
│   └── config.h       ← Budget constants
├── res/
│   ├── sprites/       ← Subdividido por tipo
│   ├── tilesets/
│   ├── backgrounds/
│   ├── audio/         ← XGM2 music + SFX
│   └── resources.rc
├── doc/
│   ├── README.md (você está aqui)
│   ├── OPTIMIZATION_TIPS.md
│   └── ADVANCED_CONCEPTS.md
└── examples/
    ├── 01_camera_system/
    ├── 02_parallax_scrolling/
    ├── 03_boss_fight/
    └── 04_full_game_optimized/
```

---

## Como Usar ADVANCED

### 1. Compile (Pode levar mais tempo)
```bash
cd advanced
build.bat
```

### 2. Rode no Emulador
```bash
run.bat
```

### 3. Estude Sistemas Avançados
- `camera.c`: Sistema de câmera com easing e prediction
- `boss.c`: IA de boss com padrões
- `vfx.c`: Partículas e efeitos visuais
- `audio.c`: Integração XGM2
- `save.c`: Salvamento em SRAM
- `ui.c`: Menus e HUD

### 4. Execute Exemplos Avançados
```bash
cd examples/03_boss_fight
build.bat && run.bat
```

### 5. Otimize para Seu Hardware
- Ajuste `config.h` para orçamento VRAM
- Ative/desative VFX conforme necessário
- Perfil com profiler emulador

---

## Otimizações Principais

### VRAM Budget
```c
// config.h
#define MAX_SPRITES         64      // Limite de sprites simultâneos
#define VRAM_TILE_SIZE      (64*1024) // 64KB para tiles
#define VRAM_SPRITE_SIZE    (32*1024) // 32KB para sprites
```

### DMA Scheduling
```c
// No VBlank callback:
// 1. Programar DMA de tiles
// 2. Programar DMA de sprites
// 3. Atualizar posições
// 4. Renderizar
```

### Parallax Optimization
```c
// Scroll only background planes that changed
if (camera_moved) {
  BG_setMapVRAMTile(BG_A, ..., DMA);  // Plano A
  BG_setMapVRAMTile(BG_B, ..., DMA);  // Plano B
  // Window plane fica estático (HUD)
}
```

---

## Próximos Passos Após ADVANCED

🎉 **Parabéns!**

Você agora domina:
- ✅ Plataformers estruturados
- ✅ Otimização hardware MD
- ✅ Áudio dinâmico
- ✅ Efeitos visuais pro
- ✅ IA complexa

### Caminho para Publicação
1. Customize para seu jogo
2. Teste em emulador (BlastEm mínimo 60fps)
3. Valde com `tools/sgdk_wrapper/validate_resources.ps1`
4. Otimize VRAM/DMA conforme necessário
5. Puble no archive (ROM)

---

## Troubleshooting Avançado

**Erro: "Camera lag não suave"**
→ Ajuste predição em camera.c; veja OPTIMIZATION_TIPS.md

**Erro: "Áudio desincronizado"**
→ Verifique callback XGM2 em audio.c

**Performance: <60fps**
→ Perfil com BizHawk; reduza sprites/VFX

**Erro: "Save não funciona"**
→ Verifique backup RAM (SRAM) em save.c

Para mais, veja `ADVANCED_CONCEPTS.md`.

---

## Tips & Tricks Pro

- **Camera Prediction**: Use predição de movimento para smooth seguimento
- **Parallax**: Distâncie entre planos = proporção de scroll
- **DMA**: Programa DMA **dentro** de VBlank para evitar artefatos
- **Sprite Allocation**: Use `SPR_FLAG_AUTO_VRAM_ALLOC` com cuidado
- **Audio Mixing**: XGM2 suporta 4 canais FM + 3 SSG — planeje!
- **Paleta**: Fade entre paletas para efeitos suaves

---

**Tempo estimado**: 20+ horas master all systems.

**Ultimate Goal**: Seu próprio jogo AAA-like no Mega Drive. Bora! 🚀
