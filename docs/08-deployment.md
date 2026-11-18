# Deployment
Local: Python virtualenv + uvicorn. VPS: `docker compose`, com `data/` volume persistente e reverse proxy TLS. Defina senha de admin antes do deploy. Coloque `COOKIE_SECURE=1` sob HTTPS; não publique HTTP sem TLS. Backup deve copiar `data/goodz.sqlite3` de modo consistente (preferir SQLite online backup) e `data/uploads/`. Restauração: parada de container, restaurar DB e uploads e subir novamente. Configure domínio/HTTPS/URL de produção somente com autorização do proprietário. **Status: deployment público não realizado**.


## Próximo gate de HTTPS (PREPARADO, NÃO EXECUTADO)

**Bloqueado** até o proprietário fornecer/aprovar domínio, host final e links comerciais reais. Sem alteração de DNS, sem deploy, sem segredo persistido no Git.

1. No host aprovado, criar usuário administrativo operacional, firewall com SSH restrito e 80/443 públicos; a aplicação mantém somente `127.0.0.1:8000:8000` atrás de Caddy ou Nginx.
2. Emitir certificado TLS válido para o domínio aprovado; usar redirecionamento HTTP→HTTPS, HSTS somente após validar o domínio, cabeçalhos CSP já emitidos pela aplicação e limite de requisição no proxy de no máximo 9 MiB. Ajustar overhead caso necessário em teste de upload.
3. Definir `COOKIE_SECURE=1` no ambiente da aplicação e inicializar uma senha **privada de pelo menos 12 caracteres** pelo comando interativo. Não enviar senha ou segredos ao repositório/PR.
4. Configurar links iFood/99Food e redes sociais via painel; verificar que são URLs reais aprovadas. Não inventar contatos ou preços.
5. Backup consistente do SQLite via `sqlite3.Connection.backup()` e cópia sincronizada dos uploads; guardar fora do host, cifrar e testar restauração em uma instância isolada antes de produção. Preservar versões de backup e plano de rollback.
6. Gates: CI PASS, Docker build real, revisão independente da autenticação, teste de login/CSRF/upload/CRUD com backend real em HTTPS, tela mobile/desktop, cookies `Secure`/`HttpOnly`/`SameSite=Strict`, teste de upload acima de 8 MB, cabeçalhos, verificações `/health` e `/api/site`, backup/restore verificado e smoke test sem erros.
7. Fazer rollback sem expor credenciais: desligar tráfego do app, restaurar versão de imagem/backup da aplicação isoladamente e revalidar a saúde e o conteúdo; reversão de DNS só com autorização explícita.

**O limite de upload do middleware usa Content-Length e não substitui o limite do reverse proxy.** Não aceitar tráfego público sem limite independente configurado e verificado. A rota `/health` só indica processo vivo, não confirma integridade do banco, portanto verifique também `/api/site` no smoke test.


## Gates de qualificação reproduzidos no CI (não são deploy)
- Run https://github.com/KayzenRoot/goodz-site/actions/runs/44335011085: jobs test/container/browser-e2e SUCCESS (dados de teste e loopback).
- test: 13/13 Python 3.12, regressões auth e Origin, TLS autoassinado, recuperação SQLite WAL + uploads, compilação e sintaxe JavaScript.
- container: docker build, docker compose config, runtime user goodz sem privilégios, rootfs somente leitura, porta 127.0.0.1 e persistência de configuração após reinício.
- browser-e2e: Chrome do Ubuntu 24.04, Uvicorn real em localhost, fluxo login/edição/upload/produto/logout e verificação desktop/mobile. Screenshots no artefato do workflow.
- Exposição pública: BLOQUEADA. Ainda exigidos: domínio e links reais aprovados; proxy reverso em TLS com cadeia válida, redirect e HSTS; configuração de COOKIE_SECURE=1; rate limit que preserve IP real apenas atrás de proxy de confiança; limite de corpo no proxy; backup periódico criptografado fora do host, restauração ensaiada em destino isolado; verificação de segurança independente e smoke-test HTTPS de produção autorizado. Proibir mudança de DNS, credenciais reais ou publicação enquanto D003-D006 estiverem pendentes.
