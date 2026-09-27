# Suzaku: recuperar fidelidade a fonte antes de reduzir a ambicao

Data: 2026-09-26. Estado: diagnostico medido e plano de implementacao; nenhuma nova ROM de cenario aprovada.

## Decisao

A orientacao explicita do usuario e aproximar o resultado do original MUGEN. O ZIP local `rascunho/entrada_bruta/ssf2_01_ryu.zip` (SHA-256 d781b8d53d8b35789ed18985b7ad7ab9db977d220d9940b132999ed92323fb96), seu DEF e SFF voltam a ser a autoridade visual. V1–V16 permanecem historicos de experimentacao, nao a nova fonte. Preservar lua crescente, castelo proximo, telhado diagonal, parede, escala dos elementos e tabuas em perspectiva. Nao substituir isso por outra composicao bonita, repeticao ostensiva de piso ou redimensionamento global 5/6.

A estimativa de 446 tiles limita a configuracao atual da engine, nao o Mega Drive. O veredito historico de nao caber continua valido apenas naquele arranjo. A mudanca de estrategia nao demonstra que uma nova configuracao ja cabe.

## Evidencia reproduzivel

Script: `rascunho/processado/stage_takeover/audit_original_source_recovery.py`; relatorio: `rascunho/processado/stage_takeover/original_source_recovery_audit_20260926.json`. Self-check 7/7. Apenas analise, sem novos pixels de arte ou modificacao de recursos.

| Camera | Cores VDP exatas | Padroes de tiles apos conversao de cor exata | Padroes com 15 cores de cenario |
|---|---:|---:|---:|
| 0 | 53 | 816 | 800 |
| 224 | 49 | 693 | 682 |
| 448 | 49 | 873 | 864 |

Sao vistas compostas estaticas, com deduplicacao H/V; nao residencia medida de dois planos, nem ResComp ou ROM. Existem tiles com 17–18 cores na conversao exata: so arredondar para o VDP nao resolve.

A heuristica de quinze cores proprias reduz o erro RGB quadratico medio agregado em cerca de 36,5% contra oito cores de cenario mais sete cores fixas do HUD. Duas linhas condicionais reduzem cerca de 50,8%. Isso NAO e percentual de fidelidade visual, DeltaE ou aprovacao artistica. A segunda linha utiliza oito entradas adicionais e preserva sete cores HUD, escolhendo uma unica linha por tile; depende de liberar PAL3 dos FX e rever explicitamente seu ownership exclusivo. Nao foi adotada.

O castelo isolado, particionado conservadoramente em celulas de ate 32x32, custaria 14 sprites, ate cinco e 144 pixels por scanline. Nao inclui atores, clipping, prioridade, oclusao ou ResComp. E uma possibilidade mensuravel, nao um terceiro plano gratis.

O estimador cobra dois retratos mesmo com o mesmo personagem; o runtime reutiliza esse retrato. Isso muda 446 para 462 na aritmetica desse caso, sem provar disponibilidade contigua. O pool de sprites de 600 tiles precisa de medicao de liveness em combate completo. A sonda anterior sem stage e com audio dummy nao autoriza subtrair seus 247 tiles livres.

## Sequencia executavel

