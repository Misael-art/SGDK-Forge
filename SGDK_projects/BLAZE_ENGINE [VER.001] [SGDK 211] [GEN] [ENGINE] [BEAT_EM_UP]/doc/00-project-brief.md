# 00 - Project Brief - BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BEAT_EM_UP]

Este documento e o contrato curto de intencao. Ele existe para impedir que o agente comece arte, codigo ou curadoria sem entender o tipo de trabalho.

## Contexto

- Tipo de trabalho: `technical_demo`
- Gênero: `beat 'em up` (brawler de ação side-scrolling)
- Teto de promessa: `prototype`
- Frase do projeto: portar a BLAZE_ENGINE original, uma engine de beat 'em up, para o SGDK 2.11 canônico sem apagar sua lógica ou seus assets.
- Público alvo: desenvolvedores de engines e jogos Mega Drive que precisam de uma base de beat 'em up funcional.
- Plataforma alvo: Mega Drive / SGDK 2.11 / 320x224

## Pilares

Defina 3 a 5 pilares que guiam todas as decisoes.

- Pilar 1: preservar a lógica de combate e colisão da fonte.
- Pilar 2: manter sprites, cenários e áudio externos, sem rasterização procedural final.
- Pilar 3: respeitar VBlank, VRAM, tipos explícitos e APIs reais do SGDK 2.11.
- Pilar 4: cada claim termina em validação e evidência, não apenas em compilação.

## Escopo

### Dentro

- Estrutura flat compatível com o wrapper central.
- Correções necessárias para compilar e rodar com os headers SGDK 2.11.
- Smoke test de créditos, menu, seleção e primeira cena disponível na fonte.

### Fora

- Reautoria de arte, redesign de jogo, melhorias privadas do Discord não fornecidas em texto.
- Claim `ready_for_aaa` ou release final.

## Primeiro Resultado Valido

- Entrega mínima: projeto SGDK 2.11 buildável e ROM de smoke da engine.
- Evidência mínima: `out/rom.bin`, `validation_report.json` e captura BlastEm quando o host permitir.
- Critério de sucesso: build limpo, recursos validados, boot observável e limitações registradas.

## Riscos Principais

- Risco: recomendações do Discord não são legíveis sem autenticação.
  Mitigação: bloquear apenas a aplicação dessas recomendações específicas e registrar as URLs.
- Risco: a fonte tem um `main.c` monolítico e alto custo de sprites.
  Mitigação: preservar o comportamento nesta porta e medir antes de refatorar.

## Decisao de Abertura

- Data: 2026-09-20
- Decisor humano: solicitação do usuário
- Decisão: `technical_demo`
- Motivo: o pedido é de conversão de engine; a ambição AAA guia os gates, mas não cria escopo de jogo final por inferência.
