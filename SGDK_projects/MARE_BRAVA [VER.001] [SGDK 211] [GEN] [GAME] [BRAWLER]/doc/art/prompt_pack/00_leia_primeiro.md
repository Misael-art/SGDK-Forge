# Prompt Pack MARE_BRAVA — Leia primeiro

Estes documentos contêm prompts prontos para você gerar os **concepts** (Etapa A do
`doc/art/art_generation_brief.md`) num modelo de imagem capaz (Midjourney, DALL-E,
Imagen, Flux, SDXL bem tunado, etc.). O agente desta sessão não gera raster — por
isso os prompts são específicos o bastante para produzir resultado utilizável de
primeira, com critérios de aceite para você mesmo filtrar.

## Regras de uso (valem para todos os prompts)

1. **Escopo**: tudo aqui é `concept_art`. NUNCA use a saída como sprite final,
   sheet de animação ou asset de `res/`. O destino é servir de referência para o
   passo autoral (lineart 1px → key poses → strips).
2. **Idioma**: os prompts estão em inglês (modelos de imagem respondem melhor).
   Não traduza; ajuste apenas os parâmetros do seu modelo.
3. **Variações**: gere 4 variações por prompt e escolha 1-2 pelas regras de aceite
   do próprio doc. Guarde as descartadas numa subpasta `descartes/`.
4. **Onde salvar** (obrigatório, higiene do projeto):
   `data/source_art/concept/<asset_id>/<asset_id>_vNN.png`
   Ex.: `data/source_art/concept/taina_model_sheet/taina_model_sheet_v01.png`
5. **Registro**: depois de salvar, me avise na sessão — eu atualizo o
   `premium_source_manifest` e preparo o contact sheet 320x224 para a sua
   ratificação da direção de arte.
6. **Negative prompt universal** (acrescente sempre, se o modelo suportar):
   `photorealism, 3D render, soft airbrush shading, gradient background, motion blur,
   watermark, text artifacts, extra limbs, copyrighted characters, Street Fighter,
   Streets of Rage, Final Fight, Capcom, SEGA logos`
7. **Anti-clone**: nenhum prompt pode citar personagem, jogo ou artista real como
   fonte visual. Se o resultado "parecer o Axel/Guy", descarte — o
   `style_drift_policy` proíbe.

## Paleta âncora (use os hex no prompt quando o modelo aceitar)

| Domínio | Hex âncora |
|---|---|
| Cenário (entardecer) | #E8A05C areia/sol, #5C2E4A sombra roxa, #3A6B7A mar, #FFD98A luz |
| Heroína | #FF5533 laranja, #2E1F3A escuro, #F2C29A pele, #1A6B5A verde |
| Inimigos | #4A5C8A azul, #CC2244 vermelho, #8A6B4A couro, #2A2A3A escuro |
| HUD/espuma | #F2F2E0 claro, #CC2244 perigo, #111122 fundo |

## Ordem recomendada de geração

1. `01_taina_model_sheet.md` (destrava ratificação + scale contract)
2. `03_cais_world_concept.md` (destrava streaming/tileset + moodboard real)
3. `02_cria_estivador_model_sheets.md`
4. `04_logo_mare_brava.md`
5. `05_hud_fx_studies.md`
