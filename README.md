# GOODZ | Landing Page + Painel

Site institucional da marca GOODZ, com duas frentes independentes: **GOODZ Pastelaria** (iFood) e **GOODZ Dogueria** (99Food). Linguagem visual premium em grafite, dourado e creme, baseada na arte selecionada pelo proprietário.

**Situação em 18/11/2026.** A vitrine abre com as duas especialidades. O painel controla fotos, produtos e canais. A publicação aguarda domínio, hospedagem e conteúdo comercial confirmados.

## Início rápido (Python 3.12+)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m app.cli set-password
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Landing page: http://127.0.0.1:8000
- Painel: http://127.0.0.1:8000/admin
- Testes: `pip install -r requirements-dev.txt && pytest -q`

A senha é definida localmente e armazenada como hash scrypt. O site não publica credenciais de demonstração. As alterações persistem em `data/goodz.sqlite3`, e as imagens enviadas ficam em `data/uploads/`.

## Implantação com Docker (na VPS)

```bash
docker compose build
docker compose run --rm site python -m app.cli set-password
docker compose up -d
```

Para exposição pública, configure **um reverse proxy HTTPS** (Caddy/Nginx), `COOKIE_SECURE=1`, backups periódicos do diretório `data/` e firewall. Nunca exponha a porta 8000 diretamente na internet. Veja `docs/08-deployment.md`. Arquivos editados no admin persistem num volume Docker.

## Admin

1. Entre com a senha em `/admin`.
2. Em **Identidade**, envie logos separados (PNG/WebP/JPG).
3. Em **Banners**, troque a foto da seção Sobre e as imagens das duas especialidades e os textos.
4. Em **Produtos**, crie/edite/remova produtos e envie fotografias; valores são opcionais.
5. Em **Delivery & Redes**, configure os links reais do iFood, 99Food, Instagram, TikTok e WhatsApp.
6. Em **Segurança**, altere a senha do administrador.

## Escopo

Sem carrinho, pagamento, sistema de pedidos, integrações com agregadores, editor drag-and-drop ou multiusuário. O conteúdo público é responsivo e sem dependências JS de terceiros. A vitrine começa vazia para não inventar produtos ou preços; cadastre os produtos reais no painel.

## Hierarquia de fontes

`docs/12-checkpoint.md` > `docs/11-decisions-ledger.md` > `docs/03-scope.md` > `docs/10-definition-of-done.md` > `docs/04-architecture.md` > `docs/02-requirements.md` > demais fontes. Arte de referência original preservada em `static/assets/reference-concept.jpg`.

## Prévia visual local (opcional)

Com Chromium e Playwright para Python instalados, execute `PYTHONPATH=. python tools/visual_preview.py`. Ele usa respostas de API simuladas para validar layout e navegação básica do painel; os testes reais de API ficam em `tests/`. Consulte `evidence/GOODZ-WEB-001.md`.

## Qualificação de pré-deploy (GOODZ-WEB-001/CD-01)

O workflow de PR executa 3 gates independentes: testes Python + TLS local autoassinado + restauração SQLite/arquivos; build Docker em loopback e volume persistente; Playwright com backend Uvicorn real e Chrome no runner Ubuntu 24.04. Resultados e capturas: https://github.com/KayzenRoot/goodz-site/actions/runs/44335011085. **Nada foi implantado publicamente.** Reverse proxy HTTPS real, domínio, senhas de produção, links comerciais e backup cifrado externo precisam de validação independente antes do merge/deploy.
