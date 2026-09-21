# Adaptacao de presets retro ao Mega Drive

Referencia conceitual recebida: descricao de Pixel Art v2.0.0 (dodo-reach).
Nenhum codigo externo foi importado; a descricao nao inclui os scripts.

Use o `forge-art` existente. Nao crie outro quantizador ou outra autoridade
de cor para imitar presets NES, SNES, PICO-8 ou Floyd-Steinberg.

| Intencao da referencia | Implementacao no Forge |
|---|---|
| Foto/concept para pixel | Fonte imutavel, contrato de escala, traducao nativa basic/elite; conversao automatica so candidata tecnica |
| Paleta de epoca | Quatro linhas VDP, 15 indices visiveis por linha mais zero; oraculo `forge_art/vdp_color.py` |
| Blocos de pixels | Decisao em pixel nativo; tiles 8x8 sao unidade de armazenamento, nao filtro mosaico |
| Dithering | Decisao por material e movimento, depois de clusters; difusao global pode destruir silhueta e deduplicacao |
| Chuva/neve/brasa animada | Assets autorais, timeline, paleta, slots e pior scanline; MP4/GIF e preview, nao recurso SGDK |
| Repetir conversao | `python3 -m forge_art convert --project-root <projeto> --spec <spec>` com `PYTHONPATH=tools/sgdk_wrapper` |

Inspecione `forge-art --help` e `tools/sgdk_wrapper/forge_art/schemas/conversion_spec.schema.json` antes
de emitir spec. Preserve alpha/index zero e PLTE com o pixel-contract;
o numero de cores usadas sozinho nao verifica o PNG para ResComp.
Para sprite animado, timing vem do contrato em VBlank, nao do FPS do MP4.

Avaliacao visual compara fonte/basic/elite/ROM em escala nativa e 4:3,
incluindo silhueta, materiais, contato e contraste em movimento. Preview
offline nao promove arte nem substitui evidencia de BlastEm.
