# Changelog — BLAZE_ENGINE Beat 'em Up SGDK 2.11

## 2026-09-20

- Corrigida a identidade do projeto: gênero `beat 'em up`/brawler side-scrolling; renomeado o diretório e os manifests de `[FIGHTING]` para `[BEAT_EM_UP]`. O termo fighting game de arena não se aplica a este projeto.
- Recapturada a mesma ROM no BlastEm após a renomeação para atualizar os caminhos absolutos da evidência; SHA-256 permanece `c8dbc5a3922f866de15b17b8e16a8958c14458b7a968b4e9881a3ccd19b4dd2b`.

- Criado projeto técnico em `SGDK_projects/` a partir de `[ENGINE]/BLAZE_ENGINE`.
- Mantida a fonte original intacta; boot e wrappers ativos usam o pipeline central.
- Classificado como `technical_demo` com teto `prototype`.
- Registrada a indisponibilidade de leitura dos dois canais Discord fornecidos.
- Corrigida a chamada legada `VDP_showFPS(TRUE)` para `VDP_showFPS(FALSE, 1, 2)` conforme o header do SGDK 2.11.
- Corrigido o contrato de `EnemyDEF.dataAnim`, ampliado para 70 entradas para cobrir os índices usados por `ENEMY_STATE`.
- Corrigida a sintaxe de otimização dos seis sprites oversized para `NONE 1 1`, conforme o validator do workspace; nova ROM gerada e executada no BlastEm.
- Integrada sonda ROM-side `src/runtime_probe.c` com VLAB v1, CRAM, registradores VDP, CPU/jitter, sprites por scanline e ranges reais de tiles carregados por código; `VDP_loadTileSet` passou a ser medido por wrapper local.
- Criado `doc/vram_residency_report.json`, vinculando ao hash atual a residência observada na cena 8 (`bgb_credits`: 475 tiles; `bga_credits`: 332 tiles) e eliminando o bloqueio de budget VDP sem evidência explícita.
- Registrada a sessão BlastEm selada `blastem-linux-20260921T015549Z-936914`, cena 8, com ROM SHA-256 `c8dbc5a3922f866de15b17b8e16a8958c14458b7a968b4e9881a3ccd19b4dd2b`, screenshot, SRAM, VDP dump, runtime metrics e áudio em disco.
- Executada validação de áudio: 26 recursos declarados, 6,3% do budget de ROM, `pass=true`; avisos de fontes estéreo preservados.
- Criado `doc/asset_provenance_manifest.json` com 340 entradas placeholder; a origem legada continua explicitamente não verificada.
- Preenchidos GDD técnico e `technique_usage_manifest.json` com as técnicas realmente aplicadas e seus limites de evidência.
- Auditorias finais registradas: contexto/metodologia/higiene/PRD/proveniência/sincronização documental e bundle BlastEm passaram; AAA final e gameplay de combate continuam fora do claim.
