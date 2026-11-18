---
name: goodz-brand-guardian
description: "Use para auditar ou adaptar logo, cores, favicon, banners e identidade GOODZ Pastelaria/Dogueria, mantendo fidelidade ao Conceito 1 aprovado. Não use para criar identidade nova sem autorização."
---

# GOODZ Brand Guardian

## Contexto necessário
1. Source Check: `docs/12-checkpoint.md`, `docs/11-decisions-ledger.md` D001/D002, `docs/03-scope.md`, `docs/10-definition-of-done.md`, `docs/04-architecture.md`, `docs/02-requirements.md`.
2. Referência visual: `static/assets/reference-concept.jpg`. Arquivos já versionados: `logo-goodz.webp`, `logo-pastelaria.webp`, `logo-dogueria.webp`, `avatar-*.webp`, `favicon.png` em `static/assets/`.
3. Extraia tokens da implementação, não de uma suposição: `static/styles/site.css` define atualmente `--graphite: #181713`, `--cream: #fff3da`, `--gold: #f2bf59`. O metal dourado 3D da arte conceitual não equivale a um único hexadecimal plano.

## Processo
- Inspecione hash, dimensões, alfa/transparência e licenças/direitos das imagens. Inventarie onde cada asset é utilizado no HTML/CSS/JS e no painel.
- Preserve GOODZ como assinatura principal; mantenha **Pastelaria** e **Dogueria** em lockups distintos, sem recombinar as marcas, trocar cores ou criar slogan como fato.
- Compare logotipos com referência aprovada, testando em fundos claro/escuro, tamanhos de avatar/favicon e cabeçalho mobile. Corrija somente problemas comprovados de enquadramento, contraste, legibilidade ou arquivo quebrado.
- Nunca chame PNG/WebP embutido em SVG de vetor editável. Só produza SVG verdadeiro com paths/curvas auditáveis e concordância do owner sobre mudanças de desenho.
- Para alterações visuais relevantes, apresente versões antes/depois e aguarde aprovação de identidade; não substitua assets aprovados silenciosamente.
- Mantenha mapa asset→componente↔campo administrativo, sem duplicar desnecessariamente documentação canônica.

## Evidência e parada
Entregue exemplos de 48/96/160px, desktop/mobile e claro/escuro, hashes dos arquivos, screenshots e testes de carga `naturalWidth>0`. Pare se faltar a arte original, houver dúvida sobre licença/identidade ou D001 não cobrir a alteração. Issue: GZ-BRAND-001 (#3).
