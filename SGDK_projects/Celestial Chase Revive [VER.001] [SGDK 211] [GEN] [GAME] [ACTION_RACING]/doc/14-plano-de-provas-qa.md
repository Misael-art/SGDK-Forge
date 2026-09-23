# 14 - Plano de Provas QA - Celestial Chase Revive

## Status

Plano de QA em especificacao. Nenhuma prova runtime do Revive existe ainda.

## Regra

O Revive so pode sair de `documentado` quando houver artefato real:

- build;
- ROM;
- BlastEm;
- logs;
- memoria/changelog sincronizados.

## Gates de Entrega

### Gate 1 - Build

Passa quando:

- `out/rom.bin` existe;
- build usa `sdk/sgdk-2.11` do workspace;
- build log sem erro.

### Gate 2 - Validacao Estrutural

Passa quando:

- `validate_project_context.ps1` passa;
- `validate_project_methodology.ps1` passa ou blockers runtime estao explicitamente fora do escopo atual;
- `validate_project_hygiene.ps1` passa;
- `validate_resources.ps1` passa quando houver recursos.
- track data, colisao, HUD, animacao, tuning, assets, boss, flow e build possuem contratos sem JSON invalido.

### Gate 3 - Boot no Emulador

Passa quando:

- BlastEm abre a ROM vigente;
- screenshot dedicada existe;
- `save.sram` existe quando o probe estiver ativo;
- `visual_vdp_dump.bin` existe quando o gate visual exigir;
- `emulator_session.json` aponta para hash da ROM vigente.

### Gate 4 - Gameplay Basico

Primeiro slice precisa provar:

- title/menu;
- logo/fonte/creditos em 320x224 nativo;
- track data do setor 1 carregado a partir de tabela, nao hardcode solto;
- colisao de Lio, pickups e hazards provada por fixtures;
- HUD nas coordenadas de `doc/hud_layout_contract.json`;
- animacao de Lio alinhada a hitbox;
- cutscene opening;
- entrada na corrida;
- trocar faixa;
- saltar;
- coletar Lumen;
- usar Pulse;
- tomar dano;
- ir para resultado;
- reiniciar ou voltar ao menu.

### Gate 4B - Coesao Criativa AAA

Passa quando a experiencia provar, com captura ou metrica runtime:

- Mestre Perseguidor visivel desde o Sector 01 e crescendo por setor/Pressure conforme `doc/pursuer_presence_contract.json`;
- Lumen carregado aumenta Pressure conforme `doc/lumen_pressure_economy_contract.json`;
- cada setor possui regra mecanica propria conforme `doc/sector_mechanic_identity_contract.json`;
- `shattered_lane_gauntlet` ocorre na transicao Sector 03 -> Sector 04 e deixa apenas uma faixa segura por 180 frames;
- musica reage a Pressure, Lumen e boss phase conforme `doc/reactive_music_gameplay_contract.json`;
- resultado calcula estrelas e desbloqueios conforme `doc/replayability_score_contract.json`;
- nenhuma dessas provas usa apenas texto estatico, placeholder sem comportamento ou contador debug como substituto perceptual.

### Gate 5 - Performance

Passa quando:

- 60 FPS NTSC constante no intervalo alvo;
- `over_budget_frames=0`;
- `cpu_load_max` dentro do limite do projeto;
- scanline sprites <= 20 e alvo <= 18.

### Gate 6 - Audio

Passa quando:

- recursos declarados em `.res` passam `validate_audio.ps1`;
- SFX criticos audiveis nao mascaram telegraphs;
- audio state map reflete intro, corrida, upgrade, boss e resultado;
- camadas reativas entram e saem sem clique audivel, sem reiniciar a musica base e sem esconder alertas de perigo.

### Gate 7 - Memoria Operacional

Passa quando:

