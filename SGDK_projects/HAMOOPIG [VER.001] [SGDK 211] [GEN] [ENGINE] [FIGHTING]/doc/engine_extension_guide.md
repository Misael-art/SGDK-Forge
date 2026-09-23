# Guia de extensão da engine

O runtime usa pools estáticos e definições de cena; uma extensão deve preservar
ownership e os limites do Mega Drive antes de adicionar conteúdo.

## Novo lutador

1. Converta cada frame a partir de uma fonte registrada, com índice transparente
   e paleta declarada.
2. Registre a definição no header/manifesto de recursos e associe as tabelas
   de idle, caminhada, salto, ataques, hitstun, derrota e vitória.
3. Declare pivô, corpo (`dataBBox`), hitbox (`dataHBox`), dano, hitstop e
   `metered_special`. O custo do especial é debitado somente quando a FSM
   aceita o estado.
4. Use `PLAYER_SET_SPRITE`; não libere e recrie metasprite a cada transição.
5. Acrescente testes de clamp, colisão, combo, KO e reset. A captura precisa
   mencionar o lutador, adversário, região, cenário e SHA da ROM.

## Novo golpe

O caminho de colisão deve emitir `CombatEvent`. O consumidor centraliza vida,
medidor, combo, SFX e resultado. Um overlap persistente não é multihit: use um
`sourceInstance`/índice de golpe novo quando a autoria permitir outro acerto.

## Novo cenário

Implemente uma entrada `StageDefinition` em `src/stage.c`: id, nome, largura,
altura, piso, limites de luta, capacidade PAL-240, imagem, plano/paleta,
loading model, orçamento/medição de tiles, câmera e proveniência. Converta a
arte por script determinístico e registre fonte, hash, paleta, tiles únicos,
custo de VRAM e limitações visuais. `init.c` deve carregar a imagem pela
definição, nunca por um ramo especial baseado no nome.

## Novo item de menu

Só adicione um item quando existir efeito observável, caminho de retorno e teste
ON→OFF→ON. Use `KEY_PRESSED`, limite de cursor, prioridade B/confirmar/ajustar/
navegar e preserve o cursor ao retornar. `DEFAULTS` é ação, não toggle.

## QA de pares e cenários

O executor `tests/run_p10_matrix.py` aceita `--p1=ryo|ken|musgo` e
`--p2fighter=ryo|ken|musgo` através do harness. O arquivo
`tests/blastem_qa.cfg` contém somente o cluster P2; os bindings P1 vêm do
`default.cfg` do BlastEm. O runner materializa esse default em um perfil
descartável, executa a sessão e rejeita o caso se o manifesto não coincidir
com a ROM, região, palco ou par solicitado. Nunca marque uma combinação como
passada por inferência de outra captura.

## Checklist de entrega

- [ ] fonte e proveniência registradas;
- [ ] símbolos/res sincronizados;
- [ ] teste host do contrato;
- [ ] build limpo e SHA;
- [ ] captura no emulador da rota real;
- [ ] orçamento de DMA/SAT/scanline medido;
- [ ] revisão visual e auditiva classificadas separadamente;
- [ ] memory bank, changelog e lição JSON atualizados.
