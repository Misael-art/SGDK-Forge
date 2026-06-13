# PHOTO2SGDK: AI Agent Development Bible

Este documento estabelece as **regras rígidas de contexto e desenvolvimento** para qualquer IA (incluindo você) que trabalhe no projeto **Photo2SGDK**. A adesão a estas regras não é opcional e visa garantir a CX (Customer Experience) de nível "Photoshop".

---

## 💎 1. Princípios de CX (Customer Experience)
- **Zero Placeholders:** Nunca implemente uma função "vazia" ou com `todo`. Se uma funcionalidade for sugerida, ela deve ser funcional ou possuir um fallback elegante.
- **Nomenclatura Elite:** Use termos técnicos precisos (ex: `vramCost`, `subPaletteIndex`, `tileDeduplication`). Evite nomes genéricos.
- **Visual WOW:** Toda interface proposta deve seguir padrões modernos de design (Gradients, Glassmorphism, Typografia Inter/Outfit).

## 🛠️ 2. Regras de Desenvolvimento Proativo
- **Arquitetura "Safety First":** Todo tratamento de imagem deve ser atômico e idempotente. Se uma conversão falhar, o estado original deve ser preservado.
- **Documentação de Borda:** Cada nova função deve ser documentada com JSDoc/Docstring explicando não apenas *o que* faz, mas *por que* é necessário para as limitações do Mega Drive.
- **Performance Nativa:** O processamento de imagem pesado deve ocorrer no Backend Python (Numpy/OpenCV), nunca bloqueando a Main Thread da UI.

## 🤖 3. Contexto para IA (Prompting & Fluxo)
- **Contexto de Hardware:** Toda IA deve "saber" que o alvo é o Mega Drive (15 cores + transparência, 80 sprites na tela, tiles de 8x8).
- **Verificação Contínua:** Antes de entregar qualquer código, a IA deve validar se ele respeita o alinhamento de 8 pixels.
- **Mini-Preview First:** Qualquer funcionalidade de edição deve refletir a mudança instantaneamente na janela de Mini-Preview.

## 📐 4. Padrões de Código
- **Backend (Python):** Tipagem estrita com `mypy`, seguindo PEP8.
- **Frontend (React):** Componentes funcionais, Hooks customizados para lógica de Canvas, CSS-in-JS ou Vanilla CSS elegante.
- **Comunhão:** O contrato entre UI e Backend deve ser via JSON Schema bem definido.

---

> [!IMPORTANT]
> Se você é uma IA trabalhando neste projeto, sua prioridade número 1 é a **Consistência do Contexto**. Não "esqueça" das limitações do hardware ao sugerir efeitos modernos.
