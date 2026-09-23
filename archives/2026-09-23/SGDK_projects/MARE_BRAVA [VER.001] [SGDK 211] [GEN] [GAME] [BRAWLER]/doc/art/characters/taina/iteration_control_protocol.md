# Protocolo de Controle de Iteracao — TAÍNA

Status: `active_local_art_direction_protocol`
Escopo: TAÍNA e, por extensao, qualquer asset visual critico de MARE BRAVA.

## Problema que este protocolo evita

Uma iteracao pode ficar mais limpa, mais proxima do grid ou mais conveniente para
o pipeline e, ainda assim, deixar de parecer a TAÍNA. Isso ocorreu nos probes
v05 e v07: v05 recuperou parte dos marcadores, mas caiu em proporcao chibi;
v07 melhorou escala e pivot, mas perdeu cabelo, face e leitura da guarda.

Conformidade PNG/VDP, reducao de escala e uma aparencia genericamente 16-bit
nao contam como ganho visual. Sao criterios separados da fidelidade autoral.

## Fonte de verdade e incumbencia

### Selecao humana na linha do tempo

Em 2026-07-28, o diretor de arte humano confirmou que a imagem 04 da linha do
tempo — o lote **Assinatura autoral** de 04 jul, documentado em
`data/processed/contact_sheets/authorial_style_validation_contact_sheet_v01.png`
— representa a linguagem visual adequada para MARE BRAVA.

As imagens 05 e 06 da mesma linha do tempo, que registram as comparacoes de
lineart posteriores da TAÍNA, sao classificadas pelo diretor de arte como
**retrocessos de fidelidade grafica**. Elas permanecem uteis apenas como
evidencia negativa: nao sao baseline, direcao desejada, fonte de prompt ou
referencia de geracao.

Antes de qualquer nova tentativa, o agente deve consultar nesta ordem:

1. `doc/art/characters/taina/visual_dna_manifest.json`;
2. `doc/art/characters/taina/art_gameplay_direction_gate.json`;
3. `doc/art/authorial_line_style_contract.json`;
4. a fonte conceitual humana ratificada indicada no `visual_dna_manifest`;
5. as imagens 05/06 e os relatorios de fidelidade v05/v07 como evidencia negativa.

A fonte ratificada e o **incumbente visual**. Nenhum candidato novo substitui o
incumbente por parecer mais nativo, limpo ou facil de converter. Para substitui-lo,
precisa vencer simultaneamente em:

- identidade e leitura em escala nativa;
- preservacao dos marcadores obrigatorios;
- escala/pivot e viabilidade VDP iguais ou melhores;
- parecer humano explicito.

Os probes v05/v07 e qualquer asset marcado como `negative_evidence`,
`comparison_only`, `obsolete_for_generation_source` ou `not_promoted` jamais
podem virar fonte de prompt, img2img, baseline ou proxima geracao.

## Cartao de direcao que o agente deve usar

Para cada novo candidato, declarar antes de desenhar:

```text
asset: taina_pixel_lineart_<versao>
papel: lineart_blocking_1px, nao sprite final
fonte_de_verdade: <arquivo ratificado>
escala_e_pivot: celula 48x64; alvo visivel 48px; bottom_center inteiro
must_preserve:
- massa de cabelo cacheado curta e irregular
- rosto em cunha: sobrancelha forte, nariz em cunha, mandibula compacta
- top laranja queimado + calca roxo-escura larga
- bandagens verdes e faixa lateral no mesmo lado declarado
- guarda alta diagonal de muay thai, com punhos e pes legiveis
nao_aceitar:
- anatomia realista ou chibi
- rosto liso/generico, perda de cabelo ou troca de assimetria
- bloco de massa sem guarda, materiais ou direcao do olhar
saida_permitida: candidate_for_human_review
```

O agente deve trabalhar apenas um problema visual por iteracao. Exemplo: se a
missao e corrigir altura visivel, cabelo, rosto, figurino, paleta e guarda nao
podem mudar. Se uma dessas partes precisar mudar, isso vira uma nova decisao de
direcao, nao um efeito colateral silencioso.

## Regras de producao

- Geracao de imagem e permitida somente para `concept_art`/fonte candidata.
  Para lineart, key poses, strips, tilemap e sprite final, seguir a Etapa B
  autoral do `doc/art/art_generation_brief.md`; nao pedir uma nova imagem ao
  modelo para "corrigir" a anterior.
- Nao usar upscale, downscale, quantizacao ou limpeza automatica como solucao
  de identidade. Essas operacoes so podem testar viabilidade depois de a
  silhueta e os marcadores estarem corretos.
- Nao aceitar um candidato porque ele e o mais recente. A versao anterior
  continua sendo o comparador ate haver aprovacao humana.
- Nao atualizar baseline, manifest de fonte ou status de promocao com candidato
  reprovado ou parcialmente melhorado.

## Gate de revisao obrigatorio

Cada candidato deve produzir uma comparacao lado a lado, em escala nativa e em
ampliacao de review, contra a fonte de verdade. A decisao deve responder
`passou`, `parcial` ou `reprovado` para cada marcador:

| Marcador | Pergunta de revisao |
|---|---|
| Silhueta | A guarda diagonal e a massa de cabelo ainda leem antes do detalhe? |
| Face | Sobrancelha, nariz em cunha, mandibula e olhar ainda pertencem a TAÍNA? |
| Assimetria | Faixa e bandagens continuam no lado e na funcao declarados? |
| Materiais | Pele, top, bandagens e calca permanecem semanticamente distintos? |
| Escala | Mantem 48px visiveis, pivot e proporcao 3.5 heads sem virar chibi? |
| Gameplay | Punhos, pes, linha de ataque e contato com o chao continuam legiveis? |

Falha em qualquer item `must_preserve` gera `cohesion_drift` e bloqueia a
promocao. O proximo passo e voltar ao lineart blocking do estado afetado; nao
remendar a imagem final nem compensar com runtime.

## Como registrar feedback humano

Todo comentario deve virar uma entrada com quatro partes:

```markdown
sintoma: "a versao nova parece um boneco generico e perdeu a atitude"
diagnostico_tecnico: "a correcao de escala simplificou a massa cacheada, o rosto em cunha e a guarda diagonal"
heuristica_preventiva: "ao corrigir escala, congelar cabelo, face e guarda; reprovar qualquer candidato que perca um must_preserve"
evidencia: "comparacao v05-v07 e model_sheet_to_sprite_fidelity_report_v07.json"
```

Registrar a licao em `doc/agent_learning/failure_patterns.md`. O
`learning_ledger.json` e derivado: nao deve ser editado manualmente.

## Resultado esperado

O agente deixa de otimizar "parecer pixel art" isoladamente. Ele passa a
preservar a personagem e so depois resolve grid, paleta, tiles e VRAM. Assim,
restricao de Mega Drive direciona a autoria em vez de justificar degradacao.
