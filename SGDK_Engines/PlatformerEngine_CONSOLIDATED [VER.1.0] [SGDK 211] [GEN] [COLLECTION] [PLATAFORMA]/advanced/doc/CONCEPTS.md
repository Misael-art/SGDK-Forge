# Conceitos Principais - ADVANCED

## 1. Camera System com Prediction

```c
typedef struct {
    fix16_t x, y;           // Posição câmera
    fix16_t target_x, target_y;  // Alvo
    fix16_t predict_x, predict_y; // Predição
    fix16_t velocity_x, velocity_y;
} Camera;

void update_camera_predicted(Camera *cam, Player *p) {
    // Predizer onde jogador estará em 30 frames
    fix16_t future_x = fix16_add(p->x, fix16_mul(p->vx, FIX16(30)));
    fix16_t future_y = fix16_add(p->y, fix16_mul(p->vy, FIX16(30)));
    
    // Suavizar movimento câmera (easing)
    cam->velocity_x = fix16_mul(fix16_sub(future_x, cam->x), FIX16(0.1));
    cam->x = fix16_add(cam->x, cam->velocity_x);
    
    // Aplicar limites do mapa
    if (cam->x < 0) cam->x = 0;
    if (cam->x > MAP_WIDTH - SCREEN_WIDTH) cam->x = MAP_WIDTH - SCREEN_WIDTH;
}
```

---

## 2. Parallax Scrolling

```c
void render_parallax_backgrounds(Camera *cam) {
    // Background (scroll lento)
    s16 bg_scroll = fix16_to_int(fix16_mul(cam->x, FIX16(0.2)));
    MAP_setMapVRAMTile(BG_B, 0, 0, bg_scroll, 0, 32, 28, DMA);
    
    // Midground (scroll normal)
    MAP_setMapVRAMTile(BG_A, 0, 0, fix16_to_int(cam->x), 0, 32, 28, DMA);
    
    // HUD (scroll zero, não muda)
    // Window plane fica fixo
}
```

**Efeito**: Fundo desliza mais lentamente = ilusão de profundidade.

---

## 3. Visual Effects (Particles)

```c
typedef struct {
    fix16_t x, y, vx, vy;
    u16 lifetime;
    u16 frame;
} Particle;

#define MAX_PARTICLES 64
Particle particles[MAX_PARTICLES];
u16 particle_count = 0;

void emit_particles(fix16_t x, fix16_t y, u16 count) {
    for (u16 i = 0; i < count && particle_count < MAX_PARTICLES; i++) {
        Particle *p = &particles[particle_count++];
        p->x = x;
        p->y = y;
        p->vx = FIX16(random(-2, 2));
        p->vy = FIX16(random(-4, 0));  // Cima + aleatório
        p->lifetime = 30;  // 30 frames
    }
}

void update_particles() {
    for (u16 i = 0; i < particle_count; i++) {
        Particle *p = &particles[i];
        p->x = fix16_add(p->x, p->vx);
        p->y = fix16_add(p->y, p->vy);
        p->lifetime--;
        
        if (p->lifetime == 0) {
            // Remove partícula (swap com última)
            particles[i] = particles[--particle_count];
            i--;
        }
    }
}
```

---

## 4. Boss AI com Fases

```c
typedef enum {
    BOSS_PHASE_1,  // Easy
    BOSS_PHASE_2,  // Medium
    BOSS_PHASE_3   // Hard
} BossPhase;

void update_boss(Boss *b, Player *p) {
    switch (b->phase) {
        case BOSS_PHASE_1:
            // Patrulha simples
            if (b->attack_timer-- == 0) {
                // Ataque telegrafado
                emit_boss_projectile(b->x, b->y, p->x);
                b->attack_timer = 120;
            }
            break;
            
        case BOSS_PHASE_2:
            // Perseguição + múltiplos ataques
            // ...
            break;
    }
    
    // Mudar fase quando life reduz
    if (b->health <= b->max_health / 2 && b->phase == BOSS_PHASE_1) {
        b->phase = BOSS_PHASE_2;
        emit_particles(b->x, b->y, 32);  // VFX transição
    }
}
```

---

## 5. XGM2 Audio Integration

```c
#include "xgm2driver.h"

void play_music() {
    XGM2_play(MUSIC_LEVEL_1);  // Começa música
}

void play_sfx(u16 sfx_id) {
    XGM2_playSFX(sfx_id);  // Efeito sonoro
}

void audio_callback() {
    XGM2_update();  // Chamar no VBlank ISR
}
```

**Canais XGM2**: 4 FM (PSG) + 3 SSG. 7 vozes simultâneas max.

---

## 6. VRAM Budget Optimization

```c
// config.h
#define MAX_SPRITES_PER_FRAME  32    // Não renderize >32 sprites/frame
#define TILE_CACHE_SIZE        4096  // Cache 4096 tiles
#define SPRITE_CACHE_SIZE      256   // Cache 256 sprites unique

// No render loop
// Somente renderize sprites dentro da câmera (culling)
if (sprite->x > cam->x - 16 && sprite->x < cam->x + SCREEN_WIDTH + 16) {
    SPR_addSprite(&sprite->def, sprite->x, sprite->y, ...);
}
```

---

## 7. Save/Load System (SRAM)

```c
typedef struct {
    u32 level;
    u32 score;
    u32 lives;
    u32 checksum;  // Simples proteção
} SaveGame;

void save_game(SaveGame *data, u16 slot) {
    u16 addr = slot * sizeof(SaveGame);
    SRAM_writeLong(addr, data->level);
    SRAM_writeLong(addr+4, data->score);
    SRAM_writeLong(addr+8, data->lives);
}

void load_game(SaveGame *data, u16 slot) {
    u16 addr = slot * sizeof(SaveGame);
    data->level = SRAM_readLong(addr);
    data->score = SRAM_readLong(addr+4);
    data->lives = SRAM_readLong(addr+8);
}
```

---

**Você é expert! 🏆 Customize para seu jogo e publique!**
