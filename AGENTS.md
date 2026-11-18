# GOODZ | Orientação para agentes

Repositório GOODZ: marca principal GOODZ, submarcas GOODZ Pastelaria e GOODZ Dogueria. Este arquivo orienta execução, não substitui o Source Pack.

## Hierarquia de verdade
1. `docs/12-checkpoint.md`
2. `docs/11-decisions-ledger.md`
3. `docs/03-scope.md`
4. `docs/10-definition-of-done.md`
5. `docs/04-architecture.md`
6. `docs/02-requirements.md`
7. Código, Git, testes e evidência prevalecem sobre memória de conversa. Discrepâncias exigem revisão, não aprovação implícita.

Antes de agir, faça Source Check da branch, HEAD, PR, issues e hashes das fontes críticas. Bloqueie execução se contexto estiver STALE ou PR #1 exigir correções. Planeje apenas o incremento NECESSARY permitido, com Work Order estável e Context Lock. Executor inspeciona código, aplica delta mínimo, testa, registra Evidence Bundle, abre/atualiza PR e apresenta revisão final em pt-BR. Apenas auditoria objetiva permite APPROVED e Checkpoint Delta. Sem merge ou deploy automaticamente.

## Identidade e limites
- D001 APPROVED: Conceito 1, GOODZ (marca-mãe), GOODZ Pastelaria e GOODZ Dogueria, grafite/preto, dourado e creme.
- D002 APPROVED: landing page + painel administrativo *simples* para imagens, logos, banners, textos, produtos e links.
- D003 PROPOSED; D004–D006 OPEN. Não presumir domínio, host, licença, URLs comerciais, preços ou escolhas de autenticação.
- Arquitetura atual: FastAPI, SQLite, HTML/CSS/JS simples e imagens WebP. Não migrar stack, adicionar checkout, estoque, multiusuário, editor drag-and-drop ou integrações por conveniência.
- PR #1 Draft e GOODZ-WEB-001/CD-01 continuam vinculados aos gates de produção. Issues de preparo não autorizam avançar os incrementos.
- Para o site, usar como referência visual `static/assets/reference-concept.jpg` e os arquivos reais em `static/assets/`; não confundir arte conceitual com SVG vetorial final.

## Skills deste repositório
Carregue só quando útil, por gatilho:
- `goodz-brand-guardian`: fidelidade do logo, paleta, assets e versões da marca.
- `goodz-premium-frontend`: landing, responsive, efeitos, conversão e acessibilidade.
- `goodz-admin-content`: painel, uploads, imagens, produtos e estados UX.
- `goodz-admin-security`: autenticação, Clerk/Cloudflare Access, proteção de API e revisão.
- `goodz-qa-evidence`: regressão, E2E, visual, evidência e auditoria.
- `goodz-release-gates`: Docker, TLS, domínio, backup e go/no-go.

Cada skill mora em `.agents/skills/<name>/SKILL.md`. As instruções jamais promovem uma decisão OPEN/PROPOSED por conta própria.
