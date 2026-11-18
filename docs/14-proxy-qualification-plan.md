# R01 — Plano de qualificação do proxy e limites de borda

**Status:** `SPECIFICATION_ONLY / NOT_RUN / NO PRODUCTION CLAIM`. Este documento especifica testes futuros; nenhum teste de proxy real, IP, Host, rate limit ou limite de upload foi executado neste incremento. A execução exige ambiente de homologação aprovado, domínio/chain TLS de teste e autorização separada.

## 1. Objetivo e escopo

Qualificar o caminho `cliente → reverse proxy → Uvicorn/FastAPI` para que decisões de segurança não dependam de cabeçalhos controlados pelo visitante. Cobre:

- IP real do cliente e rate limit por IP;
- cadeia `X-Forwarded-For` / `X-Forwarded-Proto` / `X-Forwarded-Host` e `FORWARDED_ALLOW_IPS`;
- validação de `Host` e rejeição de host forjado;
- limites de corpo no proxy e na aplicação, antes do parser multipart;
- cookies `Secure`/`HttpOnly`/`SameSite=Strict`, HSTS e redirect HTTP→HTTPS;
- comportamento sob múltiplos clientes, IPv4/IPv6 e reinício do proxy.

Fora do escopo: migração de autenticação, Cloudflare Access/Clerk, deploy, DNS, VPS, preços, conteúdo comercial e alteração de funcionalidades.

## 2. Pré-requisitos de execução

1. Ambiente de homologação isolado, sem dados reais, com o mesmo `ops/goodz.nginx.conf` e `compose.yaml` do release candidato.
2. Dois endereços de cliente distintos (IPv4 e, se aplicável, IPv6) e um cliente fora da rede do proxy.
3. Certificado de teste confiável pelo cliente de teste; nunca usar certificado autoassinado para declarar qualificação pública.
4. `FORWARDED_ALLOW_IPS` configurado apenas com o IP do proxy de homologação.
5. Acesso somente leitura a logs do proxy e da aplicação; nenhum segredo em evidência.
6. Aprovação explícita do owner para executar em homologação; nenhuma execução automática.

## 3. Matriz de testes

| ID | Cenário | Ação | Oráculo esperado | Evidência mínima |
|---|---|---|---|---|
| PX-01 | Bypass direto do proxy | Acessar a porta do app fora do proxy a partir de outro host | Conexão recusada ou bloqueada; app não exposto publicamente | `curl`/`nc` com saída e regra de firewall/porta |
| PX-02 | `Host` forjado | Enviar `Host: evil.example` e `Host` ausente ao vhost | 400/403 ou vhost default; nenhum conteúdo administrativo | Request/response e log do Nginx |
| PX-03 | `X-Forwarded-For` forjado | Enviar 1, 2 e 5 valores, incluindo IP do atacante antes do IP real | App e rate limit usam somente o IP do cliente confiável, não o primeiro header | Logs com IP resolvido e resposta do endpoint de login |
| PX-04 | Rate limit por IP real | 6 falhas de login em 15 min do IP A; simultaneamente 1 falha do IP B | IP A bloqueado; IP B não bloqueado; nenhum lockout global | Timestamps, status HTTP e linhas de rate limit |
| PX-05 | Proto/Host encaminhados | Requisição HTTPS via proxy com proto/host corretos e depois headers conflitantes | Cookies `Secure`, redirect/HSTS coerentes; headers não confiáveis não alteram a origem | Headers de resposta e cookie jar |
| PX-06 | Corpo acima do limite no proxy | `Content-Length` e corpo acima de `client_max_body_size` | Proxy recusa antes do app; sem parser multipart, sem escrita | Status do proxy, ausência de log de parser e arquivo não criado |
| PX-07 | Corpo acima do limite no app | Bypass controlado ao app com `Content-Length` acima de 8 MiB + overhead | 413 antes do parser; estado e disco inalterados | Status, log e ausência de arquivo temporário |
| PX-08 | `Content-Length` ausente / chunked | Upload com `Transfer-Encoding: chunked` e sem tamanho | Recusa tipada antes do parser; nenhuma mutação | Request e resposta |
| PX-09 | Origin/Referer malformados | Origin e Referer inválidos, IPv6 inválido, porta inválida em escrita autenticada | 403 sem mutação; nenhum 500 | Respostas e diff do banco/arquivos |
| PX-10 | Múltiplos clientes e IPv6 | Requisições concorrentes de dois IPs, incluindo IPv6 normalizado | Rate limit e logs separam corretamente; sem colisão de chave | Logs agregados e contadores por IP |
| PX-11 | Reinício e keep-alive do proxy | Reiniciar Nginx durante tráfego de teste; repetir requisições | App permanece íntegro; sessões/cookies conforme contrato; sem 500 persistente | Logs e sequência de requisições |
| PX-12 | TLS/HSTS e cadeia | Validar certificado, redirect 80→443 e HSTS no domínio de homologação | Chain válida, TLS 1.2/1.3, HSTS e cookies Secure | `openssl s_client`, headers e relatório do cliente |

## 4. Critérios de aprovação

- Todos os testes PX-01..PX-12 executados com evidência por ID e SHA do release candidato.
- Nenhum spoofing de `X-Forwarded-For`, `Host`, `X-Forwarded-Proto` ou `X-Forwarded-Host` altera IP, origem, cookies ou limites.
- Nenhum upload acima do limite chega ao parser multipart ou cria arquivo.
- Nenhum HIGH/CRITICAL conhecido; qualquer falha recebe correção no mesmo Work Order/CD com teste-before-fix.
- Relatório pt-BR com PASS/FAIL por ID; ausência de execução é `NOT_RUN`, nunca PASS.

## 5. Stop conditions

Interromper e reportar `BLOCKED` se: ambiente/DNS/TLS de homologação não estiver aprovado; não houver dois clientes reais; logs contiverem segredos; qualquer teste exigir alteração fora de `GOODZ-WEB-001/CD-01`; ou houver achado HIGH/CRITICAL sem mitigação comprovada. Não executar este plano em produção, não alterar DNS/VPS e não promover checkpoint por inferência.
