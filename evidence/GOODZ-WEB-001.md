# Evidence Bundle · GOODZ-WEB-001

- Source Pack base SHA: `953a92dd2ff34189180f794a788a562ad71f96dc`.
- Head SHA (PR #1): `856c7527bd29b7873be4b5df24e1d83f2f951840` na primeira avaliação.
- Escopo: landing responsiva para marca GOODZ e submarcas; painel autenticado de textos, imagens, produtos e URLs; FastAPI, SQLite, Docker.
- Design: conceito 1, preto/grafite/dourado/creme, logos e mockups fornecidos na conversa e versionados.
- Segurança: sem senha default, scrypt, sessões hash/HttpOnly, SameSite Strict, CSRF, origem, rate limit, CSP, validação upload e reencode WebP.
- Local Python: `PYTHONPATH=. pytest -q` **7/7 PASS**; `python -m compileall -q app` PASS.
- GitHub Actions: **SUCCESS**, workflow GOODZ Quality, run **44322722923**, GitHub Python 3.12.
- Visual: Chromium desktop 1440 e mobile 390 sem overflow; painel abre e alterna abas em preview com backend simulado, NÃO é E2E remoto. Imagens `preview-*.webp`.
- Docker build e teste de restauração de backup: NÃO EXECUTADOS.
- Risco: HIGH_ASSURANCE para acesso administrativo. Antes da produção, confirmar HTTPS, senha de proprietário, backup/restore, revisão independente de auth e smoke remoto.
- Dados comerciais: não criar preços ou produtos fictícios, links para delivery e redes aguardam configuração real.
- Verdict: LOCAL_TESTED + CI_PASS, mas **PUBLIC_DEPLOY_BLOCKED**, merge condicionado à auditoria; não chamar RELEASE_COMPLETE.
- Proposed Checkpoint Delta após aprovação: site local funcional e CI 7/7; manter deploy bloqueado até evidências de produção.


## Auditoria de correção GOODZ-WEB-001/CD-01 (18/11/2026)
- Context Lock: `main=953a92dd2ff34189180f794a788a562ad71f96dc`; PR head inicial=`9d137512719e03d12e61b5fe7c2b7fded2c4e05b`; as fontes do Source Pack foram lidas na hierarquia canônica.
- Verificação remota: run GitHub Actions `44323982969` SUCCESS, job `test` (Dependencies, Tests, Compile all Python PASS).
- Evidências pré-correção: URL `https://[invalid` retornava HTTP 500 e `https://example.com:abc` ou `:99999` era aceito; nomes de produto somente espaços retornavam 201 e eram gravados como vazios; upload FastAPI com `UploadFile=File(...)` era processado pelo parser multipart antes do `current_session` da rota.
- Correções delimitadas: capturar `ValueError` de urlsplit/porta e rejeitar porta fora de intervalo; rejeitar nome que fica vazio após `.strip()` tanto na criação quanto edição; middleware recusa upload sem sessão/CSRF e com corpo declarado excessivo antes do parser. Limite independente no proxy permanece obrigatório.
- Testes locais após correção: `PYTHONPATH=. pytest -q` **11/11 PASS**; `python -m compileall -q app` **PASS**; `node --check static/scripts/admin.js` e `site.js` **PASS**. Teste adicional com monkeypatch do parser verifica rejeição antecipada sem processar multipart.
- Tentativa de navegador real contra serviço local bloqueada pelo runtime com `net::ERR_BLOCKED_BY_ADMINISTRATOR`; NÃO há E2E autenticado HTTP real aprovado. Visual anterior é preview com API simulada e permanece como tal.
- Docker disponível neste runtime: **não**, portanto imagem/compose não foram executados; não afirmar integração Docker aprovada.
- Veredito antes de auditoria independente: **CORRECTION PROPOSED / PUBLIC_DEPLOY_BLOCKED**, sem merge, sem deploy, sem atualização de checkpoint como concluído. Checkpoint Delta proposto: adicionar correções testadas e riscos residuais; DoD global incompleto.


## Readback de CI e smoke HTTP (18/11/2026)
- GOODZ-WEB-001/CD-01 aplicado no mesmo PR #1; commit corretivo inicial: \`ed2a201058b4f1ba11a4af9cd247fb94b1fb6bdb\`; `main` permanece no Source Pack `953a92dd2ff34189180f794a788a562ad71f96dc`.
- GitHub Actions run `44328778898`: **SUCCESS**, job `test` SUCCESS, log `11 passed, 1 warning in 2.28s`; build/execução Docker não está coberto pelo workflow.
- Com Uvicorn HTTP local real e cliente httpx (sem simular API): inicialização CLI, autenticação, CSRF, alteração de texto, upload PNG→WebP, CRUD de produto, logout e persistência SQLite **PASS**. Dados de teste foram criados em diretório temporário, sem produção.
- Chromium E2E com servidor real **BLOCKED PELO AMBIENTE** (`ERR_BLOCKED_BY_ADMINISTRATOR`). Não reivindicar prova de navegador real.
- Auditoria de segurança HIGH_ASSURANCE: revisão independente pendente; verificação de TLS/HSTS, cookie Secure sob domínio real, backup/restauração, limites do proxy, vulnerabilidades de dependências e smoke de recuperação continuam como gates explícitos. Sem autorização para publicar ou fundir PR.


## Evidence Bundle de continuidade · GOODZ-WEB-001/CD-01 · 18/11/2026

**Context Lock e proveniência**
- Source Check: main 953a92dd2ff34189180f794a788a562ad71f96dc; branch PR #1 Draft HEAD inicial 6676edaa74f3651f52954f56ff2db6b3233ca542.
- Hierarquia lida: checkpoint > Decisions Ledger > Scope > DoD > Architecture > Requirements > Security/Deployment/WO.
- Decisões D001/D002 APPROVED mantidas; D003 PROPOSED e D004/D005/D006 OPEN, sem decisões presumidas.
- Commits de continuidade: 051523c (validação Origin/Referer), 0d50804 (TLS/backup e harness E2E), 44859f6 (Docker/CI), f05f8f5 e d1a69e3 (correções demonstradas em CI), c09df4a (Chrome do runner).

**Defeito adicional comprovado e correção mínima**
- Preflight: Origin https://[bad em PUT /api/admin/settings com token válido causava ValueError e HTTP 500. Referer malformado igualmente.
- Correção: capturar ValueError do urlsplit, responder HTTP 403 e impedir mutação. Regressão automatizada no mesmo teste e Work Order. Nenhuma funcionalidade nova.

**Matriz de provas verificadas**
- Local PYTHONPATH=. pytest -q: 13/13 PASS; Python compileall + node --check PASS.
- GitHub Actions run 44335011085: job test SUCCESS, log 13 passed (Python 3.12); job container SUCCESS; job browser-e2e SUCCESS.
- TLS: self-signed localhost com certificado verificado em httpx, COOKIE_SECURE=1, cookie Secure/HttpOnly/SameSite=Strict, CSRF contra origem diversa, CRUD, upload e logout PASS (não é CA pública).
- Backup/recovery: sqlite3.Connection.backup em WAL + cópia de uploads durante janela sem escritas; PRAGMA quick_check ok; restauração em diretório isolado, texto/produto/WebP íntegros PASS. Backup offsite real NÃO verificado.
- Docker: build e config compose, docker run local nonroot/read-only/no-new-privileges/cap_drop, bind 127.0.0.1, volume e restart PASS. Sem VPS ou serviços públicos.
- E2E Chrome com servidor Uvicorn real e API sem mock: login, mudança hero_title, cadastro de dog com foto, vitrine desktop 1365px e mobile 390px, sem overflow horizontal, logout e reabertura não autenticada PASS.
- Screenshots guardadas em https://github.com/KayzenRoot/goodz-site/actions/runs/44335011085/artifacts/14441071881; workflow https://github.com/KayzenRoot/goodz-site/actions/runs/44335011085.
- A primeira tentativa de browser no ubuntu-26.04 falhou na instalação Playwright 1.57; correção limitada no CI foi utilizar Chrome já instalado no ubuntu-24.04. A segunda falha foi uma asserção que ignorava a quebra de linha visual do título, corrigida no harness. Não são falhas da landing.

**Auditoria e bloqueios**
- Scope R01-R08 permanece, sem checkout, pagamentos ou integrações. Nenhum link, preço ou contato fictício.
- Pendente: revisão independente HIGH_ASSURANCE da autenticação, verificação HTTPS com domínio/chain/HSTS e reverse proxy REAL (inclusive tamanho máximo de corpo e IP real no rate limit), proteção do painel, análise de dependências, backup offsite cifrado com recuperação na VPS, dados comerciais reais, decisões D003-D006 e autorização expressa de deploy/merge.
- Veredito: **BLOCKED para merge, publicação e RELEASE_COMPLETE**; correções de código e gates isolados PASS. **Checkpoint Delta PROPOSED**, sem editar ou promover docs/12-checkpoint.md.
- Riscos de regressão restantes: configuração do proxy, versões de dependência sem lock, proteção de credenciais e retenção de backups; nenhum HIGH conhecido declarado como resolvido sem prova.
