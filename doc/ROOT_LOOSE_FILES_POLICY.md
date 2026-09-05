# Root Loose Files Policy

Status: `canonical_workspace_policy`

## Regra

Arquivos soltos na raiz do workspace sao proibidos por padrao.

Permitidos na raiz:

- `AGENTS.md`
- `README.md`
- arquivos de configuracao ja canonicos e existentes
- `.ai-memory.toml` como marcador consultivo controlado por `tools/sgdk_wrapper/prepare_ai_memory_integration.ps1`
- documentos historicos explicitamente mantidos por curadoria

Todo material operacional de projeto deve ficar dentro do proprio projeto em `SGDK_projects/<project>/` ou `SGDK_Engines/<project>/`.

## Destinos Canonicos

| Material | Destino |
|---|---|
| documentacao do projeto | `<project>/doc/` |
| memoria operacional | `<project>/doc/10-memory-bank.md` |
| changelog | `<project>/doc/changelog/changelog.md` |
| manifesto de tecnicas usadas | `<project>/doc/technique_usage_manifest.json` |
| assets fonte do projeto | `<project>/data/source_art/` ou `<project>/data/` |
| recursos SGDK | `<project>/res/` |
| codigo | `<project>/src/` e `<project>/inc/` |
| evidencias | `<project>/out/evidence/` |
| logs e reports | `<project>/out/logs/` |
| experimentos locais | `<project>/out/experiments/` |

## Excecoes

Excecoes so sao validas quando:

1. o artefato e parte canonica do workspace em `doc/` ou `tools/sgdk_wrapper/`;
2. o artefato externo esta declarado em `doc/technique_usage_manifest.json > allowed_external_artifacts`;
3. ha motivo e autorizacao humana registrados.

## Curadoria

Ao encontrar arquivo solto:

1. classificar o material;
2. registrar origem, hash e destino proposto;
3. nao apagar imediatamente;
4. mover somente em rodada de curadoria com manifest, checksum e rollback.

Arquivo solto nunca pode ser usado como evidencia para `ready_for_aaa`, `delivery`, `stable` ou `testado_em_emulador`.
