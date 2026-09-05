# Production Visual Quality Contract

Use este contrato para qualquer arte que possa virar `res/`, baseline visual ou
evidencia de produto. Ele impede avaliacoes relativas: um asset nao fica bom por
ser melhor que um placeholder, por compilar ou por rodar no emulador.

## Fonte de julgamento

- Cada projeto declara uma `quality_reference_board` local, com hashes e uso
  `quality_reference_only`.
- A prancha define oficio observavel; nao autoriza copiar pixels, pose, layout,
  paleta ou IP.
- Sem prancha aprovada para o papel do asset, o resultado maximo e
  `needs_review`. Laboratorio pode continuar, mas fica `lab_not_delivery`.

## Teste de promocao

O revisor registra uma decisao por asset critico em relacao a sua prancha. A
decisao so pode ser positiva quando todos os pontos aplicaveis passam:

| Papel | Condicao visual minima |
|---|---|
| Personagem | Silhueta, anatomia, rosto/maos/pes, marcadores de figurino e materiais sobrevivem no tamanho de jogo; cada material tem luz, base e sombra com funcao. |
| Animacao | Poses preservam volume e escala; antecipacao, acao, impacto e recuperacao sao legiveis em movimento, com pivot e contato coerentes. |
| Cenario | Vem de kit modular autoral com landmarks e materiais; profundidade e leitura de faixa jogavel sobrevivem ao recorte 320x224. Ilustracao achatada nao substitui kit. |
| FX | Possui fases de nascimento, pico e dissipacao por clusters; comunica evento de jogo e altera ou responde ao mundo, em vez de ornamentar a tela. |
| HUD, logo e texto | Hierarquia, contraste e identidade pertencem ao jogo; fonte/default/debug nao e entrega. |

## Mapeamento VDP

Camadas semanticas podem ser mais numerosas que o hardware. A traducao deve
declarar a composicao real em BG_A, BG_B, WINDOW e sprites; nunca alegar um
terceiro plano de background. Esta restricao nao autoriza empobrecer a fonte:
o recuo precisa preservar a leitura e a funcao visual da camada.

## Bloqueios

- `relative_quality_pass`: elogio baseado em comparacao com asset anterior.
- `source_detail_lost`: anatomia, material, landmark ou identidade da prancha
  desapareceram na traducao.
- `flattened_scene_or_fake_modularity`: cenario final e uma ilustracao
  comprimida ou nao possui kit/contrato de montagem.
- `decorative_fx_only`: efeito sem sinal de gameplay ou relacao ambiental.

Qualquer bloqueio exige `correction_request` que descreva sintoma observavel,
diagnostico tecnico e o proximo asset/contrato a corrigir. Novo build, screenshot
ou alteracao de threshold nao remove bloqueio visual.

## Relacao com os demais gates

Este contrato julga qualidade; nao substitui proveniencia, licenca, pixel
strict, budget VDP, evidencia BlastEm ou a barra viva. A promocao exige todos
eles. Em conflito, a regra mais restritiva prevalece.
