---
status: seed
prd_title: Code Review Charter
last_updated: 2026-07-03
---

# Code Review Charter - MARE_BRAVA

Review formal antes de closeout de cena (governance skill):
- proibicoes de ferro: float/double, malloc/free, DMA fora de VBlank, API inventada (verificar sdk/sgdk-2.11/inc/)
- padroes: fix16/fix32, buffers estaticos, leitura unica de input, u16/s16 (int e 32 bits no 68000)
- diff revisado contra tdd_contract (FSM, pools, ownership) antes de marcar `testado_em_emulador`.
