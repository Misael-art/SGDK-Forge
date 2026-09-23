# 17 - Audio Design - Celestial Chase Revive

## Status

Direcao sonora especificada, sem assets de audio finais.

## Identidade Sonora

FM brilhante e ritmico, baixo pulsante e PSG usado como brilho celeste. A musica deve acelerar a percepcao de corrida sem mascarar alertas.

Tese de audio: musica e telemetria emocional. O jogador deve perceber Pressure, Lumen carregado e proximidade do Mestre Perseguidor antes mesmo de olhar para a HUD.

## Estados Musicais

- `title_prayer`: motivo lento do Farol-Matriz.
- `opening_crack`: drone + stingers para cutscene.
- `race_intro`: pulso claro, pouca densidade.
- `race_pressure`: baixo mais agressivo e arpejos.
- `race_pressure_plus`: PSG percussivo e motivo do perseguidor mais presente.
- `race_climax`: bateria/ruido mais presente.
- `upgrade_beacon`: repouso curto e timbre luminoso.
- `boss_approach`: tema do Mestre Perseguidor entra em ostinato.
- `final_boss`: camadas por fase.
- `victory`: resolucao luminosa.
- `failure`: queda curta, sem humilhar o jogador.

## Camadas Reativas

Contrato: `doc/reactive_music_gameplay_contract.json`.

| Estado | Pressure | FM | PSG | DAC/PCM | Funcao |
|---|---:|---|---|---|---|
| `race_intro` | 0-24 | melodia + baixo limpo | brilho leve | off | flow |
| `race_pressure` | 25-49 | contralinha + baixo mais presente | percussao leve | off | perseguicao percebida |
| `race_pressure_plus` | 50-74 | ostinato forte | pulso rapido | hits opcionais | tensao |
| `race_climax` | 75-99 | harmonia urgente | pulso denso | beat pesado se couber | panico controlado |
| `caught_or_boss_approach` | 100 | motivo do boss | alarme | impacto | falha/transicao |

Lumen tambem interfere: acima de 40, o brilho sonoro passa a responder como isca; acima de 60, o Perseguidor deve responder com cue curta, sem mascarar telegraph.

## SFX Prioritarios

1. Dano/impacto.
2. Telegraph de perigo.
3. Pulse ready/Pulse use.
4. Boss weak point.
5. Coleta Lumen.
6. Menu/confirmacao.
7. Texto typewriter.

## Audio Cue Map

| Evento | Cue | Funcao |
|---|---|---|
| Farol racha | grave FM + PSG shard | catalizador |
| Lumen coletado | brilho curto | recompensa |
| Pulse cheio | arpejo ascendente | prontidao |
| Dano | impacto seco + duck curto | consequencia |
| Upgrade escolhido | acorde limpo | evolucao |
| Boss aparece | stinger com silencio apos | escala |
| Weak point aberto | tom agudo repetido | janela |
| Lumen cruza 40 | shimmer + horn distante | risco de carregar luz |
| Lumen cruza 60 | shimmer intenso + breath curto | perigo sistemico |
| Shattered lane impact | hoof stinger + duck de musica | momento assinatura |

## Canal e Concorrencia

O projeto deve usar `audio_architecture_card.json` para travar ownership antes de runtime. SFX de dano e telegraph vencem typewriter e menu.

SFX de dano e telegraph tambem vencem camadas reativas de musica. Se XGM2 nao permitir mistura fina por budget, usar transicoes entre estados pre-renderizados em fronteira de compasso.

## Recuos

- Se XGM2/PCM competir com performance, reduzir samples e manter FM/PSG.
- Se typewriter cansar, usar SFX por palavra ou pontuacao, nao por glifo.
- Se boss cue mascarar telegraph, reduzir canal de musica antes de reduzir SFX critico.
- Se PCM/DAC custar demais, manter FM+PSG e preservar a diferenca perceptiva entre Pressure baixo, medio e alto.
- Se layer reativo causar churn demais, trocar por stingers e estados XGM2 discretos.