1. **Fixar a referencia e sua semantica.** Conferir ZIP, DEF, SFF e hashes; registrar derivados no workset e proveniencia antes de conversao produtiva. Comparar cameras 0/224/448 e extremos intermediarios com a fonte. Localcoord 320x240, crop superior 16 e zoffset216 levam os pes a y200. A proposta original exige mundo768/camera0..448; reconciliar explicitamente o runtime640/0..320. O renderer estatico ainda nao foi validado contra MUGEN/IKEMEN e nao demonstra movimento.
2. **Liberar cores pela arquitetura.** Concluir a migracao prevista de corpo+FX para PAL1/PAL2 e HUD para PAL3 para disponibilizar PAL0 ao cenario. Conservar as aprovacoes por SHA e contratos de transparencia. Comparar quinze cores com o controle atual usando as mesmas fontes/cameras. A variante PAL3 compartilhada e apenas experimento condicionado a novo contrato; nao sobrescrever FX ou HUD. Nao alterar paletas por H-Int antes de medir necessidade, riscos de CRAM e atores cruzando faixas.
3. **Orcar residencia real.** Gerar tiles/mapas dos planos a partir da fonte; medir janelas visiveis com margem de scroll e deduplicacao exata. Construir mapa de enderecos e tempos de vida de fonte, HUD, retratos, corpos, pool e super. Medir pools600/544/512/480 se justificavel, com duas magias, saltos, sombras, audio e super. So reutilizar regioes com ownership e restauracao demonstrados. Fonte e lacunas entre tabelas nao sao memoria automaticamente livre. Nao usar flicker para resolver falta de tiles de fundo.
4. **Prototipar movimento sem redesenhar a cena.** BG_A pode separar telhado, piso principal e faixa inferior por linhas; BG_B tem ceu, castelo e parede com velocidades distintas na mesma scanline. Comparar tres solucoes: (a) agrupar seletivamente paralaxes distantes preservando pixels e avaliar erro nos extremos; (b) atualizar tiles/mapas compostos por camera e fase temporal, medindo tiles sujos, DMA por quadro, CPU, RAM e ROM; (c) deslocar apenas um elemento apropriado para sprites, medindo custo combinado e oclusao. Nao implementar todas ate o fim: selecionar pelo primeiro experimento discriminante e custo observado.
5. **Incluir o tempo, nao apenas a camera.** BG0a/BG0b possuem velocity X=-0,25; cache apenas por camera nao reproduz o ceu. BG5 tem 51 frames/278 ticks em tres janelas nao simultaneas 900..1178,1778..2056,3086..3364 dentro do ciclo3364. Medir fases, subpixel, ida/volta e mudancas de direcao. A semantica de xscale interpola o delta horizontal por linha; nao confundir com escala geometrica convencional.
6. **Levar cedo uma cena fiel ao emulador.** Depois dos contratos/recursos validos, criar build de laboratorio isolado com cena fonte e camera controlavel. Comparar original, candidato offline e captura BlastEm do mesmo enquadramento. Registrar ROM SHA, VRAM, CRAM, SAT, DMA e video. Evitar nova serie longa de conceitos antes desse teste. Integrar luta e audio para verificar o custo completo; cena isolada nao aprova gameplay.
7. **Refinar somente perdas demonstradas.** Se cores ou tiles ainda exigirem ajuste, atuar localmente em rampas, clusters e modulos existentes, preservando silhueta/composicao. Geracao de imagem fica restrita a lacunas identificadas, com mascara/brief e revisao; nunca substituir a fonte inteira. Manter mudancas reversiveis e comparacoes com a referencia.

## Criterios de aceite

- Referencia reconhecivel nas tres vistas e no percurso; sem repeticao evidente introduzida para esconder perda de detalhes.
- Contratos e arquivos derivados reproduziveis, cores e mascaras conferidas, proveniencia preservada.
- Sem seams, tiles velhos, cenario apagado por super ou cor de HUD/FX vazando; teste de flash, pausa, KO, retorno e super.
- Pressao combinada de sprites e pixels por scanline, residencia e pico de DMA medidos; nada aprovado pelo FPS do player de captura.
- Cadencia sustentada e audio avaliados na ROM exata com cenario, dois atores e efeitos pesados. Video com integridade temporal validada; screenshots so aprovam seu escopo estatico.
- Revisao visual humana por SHA e gates existentes permanecem. Nenhum resultado offline promove AAA.

## Correcao de ferramenta e aprendizado

`stage_measure._md` usava arredondamento diferente do conversor: vermelho17/18 podia colapsar, enquanto18/19 podia separar indevidamente. Agora usa `vdp_word` do conversor. Testes de fronteiras e contagem real de camada: RED 7 falhas/6 passes; GREEN com testes de stage 26 passes; suite completa 133 passes. Relatorios historicos de contagem de cores precisam ser regenerados antes de novas decisoes. Nenhum pixel do jogo foi alterado por essa correcao.

