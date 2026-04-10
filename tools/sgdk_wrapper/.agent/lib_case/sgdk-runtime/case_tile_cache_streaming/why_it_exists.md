# Why It Exists

Este caso existe para fixar que:

- mapa enorme nao implica carregar todos os tiles ao mesmo tempo
- refcount e callback de mapa resolvem reuso honesto de VRAM
- o gargalo real passa a ser custo de callback e disciplina de DMA
