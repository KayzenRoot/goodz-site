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
