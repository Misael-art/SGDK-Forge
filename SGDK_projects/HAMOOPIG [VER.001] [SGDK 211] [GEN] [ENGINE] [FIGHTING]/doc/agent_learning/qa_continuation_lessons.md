# QA simetrico e audio — 2026-09-13

Ledger local: `doc/curation/2026_09_13/test_harness_lessons.json`.
Sem promocao automatica do framework.

1. Configuracao de controle e runtime sao causas distintas. P2 nao se movia
   porque a configuracao local nao era lida. Preservar o default completo e
   conferir o diretorio efetivo do Flatpak resolveu o transporte sem editar C.
2. Zero amarelo no seletor nao e KO. Entrada de luta exige HUD visivel;
   vencedor exige imagem/video com estado e mensagem, nao nome do arquivo.
3. PAL nao compartilha todas as coordenadas de captura NTSC. Template de nome
   falhou apesar de o seletor estar rodando; nao usar isso como falha da ROM.
4. Um sink vazio grava silencio mesmo com jogo sonoro. Identificar somente o
   novo fluxo BlastEm, mover e esperar confirmacao de sink antes da captura.
   `audit_captured_audio_signal.py --self-check` mede sinal, nao musicalidade.
5. Dano antes de time-over deve ser observado. A primeira tentativa produziu
   DRAW; a seguinte, com reducao de barra confirmada, produziu P2 WINS em 00.
6. Prova de identidade nao e prova de qualidade. O selo canonico confirma
   hashes/arquivos; DMA/SAT, FPS do loop e audicao mantem contratos proprios.

Regressoes: `test_timeover_contract.py` (9.216 pares),
`test_health_contract.py` (192 transicoes) e `test_stage_palette.py`, todos
em `rascunho/temporario/`. Provas: fechamento QA de 2026-09-13.
