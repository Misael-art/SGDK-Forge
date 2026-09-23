# SGDK_projects

Projetos SGDK ativos e referências usadas pelas ferramentas do workspace. Projetos parados ou
experimentais foram arquivados (com histórico) em `archives/2026-09-23/SGDK_projects/` — veja
`archives/README.md`.

## Projetos ativos

| Projeto | Papel |
| --- | --- |
| `HAMOOPIG [...] [ENGINE] [FIGHTING]` | Engine de luta; contratos HAMOOPIG e sonda HAPE; referência do RetroDevStudio |
| `TAIKETSU ULTRA HERO GENESIS [...] [ENGINE] [FIGHTING]` | Engine de luta |
| `TAIKETSU ULTRA REBIRTH [...] [GAME] [FIGHTING]` | Jogo de luta em produção |
| `Mugenesis_Demo [...] [GAME] [FIGHTING]` | Demo do conversor mugen2sgdk (Ken) |
| `BLAZE_ENGINE [...] [ENGINE] [BEAT_EM_UP]` | Engine beat'em up |
| `SHADOWDANCER_REVISITADO [...] [ENGINE] [BEAT_EM_UP]` | Engine beat'em up |
| `KIRBY_FAN GAME CLOUDE [...] [GEN] [GAME] [ACTION_PLATFORMER]` | Plataforma de ação (linha canônica do Kirby) |

## Referências de ferramentas (não arquivar sem atualizar as ferramentas)

| Projeto | Usado por |
| --- | --- |
| `FORGE_REFERENCE [...] [LAB] [TECHDEMO]` | `tools/sgdk_wrapper/ci/run_golden_validate.ps1`, `run_reference_e2e.py` (projeto golden) |
| `SMOKE_TEST [...] [LAB]` | Fixture de build do wrapper |
| `Celestial Chase visual benchmark [...] [LAB] [TECHDEMO]` | `tools/audio-tools/vgm_to_xgm2.py`, `ci/test_audio_tools.py` |
| `Celestial Chase Revive [...] [GAME] [ACTION_RACING]` | `ci/test_celestial_damage_animation.py`, testes de curadoria canônica |
| `_agent_laboratory` | `forge_art` (modo `all_applicable` só roda dentro deste laboratório) |

Use `new-project.bat <nome>` para criar novos projetos canônicos aqui.
