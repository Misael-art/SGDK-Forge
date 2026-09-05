# LEGAL — Arquivo de referência e fan build de estudo

**Projeto:** KIRBY_FAN GAME GROK BUILD
**Natureza:** estudo técnico + **fan game non-commercial** (Mega Drive / SGDK).
**Não é** produto comercial, marketplace, free-to-play com ads/IAP, nem obra monetizada.

---

## 1. Titularidade de IP

- Personagens, nomes e universo **Kirby** são propriedade da **Nintendo Co., Ltd.** e/ou **HAL Laboratory, Inc.**
- Este repositório **não reivindica** ownership desses direitos.
- Uso aqui é de **fã / estudo / engenharia reversa visual educacional**, alinhado a builds **não comerciais e não publicadas em loja**.

---

## 2. The Spriters Resource (TSR)

Sheets em `raw/` vêm do [Spriters Resource](https://www.spriters-resource.com/).

Resumo do ToU do TSR (não substitui o texto oficial):

- Conteúdo pode ser usado onde **legalmente permitido** ou em obras **non-commercial / unpublished**.
- **Proibido** em obras comerciais: jogos pagos, free com ads/IAP, marketplace (Steam, App Store, Play), vídeos monetizados, sites com ads que redistribuem o sheet como produto.

**Neste projeto de fan/estudo, o uso de rips convertidos para:**

- calibração de pipeline (RGB333, 4bpp, index 0),
- comparação visual,
- **integração em `res/` e ROM fan local de estudo**,

está **explicitamente permitido pela política do projeto**, desde que o resultado continue **non-commercial** e **não** vá para marketplace/monetização.

---

## 3. O que este projeto permite (política interna)

| Uso | Status |
|---|---|
| Manter `raw/` + `versions/` + hashes no repo de estudo | **permitido** |
| Converter rips → PNG MD (quantize, crop, sheet 32×n) | **permitido** |
| Instalar conversões em `res/sprites`, `res/gfx` para fan build | **permitido** |
| Buildar `out/rom.bin` fan/estudo com esses assets | **permitido** |
| Publicar a ROM como produto comercial / loja / ads | **proibido** |
| Reupload dos sheets brutos como se fossem “seus assets” sem crédito TSR | **proibido** (ToU TSR) |
| Gerar arte **original** treinada nas premissas dos refs | **permitido e desejável** |

Não há barreira interna do tipo “ship só original”. A barreira é só:

1. **non-commercial / fan / estudo**, e
2. **crédito de proveniência** (MANIFEST + README).

---

## 4. Créditos

Para cada asset em `MANIFEST.json`:

- URL da página TSR
- ID numérico
- Nome do jogo
- sha256 local
- data de download

Ao distribuir a ROM **entre colaboradores de estudo**, manter o manifesto e este LEGAL acessíveis.

---

## 5. Se o status do projeto mudar

Se no futuro houver intenção de **comercializar** ou publicar em **marketplace**:

1. Remover rips de `res/` e da ROM.
2. Substituir por arte original (ou licenças explícitas).
3. Revisar este LEGAL e o README.

Até lá, **fan/estudo sem barreiras internas** para aprender e construir com referência TSR convertida.
