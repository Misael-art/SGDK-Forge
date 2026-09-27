# Suzaku: estudo de ownership dos planos e perfis semânticos

Estado: **experimentos em source-space; nenhum plano, velocidade ou asset foi
aprovado**. A fonte MUGEN é `rascunho/entrada_bruta/ssf2_01_ryu.zip`, SHA-256
`d781b8d53d8b35789ed18985b7ad7ab9db977d220d9940b132999ed92323fb96`, uso local
de estudo e conversão; redistribuição continua sem liberação.

## Cobertura do conflito

O sweep completo `suzaku_static_source_view_sweep_v1.json` (SHA-256
`bd8060753db6c987f876070e5b7e4594cad0a4f1f10f561b99ca588367e8524e`) avaliou
as 449 posições inteiras da câmera e 32.184.320 amostras de pixels visíveis.
As faixas da viewport concentram o conflito assim:

| Linhas da viewport | Grupos de velocidade fonte visíveis no percurso | Leitura para a composição |
|---|---|---|
| 0–39 | BG0b `0.0`, BG2 `0.537946`, BG3 `0.671875` | Céu, castelo/muro e telhado se cruzam; três velocidades simultâneas. |
| 40–111 | BG0b `0.0`, BG1 `0.470982`, BG2 `0.537946`, BG3 `0.671875` | Quatro velocidades; é a zona que exige reautoria mais cuidadosa. |
| 112–175 | BG2 `0.537946`, BG3 `0.671875` | Já cabe em duas velocidades sem remapeamento no source-view estático. |
| 176–211 | BG4a, uma velocidade por linha de `0.792410` a `1.091517833` | Uma massa frontal; requer tabela H-scroll por linha, mas não tem disputa simultânea no sweep. |
| 212–223 | BG4b `1.102678` | Uma massa frontal por linha. Confirmar sobreposição com HUD no storyboard. |

Esses intervalos descrevem pixels vistos pelo compositor de fonte. Não definem
BG_A/B, prioridade por tile, paleta, linha de contato ou o resultado no VDP.
No Mega Drive o índice/código 0 do plano é transparente; deslocar layers pode
abrir regiões sem pixel de fallback e revelar o backdrop/void. As camadas
animadas BG5 e BGCtrl ainda não entram nesta comparação.

## Ferramenta de perfil explícito

Foi adicionado `mugen2sgdk_forge stage-plane-profile`, com uma especificação
JSON que associa layers MUGEN a velocidades-alvo. O comando exige sweep de
câmera em posições inteiras consecutivas, viewport coberta, total de amostras
coerente e no máximo dois speeds por scanline. Ele produz estimativa de pixels
remapeados, erro/frame e drift máximo desde a câmera-âncora; isso torna a
decisão autoral testável sem chamar o resultado de tilemap ou cena VDP.

Reprodução a partir da raiz do workspace:

```bash
PYTHONPATH=tools/mugen2sgdk_forge python3 -m mugen2sgdk_forge stage-plane-profile \
  "SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/rascunho/processado/stage_takeover/suzaku_static_source_view_sweep_v1.json" \
  --spec "SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/rascunho/processado/stage_takeover/suzaku_sky_anchor_castle_front_profile_v1.json" \
  --out "SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]/rascunho/processado/stage_takeover/suzaku_sky_anchor_castle_front_profile_v1_report.json"
```

Para a prévia PNG, passar o mesmo report a `stage-plane-preview` com o pacote
de origem correspondente, `--def ssf2-01-ryu.def`, `--sff ssf2-01-ryu.sff`, o
mesmo `--source-view`, um `--preview-dir` novo sob `rascunho/` e `--out` em
outro JSON. O renderizador verifica os hashes do pacote e do source-view.

Os arquivos `suzaku_*_profile_v1.json` são briefs de estudo. Os relatórios e
previews correspondentes ficam em `rascunho/processado/stage_takeover/` e são
hash-bound ao mesmo sweep/source. `stage-plane-preview` re-renderiza o
compositor de origem nos extremos e no centro; pixels de índice 0 que aparecem
por causa do deslocamento são lacunas do estudo, não transparência validada no
hardware.

## Dois perfis estudados

| Perfil | Regra de velocidade | Remapeamento | Erro médio estimado/frame | Drift máximo | Observação visual em 1x |
|---|---|---:|---:|---:|---|
| `castle_anchor_front_preserve` | BG0b e BG1 juntam-se a BG2 `0.537946`; BG3 fica `0.671875`; faixas inferiores permanecem com uma velocidade por linha. | 43,73% | 0,78917 px/amostra/frame | 120,4999 px | Castelo e telhado ficam mais fiéis entre si, mas o céu/lua desliza muito; a lua sai da composição no extremo esquerdo. Rejeitado como pronto. |
| `sky_anchor_castle_front_merge` | BG0b fica `0.0`; BG1/BG2/BG3 juntam-se a `0.671875`; faixas inferiores permanecem com uma velocidade por linha. | 28,57% | 0,17463 px/amostra/frame | 45,0000 px | Mantém o céu/lua ancorados e o grupo castelo/telhado unido, mas move o castelo mais rápido que a fonte; no extremo direito o preview abre pixels magenta/sem fallback. Requer nova arte/overlap. |

Ambos passam o limite matemático de dois speeds por linha. Nenhum resolve a
construção coerente dos planos: os números não representam paleta, tilemap,
prioridade, ResComp, VRAM, DMA, VBlank, composição jogável ou aprovação
estética. A alternativa A move 14.074.494 amostras visíveis; a B move
9.194.580. A troca deixa claro que minimizar o número de pixels alterados não
é suficiente para preservar o ponto focal e evitar vazios.

## Direção e storyboard para a próxima rodada

Foi criado o rascunho
`doc/mugen/suzaku_plane_storyboard_draft_2026_09_26.json`: BG_B preserva o céu
e a lua em 0; BG_A reúne castelo/muro/telhado em .671875 até y175 e conserva as
bandas frontais propostas abaixo. O rascunho fixa viewport 320x224, HUD, linha
dos pés e inícios dos lutadores, e registra riscos. Isso dá uma hipótese
revisável, não uma decisão visual nem uma composição final.

O próximo passo é revisar a posição da lua/castelo/telhado sob HUD e com fighters,
fechar ownership e prioridade por tile, áreas transparentes/overlap, linha do
horizonte e contato dos pés. Reautorizar como plates as massas que precisam
compartilhar velocidade — com bleed/fill sob telhado e silhuetas de arquitetura —
sem desenhar final art por código. Depois:

1. Revisar cada storyboard 1x nos extremos e na câmera central, incluindo
   fighters como oclusores de teste.
2. Medir tiles por viewport e por faixa com saída real do ResComp, conflitos de
   paleta por tile, uso de flip/prioridade e residência do pior quadro.
3. Comparar preload local e streaming somente depois de conhecer os tiles
   simultaneamente necessários; declarar cache contíguo, bytes por movimento,
   DMA por VBlank e fallback.
4. Integrar somente em candidato isolado após storyboard/arte e budget terem
   aceitação; implementar BG5/BGCtrl depois que a cena estática couber.
5. Provar câmera, reversão, push/corner, super, HUD, audio e a ROM exata em
   BlastEm. Aprovação artística continua humana e presa ao SHA.

Status de produção continua `pre-producao_medida`; nenhuma imagem foi promovida
para `res/`, nenhum runtime foi alterado e nenhuma captura BlastEm do Suzaku foi
feita nesta etapa.
