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
