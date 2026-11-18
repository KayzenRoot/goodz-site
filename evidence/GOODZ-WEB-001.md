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

## Correction Delta GZ-SEC-001 F01/F02 + R01 — 18/11/2026

**Autorização delimitada:** GOODZ-WEB-001/CD-01, PR #1 Draft, branch `feat/goodz-web-001-landing-admin`. Base main `953a92dd2ff34189180f794a788a562ad71f96dc`; HEAD de entrada `8c891b3388263231596984e1bfde0db1ddb8dff9`; HEAD deste delta `03d6b492104dd90474d22224b72f795c9c436404`; ambos revalidados antes da edição. Sem merge, deploy, DNS, VPS, segredos ou promoção de checkpoint.

### F01 — cadeia de dependências e relatórios por commit

- Job `security` no workflow `GOODZ Quality` instala ferramentas CI fixadas em `ops/requirements-security.txt` (bandit 1.9.4, cyclonedx-bom 8.0.1, pip-audit 2.10.1, pip-licenses 5.5.5 e transitivas resolvidas).
- SCA de produção (`requirements.txt`, 21 pacotes) e desenvolvimento (`requirements-dev.txt`, 29 pacotes) via pip-audit JSON.
- SAST de `app/` via bandit JSON; o gate falha em severidade HIGH.
- SBOM CycloneDX 1.6 com 22 componentes e inventário de licenças de 21 pacotes de produção.
- `tools/validate_security_reports.py` falha fechado para relatório ausente/corrompido, vulnerabilidade conhecida, SAST HIGH, SBOM inválido, licença desconhecida e proveniência incompleta.
- Artefato `goodz-security-<sha>` com retenção de 90 dias, contendo os relatórios e `provenance.json` com commit, ref, workflow e run.
- Resultado local observado (Windows; uvloop é marcado por plataforma e não entra no audit local): `SCA(production) packages=21 vulnerabilities=0; SCA(development) packages=29 vulnerabilities=0; SAST findings=1 high=0; SBOM components=22; licenses packages=21 unknown=0; SECURITY_REPORTS_OK`.
- O único achado SAST é B608 MEDIUM em `app/main.py:215`; o trecho monta `WHERE visible=1` a partir de constante interna, não de entrada do usuário. Não foi suprimido; permanece visível no relatório e não é HIGH.

### F02 — imagem-base fixada e multi-arquitetura

- `Dockerfile` fixa `python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b` (índice oficial 3.12.16-slim-trixie).
- Digest confirmado de forma independente pelo header `Docker-Content-Digest` do Docker Hub e por `docker buildx imagetools inspect`.
- `tools/verify_base_image.sh` rejeita tag sem digest, digest divergente e ausência de `linux/amd64`/`linux/arm64`; executado localmente: `BASE_IMAGE_OK digest=sha256:5e2bdb… platforms=linux/amd64,linux/arm64 python=3.12`.
- Job `container` passa a rodar a verificação, o smoke e o build real em `ubuntu-latest` (amd64) e `ubuntu-24.04-arm`.
- Reprodutibilidade de dependências: `tools/check_image_reproducibility.sh` compara Python e closure de pacotes entre o build do smoke e um rebuild `--no-cache`; local `IMAGE_REPRO_OK packages=23`. Não é alegada reprodutibilidade bit-a-bit de camadas.
- Build amd64: smoke PASS (build, loopback, nonroot, rootfs read-only, SQLite persistente após restart).
- Build arm64 por emulação local: `python:3.12.16`, `aarch64`; container read-only com volume respondeu `/health` 200 em 18 s. A execução nativa arm64 será comprovada pelo CI do runner arm.

### R01 — especificação apenas, não executada

- `docs/14-proxy-qualification-plan.md` define PX-01..PX-12 para bypass do proxy, Host, X-Forwarded-For/Proto/Host, rate limit por IP real, limites de corpo no proxy/app, chunked, Origin/Referer, IPv6, reinício e TLS/HSTS.
- Status explícito `SPECIFICATION_ONLY / NOT_RUN`; nenhum teste de proxy, IP real ou borda foi executado e nenhum PASS é reivindicado.

### Testes locais observados

- `PYTHONPATH=. pytest -q`: **13 passed**, 1 warning (mesmo warning Starlette/httpx anterior).
- `python -m compileall -q app tests tools`: PASS.
- `node --check static/scripts/admin.js` e `site.js`: PASS.
- `bash -n` dos dois novos scripts: PASS.
- `tools/validate_security_reports.py`: PASS com relatórios reais e FAIL fechado nos quatro casos negativos testados (vulnerabilidade sintética, SAST HIGH sintético, licença desconhecida e relatório ausente).
- `tools/ci_docker_smoke.sh`: PASS com `GITHUB_RUN_ID` definido; a invocação local sem a variável produz nome de volume inválido, comportamento pré-existente do harness, não introduzido por este delta.
- `tools/check_image_reproducibility.sh`: PASS.
- Docker build arm64 por emulação: PASS e health 200.

### CI remota no HEAD 03d6b49

Run [44400617794](https://github.com/KayzenRoot/goodz-site/actions/runs/44400617794) no HEAD `03d6b492104dd90474d22224b72f795c9c436404`, PR #1:

- `security` SUCCESS (job 135142289248): `SCA(production) packages=22 vulnerabilities=0; SCA(development) packages=29 vulnerabilities=0; SAST findings=1 high=0; SBOM components=22; licenses packages=22 unknown=0; SECURITY_REPORTS_OK`.
- Artefato `goodz-security-03d6b492104dd90474d22224b72f795c9c436404` (id 14472154679), 64.768 bytes, não expirado; `provenance.json` confirma commit `03d6b49…`, merge commit `8ce4664…`, PR 1, run 44400617794.
- `container (ubuntu-latest, true)` SUCCESS (job 135142289364): `BASE_IMAGE_OK`, `Docker PASS`, `IMAGE_REPRO_OK packages=23`.
- `container (ubuntu-24.04-arm, false)` SUCCESS (job 135142289025): `BASE_IMAGE_OK`, `Docker PASS` com wheels `aarch64`.
- `test` SUCCESS (job 135142289604): `13 passed, 1 warning in 2.68s`.
- `browser-e2e` SUCCESS (job 135142289338): `Browser E2E PASS with real backend, upload, admin and both viewports`.
- Socket Security: PR Alerts e Project Report PASS.

### Limitações e riscos

- Relatórios CI serão os autoritativos por HEAD e run; valores locais acima não substituem o run remoto.
- SAST cobre `app/` com bandit, não toda a superfície de scripts/CI; não é prova de ausência de vulnerabilidades.
- SCA depende das bases OSV/PyPI disponíveis no momento; ausência de achado não é garantia absoluta.
- Licenças foram inventariadas, mas D006 continua OPEN; nenhuma licença do projeto foi escolhida ou ratificada.
- Arm64 local foi emulado; a prova nativa depende do runner CI correspondente.
- R01 permanece NOT_RUN; proxy real, IP real, Host, rate limit e limites de borda continuam gate de homologação.
- Não há alegação de RELEASE_COMPLETE, merge, deploy ou segurança integral.

### Checkpoint Delta PROPOSED (não promovido)

Registrar que F01/F02 foram implementados e provados em CI no HEAD deste delta, com artefato por commit e digest verificado; manter R01 NOT_RUN, D003 PROPOSED, D004-D006 OPEN, deploy/merge bloqueados e `docs/12-checkpoint.md` intacto até auditoria e autorização posteriores.
