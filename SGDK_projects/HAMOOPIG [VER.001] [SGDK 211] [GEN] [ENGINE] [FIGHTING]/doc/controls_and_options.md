# Controles e opções

## Front-end

Somente P1 é lido no título, opções, debug e seleção de cenário. P2 entra em
ação apenas quando a luta começa.

| Controle | Título/opções | Seleção |
|---|---|---|
| Cima/Baixo | move o cursor por borda | — |
| Esquerda/Direita | alterna o valor por borda | troca lutador |
| A ou START | confirma; START inicia a seleção | confirma slot |
| B | retorna à página anterior | — |
| C | — | alterna PARK/BGB2 quando STG2 está ON |

Botão mantido não repete uma ação: a navegação usa `KEY_PRESSED`. Durante fade,
carga e lock de página, a entrada é ignorada para impedir confirmação duplicada.

## Opções atuais

- `SFX`: bloqueia novos efeitos sonoros;
- `MUSIC`: para/retoma a música da cena na borda da preferência;
- `LIFE`: oculta a barra sem alterar dano ou KO;
- `CLOCK`: oculta números sem desativar o limite;
- `TBG`: liga/desliga apenas o painel compacto do relógio;
- `TIME`: alterna 99, 60 e OFF para a próxima partida;
- `SPCL`: oculta a barra especial;
- `HITS`: oculta o feedback de combo;
- `RULES`: ON cobra especial; FREE libera o golpe configurado;
- `STG2`: controla a disponibilidade do segundo cenário;
- `INTRO`: controla a abertura na próxima entrada ao título. `B` na seleção ou
  na tela pós-luta é a rota de retorno que torna a preferência observável;
- `FADE`: liga/desliga os fades da abertura e do título nessa mesma rota;
- `DEBUG`: abre BOX, HIT, TEXT, PERF, FRM, STEP, TICK, 240 e BACK;
- `DEFAULTS`: restaura os defaults da sessão;
- `BACK`: retorna ao menu principal.

`OPENING` e `FADE` não usam SRAM; porém são apresentados porque SELECT e
AFTER_MATCH possuem retorno real ao título durante a sessão. `B` na seleção
retorna pela abertura quando INTRO está ON, ou diretamente ao título quando
está OFF.
