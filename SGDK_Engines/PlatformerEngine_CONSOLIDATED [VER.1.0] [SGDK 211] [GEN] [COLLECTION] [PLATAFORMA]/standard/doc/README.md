# 📍 STANDARD Level - Intermediário (Nível 2)

## O Que é STANDARD?

STANDARD é a **versão completa funcional** de um plataformador. Contém:
- Física de plataforma (gravidade, pulo)
- Animação de personagem
- Múltiplos inimigos com IA
- Detecção de colisão avançada
- Sistema de vidas/game over
- Mapas de nível com tiles
- Pontuação

**Objetivo**: Um jogo prototipado e pronto para customização.

---

## Conceitos-Chave Ensinados

1. **Physics** — Gravidade, velocidade, aceleração, jump boost
2. **Animation** — Mudança de frames baseada em estado
3. **Collision** — Detecção pixel-perfect e tilemap
4. **Enemy AI** — Patrulhas, perseguição, ataque
5. **Level Design** — Construir mapas com tiles
6. **State Machine** — Player states (idle, running, jumping, falling, hurting)
7. **Audio** — Sons básicos de efeito
8. **Scoring System** — Pontuação e vidas

---

## Estrutura

```
standard/
├── src/
│   ├── main.c         ← Game loop
│   ├── player.c       ← Lógica do jogador
│   ├── enemy.c        ← Lógica de inimigos
│   ├── physics.c      ← Cálculos de física
│   ├── collision.c    ← Detecção de colisão
│   ├── map.c          ← Gerenciador de mapa
│   └── input.c        ← Entrada de controle
├── inc/
│   ├── types.h
│   ├── player.h
│   ├── enemy.h
│   └── ...
├── res/
│   ├── player_sprite.png
│   ├── enemy_sprite.png
│   ├── tileset.png
│   └── resources.rc
├── doc/
│   ├── README.md (você está aqui)
│   ├── CONCEPTS.md
│   └── TODO_NEXT.md
└── examples/
    ├── 01_basic_level/
    ├── 02_with_enemies/
    ├── 03_full_game/
    └── 04_animations/
```

---

## Como Usar STANDARD

### 1. Compile
```bash
cd standard
build.bat
```

### 2. Rode no Emulador
```bash
run.bat
```

### 3. Estude o Código Modular
- `player.c`: Como o personagem se move, pula, toma dano
- `enemy.c`: Patrulha, detecção de jogador, ataque
- `physics.c`: Funções de gravidade e movimento
- `map.c`: Carregamento e renderização de níveis

### 4. Execute Exemplos
```bash
cd examples/02_with_enemies
build.bat && run.bat
```

### 5. Customize
- Mude velocidade do jogador
- Adicione novos tipos de inimigos
- Crie novo mapa de nível

---

## Próximos Passos Após Dominar STANDARD

✅ Conseguiu:
- [ ] Compilar e rodar
- [ ] Entender physics.c
- [ ] Modificar inimigos
- [ ] Criar novo tilemap

❌ Não abordado (próximo nível):
- Camera avançada com lag/easing
- Efeitos de partículas
- Boss fights
- XGM2 audio integrado
- Otimizações de performance

✅ Está pronto para → **ADVANCED Level**

Quando, continue em `advanced/doc/README.md`.

---

## Troubleshooting

**Erro: "Inimigos não aparecem"**
→ Verifique `enemy_init()` em enemy.c

**Erro: "Colisão não funciona"**
→ Verifique `check_collision()` em collision.c

**Erro: "Mapa não carrega"**
→ Verifique `level_load()` em map.c e res/resources.rc

**Performance baixa?**
→ Veja `ADVANCED` para otimizações

Para mais, veja `../doc/TROUBLESHOOTING.md`.

---

## Tips & Tricks

- **Modular Code**: Cada módulo (player, enemy, physics) é independente
- **Reusable**: Copie `physics.c` para seus projetos
- **Extensível**: Adicione `power_up.c`, `boss.c` seguindo padrão
- **Debug**: Use prints em VBlank callback para debugar
- **Assets**: Tiles 8x8, sprites múltiplos de 8x8 para hardware MD

---

**Tempo estimado**: 8-16 horas para compreender e customizar.

**Próxima etapa**: Progresse para `ADVANCED` para otimizações e efeitos avançados.
