# Memória operacional — BLAZE_ENGINE Beat 'em Up SGDK 2.11

<!-- SGDK GENERATED STATUS START -->
ROM vigente: `out/rom.bin` SHA-256 `c8dbc5a3922f866de15b17b8e16a8958c14458b7a968b4e9881a3ccd19b4dd2b`; status técnico observado: bundle BlastEm selado, AAA não promovido.
<!-- SGDK GENERATED STATUS END -->

## Estado atual

- 2026-09-20: fonte copiada de `[ENGINE]/BLAZE_ENGINE` para este projeto, preservando a fonte original.
- Contexto: `technical_demo`, teto `prototype`.
- Gênero corrigido: `beat 'em up` / brawler de ação side-scrolling; não é fighting game de arena.
- 2026-09-21: diretório, manifesto e documentação renomeados para o gênero correto `[BEAT_EM_UP]`; a ROM e o bundle BlastEm foram recapturados sem alteração do binário.
- SGDK canônico: `sdk/sgdk-2.11` do workspace.
- Fonte de runtime: `src/main.c`; recursos: `res/gfx.res`, `res/sprite.res`, `res/sound.res`.
- A fonte já usava `SPR_addSpriteExSafe` e flags presentes no header SGDK 2.11; isso será confirmado pelo build, não presumido.
- Corrigida a chamada `VDP_showFPS` para a assinatura SGDK 2.11 `(asFloat, x, y)`, mantendo a exibição inteira em `(1,2)` quando `show_debug` está ativo.
- Ampliado `EnemyDEF.dataAnim` de 10 para 70 entradas: o código inicializa e consulta índices até 24; a alteração elimina o overflow estrutural reportado pelo GCC 13.2.0.
- Build canônico SGDK 2.11 concluído em 2026-09-20; ROM vigente: `out/rom.bin`, 2.490.368 bytes, SHA-256 `c8dbc5a3922f866de15b17b8e16a8958c14458b7a968b4e9881a3ccd19b4dd2b`.
- A ROM agora integra `src/runtime_probe.c`: captura VLAB v1, CRAM, registradores VDP, CPU/jitter, sprites por scanline, sprites ativos e intervalos reais de `VDP_loadTileSet`.
- `doc/vram_residency_report.json` registra a residência medida da cena 8: `bgb_credits` ocupa 475 tiles a partir do tile 1 e `bga_credits` ocupa 332 tiles a partir do tile 501; a prova é local à cena e vinculada ao hash da ROM.
- BlastEm selou a sessão `blastem-linux-20260921T015549Z-936914` na cena 8: 60.6 fps no título, 661 amostras, CPU máxima 11%, 0 sprites por scanline na tela de créditos e ranges VRAM `[1,475]`/`[501,332]`. Bundle canônico está íntegro e ligado ao hash atual.
- Validação de recursos: os seis erros de pressão de sprite foram eliminados; o budget de tiles carregados por código agora tem evidência VDP real. O projeto continua `technical_demo` com teto `prototype`.
- Áudio: `validate_audio.ps1` passou para 26 recursos e 6,3% do budget de ROM; os avisos de fontes estéreo permanecem registrados. A captura BlastEm também gerou áudio em disco na mesma sessão.
- Proveniência: `doc/asset_provenance_manifest.json` declara os 340 símbolos como `placeholder`, com origem legada não verificada; isso remove o bloqueio de declaração sem promover os assets a finais.
- Últimas validações: contexto, metodologia, higiene, PRD, proveniência, sincronização documental e bundle BlastEm passaram; freshness foi atualizado após esta medição; performance sustentada, gameplay de combate e barra visual AAA continuam não provados.

## Claims não provados

- Há ROM nova, bundle BlastEm selado, métricas VDP/runtime e áudio objetivo; isso não prova performance sustentada, game feel ou gameplay de combate.
- Os dois canais Discord foram lidos pela sessão autenticada do Chrome; não havia patch textual objetivo para o engine. A ferramenta `SIMPLE PAL EDITOR` foi registrada, mas não aplicada sem paleta-alvo.
- O projeto não é um jogo AAA final e não possui claim `ready_for_aaa`.

## Próxima ação causal

Próximo passo causal: executar uma captura dedicada da cena 11 com bootstrap de gameplay e revisar os assets placeholder com seus autores; não elevar o claim até existir evidência de combate, áudio em contexto e performance sustentada.
