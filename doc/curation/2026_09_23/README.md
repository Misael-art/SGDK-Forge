# Curadoria MUGEN → Mega Drive — 2026-09-23

**Resultado: proposta para revisão humana. Nenhuma promoção canônica ou AAA.**
A arquitetura é útil e já converte uma fatia real do Ken, mas passar nos testes do conversor não demonstra fidelidade completa, qualidade audiovisual ou orçamento estável.

## Leitura e entregas

1. [Referência de domínio](../../../tools/sgdk_wrapper/.agent/references/mugen_engine_learning_2026_09_23.md) — princípios e limites da tradução.
2. [Matriz de fidelidade](../../../tools/sgdk_wrapper/.agent/references/mugen2sgdk_fidelity_matrix.md) e JSON adjacente — estágio por estágio.
3. [Lacunas de ferramentas](mugen2sgdk_toolgap_register.md).
4. [Auditoria das 54 skills](skill_audit_matrix.md), com inventário de fontes e notas em JSON.
5. [Técnicas e IDs reais](mugen_md_technique_catalog.md).
6. [Revisão das 12 lições E0–E3](lesson_adjudication.md).
7. [Roadmap e três quick wins](robustness_roadmap.md).
8. [Índice de evidências](evidence_index.json), [validações](validation/checks.json) e [fechamento](closeout.md).

## Escopo e identidade

- Fonte auditada: commit `12c63349d72fb8d96ecd16148fcfe9a9bde5965c` da branch de desenvolvimento; isso **não** significa que esses avanços já estavam em main.
- Branch de curadoria: `codex/mugen-curation-20260923`, criada de main `caf10a2d66cf3d418d47da7b87a87a4ac3a60bc5`. PR documental separado; não transporta implementação ou conteúdo de terceiros.
- Código e documentos do conversor lidos na fonte; suíte pytest reexecutada: **39 passed, sem skips**, 7,78 s. `unittest discover` não descobre essa suíte pytest; não é evidência de aprovação.
- Bundle P5 arquivado conferido: ROM `46a9cd6581bf2e7a9c16e15b5406767b9f24bd8a82c9d2591d02838b1d037c90`; cinco hashes conferem. Screenshot inspecionado. Nenhuma nova execução do emulador e nenhuma audição nesta curadoria.
- Arte, ROM e áudio de terceiros não são incluídos. Cópias de reports textuais preservam caminhos históricos como proveniência, não como dependências ativas.

## Achados prioritários

- **Desempenho reprovado no recorte:** P5 registra 591 ocorrências acima do orçamento e contador de 2191 frames (quociente bruto 26,97%; denominador de medição precisa excluir warmup), pico CPU 158%. Título da janela 61,2 fps não demonstra cadência da lógica. DMA e residência têm campos `null`; pico de 10 sprites/linha não cobre o pior quadro de todas as ações.
- **Áudio não aprovado:** sessão P5 usou `audio_driver=dummy`, sem arquivo de áudio. A rota SND→WAV mono 13.300 Hz→rescomp XGM2→playPCM existe. Falta provar simultaneidade, canais, inteligibilidade e custo com áudio ligado.
- **Proveniência bloqueada:** enum `third_party_mugen_conversion` não pertence ao schema. A invalidação faz o auditor tratar símbolos como não declarados; não se deve interpretar cada ocorrência em cascata como uma infração independente comprovada. A tabela `neg1_masks` é lógica, não pixel: finding do auditor requer correção com fixture negativo e positivo.
- **Governança:** adoção preservou manifests existentes; contexto continua `unclassified`; higiene acusa `out_prof`, `out_test` e `.gitignore` não classificados. São bloqueios do projeto fonte; esta é uma auditoria com resultado reprovado, não closeout de produto.
- **Semântica:** 796 controladores classificados pelo compilador (702 direct, 73 approximate, 21 unsupported) não equivalem a 702 controladores validados em ROM. Há juggle sem enforcement, helpers reduzidos, ChangeAnim2 aproximado e 46 elementos AIR com blending sem equivalência visual.
- **Limites de geração:** `a.frames[:255]` e `cm.steps[:255]`; runtime limita bitmap de -1 a 8 words. Exigir diagnóstico explícito de overflow; truncamento silencioso não pode parecer conversão bem-sucedida.
- **Não criar escolas duplicadas:** já há `fighting-game-design`, budgets antes de FX, engenharia de paleta e revisão audiovisual. O principal déficit é integração e evidência, além de pontos específicos de semântica MUGEN.

## Limites deste parecer

Notas de skill avaliam contrato documental no recorte auditado, não competência comprovada de um agente. Relatórios históricos são identificados como históricos. O estudo P3 contém estimativas e entradas mencionadas apenas no histórico: não recebeu selo de benchmark reproduzido. O P5 é evidência local observada, não aprovação do roster, de animações inteiras, de estágio ou de desempenho global.
