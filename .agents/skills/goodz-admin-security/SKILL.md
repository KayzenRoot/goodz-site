---
name: goodz-admin-security
description: "Use em revisão HIGH_ASSURANCE do login, sessões, CSRF, uploads, proxy e decisão Cloudflare Access versus Clerk para o painel GOODZ. Não instala provedor sem ADR e domínio aprovados."
---

# GOODZ Admin Security

## Preflight obrigatório
Consulte Source Pack canônico, `docs/05-security.md`, `docs/08-deployment.md`, `app/main.py`, `compose.yaml`, `ops/goodz.nginx.conf`, testes e PR #1. Obtenha Context Lock e estado das decisões D003–D006; qualquer mudança em auth é HIGH_ASSURANCE.

## Escolha de autenticação
- Existe hoje uma senha local scrypt, sessão HttpOnly/SameSite=Strict/Secure no HTTPS, CSRF e proteção das rotas. Não presuma que é inexistente.
- Compare explicitamente **Cloudflare Access** com allowlist do administrador, IdP/MFA e JWT validado no origin, se domínio/infra forem compatíveis; **Clerk** é alternativa para gestão de identidade sem Access. Privy/Web3 não é exigido por este portal simples.
- Avalie custo oficial atual, confiabilidade, recuperação, revogação, contas e dependência do fornecedor. A escolha precisa de ADR ratificada; documentar rollback/migração de credenciais antes da troca.
- Feche bypass por IP/origem alternativa, hostname, `/admin` e `/api/admin/*`, spoofing de forwarded headers, CSRF, sessão expirada e upload fora de limite. Evite mecanismos paralelos sem modelo de trust boundary.

## Provas
Rode regressões de autenticação, CSRF, controle de sessão, upload malicioso e de grande porte, dependências e headers no proxy real. Exija validação independente dos achados HIGH/CRITICAL, nunca testes autodeclarados. Nada de chaves ou domínios internos no commit. Pare se acesso real, DNS, MFA ou segredo exigir decisão do owner. Issues: GZ-AUTH-001 (#6), GZ-SEC-001 (#7).
