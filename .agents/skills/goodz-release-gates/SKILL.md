---
name: goodz-release-gates
description: "Use para qualificar e documentar deploy GOODZ com Docker, Nginx, HTTPS, domínio, backup restic, rollback e decisão go/no-go. Não publica sem autorização."
---

# GOODZ Release Gates

## Source Check
Leia Source Pack, `docs/08-deployment.md`, `ops/goodz.nginx.conf`, `ops/backup.sh`, `compose.yaml`, `Dockerfile`, CI e issues GZ-DEPLOY-001 (#10), GZ-BACKUP-001 (#11) e GZ-RELEASE-001 (#13).

## Ordem necessária
1. Validar ratificação do host/domínio/provedor, licença e links externos sem inventar valores (D003–D006).
2. Fazer preflight read-only da VPS e snapshots; staging isolado antes de publicar. Se acesso inexistente, listar bloqueio e não simular execução.
3. Qualificar Nginx `nginx -t`, cadeia HTTPS, renovação, HSTS, tamanho máximo do body, headers confiáveis e bind da aplicação apenas em loopback.
4. Qualificar Docker sem root, rootfs read-only, volumes, health, reinício, logging e rollback por imagem/commit fixado.
5. Ensaio real de backup criptografado **offsite** e restauração de banco + uploads em instância independente, com evidência de integridade e tempos.
6. Aprovar gates de segurança, conteúdo comercial real, visão mobile/desktop, Core Web Vitals, E2E contra backend real e smoke HTTP externo antes de solicitar autorização para deploy.

## Condições de parada
Não criar DNS, trocar credenciais, fazer merge, habilitar indexação, apagar arquivos ou promover checkpoint por inferência. Se qualquer HIGH/CRITICAL conhecido ou evidência ausente: BLOCKED. Entregue matriz de go/no-go e runbook de rollback, ambos em pt-BR, com base/head SHA e provas reais. Após autorização expressa e go-live validado, propor Checkpoint Delta para auditoria.
