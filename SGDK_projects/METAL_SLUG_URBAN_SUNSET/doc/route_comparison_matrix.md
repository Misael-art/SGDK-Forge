# Route Comparison Matrix - METAL_SLUG_URBAN_SUNSET

Este documento registra o teste comparativo das rotas visuais propostas para a cena urbana.

## Escopo do teste

- manter a mesma cena e o mesmo enquadramento
- tratar as rotas como alternativas de direcao de arte, nao como redesigns de layout
- medir duas coisas ao mesmo tempo:
  - apelo visual em versao estrita `15 colors`
  - risco estrutural se a cena fosse promovida como `compare_flat`

## Fontes usadas

- source original: [source.png](/F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/res/data/source/source.png)
- crop de estudo: [city_cropped_448x224.png](/F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/res/data/city_cropped_448x224.png)
- board de exploracao: [route_exploration_board.md](/F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/doc/route_exploration_board.md)
- resumo machine-readable: [route_comparison_summary.json](/F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/out/route_tests/route_comparison_summary.json)
- board visual gerado: [route_compare_strict15_board_v2.png](/F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/out/route_tests/route_compare_strict15_board_v2.png)
- board final com incumbente + anime: [route_compare_with_incumbent_and_anime.png](/F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/out/route_tests/route_compare_with_incumbent_and_anime.png)

## Identidade real das variantes

- `A`: `high_key_haze`
- `B`: duplicata exata de `A`
- `C`: `grid_alignment_diagnostic`
- `D`: `cool_evening`
- `E`: `anime_style`

## Metodo

1. Reducao `nearest-neighbor` para `448x224`.
2. Teste rapido de conversao com `ordered-dither` direto.
3. Verificacao de compatibilidade:
   - o `ordered-dither` direto do ImageMagick nao ficou em `15 colors`, portanto nao foi usado como prova final de compatibilidade.
4. Prova estrita:
   - quantizacao adaptativa estrita para `15 colors`, `depth=4`.
5. Juiz estetico:
   - `analyze_aesthetic.py`
   - `role=bg_a`
   - `reference-profile=generic-megadrive-elite`
6. Pressao estrutural:
   - contagem de tiles `8x8`
   - contagem de tiles unicos exatos
   - comparacao contra o teto pratico atual de `1264` tiles para `compare_flat`

## Resultados das rotas desafiantes

| Rota | Papel | Score | Palette | Silhouette | Reuse | Tiles unicos | Compare Flat |
|------|-------|-------|---------|------------|-------|--------------|--------------|
| `high_key_haze` | candidata real | `0.7491` | `0.4929` | `0.8627` | `0.0402` | `1512` | `nao cabe` |
| `cool_evening` | candidata real | `0.7414` | `0.4571` | `0.8463` | `0.0357` | `1518` | `nao cabe` |
| `anime_style` | candidata real | `0.8267` | `0.9318` | `1.0000` | `0.2481` | `1191` | `cabe` |
| `grid_alignment` | diagnostico | nao ranquear | nao ranquear | nao ranquear | nao ranquear | nao usar | nao promover |

## Incumbente padrao do projeto

O metodo padrao atual nao deve ser julgado como `city_bg_a` isolado.

Ele deve ser julgado como solucao composta:

- `sky_bg_b` + `city_bg_a`
- mesma cena
- mesma base espacial
- mesma estrategia multi-plano do projeto

Resultados do incumbente composto:

| Metodo | Papel | Score | Palette | Silhouette | Reuse | Tiles unicos | Compare Flat |
|--------|-------|-------|---------|------------|-------|--------------|--------------|
| `default_multi_plane_method` | incumbente composto | `0.7229` | `0.4241` | `0.9287` | `0.1977` | `1260` | `cabe` |

Leitura:

- o score bruto isolado do incumbente fica abaixo dos desafiantes
- mas a silhueta e o reuse estrutural ficam muito melhores
- principalmente, ele quase zera a diferenca de budget e cabe no teto flat equivalente

Regra de decisao:

- para desafiar o incumbente, nao basta ganhar em score bruto de imagem
- precisa ganhar tambem como solucao de sistema

## Leitura tecnica

### `high_key_haze`

- venceu por pouco em score geral
- melhor leitura de massa
- melhor economia relativa de tiles repetidos
- risco artistico:
  - afasta a cena do `urban sunset` original
  - puxa para uma leitura mais limpa e menos dramatica

### `cool_evening`

- perdeu por pouco no juiz estetico
- continua forte como rota valida
- melhora a separacao termica entre ambiente frio e luz interna quente
- risco artistico:
  - desloca a cena para dusk mais generico
  - perde parte da assinatura quente do source original

### `anime_style`

- foi recomposicao real, nao apenas quantizacao cosmetica
- simplificou materiais em massas mais chapadas, com ceu limpo e sombra cel-shaded
- foi a primeira rota desafiante a vencer simultaneamente:
  - `perceptual win` no juiz
  - `system win` em tiles unicos
- risco artistico:
  - muda a filosofia de pintura do projeto
  - precisa de aprovacao humana explicita antes de substituir o default

## Laudo de budget

Como imagem unica em `compare_flat`, as rotas dividiram-se em dois grupos:

- teto pratico atual: `1264` tiles
- `high_key_haze`: `1512`
- `cool_evening`: `1518`
- `anime_style`: `1191`

Decisao:

- `high_key_haze`: `nao cabe` como `compare_flat`
- `cool_evening`: `nao cabe` como `compare_flat`
- `anime_style`: `cabe` como `compare_flat`
- como direcao de arte para reinterpretacao multi-plano:
  - `high_key_haze`: `cabe com recuo`
  - `cool_evening`: `cabe com recuo`
  - `anime_style`: `cabe` e tambem cabe como filosofia para promocao multi-plano futura

Recuo necessario:

- usar as rotas como referencia visual
- nao promover os PNGs diretamente como asset final da cena
- reinterpretar a rota escolhida no pipeline por layers `BG_B` + `BG_A` + foreground

## Recomendacao atual

Se a prioridade for:

- impacto imediato, polish e leitura mais limpa: escolher `high_key_haze`
- atmosfera mais fria e contraste termico mais explicito: escolher `cool_evening`
- linguagem de anime background, sombra chapada e melhor economia estrutural: escolher `anime_style`

Recomendacao da curadoria neste teste:

- `anime_style` sobe para a frente entre as rotas desafiantes
- `high_key_haze` e `cool_evening` continuam validas como referencias de atmosfera
- o metodo padrao do projeto continua travado como default ate haver escolha humana explicita
- a partir deste teste, `anime_style` e a primeira rota que pode honestamente pedir a troca do default

## Proximo passo

Depois da escolha:

1. registrar em `route_decision_record`
2. manter `locked_visual_direction = default_multi_plane_method` ate o usuario congelar uma nova direcao
3. usar `high_key_haze` e `cool_evening` como referencias de atmosfera quando fizer sentido
4. promover `anime_style` a rota pronta para escolha humana
5. so reabrir a decisao sem usuario se um desafiante provar `perceptual win` e `system win` de forma inequívoca e ainda preservar a fantasia-base do projeto
