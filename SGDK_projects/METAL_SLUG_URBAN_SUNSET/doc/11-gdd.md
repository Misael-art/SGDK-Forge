# 11 - Game Design Document — METAL_SLUG_URBAN_SUNSET

## Visao

METAL_SLUG_URBAN_SUNSET e um slice de traducao visual Mega Drive orientado por producao real. O objetivo nao e apenas exibir uma arte bonita, mas demonstrar como uma cena editorial rica pode virar runtime SGDK valido, com leitura forte, profundidade clara e evidencias rastreaveis em emulador.

Este projeto nao e um mockup de Photoshop nem um benchmark sem disciplina. Ele existe para treinar a passagem correta entre curadoria semantica, budget de hardware, montagem de planos BG_A/B, prioridades visuais e gate canônico do workspace.

## Mecanicas core

- Scroll lateral com leitura de rua destruida como plano jogavel principal.
- Profundidade percebida por parallax real, com BG_B subdividido em ceu e skyline e BG_A carregando a arquitetura de maior detalhe.
- Overlay de prova e captura de evidencia tecnica sem contaminar a composicao cenica.

## Progressao

- A progressao do projeto ocorre em etapas de producao: curadoria da referencia, prova visual estavel, retomada dinamica, medicao de hardware e gate final em emulador.
- A progressao da cena acontece por ganho de profundidade: primeiro a composicao correta, depois o parallax de fundo e por ultimo a aprovacao ou fusao controlada do foreground.

## Regras e limites

- A cena final deve respeitar a topologia real do Mega Drive: dois planos scrollaveis reais, WINDOW apenas como overlay e nada de terceiro plano fullscreen inventado.
- Toda decisao visual precisa justificar paleta, tiles, prioridade e custo de runtime; qualidade sem prova tecnica nao conta como concluida.
- O foreground nao entra como plano independente por intuicao; ele so entra se SAT, VRAM e leitura em ROM confirmarem.
- O que nao e escopo desta fase: combate completo, IA de inimigos, audio final, HUD de jogo completo e qualquer expansao fora do slice urbano ao por do sol.

## Escopo atual

- Slice unico da cena urbana Metal Slug Urban Sunset, com assets elite gerados, runtime estatico implementado e estrategia formal para retomar dinamismo via parallax e foreground controlado.
- Fora do escopo atual: transformar o caso em fase jogavel completa, adicionar sistema de personagens ou declarar validacao total sem os 7 eixos de QA.
