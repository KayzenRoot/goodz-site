# Publicação da GOODZ

O domínio definitivo, o host de produção e os destinos de pedido aguardam confirmação. O exemplo usa `site.example.invalid`. A qualificação de CI em ambiente descartável cobre TLS local, recuperação local de SQLite e uploads, reinício do contêiner e jornada do painel. [Evidências anteriores](https://github.com/KayzenRoot/goodz-site/actions/runs/44335563382)

## Preparar a versão no servidor Linux

1. Defina `COMPOSE_PROJECT_NAME=goodz` no ambiente operacional ou em arquivo de ambiente fora do checkout e use o mesmo nome ao atualizar. O nome identifica o volume persistente. Registre o commit aprovado e mantenha a imagem da versão anterior no host.
2. No checkout limpo do commit aprovado, execute os comandos abaixo. Inicialize a senha no terminal interativo privado durante o primeiro provisionamento. Em atualizações, preserve a conta operacional e faça backup antes de trocar a imagem.

```bash
export COMPOSE_PROJECT_NAME=goodz
export GOODZ_RELEASE=$(git rev-parse HEAD)
docker compose config --quiet
docker compose build site
docker compose run --rm site python -m app.cli set-password
docker compose up -d --no-build
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/api/site
```

A raiz do contêiner é somente leitura. O volume em `/app/data` persiste SQLite e imagens. `/tmp` é temporário e a porta atende em loopback. O padrão é `COOKIE_SECURE=1`. Somente para desenvolvimento HTTP em loopback, exporte `COOKIE_SECURE=0` antes de subir o ambiente local.

## Ativar o proxy e verificar o domínio

Use Nginx diretamente no host. Restrinja o acesso SSH e libere publicamente apenas as portas da web. Crie o registro DNS aprovado apontando para o host autorizado. Confirme os destinos IPv4 e IPv6 publicados e a titularidade do domínio. Providencie o certificado para o domínio exato e configure sua renovação, por exemplo com o cliente ACME do host. Para o primeiro certificado com webroot, ative inicialmente apenas o bloco HTTP com o caminho do desafio gravável pelo cliente ACME.

Substitua todas as ocorrências de `site.example.invalid` em uma cópia de `ops/goodz.nginx.conf`, ajuste os caminhos do certificado, instale a configuração no host e valide com `nginx -t` antes do reload. Confira no navegador a cadeia TLS, o redirecionamento e o HSTS. O proxy limita o corpo a 9 MiB e substitui os cabeçalhos de encaminhamento pelo protocolo e IP observados na conexão. Esse exemplo pressupõe tráfego direto ao Nginx.

Descubra o endereço do gateway da rede do serviço com `docker inspect "$(docker compose ps -q site)" --format '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}'`. Em uma ponte Docker dedicada, confirme em homologação que é o par TCP visto pelo Uvicorn para conexões vindas do Nginx. Defina `GOODZ_PROXY_IP` com esse IP individual e recrie o serviço. Valide que dois clientes de IP distintos produzem identificação distinta no aplicativo e que cabeçalhos enviados pelo visitante não mudam essa identificação. Restrinja o acesso de usuários e contêineres locais ao host.

Antes de abrir tráfego, valide login, alteração de texto, senha e logout, atributos Secure/HttpOnly/SameSite, upload aceito e limite do proxy. Faça o teste com dados descartáveis na homologação. No domínio final, confira saúde e dados, as fotos, os dois destinos de pedido oficiais e os resultados do primeiro backup.

## Backup fora do host

O script foi preparado para Bash/Linux, Compose, flock e restic. No servidor, configure um repositório restic fora da VPS com credencial de escopo limitado. Gere a senha do repositório fora do Git, guarda independente para recuperação e arquivo legível apenas pelo operador. Configure `RESTIC_REPOSITORY`, `RESTIC_PASSWORD_FILE`, as credenciais do backend e `GOODZ_BACKUP_TMP` (diretório privado em disco cifrado, com espaço para o volume). Inicialize o repositório novo uma única vez com `restic init`.

No diretório da versão, use o mesmo projeto Compose, imagem e ambiente do deploy. Rode `bash ops/backup.sh`. O script para brevemente a aplicação, copia o volume em repouso, reinicia o serviço e envia o arquivo ao repositório cifrado. Há interrupção durante a cópia local. Um erro de transporte encerra com falha. Após interrupção do host, confira a aplicação e remova arquivos temporários residuais somente após confirmar os caminhos. Agende a execução pelo timer ou cron do operador em horário aprovado, com alerta para código de saída diferente de zero e para ausência de snapshots recentes. Defina a retenção com o responsável, valide `restic snapshots --tag goodz` e execute `restic check` periodicamente.

## Ensaio de restauração e rollback

Use no ensaio uma máquina de recuperação e uma cópia confiável da imagem. Escolha um snapshot com a tag goodz e confirme a versão da aplicação associada no registro operacional. Guarde o ID do snapshot, a versão e o horário de cada implantação. Use um projeto Compose novo e porta em loopback diferente. O comando abaixo aceita um volume novo com a pasta uploads vazia criada pela imagem. Extrai apenas em volume isolado e impede sobrepor um banco existente.

```bash
set -eo pipefail
export COMPOSE_PROJECT_NAME=goodzdrill$(date +%s)
export GOODZ_PORT=18080
: "${GOODZ_RELEASE:?defina a versão da imagem restaurada}"
: "${SNAPSHOT:?defina o ID do snapshot conferido}"
restic dump "$SNAPSHOT" /goodz.tar | docker compose run --rm -T --no-deps site sh -ec \
  'cd /app/data; test ! -e goodz.sqlite3; tar -xf -; test -s goodz.sqlite3'
docker compose run --rm -T site python -c "import sqlite3; db=sqlite3.connect('/app/data/goodz.sqlite3'); assert db.execute('pragma integrity_check').fetchall()==[('ok',)]"
docker compose run --rm site python -m app.cli set-password
docker compose up -d --no-build
curl -fsS http://127.0.0.1:18080/health
curl -fsS http://127.0.0.1:18080/api/site
```

Use a senha operacional vigente no procedimento interativo para invalidar sessões do snapshot. Confira um produto conhecido e sua imagem, abra o painel via HTTPS em homologação e registre o tempo total e a data do conteúdo recuperado. Para rollback apenas de imagem, retome o projeto original e a tag anterior, preserve o volume somente se o esquema continuar compatível e execute `docker compose up -d --no-build`. Caso os dados também exijam recuperação, mantenha o serviço afetado fora de tráfego, restaure em projeto novo pelo procedimento acima e aponte o proxy ao serviço recuperado somente após o aceite. Registre alterações posteriores ao snapshot a reconciliar e preserve o volume anterior.

## Dependências

As versões e hashes de produção em `requirements.txt` são gerados a partir de `ops/requirements.in`. O arquivo de desenvolvimento fixa também as dependências de teste com as mesmas restrições de produção. Para atualizar, rode os comandos de geração escritos nos cabeçalhos dos dois arquivos, execute `pip-audit -r requirements.txt --disable-pip --no-deps` e revalide CI, imagens e uploads antes da publicação.

O CI `GOODZ Quality` gera, por commit, relatórios de SCA (`pip-audit`), SAST (`bandit`), SBOM CycloneDX, inventário de licenças e proveniência no artefato `goodz-security-<sha>`. A ausência, corrupção ou vulnerabilidade conhecida em qualquer relatório reprova o job `security`; um achado HIGH de SAST também reprova. Não substituir esse gate por inspeção manual.

A imagem-base `python:3.12-slim` é fixada por digest multi-arquitetura no `Dockerfile`. Toda atualização deve ser feita em PR próprio do mesmo Work Order, verificar o digest oficial e as plataformas `linux/amd64` e `linux/arm64` com `bash tools/verify_base_image.sh`, reconstruir com `--no-cache`, executar o smoke e o teste de reprodutibilidade de dependências, e registrar o novo digest na evidência antes de publicar. Não trocar o digest por conveniência sem essa cadeia.
