---
name: megadrive-pixel-strict-rules
description: Use para validar ou corrigir conformidade absoluta de sprites, tilesets e backgrounds com as restricoes rigidas de pixel art do VDP do Mega Drive: paleta, index 0, grid 8x8, cores validas e limites por tile. Nao use para decidir sourcing de arte, analisar budget global da cena ou conduzir direcao estetica mais subjetiva.
---

# Mega Drive Pixel Strict Rules

Estas sao as restricoes absolutas do hardware grafico do Mega Drive. Nenhuma excecao e permitida. Todo asset, sprite, tileset ou cenario DEVE obedecer a cada regra abaixo antes de ser aceito no pipeline.

---

## 1. Cor indexada 4-bits

- Cada tile usa **exatamente 1 paleta** de 16 entradas.
- **Index 0 e obrigatoriamente transparente** (convencao: magenta `#FF00FF` no PNG fonte).
- Maximo de **15 cores visiveis** por paleta.
- O VDP possui **4 paletas** (PAL0-PAL3) = 64 entradas totais (60 cores visiveis + 4 transparentes).

## 2. Resolucao de cor 9-bits

Cada canal (R, G, B) tem 3 bits = 8 niveis. Os unicos valores validos em hexadecimal por canal sao:

```
0x00  0x22  0x44  0x66  0x88  0xAA  0xCC  0xEE
```

Qualquer cor fora deste grid de 512 cores sera rejeitada. Nao existe dithering automatico de paleta no hardware.

## 3. Grid 8x8 obrigatorio

- Todo tile tem **8x8 pixels**, sem excecao.
- Sprites sao compostos por blocos de tiles: 1x1, 1x2, 2x1, 2x2, 1x3, 3x1, 1x4, 4x1, 2x2, 2x3, 3x2, 2x4, 4x2, 3x3, 3x4, 4x3, 4x4.
- Tamanho maximo de sprite hardware: **4x4 tiles** = 32x32 pixels.
- Sprites maiores exigem metasprite (multiplas entradas na sprite table).

## 4. Escala 1x

- Todo pixel desenhado deve ser **1:1 com o pixel do VDP**.
- Nao existe scaling por hardware (sem Mode 7, sem zoom).
- Se precisar de escala, pre-renderize frames em diferentes tamanhos como tiles separados.

## 5. Bounding box justo

- Sprites devem ter o **menor retangulo possivel** que contenha os pixels visiveis.
- Area transparente desperdicada dentro do bounding box e VRAM perdida.
- Recorte bordas vazias antes de exportar.

## 6. Tile flipping via hardware

- O VDP suporta flip horizontal e vertical por tile.
- **Reutilize tiles espelhados** em vez de duplicar no tileset.
- Ao projetar cenarios simetricos, projete metade e espelhe via atributos do tilemap.

## 7. Economia de VRAM

- VRAM total: **64 KB** (2048 tiles de 32 bytes cada, dos quais ~1536 ficam disponiveis apos reserva de scroll tables e sprite table).
- Cada tile ocupa **32 bytes** (8x8 pixels x 4 bits).
- Compartilhe tiles entre sprites e cenarios sempre que possivel.
- Priorize reuso de tiles duplicados, espelhados ou com paleta alternada.

---

## Proibicoes absolutas

Estas tecnicas **nao existem** no hardware e devem ser bloqueadas em qualquer etapa do pipeline:

1. **Anti-Aliasing** — nao existe. Bordas de sprite sao hard-edge. Nunca suavize bordas com cores intermediarias pensando em blending.
2. **Canal Alpha / Opacidade parcial** — nao existe. Pixel e 100% visivel ou 100% transparente (index 0). Sem semi-transparencia.
3. **Baked Lighting complexo** — proibido assar iluminacao gradiente nos tiles. Use shadow/highlight do VDP (modo S/H) ou engine para simular. Dithering manual controlado e aceito.
4. **Sombras assadas na arte** — proibido pintar sombra como parte do sprite. Use shadow bit do VDP ou sprites de sombra simples via engine.
5. **Sub-pixels reais** — nao existem. Toda movimentacao e em incrementos de pixel inteiro no render final. Posicao sub-pixel e apenas logica interna (fixed-point), nunca visual. Micro-movimento por mudanca de luz/sombra interna so e permitido como `subpixel_shading_motion_report`, sem AA, blur, nova cor de ruído ou alteracao da silhueta externa.
6. **Gradientes suaves** — com 15 cores por paleta e 512 cores totais, gradientes suaves sao impossiveis. Use dithering manual de 2-3 cores ou ramp curto.
7. **Rotacao por hardware** — nao existe. Pre-renderize frames rotacionados como tiles individuais.