- `doc/10-memory-bank.md` atualizado;
- `doc/changelog/changelog.md` atualizado;
- freshness sem stale bloqueante;
- scene closeout executado ou justificativa conservadora registrada.

## Evidencia Minima por Cena

| Cena | Screenshot | SRAM | VDP Dump | Runtime Metrics | Regressao |
|---|---|---|---|---|---|
| title_menu | sim | opcional | se visual delivery | sim | sim |
| branding_sigil | sim | opcional | se visual delivery | sim | sim |
| credits_roll | sim | opcional | se UI final | sim | sim |
| opening_cutscene | sim | sim | sim para entrega | sim | sim |
| sector_01 | sim | sim | sim | sim | sim |
| upgrade | sim | opcional | se UI final | sim | sim |
| boss_approach | sim | sim | sim | sim | sim |
| final_boss | sim | sim | sim | sim | sim |
| pause_overlay | sim | opcional | se UI final | sim | sim |
| game_over | sim | opcional | se UI final | sim | sim |
| continue | sim | opcional | se UI final | sim | sim |

## Perceptual Motion Gate

Quando `critical_motion` virar required:

- motion GIF/WebP;
- aprovacao humana;
- `perceptual_check.fluidez > 0`;
- `perceptual_check.leitura > 0`;
- `perceptual_check.naturalidade > 0`;
- `perceptual_check.impacto > 0`;
- screenshot dedicado;
- SRAM fresca;
- VDP dump.

## Visual Gate

Bloqueia se:

- asset critico estiver `placeholder`, `needs_review`, `debug_lab` ou `benchmark-derived`;
- fonte premium nao estiver em `data/source_art`;
- logo nao tiver `brand_identity_manifest`;
- menu/creditos nao tiverem contrato de superficie pixel;
- HUD nao tiver wireframe e contrato de coordenadas;
- sprites criticos nao tiverem contrato de animacao/hitbox;
- boss nao tiver padroes de ataque e weakpoints testaveis;
- setor jogavel nao tiver track data autorado;
- setor jogavel nao tiver regra mecanica propria documentada e testavel;
- perseguidor nao estiver visualmente presente antes do boss final;
- Lumen continuar sendo apenas moeda sem risco sistemico;
- momento assinatura nao tiver contrato de runtime e evidencia planejada;
- build nao usar o wrapper central;
- clone risk nao medido;
- HUD parecer debug;
- screenshot tiver baixa informacao visual;
- dump VDP ausente em entrega visual.

## Provas Criativas Especificas

| Prova | Contrato | Evidencia minima |
|---|---|---|
| Presenca do perseguidor | `doc/pursuer_presence_contract.json` | 3 capturas por Pressure band + log de escala/distancia |
| Lumen como risco | `doc/lumen_pressure_economy_contract.json` | log de Pressure com 0, 20, 40 e 60 Lumen carregado |
| Identidade de setores | `doc/sector_mechanic_identity_contract.json` | fixture por setor provando sua regra exclusiva |
| Momento assinatura | `doc/signature_setpiece_contract.json` | captura BlastEm + metricas de lane mask e debris |
| Musica reativa | `doc/reactive_music_gameplay_contract.json` | log de transicoes musicais e checagem auditiva humana |
| Replay/mastery | `doc/replayability_score_contract.json` | tela de resultado com estrelas, shards e unlock flags |

## Status Atual dos Eixos

- build: `nao_testado`;
- validation_report: `nao_testado`;
- boot_emulador: `nao_testado`;
- gameplay_basico: `nao_testado`;
- performance: `nao_medido`;
- audio: `nao_testado`;
- memoria operacional: `documentada`;
- ready_for_aaa: `false`.

## Primeiro Closeout Planejado

Sequencia:

1. `preflight_host.ps1`;
2. build pelo wrapper;
3. `validate_resources.ps1`;
4. captura BlastEm;
5. scene regression;
6. freshness audit;
7. scene closeout gate;
8. atualizar memoria/changelog.
