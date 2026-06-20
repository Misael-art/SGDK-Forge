# Production Truth Protocol

Use este protocolo antes de corrigir um projeto, iniciar producao criativa ou
atribuir uma falha ao runtime.

## Quatro diagnosticos independentes

Classifique cada camada separadamente:

1. `host_executor`: sessao interativa, criacao de processos, permissoes,
   foreground, captura e encerramento de aplicativos.
2. `toolchain_wrapper`: dependencias, versoes, caminhos, compilacao, link,
   geracao de ROM e pos-processamento.
3. `rom_runtime`: boot, input observado, cenas, gameplay, audio, performance,
   SRAM, VDP e regressao.
4. `creative_quality`: direcao, legibilidade, coesao, acabamento e adequacao ao
   GDD.

Uma camada bloqueada nao prova falha nas demais. Registre por camada:

- `status`: `passed`, `warning`, `blocked`, `not_run` ou `not_applicable`;
- evidencia observada;
- causa confirmada ou `unknown`;
- proxima acao segura;
- arquivos e hashes relevantes.

Se o executor nao consegue criar processos, use
`host_executor_blocked`. Nao altere C, assets ou wrapper para tentar corrigir
uma falha que ainda pertence ao host.

## Autoridades tecnicas

- Metadados gerados pelo RESCOMP prevalecem sobre inferencias visuais da sprite
  sheet.
- Headers SGDK 2.11 prevalecem sobre memoria ou exemplos antigos.
- Evidencia explicita de VRAM e VDP dump prevalece sobre heuristica estatica.
- Input enviado nao equivale a input recebido. A ROM deve confirma-lo por
  telemetria, SRAM ou efeito observavel inequívoco.
- Boot nao prova gameplay. Screenshot isolado nao prova performance.

## Build transacional

Reporte separadamente:

1. compilacao;
2. link;
3. geracao da ROM;
4. pos-processamento;
5. documentacao.

Uma ROM pode existir apesar de falha posterior. Isso autoriza somente
investigacao controlada, nunca o claim de pipeline limpo.

Antes da captura:

- copie ou sele a ROM candidata;
- registre SHA-256 e tamanho;
- proiba rebuild durante a rota;
- vincule screenshot, SRAM, VDP dump, metricas e manifesto ao mesmo hash;
- invalide a evidencia se o hash mudar.

## Correcao causal

Para qualquer bug:

1. reproduza na ROM vigente;
2. identifique simbolo e caminho exatos;
3. crie regressao vermelha;
4. altere somente a causa confirmada;
5. rode a regressao;
6. use o build central;
7. recapture a mesma rota;
8. compare hash e evidencias.

Nao misture runtime, arte, audio e expansao de conteudo na mesma rodada de
correcao.

## Closeout sem falso bloqueio

Modele a sequencia como DAG, nao como validadores que se invalidam
circularmente:

`bootstrap -> build -> contratos -> regressao -> captura -> selo -> budgets -> memoria -> freshness -> validacao tecnica -> gate criativo`

Os estados abaixo podem coexistir legitimamente:

```text
technical_closeout: passed
creative_promotion: blocked
```

Uma aprovacao tecnica nao promove qualidade criativa. Um hold criativo nao
apaga uma ROM tecnicamente comprovada.

## Padroes proibidos

- tornar `PostMessage`, `SendInput` ou qualquer transporte local uma solucao
  universal;
- relaxar gate para obter resultado verde;
- tratar placeholder como arte final;
- registrar `audio: ok` quando o correto e `not_required` ou
  `not_implemented`;
- usar screenshot isolado como prova de gameplay;
- inserir workaround de uma maquina no wrapper central;
- manter instrumentacao QA ativa em build de entrega;
- derivar claim AAA apenas de testes automaticos.
