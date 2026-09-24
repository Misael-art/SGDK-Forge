# Reavaliação do PR19 — b69e92cc

Fonte: `b69e92cc4be555a9f3f4b52b1e7ce73c08a65c50`. Revisão em2026-09-24; nenhum merge executado nesta sessão.

Resultado: correções centrais do parecer anterior confirmadas. Suíte reexecutada: **62 passed em21,73s**, sem skips. `check_project` reproduziu14 classes de corpo (8 estáveis/6 variáveis), fusão1/6, um slot livre, nove coresFX sem par estável, `exact_need=23`, `fits=false`, `remap_lossless_verified=true`. O resultado é do contrato estático implementado, não prova de mínimo artístico global.

Recomendação: integrar contrato/verificador antes da reautoria, após alinhar duas frases do documento `palette_contract_rule1.md` ao código e à decisão vigentes:

1. A seção1 ainda chamaΔE≤10 de “mesma cor” no contexto da reprovação. O gate agora usa contagem exata; ΔE é estimativa de aproximação separada. Corrigir essa descrição.
2. A seção3 declara corretamente que5/6 não restaura universalmente a proporção, mas depois volta a afirmar que “devolve a proporção que o artista desenhou”. Remover a afirmação contraditória; manter como estudo fora desta rodada.

Não é necessário aguardar arte para integrar essa ferramenta. Nenhuma aprovação de migração ou qualidade decorre do merge.

## Próximas tarefas

- Preparar piloto de uma famíliaFX com contrato8+6+1, hashes, AIR, pivots, grade, duração, contexto, limites de tiles/DMA e source→output. O remap1/6 deve ser efetivamente aplicado ao candidato antes de ocupar o antigo6; a prova algébrica não significa que a migração já ocorreu nos assets.
- Separar aceite do piloto de aceite do personagem completo. O checker global continuará reprovando enquanto outras famílias permanecerem na paleta antiga. Avaliar o piloto com escopo explícito e executar o checker global na migração completa; não esconder recursos restantes para obter verde, nem usar waiver como aprovação.
- O slotFX é compartilhado pelas famílias do personagem sob contrato estático. Escolher sua cor considerando o catálogo inteiro; não aprovar diferentes cores incompatíveis para cada família sem nova decisão explícita.
- Retomar flash/shake no ramo técnico: tabela por lutador, restauração e testes de hitstop, hits consecutivos, projétil distante, super, KO, pausa. O teste definitivo de spill depende dos FX realmente migrados à linha do lutador; teste na alocação antiga é evidência parcial.
- Atualizar candidatos já registrados com commit de correção, testes independentes, números invalidados e limites remanescentes. Não criar cinco cópias novas das mesmas lições e não promover automaticamente ao cânone.

O agente gráfico continua indicado para o piloto visual. O agente técnico mantém a autoria do contrato, da medição e da integração. Esta reavaliação não criou imagens, não auditou esteticamente o piloto inexistente e não executou novaROM.
