# Workflow: Premium Audio Pipeline

Pipeline criativo de audio para impedir que audio seja tratado apenas como "compila" ou "nao quebra". Audio de produto precisa de identidade, mix, prioridade de canais e teste auditivo em emulador.

## Principio

Audio final deve sustentar fantasia, gameplay e leitura de estado. Silencio pode ser intencional, mas precisa ser declarado. PSG procedural de lab nao substitui trilha autoral de produto sem decisao criativa explicita.

## Ordem canonica

| # | Etapa | Entrada minima | Saida minima | Gate |
|---|---|---|---|---|
| 1 | tema principal | GDD, pilares, ritmo de fase | `main_theme_brief` com BPM, escala, energia e instrumentacao | tema alinha com fantasia |
| 2 | leitmotifs | personagens, faccoes, boss | `leitmotif_map` por personagem/faccao/ameaca | repeticao tem funcao dramatica |
| 3 | stingers | eventos de gameplay | `stinger_catalog` para alerta, blackout, boss, morte, item | stinger nao cobre leitura critica |
| 4 | ambience | cena, clima, densidade | `ambience_bed_plan` por cena | ambience nao mascara SFX |
| 5 | banco SFX autoral | acoes, UI, impactos, ambiente | `sfx_bank_manifest` com fonte, hash e licenca | placeholder separado de final |
| 6 | prioridade de canais | driver, PCM/PSG/FM, eventos simultaneos | `channel_priority_map` | evento critico vence evento cosmetico |
| 7 | mix por cena | budget de canais, gameplay e HUD | `scene_mix_sheet` | estados de gameplay audiveis |
| 8 | cue timeline | roteiro, cutscene, boss, fase | `audio_cue_timeline` | cues tem trigger e teardown |
| 9 | teste auditivo em emulador | ROM vigente, input script ou roteiro | `audio_emulator_review` com BlastEm/BizHawk complementar | audio ok no hardware alvo |
| 10 | sync report | cena ritmica, eixo 16, cutscene ou impacto | `audio_sync_report` | obrigatorio quando timing define gameplay |

## Regras bloqueantes

- Tema principal obrigatorio para piloto de produto.
- Leitmotif obrigatorio para personagem/faccao/boss recorrente.
- Stingers obrigatorios para mudanca de estado com risco: alerta, blackout, boss, dano ou fase completa.
- Banco de SFX autoral deve diferenciar `placeholder`, `lab`, `licensed_reference` e `final`.
- Prioridade de canais deve existir antes de misturar chuva, menu, golpe, boss e UI.
- Cada cena precisa de mix por cena e cue timeline quando tiver narrativa, boss, cutscene ou mecanica ritmica.
- Teste auditivo em emulador e gate obrigatorio de entrega.
- `audio-sync report` e obrigatorio para eixo 16, cenas ritmicas, cutscenes temporizadas e setpieces de impacto.

## Artefatos esperados

- `main_theme_brief`
- `leitmotif_map`
- `stinger_catalog`
- `ambience_bed_plan`
- `sfx_bank_manifest`
- `channel_priority_map`
- `scene_mix_sheet`
- `audio_cue_timeline`
- `audio_emulator_review`
- `audio_sync_report` quando aplicavel

## Handoff

- Para runtime: entregar ownership de driver, canais, triggers, pause/resume e fade.
- Para QA: entregar ROM hash, roteiro de escuta, evidencia de emulador e lista de eventos testados.
- Para produto: registrar quais cues ainda sao placeholders e qual milestone os substitui.
