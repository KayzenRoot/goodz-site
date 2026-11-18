---
name: goodz-qa-evidence
description: "Use para testar e auditar mudanças GOODZ em Python, Docker, Playwright, frontend/mobile, imagens e segurança, gerando Evidence Bundle objetivo e veredito pt-BR."
---

# GOODZ QA & Evidence

## Preparação
Source Check contra `main` e PR em foco; leia Source Pack por hierarquia. Consulte `tests/test_app.py`, `tests/test_https_backup.py`, `tools/e2e_browser.py`, `.github/workflows/quality.yml`, `evidence/GOODZ-WEB-001.md`. Distinguir **previews simuladas**, API TestClient, HTTP real e HTTPS em host efetivo.

## Matriz de gates
- Mínimo: Pytest + compileall + sintaxe JS; E2E Playwright com backend real cobrindo login, upload, CRUD, logout e versões desktop/mobile.
- Design: imagens com carregamento real, screenshot vs `reference-concept.jpg`, contraste/teclado, viewport 320 a 1440 e estados vazios.
- Segurança: autorização de cada API administrativa, CSP, CSRF/Origin, cache, uploads e logs; SCA e problemas conhecidos sem ocultação.
- Dados: gravação SQLite e arquivos após reinício, backup consistente e restauração isolada.
- Infra: build Docker real, permissões, proxy TLS e roteamento para o host/domínio aprovado. Testes de TLS autoassinado local **não** provam TLS público.

## Evidence Bundle e auditoria
Registre Work Order, base/head SHAs, arquivos, diff, comandos, resultados stdout relevantes, run CI, screenshots, riscos, decisões, falhas corrigidas e Checkpoint Delta PROPOSED. Carimbe cada teste PASS/FAIL/NOT_RUN/BLOCKED; nunca transforme NOT_RUN em PASS. Auditoria final pt-BR: APPROVED, CORRECTION REQUIRED ou BLOCKED. Sem merge/deploy/atualização canônica se DoD faltar. Issue: GZ-QA-001 (#12).
