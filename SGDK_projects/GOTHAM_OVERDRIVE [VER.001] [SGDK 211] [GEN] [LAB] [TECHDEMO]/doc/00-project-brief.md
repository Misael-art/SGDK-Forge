# 00 - Project Brief — GOTHAM_OVERDRIVE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

## 1. One-Sentence Goal
Demonstrar a potência visual máxima do Mega Drive (Motorola 68000 + VDP) através de uma cena de perseguição do Batmóvel contra um tanque biônico modular com pseudo-3D multi-eixo, gerenciamento massivo de sprites/partículas e iluminação dinâmica Dark Deco a 60 FPS estáveis.

## 2. Pilares de Design e Tecnologia
1. **Pseudo-3D Radical e Raster Scrolling Multi-Eixo**: Manipulação de 224 scanlines com `HSCROLL_LINE` e 20 colunas com `VSCROLL_COLUMN` para simular rotação, escala e horizonte banking da estrada e skyline de Gotham.
2. **Chefe Colossal Modular ("Two-Face Siege Dreadnought")**: Inimigo mecânico pesado construído por peças de Lego articuladas (chassi, torre de canhão duplo de plasma, esteiras animadas, pod de mísseis) com mira e estados proceduralmente gerenciados.
3. **Gerenciamento Maciço de Sprites e Partículas**: Pool estático em ponto fixo (`fix16`) para o Batmóvel, drones de escolta, rajadas Vulcan, mísseis Batarang e centenas de centelhas/detritos sem estouro do VDP.
4. **Estética Dark Deco e Iluminação Dinâmica**: 15 cores indexadas por paleta, contraste extremo com preto puro ($000$), varredura de feixe do Bat-Sinal nos céus e sombreamento por *dithering* puro.
5. **Telemetria de Performance ao Vivo**: HUD de diagnóstico exibindo carga de CPU, contagem de hardware sprites e taxa de 60 quadros por segundo.

## 3. Escopo e Não-Escopo
- **Escopo**: Cena jogável completa de Tech Demo, controle do Batmóvel (tiros, mísseis, turbo boost), combate dinâmico contra o chefe modular e drones, distorção raster em tempo real e monitor de telemetria.
- **Não-Escopo**: Jogo comercial completo com múltiplos mundos/fases longas (trata-se de um demonstrador técnico / proof of concept focado na orquestração de hardware).
