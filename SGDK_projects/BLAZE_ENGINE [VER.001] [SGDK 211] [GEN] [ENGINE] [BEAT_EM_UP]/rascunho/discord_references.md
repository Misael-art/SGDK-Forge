# Referências externas pendentes

- https://discord.com/channels/998549684530446448/998577914666832003
- https://discord.com/channels/998549684530446448/1291714121548435567

Estado em 2026-09-20: os canais foram lidos pela sessão autenticada do Chrome.

## Evidência observada

- `#blaze-engine`: conversa sobre ports de beat 'em up para Mega Drive/Genesis, referência a TMNT Arcade Port com introdução e gerenciamento de cenas, e discussão de jogos/releituras. Não há uma lista objetiva de patches para o BLAZE_ENGINE.
- `#dev-tools`: publicação do `SIMPLE PAL EDITOR`, ferramenta HTML5/ZIP para reordenar cores de paleta por arrastar e soltar. Não há uma paleta-alvo nem instrução de quais assets do BLAZE_ENGINE devem ser alterados.

## Decisão de escopo

As referências foram registradas, mas não foi feita transformação visual arbitrária. A migração aplicou apenas correções reproduzíveis no SGDK 2.11 e no build: assinatura de `VDP_showFPS`, capacidade de `EnemyDEF.dataAnim` e redução de fragmentação de sprites oversized. O uso do editor de paleta fica pendente de uma paleta-alvo/asset explicitamente indicado.
