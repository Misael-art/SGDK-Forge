# TAINA — relatório de produção visual v02

> **SUPERADO / NAO ABRIR GATE HUMANO.** A curadoria de 2026-08-31 encontrou
> matte retangular/halo, aliases de paleta, mapas semanticos geometricos e erro
> no modelo de links por scanline. Este pacote e evidencia de retrabalho. A
> rota correta e regenerar v03 com as guardas canonicas atuais.

## 1. Contexto e verdade operacional

TAINA permanece em `technical_candidate`. O model sheet aprovado é a única fonte visual de geração; incumbent, probes antigos e `res/` são apenas comparação/controle. Nenhum arquivo de `res/` foi alterado.

## 2. Diagnóstico de arte

O diagnóstico do projeto confirmou `2_res_inadequate_check`: há arte de fonte disponível, nenhum blocker estrutural, e o incumbent 48×64 é comparação apenas. O gargalo real continua sendo fidelidade nativa, não ausência de material.

## 3. Alternativas geradas

Foram gerados dois estudos distintos em cada escala pelo canal `native_chat_image_generation_callable`, sempre referenciando somente o model sheet aprovado. Cada estudo foi persistido antes da conversão e recebeu SHA-256 no manifesto do pacote.

## 4. Tradução para células nativas

Cada alternativa tem PNG indexado exatamente em 48×64 ou 64×96, índice 0 transparente, até 15 cores visíveis e cores na grade RGB de 9 bits. Cada uma possui `silhouette_mask`, `semantic_region_map` e `contour_overlay` nativos, distintos, com hashes e vínculos de `asset_id`, escala e fonte.

## 5. Validador e fixtures

O resultado 22/22 do validador v2.3 era insuficiente: aceitava silhueta
retangular e rotulos semanticos artificiais. Schema v1.3 e validador v2.4 exigem
matte report, igualdade de mascara, uniao exata, area significativa por regiao
e contorno rederivado; a suite passa 28/28.

## 6. Painel de comparação

O painel v02 e mantido como evidencia, mas sua pontuacao e recomendacao foram
invalidadas. O retangulo amarelo era footprint de celula, nao hitbox declarado.

## 7. Pré-seleção perceptual

Nao existe pre-selecao valida no v02. O usuario observou B como perceptualmente
melhor, mas a decisao so abre depois do recorte limpo e da medicao corrigida.

## 8. Budget VDP medido

| Escala | Tiles únicos | VRAM única | Metasprite | Pico de pixels/linha | Hero + 4 inimigos |
|---|---:|---:|---:|---:|---|
| 48×64 A | 48 | 1536 B | 4 | 42 px | ok, 20 links/linha |
| 48×64 B | 30 | 960 B | 4 | 23 px | ok, 20 links/linha |
| 64×96 A | 53 | 1696 B | 6 | 32 px | **overflow: 22 links/linha** |
| 64×96 B | 63 | 2016 B | 6 | 41 px | **overflow: 22 links/linha** |

Esta tabela esta invalidada. O simulador v1.1 aplicou o total de celulas
verticais em todas as linhas. Com a decomposicao v1.2, no mesmo cenario teorico,
48x64 mede pico 6 sprites/176 px por linha e 64x96 mede 6 sprites/192 px; ambos
cabem em H40. Isso reabre a escala, sem provar runtime.

## 9. Recomendação e estado dos gates

Sem recomendacao. Estado: `rework`, `visual_pass=false`, `human=not_started`,
`promotable=false`. Nao ha promocao para `data/processed`, `res/` ou ROM.

## 10. Gate humano e próximos passos

Primeiro gere v03 com matte conectado as bordas, alpha binario, NEAREST,
paleta compacta, mapa semantico real e budget v1.2. Depois o gate humano compara
1x/8x/camera. Esta entrega nao e `visual_pass`, `ready_for_res`, jogo ou AAA.

Artefatos principais: `taina_visual_comparison_panel.png`, `taina_visual_review_report.json`, `scale_budget_report.json`, `candidates/challenger_package_manifest.json` e `doc/art/characters/taina/native_sprite_production_record.json`.
