# Host-format handoff — 2026-09-21

## Objetivo

Registro versionado do estado que deve sobreviver à formatação do HD e do
SDcard. Este documento é uma transferência de desenvolvimento, não uma
aprovação de release final.

## Repositório principal

- Remote: `https://github.com/Misael-art/SGDK-Forge.git`
- Branch de trabalho: `codex/taiketsu-ultra-rebirth-aaa`
- Base remota observada antes do fechamento: `origin/codex/taiketsu-ultra-rebirth-aaa`
- Estado: mudanças locais de código, assets, testes e documentação aguardando
  commit; saídas em `out/` permanecem fora do Git por política.

## Candidato HAMOOPIG

- Projeto: `SGDK_projects/HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]`
- Classificação: `technical_demo`
- Rota de build: Linux Wine bridge com `sdk/sgdk-2.11`
- Build local: passou em 2026-09-21
- ROM observada: `out/rom.bin`
- SHA-256 da ROM observada no fechamento: `9018c2c235b6d6acff8066ac96643c7148b54da97e280313de1dbb14a938aa9d`
- Tamanho: `2490368` bytes
- Mastering: `mastering_needs_fix`

## Gatilhos que permanecem abertos

- evidência BlastEm/P10 ainda aponta para ROM anterior (`8ac1…`);
- ausência de evidência BlastEm fresca ligada ao SHA acima;
- header ROM informa fim `0x000FFFFF`, menor que o arquivo entregue;
- validator de recursos reporta higiene da árvore, reports de tile/paleta,
  freshness/closeout, changelog e gate visual/audio stale;
- review independente vigente decide `revise_before_growth`;
- 36 casos P10 estão pendentes de nova captura/revalidação;
- a validação de contratos do workspace tem falhas de infraestrutura Linux
  porque vários testes invocam `powershell` em vez de `pwsh` e há uma fixture
  de dependência Python (`rpds`) quebrada.

## O que é recuperável pelo GitHub

O commit de fechamento deve conter o código-fonte, assets autorais usados pelo
`.res`, testes, manifests e documentação não ignorados. A ROM e a evidência
pesada ficam em artefatos de release/backup separados; `out/emulator_evidence`
e `out/audiovisual_review` não devem ser adicionados ao histórico Git.

## Regra de retomada

Após o download, conferir o commit e este SHA da ROM, reconstruir pela rota
Linux Wine bridge, corrigir o header/mastering, capturar evidência nova no
BlastEm e só então reabrir P10, freshness, closeout e qualquer promoção de
status.
