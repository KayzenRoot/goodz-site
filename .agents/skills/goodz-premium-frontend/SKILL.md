---
name: goodz-premium-frontend
description: "Use para refinamento de landing page GOODZ com estética premium em grafite/dourado/creme, experiência mobile, UX, CSS, acessibilidade e CTAs Pastelaria/Dogueria. Não amplia checkout ou stack."
---

# GOODZ Premium Frontend

## Ler antes de editar
Source Pack completo na ordem do `AGENTS.md`; `static/index.html`, `static/styles/site.css`, `static/scripts/site.js`, `static/assets/reference-concept.jpg`, skill `goodz-brand-guardian` quando mexer em identidade. Compare PR #1 e screenshots E2E reais, não apenas preview com API simulada.

## Fluxo
1. Observe a landing atual antes de modificar: hero, dois cartões de especialidade, produtos filtráveis, Sobre, footer e links.
2. Defina problema mensurável por viewport 320, 375, 390, 768, 1024 e 1440px: cortes, densidade, falta de hierarquia, contraste, imagem quebrada, foco, CLS ou CTA.
3. Faça menor correção que respeite D001 e D002. Preserve marcas e canais separados: iFood pertence à Pastelaria, 99Food à Dogueria; quando link faltar, não invente destino.
4. Trabalhe com layout responsivo e conteúdo dinâmico real, evitando bibliotecas externas e efeitos pesados sem necessidade. Respeite `prefers-reduced-motion`.
5. Confirme texto com a fonte comercial aprovada. Não invente preço, avaliações, horário, endereço ou depoimentos.
6. Teste vazio, erro de API, imagem ausente, texto longo, teclado, ARIA e links com `rel=noopener noreferrer`.

## Gate
Entregue screenshots before/after em mobile e desktop, Playwright contra backend real, checagem de imagens e console, contraste e orçamento de performance. Não declare sucesso visual sem comparação com `reference-concept.jpg` e aprovação do owner para desvios de marca. Issues: GZ-FE-001 (#4), GZ-WEB-001 (#8).
