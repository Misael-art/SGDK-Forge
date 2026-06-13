# Prompt Mestre - Telas de Assinatura do Template

Use este prompt para direcionar um agente de IA a construir as telas obrigatorias de assinatura de qualquer novo projeto MegaDrive_DEV.

```text
[Contexto MD Carregado]

Voce esta na raiz do projeto ativo. Sua tarefa e construir e validar as tres telas padrao de assinatura que todo projeto SGDK 2.11 do workspace deve herdar:

1. tela engine
2. tela do autor
3. tela do projeto

Objetivo visual:
- criar uma abertura com impacto de marca no nivel de consoles 16-bit comerciais;
- evitar imagem estatica pobre;
- usar efeitos reais de VDP, paleta, scroll, texto e audio sincronizado;
- manter 60 FPS no Mega Drive;
- preservar rastreabilidade, budget e prova em emulador.

Regra de prioridade de imagem:
- para assets premium/AAA, use primeiro o recurso proprio/nativo de geracao de imagem do agente, se disponivel;
- nao use `tools/ai_imagegen` como caminho padrao de fonte premium;
- `tools/ai_imagegen` so pode ser usado como fallback tecnico/laboratorio/prova de canal, e qualquer resultado local apenas legivel deve ser marcado como `aceito_apenas_como_prova_tecnica`, nunca como `fonte_premium_aprovada`.

Arquivos que voce deve ler antes de agir:
- `AGENTS.md`
- `doc/10-memory-bank.md` do projeto alvo, se existir; senao use `doc/06_AI_MEMORY_BANK.md`
- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
- `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/image-generation-routing/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/art-creation-sourcing/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/art-conversion-pipeline/SKILL.md`
- headers SGDK 2.11 relevantes em `sdk/sgdk-2.11/inc/`, especialmente VDP, PAL, SYS e XGM2.

Entregaveis obrigatorios:
- `runtime_decision_log` explicando a arquitetura das tres telas;
- `branding_sequence_contract.json` com:
  - nome da engine;
  - nome do autor;
  - nome do projeto/label;
  - duracao de cada tela em frames NTSC;
  - paletas usadas;
  - plano VDP dono de cada elemento;
  - audio cue map;
  - teardown/reset plan;
  - fallback sem assets finais;
- assets fonte em `res/data/branding/` quando houver arte real;
- assets finais em `res/branding/` somente depois de conversao;
- entradas `res/resources.res` somente para assets reais ja validados;
- cena C modular, sem colocar tudo em `main.c`;
- header da cena em `inc/scenes/`;
- integracao no scene manager do projeto;
- relatorio de budget VDP/VRAM/DMA;
- validation report limpo;
- build gerando `out/rom.bin`;
- evidencia BlastEm: screenshot, SRAM/metricas quando aplicavel, e registro de 60 FPS/sem corrupcao visual.

Arquitetura obrigatoria:
- criar uma cena dedicada antes do menu/boot normal, por exemplo `APP_SCENE_BRANDING`;
- a cena deve ter `enter`, `update` e teardown;
- `main.c` deve continuar com loop canonico:
  - input update;
  - app/scene update;
  - sprite update;
  - `SYS_doVBlankProcess()`;
- nao chamar loops bloqueantes longos dentro da cena;
- nao chamar DMA inseguro fora do fluxo aceito;
- resetar scroll, paletas especiais, sprites, PSG/XGM2 e planos ao sair.

Direcao das telas:

Tela 1 - Engine
- funcao: assinatura da tecnologia/base;
- texto provisiorio aceito: `MEGA FORGE ENGINE` ou nome final definido pelo projeto;
- visual: metal, bigorna/engrenagem/forja, brilho por paleta ou scanline;
- efeito minimo: fade/palette shimmer ou scroll controlado;
- audio minimo: impacto curto, PSG placeholder aceito ate haver PCM/XGM2 real.

Tela 2 - Autor
- funcao: assinatura humana;
- texto provisiorio aceito: `MISAEL OLIVEIRA`;
- visual: terminal/HUD/assinatura digital, limpo e elegante;
- efeito minimo: reveal temporizado de texto/linhas;
- audio minimo: beep/confirmacao curta.

Tela 3 - Projeto
- funcao: label/projeto que entra antes do jogo;
- texto provisiorio aceito: nome do projeto ou `MEGA MASTER GAMES` ate haver marca final;
- visual: selo arcade, logo robusto, sombra forte e alto contraste;
- efeito minimo: entrada por scroll, wave leve ou brilho de paleta;
- audio minimo: hit final sincronizado.

Regras tecnicas nao negociaveis:
- SGDK 2.11 real, sem APIs antigas;
- sem `float`/`double`;
- sem `malloc`/`free`;
- `int` nao deve ser usado para supor 16 bits; prefira `u16`, `s16`, `u32`;
- `PAL_setPalette`/`PAL_setColors` com assinatura SGDK 2.11 verificada em header;
- usar `XGM2_play`, `XGM2_playPCM` ou PSG apenas depois de verificar header;
- se nao houver audio real, implementar placeholder audivel e registrar como placeholder;
- assets visuais finais devem ter dimensoes multiplas de 8, paleta compativel e index 0 transparente quando aplicavel;
- nao promover PNG bruto de IA direto para `res/`.

Politica de bloqueio:
- voce nao pode encerrar dizendo "falta gerar assets" se ainda pode entregar a estrutura procedural placeholder que compila;
- voce nao pode declarar `pronto` sem ROM rodando no BlastEm;
- se um asset AAA nao atingir qualidade, registre como `needs_art_review` e mantenha o fallback procedural;
- se build falhar, corrija;
- se validator falhar, corrija;
- se emulator gate falhar, corrija ou registre blocker tecnico concreto com log;
- nao pare no plano: implemente, valide e atualize memoria operacional.

Passos obrigatorios, sem pular:
1. Ler os arquivos canonicos.
2. Criar/atualizar contrato da sequencia.
3. Implementar cena modular de branding no template/projeto.
4. Adicionar estrutura de pastas `res/data/branding/` e `res/branding/`.
5. Se assets reais existirem, converter e declarar em `.res`; se nao existirem, manter fallback procedural compilavel.
6. Buildar pelo wrapper.
7. Rodar validadores de recursos.
8. Rodar no BlastEm e capturar evidencia.
9. Atualizar `doc/10-memory-bank.md` do projeto ou `doc/06_AI_MEMORY_BANK.md` no workspace.
10. Entregar resumo com status honesto dos 7 eixos de QA.

Status permitido:
- `documentado`: so contrato/prompt existe.
- `implementado`: codigo existe, ainda nao buildado.
- `buildado`: ROM compila, sem emulador.
- `testado_em_emulador`: BlastEm rodou com evidencia.
- `validado_budget`: budget VDP/DMA/sprites confirmado.
- `placeholder`: estrutura visual/sonora provisoria.
- `fonte_premium_aprovada`: somente com arte de alto nivel, lineage, conversao, validacao e revisao.

Nao encerre sua resposta enquanto houver comando razoavel a executar localmente. So pare quando:
- a ROM estiver testada no BlastEm com evidencia; ou
- houver blocker externo inevitavel documentado com caminho, comando, log e proximo passo exato.
```

## Incorporacao no Modelo

O modelo canonico ja nasce com `APP_SCENE_BRANDING` em `src/scenes/scene_branding.c`.
Essa cena e uma estrutura procedural placeholder para compilar sem assets finais.
Quando a marca real existir, substitua os textos/efeitos procedurais por assets em `res/data/branding/`, mantendo o mesmo contrato de cena, teardown e validacao.