Licoes locais: preservar a fonte em tarefas de port; distinguir limite da engine de limite do hardware; medir conversao com a mesma semantica e vetores independentes conhecidos; incluir tempo em fontes com movimento autonomo. Nao promover automaticamente ao canon.

Referencia primaria de semantica: https://elecbyte.com/mugendocs/bgs.html . Ports comerciais provam que ha alternativas de oficio, mas nao atribuir tecnicas a eles sem codigo, dump ou evidencia equivalente.

## 2026-09-26 — Geometria de fonte, HUD real e custo de camera exata

- `suzaku_source_coordinate_board_20260926_v1.json` registra, por camada, o sprite SFF, dimensao/eixo, mascara MUGEN, `start`, `delta`, `xscale`, velocidade autonoma e bounds visiveis nas cameras 0/224/448. O centro 224 e ancora; as tres vistas estao ligadas ao ZIP/DEF/SFF pelos hashes da fonte.
- O V17 gerado como panorama unico foi recusado: camadas com velocidades diferentes foram fundidas em uma coordenada mundial comum, deslocando landmarks e encurtando o piso. O PNG permanece `negative_case_evidence` no workset; nao pode orientar pixels de producao.
- A estimativa anterior tratou todo o retangulo do WINDOW em y=0..55 como opaco; essa premissa foi invalidada ao confrontar `fight_hud.c`, que zera as 40x7 celulas e redesenha apenas partes do HUD. As contagens 679/710 da janela que removia essas linhas sao somente um limite inferior hipotetico, nao residencia visivel de producao. A errata e o novo comparativo source-anchor estao em `rascunho/processado/stage_takeover/suzaku_visible_window_residency_20260926_v2/visible_window_report_erratum_20260926.json`.
- Foi medido um controle mais fiel: recompor as camadas estaticas em cada uma das 449 posicoes de camera preserva os deltas originais offline. Na camera central, o quadro usa 466 padroes (8+7) ou 481 (15 cores); no sweep, o pico e 629/638. Uma transicao adjacente de 1 px muda ate 739 celulas e exige ate 19.776/19.838 bytes inferiores de padroes+mapa. Esta rota de recomposicao completa nao fecha como atualizacao direta por quadro; falta um mecanismo que reduza mudancas, nao um limite alegado de VBlank.
- Conclusao atual: manter os PNGs originais por camada como autoridade e usar as vistas exatas como alvo de comparacao; nao achatar todos os deltas em um panorama nem substituir o cenario por arte gerada. Um agrupamento de movimento so pode seguir se preservar os landmarks em 0/224/448, caber no budget combinado e sobreviver a uma revisao visual. O contrato por camada e o primeiro gate, nao uma aprovacao de arquitetura.
- Relatorios: `suzaku_visible_window_residency_20260926_v2/visible_window_residency_report.json`, `suzaku_exact_camera_screen_tiles_20260926_v2/exact_camera_screen_tile_cost.json` e `suzaku_source_coordinate_board_20260926_v1.json`. Evidencia visual de referencia: `suzaku_source_camera_atlas_20260926_v5/source_vs_palette_camera_contacts.png`; quadro indexado central continua somente referencia, sem aprovacao.
- Ainda nao houve alteracao em `res/`, runtime C ou ROM. Falta selecionar uma representacao de movimento que preserve detalhe de fonte com custo de tiles/DMA menor; depois converter o enquadramento central como asset reversivel, integrar em ROM isolada, validar camera e auditar a cena de luta com audio.


### Pool de sprites: chamadas por estado, nao por busca textual

`src/core/app.c` inicializa `SPR_initEx(16)` no boot para branding; `src/scenes/scene_demo.c` faz `SPR_end()` e reabre o pool com `SPR_initEx(FIGHT_SPR_VRAM)` (600) antes de criar os dois lutadores. O validador atual encontrou 16 porque tomou a primeira chamada do workspace; nao distinguiu estado/cena. O relatorio de recursos reporta `budget_doc_mismatch`, mas isso nao autoriza reduzir o pool de luta. O calculo de 304 tiles continua condicionado ao pool 600, duas sheets maximas de 260 e 112 tiles fixos; HUD, retratos, FX, fragmentacao e buffers de stream ainda reduzem a folga. O ROM em `out/rom.bin` tem SHA `200346548a57cb6196cf21773c9233bd53b72b02e1bdf7f6548fd3331aa81c2c` e o relatorio de validacao aponta identidade stale/mismatched; logo, pool observado em hardware/emulador ainda nao foi confirmado.

