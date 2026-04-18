# Conceitos Principais - STANDARD

## 1. Physics Engine

```c
// Gravidade constante (aceleração para baixo)
#define GRAVITY FIX16(0.5)  // 0.5 pixels/frame²

void apply_physics(Player *p) {
    p->vy = fix16_add(p->vy, GRAVITY);  // Aumenta velocidade queda
    p->y = fix16_add(p->y, p->vy);       // Atualiza posição
}

void jump(Player *p) {
    if (p->on_ground) {
        p->vy = FIX16(-10);  // Impulso negativo = pulo
        p->on_ground = FALSE;
    }
}
```

---

## 2. Collision Detection (avançada)

```c
// Broad-phase (AABB)
bool aabb_collision(Entity *a, Entity *b) {...}

// Narrow-phase (pixel-perfect)
bool pixel_collision(Entity *a, Entity *b) {...}

// Use broad-phase DEPOIS narrow-phase para performance
```

---

## 3. State Machine

```c
typedef enum {
    PLAYER_IDLE,
    PLAYER_RUNNING,
    PLAYER_JUMPING,
    PLAYER_FALLING,
    PLAYER_HURTING
} PlayerState;

void update_player_state(Player *p) {
    switch (p->state) {
        case PLAYER_JUMPING:
            if (p->vy > 0) p->state = PLAYER_FALLING;
            break;
        ...
    }
}
```

---

## 4. Animation System

```c
typedef struct {
    u16 frame_list[8];      // IDs de frames do sprite
    u16 frame_count;        // Quantos frames
    u16 frame_index;        // Frame atual
    u16 frame_timer;        // Timer para próximo frame
} Animation;

void animate_sprite(Animation *anim) {
    anim->frame_timer--;
    if (anim->frame_timer == 0) {
        anim->frame_index = (anim->frame_index + 1) % anim->frame_count;
        anim->frame_timer = 8;  // 8 frames de espera
    }
}
```

---

## 5. Simple Enemy AI

```c
typedef enum {
    ENEMY_IDLE,
    ENEMY_PATROL,
    ENEMY_CHASE,
    ENEMY_ATTACK
} EnemyState;

void update_enemy(Enemy *e, Player *p) {
    s16 dist = abs(p->x - e->x);
    
    if (dist < 200) {                      // 200 pixels
        e->state = ENEMY_CHASE;
    } else {
        e->state = ENEMY_PATROL;
    }
    
    switch (e->state) {
        case ENEMY_PATROL:
            e->vx = e->patrol_direction ? FIX16(1) : FIX16(-1);
            break;
        case ENEMY_CHASE:
            e->vx = (p->x > e->x) ? FIX16(2) : FIX16(-2);
            break;
    }
}
```

---

## 6. Tilemap Collision

```c
// Definir tile sólido (ex: tile 0-3 são sólidos)
bool is_solid_tile(u16 tile_id) {
    return tile_id >= 0 && tile_id <= 3;
}

// Testar se posição colidiu com tilemap
bool tilemap_collision(s16 x, s16 y) {
    u16 tile_x = x / 8;
    u16 tile_y = y / 8;
    u16 tile_id = map[tile_y][tile_x];
    return is_solid_tile(tile_id);
}
```

---

**Próximo**: Leia `TODO_NEXT.md` para evoluir para ADVANCED.
