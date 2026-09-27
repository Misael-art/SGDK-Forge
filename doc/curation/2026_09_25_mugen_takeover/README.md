# Curadoria de continuidade MUGEN→SGDK — 2026-09-25

Esta rodada assume a execucao do projeto Mugenesis_Demo. Status: **em curso**;
nenhum cenario ou faixa de luta foi entregue e nenhuma promocao AAA foi feita.
`validation_report.json` separa o que foi realmente executado dos gates
pendentes. Fonte operacional completa no memory bank e no
`doc/mugen/stage_suzaku_route_2026_09_25.md` do projeto.

Licoes qualificadas para o agente canonico, adicionadas a
`tools/sgdk_wrapper/.agent/references/mugen_curation_operational_2026_09_25.md`:

1. Paleta 4bpp valida nao prova VRAM. Para stage rolavel, derivar largura da
   camera por plano; medir uniao total, pior janela visivel, tabela do VDP,
   compilado ResComp e qualidade em 1x. O crop 512/512 omitiu 130 tiles de
   Suzaku; a medida corrigida e 1366 com pico visivel 845.
2. O parametro de cena do runner e intencao, nao fato. ROM direct-fight pediu
   menu mas apresentou luta; ferramenta agora bloqueia `scene_id` diferente
   ou ausente antes de publicar evidencia canonica. Um build separado provou
   a rota positiva do menu.
3. Skills duplicadas em `.agents/skills` podem divergir da fonte canonica.
   Preservar backup e validar que a ponte resolve ao diretorio certo. O guard
   passou apos a substituicao da copia por symlink.
4. `audio.raw` nao equivale a musica aprovada. Cues PSG que chamavam
   `AUDIO_stopAll()` interrompiam o BGM; o codigo foi corrigido e compilado,
   mas ainda falta disparar o cue no menu e escutar o resultado.
5. Validar cabecalhos de audio gerado contra a especificacao independente:
   o VGM do menu deslocava total/loop/rate em quatro bytes, embora o ResComp
   aceitasse. A correcao passou teste, build e BlastEm. A comparacao longa
   teve sinal de audio nas ROMs antiga e nova; o cabecalho invalido nao pode
   ser apresentado como causa observada de silencio ou como prova auditiva.
6. Auditor de recursos deve ler apenas os `.res` ativos por padrao. Copias
   dentro de `rascunho/` inflaram o grafo para 484 problemas falsos; com
   escopo correto, 3 `.res` e 161 declaracoes resultaram em um aviso real.
   O validador da ponte tambem precisava resolver links relativos a partir
   da pasta do link, preservando portabilidade entre hosts.

Itens que **nao** viram regra geral: a paleta especifica do Suzaku, pool de
sprites 600 ou 384, os deltas compostos .43/.67, o recorte vertical 16 e a
qualidade estetica da candidata. Esses numeros pertencem a um unico projeto
e a uma ROM conhecida. A correcao do runner e geral porque a semantica
pedido→observacao foi testada com match, mismatch e ID ausente.

O `audit_project_learning.ps1 -Mode Capture` registrou 51 licoes locais, 30
candidatos, `canonical_promotion_performed=false`. Atualizar skill geral
somente apos revisar a formulacao qualificada e seu escopo.
