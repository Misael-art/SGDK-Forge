# Proposta visual P2 — masters HD arcade

Estado: `proposal_only_human_review_required`
Método: geração integrada de imagem
Data: 2026-08-06

Esta pasta é isolada de `data/source_art/`, `res/` e do pipeline de ROM. Contém
masters raster HD para avaliação humana da direção: pixel art arcade dos anos
90, contornos limpos, cores sólidas, clusters definidos e ausência de blur,
gradiente e sujeira de compressão.

## Limites

- A preservação idêntica do personagem do conceito aprovado foi recusada pelo
  gerador.
- Para não alegar fidelidade inexistente, os masters usam uma identidade nova e
  original: Lumo, Bramble Hopper e Elder Bramble.
- Eles avaliam acabamento, staging, leitura e linguagem de animação; não são
  uma substituição aprovada do personagem ou IP original.
- Não converter, fatiar, quantizar, integrar em `res/` ou usar em ROM sem nova
  decisão humana explícita.

## Entregas

| Área | Arquivo | Conteúdo |
|---|---|---|
| A1 | `A1_hero/lumo_hd_pose_master_v1.png` | oito key poses do protagonista original |
| A2 | `A2_enemy/bramble_hopper_hd_pose_master_v1.png` | três poses do inimigo original |
| B | `B_stage/orchard_valley_hd_scene_master_v1.png` | cenário jogável de pomar |
| C | `C_boss/elder_bramble_hd_pose_master_v1.png` | quatro poses do chefe original |
| D | `D_ability_fx/arcade_fx_hd_master_v1.png` | cinco famílias de FX |
| E | `E_title_scene/orchard_title_scene_hd_master_v1.png` | cenário de título com placa sem texto |

Veja `prompts.md` e `proposal_manifest.json` para rastreabilidade.
