# Próximos Passos (Standard → Advanced)

## Checklist de Domínio STANDARD

Antes de avançar, confirme que sabe:

- [ ] Como aplicar gravidade e velocidade
- [ ] Fazer um personagem pular realista
- [ ] Implementar animação frame-based
- [ ] Criar enemies com patrulha e chase
- [ ] Detecção de colisão AABB + tilemap
- [ ] State machine para transições
- [ ] Carregar e renderizar mapas

---

## Conceitos Novos em ADVANCED

Quando passar para `/advanced`, você aprenderá:

### Advanced Camera
- **Following**: Câmera segue jogador com interpolação
- **Prediction**: Extra-polação posição futura do jogador
- **Easing**: Smooth acceleration/deceleration de câmera
- **Boundaries**: Câmera não ultrapassa limites do mapa

### Parallax Scrolling
- **Multiple Layers**: Fundo (BG_B) + mid (BG_A) + HUD (WINDOW)
- **Scroll Differential**: Cada layer scroll a velocidade diferente
- **Depth Illusion**: Fundo lento = ilusão de profundidade

### Visual Effects (VFX)
- **Particles**: Pó, sparks, explosões
- **Screen Shake**: Feedback tátil de eventos
- **Transitions**: Fades, wipes, scrolls entre cenas

### Boss Fights
- **Complex AI**: Boss com múltiplas fases, padrões de ataques
- **Telegraphing**: Animar antes de ataque (feedback ao jogador)
- **Damage Feedback**: Knockback, invulnerabilidade, cores

### Audio (XGM2)
- **Music**: Música dinâmica que muda com estado
- **SFX**: Efeitos sonoros sincronizados
- **Mixing**: Gerenciar 4 FM + 3 SSG channels

### Performance Optimization
- **VRAM Budget**: Sprite/tile allocation planning
- **DMA Scheduling**: Quando programar DMA para não colar
- **Culling**: Não renderizar sprites fora da câmera
- **Profile**: Usar profiler emulador para bottlenecks

---

## Recursos Necessários (Advanced)

Você precisará de:
- Tudo de STANDARD +
- Sprites de boss complexos
- Música XGM2 compilada
- Efeitos sonoros (WAV)
- Backgrounds parallax (múltiplas camadas)

---

## Como Transicionar

1. **Entenda** este `CONCEPTS.md`
2. **Rode** exemplo camera em `../examples/01_camera_system/`
3. **Leia** `/advanced/doc/README.md`
4. **Estude** `/advanced/src/camera.c` (câmera com predição)
5. **Estude** `/advanced/src/boss.c` (IA complexa)
6. **Modifique** um exemplo
7. **Customize** para seu jogo

---

## Armadilhas Comuns

❌ **Câmera muito rápida/lenta**
→ Ajuste prediction factor em camera.c

❌ **VFX travando frame**
→ Limitar número de particles simultâneas

❌ **Áudio desincronizado**
→ Verifique callback XGM2 em audio.c

❌ **Performance <60fps**
→ Profile com BizHawk; identifique bottleneck

---

**Você está pronto para master o Mega Drive! 🚀 Vá para `/advanced/`**
