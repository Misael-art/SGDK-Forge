# Success patterns (local)

- Tratar `48x64` como contrato e travar pivô/recorte antes de iniciar frames.
- Separar `PAL2` (corpo) e `PAL3` (fx) em strips distintos para evitar mistura de paleta no mesmo tile.
- Manter rampas curtas por material (pedra/pele/tecido) e usar contraste de outline para leitura em 320×224.
- Garantir `PLTE <= 16` no PNG final (evita reindex silencioso e simplifica debug de paleta).
