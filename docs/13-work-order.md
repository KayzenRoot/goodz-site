# Work Order GOODZ-WEB-001
OBJECTIVE: Landing page GOODZ responsiva + admin básico funcional.
CONTEXT: marca principal e submarcas aprovadas; conceito 1 como fonte visual.
SCOPE: R01-R08. OUT OF SCOPE: checkout, integrações iFood/99Food, pagamentos, multiusuário.
FILES/SOURCES TO READ: docs/12-checkpoint, 11-decisions-ledger, 03-scope, 10-definition-of-done, 04-architecture, 02-requirements, reference-concept.jpg, assets originais.
REQUIREMENTS: CRUD, segurança, branding, link editável, persistência.
ARCHITECTURE RULES: projeto leve e monolítico, sem serviço externo obrigatório.
CONSTRAINTS: links reais não inventados; proteção CSRF e upload; sem deploy sem domínio/HTTPS.
ACCEPTANCE CRITERIA: interface utilizável desktop/mobile; admin altera elementos e alterações persistem; imagens seguras; testes passam.
TESTS: pytest + visual Chromium desktop/mobile + smoke local.
DELIVERABLES: código ZIP + README + source pack + imagens + evidências.
REVIEW FORMAT: relatório objetivo em pt-BR com PASS/FAIL, limitações e bloqueios.
STOP CONDITION: sem avanço para checkout, integração, produção ou ações destrutivas sem autorização.


## Correction Delta GOODZ-WEB-001/CD-01 (mesma PR #1)
- BASE HEAD: `9d137512719e03d12e61b5fe7c2b7fded2c4e05b`.
- Objetivo: corrigir apenas falhas reproduzidas na validação de links, em nomes de produtos e no consumo de upload antes da autenticação/limite.
- Fora do escopo: e-commerce, deploy, novos serviços, rotas comerciais fictícias ou publicação.
- Critérios: links malformados retornam 422 sem 500; produto em branco retorna 422 sem gravar; upload sem autenticação e com corpo declarado acima do limite é recusado antes do parser multipart.
- Testes: regressões Pytest, compilação e sintaxe JS; CI na própria PR. Auditoria/Checkpoint Delta somente após provas; sem merge automático.
