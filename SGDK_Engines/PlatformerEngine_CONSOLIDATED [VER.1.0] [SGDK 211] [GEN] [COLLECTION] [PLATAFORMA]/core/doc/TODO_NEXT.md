# Próximos Passos (Core → Standard)

## Checklist de Domínio CORE

Antes de avançar, confirme que sabe:

- [ ] O que é VBlank e por qué usamos
- [ ] Como carregar e renderizar um sprite
- [ ] Como ler entrada do controle
- [ ] Como fazer colisão AABB básica
- [ ] O que é fix16 e por qué não usar float
- [ ] Como estruturar game loop (init/update/render)

---

## Conceitos Novos em STANDARD

Quando passar para `/standard`, você aprenderá:

### Physics
- **Gravidade**: Aceleração constante para baixo (-1 pixel/frame²)
- **Velocidade Vertical**: vy += gravity (accumulation)
- **Jump Boost**: Aplicar impulso positivo vy quando jump é pressionado

### Animation
- **Frame Counter**: frame++; if (frame >= max) frame = 0
- **Animation Queue**: sprite → idle/running/jumping frames

### Enemies
- **Simple AI**: Patrulha (esquerda ↔ direita) + detecção jogador
- **State Machine**: idle → chase → attack

### Level Design
- **Tilemap**: Grade de tiles 8x8 renderizada com BG_A
- **Collision Map**: Separado de visual; define quais tiles são sólidos

---

## Recursos Necessários (Standard)

Você precisará de:
- Sprite do jogador (16x32 ou maior, multi-frame)
- Sprites de inimigos
- Tileset 8x8 para o mapa
- Paleta física da cena

---

## Como Transicionar

1. **Entenda** este `CONCEPTS.md`
2. **Rode** os exemplos em `../examples/01_basic_level/`
3. **Leia** `/standard/doc/README.md`
4. **Estude** `/standard/src/player.c` (como pulo + gravidade)
5. **Modifique** um exemplo e recompile
6. **Customize** para seu jogo

---

## Armadilhas Comuns

❌ **Usar float em vez de fix16**
→ Fix16 é 16.16 fixed-point; muito mais rápido

❌ **Modificar sprite fora do VBlank callback**
→ Causa artefatos; espere ISR

❌ **Não verificar bounds do mapa**
→ Jogador pode sair da tela; sempre valide

❌ **Colisão por pixel sem otimização**
→ Lento; use AABB broad-phase primeiro

---

**Você está pronto! 🚀 Vá para `/standard/`**
