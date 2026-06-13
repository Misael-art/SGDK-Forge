# Celestial Chase - Highscore Endless em SRAM (CCSV v1)

## Status

- Origem: solicitação do usuário (2026-06-05).
- Aprovação: aprovada em chat (abordagem A: `CCSV v1` sem checksum; atualização apenas no Result e apenas no Endless).
- Escopo: persistência do highscore do modo `CHASE_MODE_ENDLESS` + HUD/Result exibindo `SCORE`/`HIGH`.

## Objetivo

Persistir e recuperar o melhor score do modo Endless em SRAM, usando schema simples e determinístico, sem gravação contínua durante a run.

## Restrições e Regras

- Usar SRAM no offset `0x600`.
- Magic/tag: `CCSV` + versão `1`.
- Atualizar apenas no Result e apenas para `CHASE_MODE_ENDLESS`.
- Se magic/version inválidos, assumir `highscore=0` sem “formatar” SRAM automaticamente.
- Não usar `malloc/free`.
- Acesso à SRAM deve ser curto, direto e sem DMA (SRAM é mapeada via mapper).

## Layout SRAM (CCSV v1)

Offset base `0x600`:

- `0x00..0x03`: ASCII `CCSV`
- `0x04..0x05`: `u16` versão (big-endian) = `1`
- `0x06..0x09`: `u32` highscore (big-endian)
- `0x0A..`: reservado (ignorado)

## API (novo módulo system/save_data)

Arquivos:

- `inc/system/save_data.h`
- `src/system/save_data.c`

Interface:

- `void SAVE_DATA_init(void);`
  - Lê o bloco `CCSV v1` em `0x600` e cacheia `highscore` em RAM.
  - Se inválido, cacheia `0`.
- `u32 SAVE_DATA_highscore(void);`
  - Retorna `highscore` cacheado.
- `bool SAVE_DATA_trySubmitEndlessScore(u32 score);`
  - Se `score <= highscore`, retorna `FALSE` sem gravar.
  - Caso contrário, grava `CCSV v1` + score em SRAM e atualiza o cache; retorna `TRUE`.

## Integração na cena

- `scene_chase.c`
  - Em `SCENE_chaseEnter`, chamar `SAVE_DATA_init()` para garantir que HUD/Result tenham o valor atual.
  - Ao entrar no estado de Result, se `rules.mode == CHASE_MODE_ENDLESS`, chamar `SAVE_DATA_trySubmitEndlessScore(rules.score)` e repassar ao HUD o `score`, `highscore` e flag `new_record`.

## HUD/Result

- Durante gameplay Endless:
  - Quando `!cinematic`, usar as linhas `2/3` do `WINDOW` para exibir `SCORE` e `HI` (rate-limit igual ao resto do HUD).
- Na tela de Result:
  - Sempre exibir `SCORE` e `HIGH`.
  - Opcionalmente, exibir `NEW RECORD` quando o score tiver sido promovido.

## Validação

- Build gera `out/rom.bin`.
- Prova BlastEm canônica (gate):
  - screenshot dedicado da janela do BlastEm
  - `save.sram` contendo `CCSV v1` no offset `0x600` e `highscore` esperado
  - `visual_vdp_dump.bin` (já existente no projeto via `VLAB`)
