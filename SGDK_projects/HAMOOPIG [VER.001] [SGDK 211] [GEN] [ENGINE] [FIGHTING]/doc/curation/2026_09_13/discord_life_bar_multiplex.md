# Orientação do desenvolvedor original — life bar compacta

Data da investigação: 13/09/2026

## Fonte

Esta nota registra orientação observada nas conversas do Discord do RETRODEVBR, atribuída ao Rheo (autor original da engine/estudo Fatal Fury), e não uma decisão inventada pelo projeto.

- Captura fornecida pelo usuário: `/run/user/1000/codex-desktop/tmp/codex-clipboard-9980088b-6e64-4c6f-8c06-ab0c7bf8b9b2.png`.
- Canal visualizado: [ff-rheo-bout](https://discord.com/channels/998549684530446448/1043146630871916575).
- Canais complementares consultados por busca interna: [tutoriais](https://discord.com/channels/998549684530446448/1015983874209222778), [fatal-fury-one](https://discord.com/channels/998549684530446448/1024678191492759552), [kunio](https://discord.com/channels/998549684530446448/1036755630163234856), [street-fighter-1](https://discord.com/channels/998549684530446448/1101912425160257536), [hamoopig](https://discord.com/channels/998549684530446448/998577800405586030), [blaze-engine](https://discord.com/channels/998549684530446448/998577914666832003), [sd89-engine](https://discord.com/channels/998549684530446448/1145347666855866449), [ssf2-omega](https://discord.com/channels/998549684530446448/1208759771465916496), [kofmd](https://discord.com/channels/998549684530446448/1044357112089825396), [importantes](https://discord.com/channels/998549684530446448/998597324311896205), [musica](https://discord.com/channels/998549684530446448/1000113702420357132), [canal-1043146630871916575](https://discord.com/channels/998549684530446448/1043146630871916575), [canal-1475844016284106845](https://discord.com/channels/998549684530446448/1475844016284106845), [canal-1489370929447436370](https://discord.com/channels/998549684530446448/1489370929447436370), [canal-1512536342532198531](https://discord.com/channels/998549684530446448/1512536342532198531).

## Regra técnica extraída

Na captura de 20/03/2026, Rheo responde à proposta de barras com larguras diferentes: essa forma exigiria mais memória de vídeo. A prática recomendada é montar a barra com células de largura fixa, pequenas e repetíveis, organizadas em sequência. A mesma célula pode ser referenciada por vários sprites (ou por várias entradas do tilemap), enquanto a quantidade visível é controlada por estado de vida.

Consequências para SGDK/Mega Drive:

1. Uma célula fixa de 16×8 usa dois tiles (64 bytes de padrão); oito células da barra reutilizam o mesmo par em vez de reservar uma imagem de 128×16 com 32 tiles por jogador.
2. O primeiro sprite recebe alocação/upload automáticos; as demais instâncias recebem o mesmo índice de tile e não fazem upload duplicado. Como a defragmentação pode mover o primeiro bloco, o HUD mantém as instâncias fixas durante a cena e só libera tudo no reset.
3. Larguras não padronizadas (por exemplo, trechos 4, 12 ou 20 px) quebram a reutilização e fazem o ResComp reservar tiles preenchidos até o tamanho de sprite suportado.
4. A barra pode ser desenhada no SAT, sobre o cenário, sem ativar a WINDOW inteira. Assim o plano de fundo continua visível atrás dos trechos vazios e desaparece a faixa preta superior.
5. O custo desloca-se de VRAM/DMA para entradas SAT/scanlines; por isso a implementação precisa medir sprites ativos e máximo por linha. Não é permitido promover a técnica sem essa medição.

## Aplicação no HAMOOPIG

O HUD foi convertido para um protótipo de células fixas:

- `res/sprite/hud/energy_yellow_segment.png`: célula autorada 16×8, derivada do centro repetível da barra existente.
- `spr_hud_energy_segment`: dois tiles carregados uma vez e compartilhados por 16 instâncias (8 por jogador); o pior caso da linha fica em 16 sprites, dentro do limite físico do Mega Drive.
- `spr_hud_clock_digit`: atlas de dígitos usado por dois sprites, com o atlas VRAM compartilhado.
- `src/hud.c`: vida 0–96 quantizada em oito células de 16 px; P1 consome da esquerda para a direita e P2 da direita para a esquerda; células vazias ficam ocultas.
- `src/init.c`: a faixa WINDOW deixou de ser usada para barras/relógio; somente a fonte de mensagem e uma célula preta temporária permanecem no plano A.

## Critérios de validação

- Build SGDK 2.11 sem erro.
- Captura no emulador mostrando cenário até o topo, barras sem retângulo preto e relógio legível.
- Probe HPRB: `max_active` ≤ 80, `max_scanline` ≤ 20 e DMA worst-frame medido; comparar com o baseline de 10.064 bytes.
- Testar energia cheia, parcial e zero para os dois jogadores e confirmar que o P2 zera completamente.
- Se SAT/scanline ou DMA piorarem, manter a técnica documentada, mas reverter a promoção e investigar uma variante em tilemap transparente/duas células por sprite.

Status: implementado, buildado e capturado em emulador; `validado_budget=false` global porque o HPRB curto ainda não substitui a medição de pior quadro de combate. Variante final: ROM `f001418a654fc0aaf4a3c53cc4eb9f62470ac0f747c0dd2b3ba2b0c86453ec0b`, captura `visual_ko_20260914T030007Z`, HPRB `hprb_probe_report_20260914_life_bar_final.json`.
