# TAÍNA v08 — Visual Breakdown de Produção

Persona responsável: `art-director` do projeto.
Função: tornar a imagem 04 uma especificação observável para a lineart v08.

## Referências técnicas de Mega Drive

Estas referências definem eixos técnicos, não licença para copiar personagem,
pose, paleta ou composição.

1. *Streets of Rage 2* — silhueta de lutador e leitura de impacto contra fundo ativo.
2. *Shinobi III* — contraste de sprite e economia de forma em ação rápida.
3. *Comix Zone* — cortes angulares de linha e massa de sombra como linguagem gráfica.

## Hierarquia de leitura em 48x64

1. **Decisão:** guarda alta diagonal, cabelo cacheado e faixa lateral.
2. **Identidade:** sobrancelha, nariz em cunha, mandíbula e direção do olhar.
3. **Material:** top gasto, bandagens/faixa e calça larga.
4. **Detalhe:** dobras grandes, nós e cortes de tecido; nunca textura miúda.

Se a leitura não sobreviver nessa ordem em 320x224, o detalhe inferior sai; a
silhueta não é sacrificada para preservar enfeite.

## Linha e volume

- Contorno externo: marinho/roxo escuro, espesso apenas nos pontos que separam
  cabeça, punhos, pernas e faixa do fundo.
- Linhas internas: cortes curtos em cunha; não hachura e não contorno uniforme.
- Sombra futura: triângulos ou trapézios claros, acompanhando planos de tronco,
  calça e bandagem; não manchas suaves.
- Ombros e quadril: diagonais que sustentam guarda e deslocamento de peso.

## Materiais e paleta futura

O v08 ainda é lineart. Ao passar no gate, o color blocking deve respeitar o
DNA visual já travado:

| Material | Leitura exigida | Rampa planejada |
|---|---|---|
| Pele | rosto e mãos/pés legíveis | sombra fria, luz quente |
| Top laranja | pico cromático da heroína | cortes triangulares, sem ruído |
| Bandagens/faixa verdes | assimetria e contato | blocos claros, sem linhas repetidas |
| Calça roxo-escura | massa inferior ampla | dobras grandes em cunha |

## Veto do Art Director

Reprovar a v08 se ela parecer uma figura genérica que apenas cabe em 48x64.
Reprovar também se corrigir altura ao custo de cabelo, face, guarda, faixa ou
atitude. `technical_pass` não compensa `cohesion_drift`.

## Saída deste breakdown

A única saída autorizada agora é a lineart v08 de quatro vistas definida no
`taina_lineart_v08_authoring_card.md`. Color blocking, key poses, strip,
paleta final e `.res` continuam bloqueados até revisão humana.
