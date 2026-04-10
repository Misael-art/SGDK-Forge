# Conceitos Principais - CORE

## 1. Game Loop

```c
void main() {
    init_system();           // Inicializa SGDK
    init_game();             // Configura jogo
    
    while (TRUE) {
        wait_vblank();       // Aguarda VBlank (60Hz)
        update_game();       // Atualiza lógica
        render_game();       // Renderiza sprites/tiles
    }
}
```

**Por que VBlank?** Hardware sincroniza updates com tela para evitar tearing.

---

## 2. Sprite Rendering

```c
// Carregar sprite
Sprite *player = SPR_addSprite(
    &player_sprite,      // Definição do sprite
    128, 128,            // Posição X, Y
    SPRITE_SIZE(1,1),    // 16x16 pixels
    0                    // Paleta 0
);
```

**Tamanho**: Sprites MD são múltiplos de 8x8 (8, 16, 24, 32 pixels).

---

## 3. Input Handling

```c
u16 pad = joy_readJoypad(JOY_1);

if (pad & BUTTON_RIGHT) player_move_right();
if (pad & BUTTON_LEFT)  player_move_left();
if (pad & BUTTON_A)    player_jump();
```

**Botões**: Um, Baixo, Esquerda, Direita + A, B, C, Start.

---

## 4. Collision Detection (AABB)

```c
// Axis-Aligned Bounding Box
bool check_collision(Entity *a, Entity *b) {
    return !(a->x + a->w < b->x ||
             b->x + b->w < a->x ||
             a->y + a->h < b->y ||
             b->y + b->h < a->y);
}
```

---

## 5. Fixed-Point Arithmetic

```c
// Use fix16_t em vez de float!
fix16_t x = FIX16(10);        // 10.0
x = fix16_add(x, FIX16(5));   // x = 15.0
x = fix16_mul(x, FIX16(2));   // x = 30.0

// Por quê? Mega Drive não tem FPU; fix16 é rápido!
```

---

## 6. VBlank Interrupt Service Routine (ISR)

```c
void vblank_isr() {
    SPR_update();        // Atualiza sprites renderizados
    PAL_update();        // Aplica mudanças de paleta
}

// Registrar callback
SYS_setVIntCallback(vblank_isr);
```

---

**Próximo**: Leia `TODO_NEXT.md` para evoluir para STANDARD.