---

## Checklist de validacao de asset

Antes de aceitar qualquer imagem no pipeline:

- [ ] Formato PNG indexado (8-bit ou 4-bit)
- [ ] Se veio de IA/high-res, downscale foi feito por nearest-neighbor ou foi redesenhado manualmente em grid nativo
- [ ] Index 0 da paleta = transparente (magenta no fonte)
- [ ] Maximo 15 cores visiveis na paleta do tile
- [ ] Todas as cores dentro do grid 9-bits (multiplos de 0x22)
- [ ] Dimensoes multiplas de 8 pixels (largura E altura)
- [ ] Bounding box sem bordas vazias desnecessarias
- [ ] Tiles duplicados ou espelhaveis identificados para reuso
- [ ] Nenhuma tecnica proibida presente (AA, alpha, baked light, sombra assada)
- [ ] Sem fake pixel art: bordas nao tem interpolacao, halo, subpixel fracionario, blur, gradient suave ou PLTE inflada
- [ ] UI, fonte, health bar e icones usam posicionamento inteiro e nao dependem de free-scale, AA ou interpolacao

## Gate `fake_pixel_art_rejection`

Todo asset gerado por IA, render high-res, mockup ou source nao-nativo deve
passar por este gate antes de virar sprite, tileset ou sheet final.

Bloqueia:

- downscale bicubico, bilinear, lanczos ou qualquer interpolacao suave;
- anti-aliasing automatico em bordas, olhos, cabelo, armas ou outline;
- paleta com microvariacoes da mesma cor apos quantizacao;
- fundo de chroma-key nao uniforme ou nao-indexado;
- PLTE com 256 entradas quando o asset deveria ter ate 16;
- pixels orfaos, halos ou fragmentos fora da celula do personagem;
- gradiente suave tentando substituir rampa curta/dithering manual.
- health bar, fonte ou moldura de UI com borda interna suavizada, fill escalado por fracao ou atlas produzido por interpolacao.

Passa quando:

- a arte foi desenhada em grid nativo ou reduzida por nearest-neighbor;
- a paleta foi indexada, limpa e snapped para 9-bits;
- bordas sao hard-edge;
- a limpeza manual removeu jaggies, ilhas e residuos;
- `sprite_artifact_report` nao contem blockers de celula quando for strip.
- UI final com leitura pixel-perfect possui `ui_pixel_surface_contract` quando houver fonte, health bar, micro-icone, caixa ou cursor de entrega.

## Contrato Operacional

### Entrada minima

- PNG, tileset, sprite sheet ou background a validar
- paleta esperada, index transparente e dimensoes alvo
- `master_style_manifest` e `asset_lineage_record` quando o asset veio de sourcing/IA
- linha `.res` pretendida quando houver integracao SGDK
- contexto se o asset e sprite, `IMAGE`, `TILESET`, `MAP` ou `PALETTE`
- `ui_pixel_surface_contract` quando o asset for UI final, health bar, fonte, micro-icone, caixa ou cursor com exigencia pixel-perfect
- se o asset veio do Bonsai 4B: `prompt_pack_manifest.json` co-localizado
  (model_variant, license_ack_sha256, asset_role esperado em
  `{concept_art, tileset_concept, dither_mask, contrast_study}`)

### Saida minima

- `pixel_compliance_report`
- lista de blockers por asset e correcao recomendada
- confirmacao de grid 8x8, index 0, PLTE e grid 9-bits
- sinalizacao quando a conformidade tecnica ainda contradiz o `master_style_manifest`
- decisao: `aprovado`, `aprovado_com_ajustes` ou `rejeitado`
- quando asset_role ∈ forbidden_scopes (`animated_sprite_final`, `hud_final`,
  `res_direct`, `aaa_final_asset`): registrar `res/asset_role_forbidden` e
  rejeitar independente da conformidade tecnica

