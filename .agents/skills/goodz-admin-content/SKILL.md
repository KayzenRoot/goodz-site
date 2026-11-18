---
name: goodz-admin-content
description: "Use quando aprimorar o painel GOODZ para trocar banners, fotos, logos, textos, links, produtos e prévias, mantendo uma única conta e experiência simples em celular."
---

# GOODZ Admin Content

## Contexto
Leia Source Pack na ordem canônica, `static/admin.html`, `static/scripts/admin.js`, `static/styles/admin.css`, `app/main.py`, `tests/test_app.py` e `docs/07-data-model.md`. Antes de escrever, confirme que a funcionalidade ainda não existe.

## Procedimento
- Mapeie cada controle para chave real de `/api/admin/state` e reflexo público em `/api/site`; se não houver mapeamento, registre defeito reproduzível.
- Preserve três logos independentes (GOODZ, Pastelaria, Dogueria), três imagens de vitrine (Sobre, Pastelaria, Dogueria), títulos, descrições, links e catálogo separado.
- Preview e feedback de upload precisam mostrar sucesso/erro, formato permitido, limite e comportamento de persistência. Valide no servidor, nunca somente por `accept` de input.
- Mantenha o upload transacional e pasta persistente com política de recuperação. Não faça remoção automática de imagem anterior sem prova de referência/backup e autorização.
- Produto: categorias, nome, foto, descrição, preço opcional, ordem e visibilidade. Não expor preço ou links fictícios.
- Controle de sessão, CSRF, headers e autorização pertencem à API. Não renderize conteúdo do usuário com `innerHTML`, nem introduza segredos no JS cliente.
- UX mobile: labels associadas, foco, aviso de salvar, confirmação de exclusão e estado offline/erro claro.

## Aceite
E2E com Uvicorn real: login, editar banner/logo, criar/ocultar/excluir produto, links por marca, upload inválido, logout e reinício persistente; evidências desktop/mobile. Se tarefa exigir multiusuário, page builder, checkout ou alteração de autenticação, pare e encaminhe à issue correspondente. Issue: GZ-ADMIN-001 (#5).