Aprendizado de ferramenta: para runtime com varios estados, medir ownership do allocator na transicao real e nao selecionar o primeiro `SPR_initEx()` encontrado no C. Registrar ambos os pools e a sequencia de chamadas ate haver evidencias de cena em ROM.

### 2026-09-26 — Quadro-fonte Suzaku e errata do recorte do HUD

- A composicao do DEF/SFF original foi recomposta na ancora de camera 224 a partir de BG0a/BG0b e BG1..BG4, com zero pixels RGB divergentes do compositor offline antes da quantizacao. A base fonte `source_composite_anchor.png` tem SHA `d399b5550af26f199e4ac92eae7bda8c2730186a6cb1af766f803672106dbbb5`.
- A quantizacao compartilhada em 15 cores mede MAE/RMSE RGB 12.169/15.442, 758 tiles pareados BG_B+BG_A e 26.736 bytes no ResComp3.95; o controle flat e 712 tiles/24.994 bytes. A versao em 8 cores mede 15.030/19.390 e 685/24.182. As duas sao candidatas tecnicas, nenhuma aprovada.
- O candidato de 15 cores ainda conflita com o owner atual de CRAM: palco usa PAL0 slots1..8, HUD usa PAL0 slots9..15 e FX usa PAL3. Para preservar 15 cores do palco, precisa concluir uma migracao revisada de HUD/FX; nao carregar essa paleta sobre o HUD/FX atual. A opcao 8-color cabe no recorte de paleta existente, mas reduz fidelidade cromatica.
- Corrigido um erro de premissa: `VDP_setWindowVPos(FALSE, WROWS)` posiciona o Window; nao torna opacos pixels vazios. `clearWindow()` limpa as 40x7 celulas, e `drawStatic`/`FIGHT_HUD_update` escrevem somente retratos, barras e texto em celulas escolhidas. Color code 0 revela a composicao inferior. Logo o corte superior usado no relatorio de residencia nao pode ser creditado sem medir a mascara real e confirmar na ROM com Suzaku carregado. Os valores clipped (516 tiles em 15 cores e 506 em 8) sao invalidos para o budget de producao atual.
- `SPR_initEx(n)` cria o allocator no intervalo `[TILE_FONT_INDEX-n, TILE_FONT_INDEX)`. No SGDK 2.11 H40, `TILE_MAX_NUM=1536` e `TILE_FONT_INDEX=1440`: pool600 comeca no indice840; pool446 comeca no994 e aumenta tiles fixos de824 para978 (+154). Isso reduziria o pool de sprites; a sonda anterior viu pico353 usados e maior bloco contiguo72 somente sem palco e com audio dummy. E uma hipotese de budget, nao uma recomendacao nem seguranca demonstrada. Mesmo com emprestimo temporal dos 272 tiles de BGFX, o frame-ancora completo sem mascara HUD mede758 tiles, 242 acima do teto condicional516. A mascara por pixel ainda nao mediu se celulas integralmente ocultas permitem alguma economia.
- Direcao mantida: usar a composicao original como controle visual; nao voltar a V18 ou substituir por uma cena generica. A proxima etapa e Pareto de economia de tiles por regiao sem recortar o ceu, seguida de auditoria de mapa por camera e teste de compartilhamento exato de sheets quando P1/P2 usam o mesmo `MgCharDef`. Pool candidato so muda em ROM descartavel apos layout estatico fechar e com captura pareada de stage/audio, pico alocador, bloco contiguo, DMA, scanline e cadencia.
- Relatorio hash-bound: `rascunho/processado/stage_takeover/suzaku_visible_window_residency_20260926_v2/visible_window_report_erratum_20260926.json`. Sem alteracao em `res/`, runtime ou ROM; nenhum asset promovido.