### Passa quando

- todo asset usa paleta indexada compatível com 4-bits e maximo 15 cores visiveis
- index 0 e transparente conforme contrato do pipeline
- dimensoes e bounding box nao desperdicam tiles sem justificativa
- nenhuma tecnica inexistente do VDP foi usada como atalho visual
- se asset_role ∈ forbidden_scopes: NAO PASSA. Redirecionar para outro canal.
- health bar, fonte ou caixa de UI que usa borda/fill anti-aliased, escala fracionaria ou suavizacao fica `rejeitado`, mesmo que compile.

### Handoff para proxima etapa

- entregar blockers para `art-conversion-pipeline` quando houver correcao mecanica
- entregar assets aprovados para `megadrive-vdp-budget-analyst`
- entregar riscos de leitura para `visual-excellence-standards` quando a conformidade tecnica ainda nao garante qualidade

## Caso especial: source Bonsai 1-bit dithered → paleta MD 16-cores

Quando o asset e uma saida do `imagegen_circuit.py run --asset-role
{concept_art, tileset_concept, dither_mask, contrast_study}` e foi gerado
pelo Bonsai 4B, o source chega em 2 tons (preto + branco puros, com
dithering pattern como portador de informacao de luminancia). O contrato
de traducao para o VDP:

1. **Tom 0 (preto puro)** → mapeia para **indice 0** da paleta =
   transparente (conforme regra geral "Index 0 obrigatoriamente
   transparente"). Isso so faz sentido se o asset for uma mascara
   (`dither_mask`); para `concept_art` e `tileset_concept`, o tom 0
   vira **indice 1** (cor base escura) e nao transparente.
2. **Tom 1 (branco puro)** → mapeia para **indice 15** (cor principal)
   ou para um trio Highlight/Shadow/Base dependendo do papel no
   `master_style_manifest`.
3. **Dither pattern** (pares adjacentes de pixels preto/branco) →
   interpretado como **mascara H/S**:
   - Cada par preto/branco vizinho vira um par de indices Highlight
     (luminancia alta) e Shadow (luminancia baixa) na mesma paleta.
   - Padroes 2x2 Bayer, 4x4 ordered, e diagonais comuns no Bonsai 1-bit
     devem virar ate 3 tons (Highlight / Base / Shadow) por plano, nao
     mais — para respeitar a regra de 3 tons por paleta.
4. **Validacao pixel-strict obrigatoria**:
   - [ ] Source original tem apenas 2 tons? Caso contrario, asset ja
         foi quantizado uma vez — abrir issue no `visual_feedback_bank`
         e tratar como `provisional` ate nova geracao.
   - [ ] Dimensoes multiplas de 8 (largura E altura)?
   - [ ] BitDepth = 4, colorType = 3 (indexed)?
   - [ ] PLTE com no maximo 16 entradas?
   - [ ] Grade 9-bits: cada canal R, G, B em 0x00, 0x22, 0x44, 0x66,
         0x88, 0xAA, 0xCC, 0xEE? Bonsai 1-bit ja respeita por construcao.
   - [ ] Index 0 = transparente (apenas para `dither_mask`); para
         outros roles, index 0 = cor base escura e o slot transparente
         vem do pipeline de chroma-key previo, nao do source.
5. **Anti-padroes** especificos para Bonsai:
   - Tratar o output 1-bit como "preto e branco" sem ler o dither
     pattern (destroi a informacao H/S).
   - Aplicar blur/AA no source antes de indexar (proibido pelo
     regulamento geral).
   - Aceitar 256 cores no PLTE (inflacao de paleta; quebra reuso
     de tiles).
   - Promover direto para `res/` sem o gate de
     `art-translation-to-vdp` + BlastEm.
6. **Handoff pos-validacao**: o asset passa para
   `art-translation-to-vdp` se o `master_style_manifest` pede
   `basic`+`elite` paralelo, ou direto para
   `imagegen_tool.py convert` se o brief ja congela uma unica rota.
