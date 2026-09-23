# 14 - Plano de Provas QA — GOTHAM_OVERDRIVE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

## 1. Critérios de Aceitação do MVP Técnico

| Eixo | Requisito | Método de Prova | Status |
|------|-----------|-----------------|--------|
| **1. Build** | Compilação limpa sem erros ou warnings gerando `out/rom.bin` | `tools/sgdk_wrapper/build.sh` | APROVADO |
| **2. Raster Pseudo-3D** | 224 scanlines com `HSCROLL_LINE` e 20 colunas de `VSCROLL_COLUMN` ativas | Inspeção VDP / Emulador | APROVADO |
| **3. Boss Modular** | Articulação de 5 sprites independentes, mira da torre e máquina de estados | Gameplay no Emulador | APROVADO |
| **4. Alta Densidade de Sprites** | Batmóvel, chefe, drones e dezenas de projéteis/partículas simultâneas | Monitor de Hardware Sprites | APROVADO |
| **5. Iluminação Dark Deco** | Bat-Sinal com cycling dinâmico, paletas de 15 cores e contraste preto puro | Renderização VDP | APROVADO |
| **6. Performance** | 60 FPS travados e estáveis no BlastEm | Telemetria ao vivo / Logs | APROVADO |
| **7. Controles** | D-Pad movimentação, A (Vulcan), B (Mísseis), C (Turbo), START (Pause), MODE (Debug) | Leitura de Joypad | APROVADO |
