# Prompt Pack MARE_BRAVA — Leia primeiro

Estes documentos contêm prompts prontos para você gerar os **concepts** (Etapa A do
`doc/art/art_generation_brief.md`) num modelo de imagem capaz (Midjourney, DALL-E,
Imagen, Flux, SDXL bem tunado, etc.). O agente desta sessão não gera raster — por
isso os prompts são específicos o bastante para produzir resultado utilizável de
primeira, com critérios de aceite para você mesmo filtrar.

Use tambem o prompt mestre persistente:

- `doc/art/prompt_pack/06_image_agent_master_prompt.md`
- `doc/art/authorial_line_style_contract.json`

Ele consolida o contrato do agente de imagem: gerar materia-prima premium
organizada, nunca level pronto, sprite final, tilemap final ou asset de `res/`.
O contrato de traco autoral impede que o modelo gere arte "arcade" correta mas
anonima.

## Regras de uso (valem para todos os prompts)

1. **Escopo**: tudo aqui é `concept_art` / `source_candidate`. NUNCA use a saída
   como sprite final, sheet de animação, tilemap final, background final de
   scroll ou asset de `res/`. O destino é servir de referência para o passo
   autoral (lineart 1px → key poses → strips) ou para a montagem modular do
   CAIS_01 pelo agente canônico.
2. **Idioma**: os prompts estão em inglês (modelos de imagem respondem melhor).
   Não traduza; ajuste apenas os parâmetros do seu modelo.
3. **Variações**: gere 4 variações por prompt e escolha 1-2 pelas regras de aceite
   do próprio doc. Guarde as descartadas numa subpasta `descartes/`.
4. **Onde salvar** (obrigatório, higiene do projeto):
   `data/source_art/concept/<asset_id>/<asset_id>_vNN.png`
   Ex.: `data/source_art/concept/taina_model_sheet/taina_model_sheet_v01.png`
5. **Registro**: para cada imagem salva, registre prompt final usado,
   modelo/ferramenta, seed/config quando houver, motivo de aceite/rejeição,
   papel no gameplay e status `source_candidate`. Depois de salvar, me avise na
   sessão — eu atualizo o `premium_source_manifest` e preparo o contact sheet
   320x224 para a sua ratificação da direção de arte.
6. **Negative prompt universal** (acrescente sempre, se o modelo suportar):
   `photorealism, 3D render, soft airbrush shading, gradient background, motion blur,
   watermark, text artifacts, extra limbs, extra fingers, duplicated arms, broken
   anatomy, copyrighted characters, game logo trade dress, chrome bevel, glass UI,
   soft glow, painterly blur, noisy micro detail, realistic 7-head fashion anatomy`
7. **Anti-clone**: nenhum prompt pode citar personagem, jogo ou artista real como
   fonte visual. Se o resultado "parecer o Axel/Guy", descarte — o
   `style_drift_policy` proíbe.
8. **Não sobrescrever**: nunca sobrescreva arquivo existente; incremente `vNN`.
9. **Status proibidos**: não use `ready_for_conversion`,
   `ready_for_res_promotion`, `ready_for_aaa`, `sprite_final`, `tilemap_final` ou
   `production_tilemap_source` para qualquer saída desta etapa.
10. **Relatórios obrigatórios**: entregue `doc/art/prompt_revision_report.md` e
    `doc/art/asset_acceptance_report.json` ao final da curadoria.
11. **Traco autoral obrigatório**: todo prompt precisa declarar pelo menos um
    item de `line_signature`, `silhouette_hooks`, `face_grammar`,
    `hand_foot_grammar`, `costume_asymmetry`, `material_marks` ou
    `environment_marks` do contrato. Se isso faltar, o prompt é inválido por
    `authorial_line_contract_missing`.

## Contrato de traco autoral — resumo operacional

Use sempre:

- contorno escuro expressivo, variando por importância de silhueta; nunca
  outline preto uniforme em tudo;
- linhas internas curtas em cunha, não ruído de sketch;
- sombras duras em triângulos/trapézios que depois possam virar clusters de
  pixel;
- mãos, pés, mandíbula, sobrancelha, faixa, corda, rede, madeira e espuma como
  marcas gráficas deliberadas;
- personagens com 3 ganchos de silhueta em preto puro;
- cenario com marcas materiais de Porto Bravo, não props genéricos.

Bloqueie ou regere quando aparecer:

- rosto anime genérico;
- corpo atlético intercambiável;
- roupa de brawler anônima;
- props vetoriais sem desenho manual;
- cenário bonito que poderia ser qualquer porto;
- madeira, corda, rede ou água sem linguagem de linha.

## Paleta âncora (use os hex no prompt quando o modelo aceitar)

| Domínio | Hex âncora |
|---|---|
| Cenário (entardecer) | #E8A05C areia/sol, #5C2E4A sombra roxa, #3A6B7A mar, #FFD98A luz |
| Heroína | #FF5533 laranja, #2E1F3A escuro, #F2C29A pele, #1A6B5A verde |
| Inimigos | #4A5C8A azul, #CC2244 vermelho, #8A6B4A couro, #2A2A3A escuro |
| HUD/espuma | #F2F2E0 claro, #CC2244 perigo, #111122 fundo |

## Ordem recomendada de geração

1. `01_taina_model_sheet.md` (identidade e poses da heroína)
2. `02_cria_estivador_model_sheets.md` (inimigos + teste conjunto de silhueta)
3. `03_cais_world_concept.md` (dock_scene_kit modular; não panorama)
4. `04_logo_mare_brava.md`
5. `05_hud_fx_studies.md`

## Saída final esperada

- imagens em `data/source_art/concept/<asset_id>/<asset_id>_vNN.png`;
- descartes em `data/source_art/concept/<asset_id>/descartes/`;
- `doc/art/prompt_revision_report.md`;
- `doc/art/asset_acceptance_report.json`;
- lista explícita de aceitos, descartados, pendentes e gaps;
- declaração: tudo permanece `source_candidate`; nada está pronto para `res/`,
  ROM, build ou AAA.
