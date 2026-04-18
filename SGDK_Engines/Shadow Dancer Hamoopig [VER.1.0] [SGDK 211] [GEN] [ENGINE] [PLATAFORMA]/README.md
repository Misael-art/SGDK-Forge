## SHADOW DANCER PROJECT by GameDevBoss

### Creator: 
- GameDevBoss - https://www.youtube.com/@GameDevBoss

# Thanks to:                          

- Edmo Caldas (music)                   https://www.youtube.com/@edmocaldas
- Ray Castello (gfx, art)               https://twitter.com/ray_castello
- Vubidugil (Ninja original sprites)    https://twitter.com/VubidugiL
- Gabriel Pyron (Gfx, art)              https://www.youtube.com/@PyronsLair

---

## Como compilar e rodar

Este projeto usa as **ferramentas centrais** do repositório MegaDrive_DEV (wrapper SGDK). Na pasta do projeto:

- **Compilar:** duplo clique em `build.bat`
- **Rodar a ROM:** duplo clique em `run.bat` (abre o emulador com a ROM)
- **Limpar artefatos:** executar `clean.bat`
- **Limpar e recompilar:** executar `rebuild.bat`

Para detalhes, pré-requisitos (Java, ambiente) e troubleshooting, consulte:  
[doc/migrations/MIGRATION_SHADOW_DANCER_HAMOOPIG.md](../../doc/migrations/MIGRATION_SHADOW_DANCER_HAMOOPIG.md)

---

## Conteúdo pedagógico (main.c)

O `src/main.c` está comentado para estudo com SGDK 2.11. Sugestão de leitura:

1. **Cabeçalho do arquivo** – propósito do projeto, créditos e índice das seções.
2. **Constantes e globais** – resolução VDP 320x224, margens de câmera, limites de objetos.
3. **Structs** – `PlayerDEF` (FSM, física, animação), objetos de efeito, inimigos, projéteis.
4. **main()** – inicialização VDP e loop por “rooms” (gRoom); em room 10: FSM → ANIMATION → PHYSICS → CAMERA → UPDATE/DRAW.
5. **PLAYER_STATE / FSM** – estados do jogador (convenção teclado numérico) e transições.
6. **COLLISION_HANDLING** – uso de DM (Directional Movement) para corrigir posição após colisão AABB.
7. **CAMERA** – scroll com zona morta e MAP_scrollTo; parallax em BG_B para certos mapas.
8. **CREATE_STAGE** – carregamento de tilesets, MAP_create, matrizes de colisão e de troca de plano.

Para aprofundar: ANIMATION (dataAnim/animRow), PHYSICS (impulso, gravidade, groundSensor), e as funções UPDATE_*/DRAW_* de cada tipo de objeto.
