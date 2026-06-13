# Why It Exists

Este caso existe para fixar que:

- texto longo pode ser emitido como stream, sem montar a string inteira de uma vez
- `preshift` e ring buffer resolvem wrap de tile e reuse de VRAM
- esse padrao e ideal para typewriter text e scripts com control codes
