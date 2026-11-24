# Relatório de Atualizações e Bugs — Pós-Merge da PR #46 (`dev`)

**Branch auditada:** `dev` (`ee73c10`)  
**Data da auditoria:** 2026-11-24  
**Baseline de qualidade:** `ruff check src` OK, `manage.py check` OK (0 silenced), `makemigrations --check --dry-run` sem pendências, `73` testes passando em `src/apps`.

---

## 1. Atualizações Identificadas na `dev`

Após `git pull origin dev`, o histórico recente até o commit `ee73c10` inclui:

- **PR #41** (`feature/#8-tela-mobile-camera`): ajustes da tela mobile/câmera para lançamento de despesas.
- **PR #42** (`fix/nomenclatura-coordenacoes-despesas`): ajustes de nomenclatura de coordenações e despesas.
- **PR #43** (`feature/#34-relatorios-exportacao`): implementação inicial do módulo de relatórios e exportação.
- **PR #44** (`fix/restaurar-nomenclatura-pos-merge-41`): restauração de nomenclatura após merge da PR #41.
- **PR #46** (`fix(relatorios): exporta prestação de contas em CSV e balancete (RF08)`, `Closes #45`, mergeada em `2026-11-24T12:05:14Z`): exportação de prestação de contas em CSV e balancete sintético.

Embora os `73` testes automatizados existentes passem na `dev`, a revisão estática e funcional identificou **5 bugs** que atualmente não possuem cobertura de teste.

---

## 2. Bugs Identificados e Como Corrigi-los

### Bug 1 — Bypass de RBAC em `DespesaForm` e `criar_ou_atualizar_despesa`
- **Severidade:** Alta (Segurança / Regra de Negócio)
- **Onde está:**
  - `src/apps/despesas/forms.py` (linhas 164–166)
  - `src/apps/despesas/views.py` (linhas 98, 143–146, 184, 229)
  - `src/apps/despesas/services.py` (`criar_ou_atualizar_despesa`, em contraste com `simular_impacto_orcamentario` na linha 51)
- **O que acontece:**
  - `DespesaForm.__init__` popula `self.fields['coordenacao'].queryset` com `Coordenacao.objects.filter(ativo=True).order_by('nome')` para qualquer usuário.
  - Em contraste, `simular_impacto_orcamentario` (`src/apps/despesas/services.py`, linha 51) restringe a consulta a `coordenacoes_visiveis(usuario)`, e `previa_orcamento_view` retorna HTTP 404 quando um `COORDENADOR` seleciona uma pasta diferente da sua.
  - Resultado: um `COORDENADOR` enxerga todas as coordenações ativas no `<select>`, recebe `404` no JavaScript do termômetro ao selecionar outra pasta, mas ainda consegue enviar um `POST` e criar/atualizar/debitar despesa em coordenação de terceiros porque `criar_ou_atualizar_despesa` também não valida `coordenacoes_visiveis(usuario)`.
- **Como corrigir:**
  1. Aceitar `usuario=None` em `DespesaForm.__init__` e, quando informado, filtrar `self.fields['coordenacao'].queryset = coordenacoes_visiveis(usuario).filter(ativo=True).order_by('nome')`.
  2. Passar `usuario=request.user` nas instanciações de `DespesaForm` em `nova_despesa_view` e `editar_despesa_view` (`src/apps/despesas/views.py`).
  3. Na camada de serviço (`criar_ou_atualizar_despesa` em `src/apps/despesas/services.py`), validar explicitamente se `coordenacao` pertence a `coordenacoes_visiveis(usuario)` e levantar `ValidationError` / `PermissionDenied` caso contrário.
  4. Adicionar testes `TestCase` garantindo que: (a) `COORDENADOR` só vê sua coordenação no formulário; (b) `POST` forjado com `coordenacao` de outra pasta é rejeitado tanto no form quanto no service.

---

### Bug 2 — CSV Formula Injection (CWE-1236) em `gerar_csv_despesas`
- **Severidade:** Média-Alta (Segurança)
- **Onde está:**
  - `src/apps/relatorios/services.py` (linhas 164–180)
  - `src/apps/relatorios/views.py` (linha 72, onde o conteúdo é entregue com UTF-8 BOM `'\ufeff' + conteudo` para Excel)
- **O que acontece:**
  - `gerar_csv_despesas` escreve diretamente campos controlados por usuário (`despesa.titulo`, `_nome_solicitante(despesa.solicitante)`, `despesa.coordenacao.nome`) sem neutralização de prefixos de fórmula.
  - Valores iniciados por `=`, `+`, `-`, `@`, `\t` ou `\r` podem ser interpretados como fórmulas ao abrir o CSV no Excel/LibreOffice Calc.
- **Como corrigir:**
  1. Criar um helper `_sanitizar_celula_csv(valor)` em `src/apps/relatorios/services.py` que converta o valor para `str` e prefixe com apóstrofo (`'`) quando o primeiro caractere (ou após espaços/controle iniciais, conforme política definida) for `=`, `+`, `-`, `@`, `\t` ou `\r` — preservando colunas numéricas formatadas intencionalmente se necessário ou tratando especificamente colunas textuais (`titulo`, `solicitante`, `coordenacao.nome`, `coordenacao.sigla`, `forma_pagamento_original`).
  2. Aplicar `_sanitizar_celula_csv` às colunas textuais em `gerar_csv_despesas`.
  3. Adicionar testes `TestCase` em `src/apps/relatorios/tests.py` com títulos/nomes iniciados por `=cmd|...`, `+1+1`, `-1+1` e `@SUM(...)` verificando o escape com `'`.

---

### Bug 3 — `messages.error()` renderiza classe CSS inexistente `alert-error` no Bootstrap 5
- **Severidade:** Média (UI/UX)
- **Onde está:**
  - `src/templates/base.html` (linhas 115–122)
  - `src/config/settings/base.py` (linhas 75–108, sem `MESSAGE_TAGS`)
  - Diversas views que usam `messages.error(...)` (ex.: `src/apps/despesas/views.py` linhas 177, 269, 368, 392, 408, 432, 448)
- **O que acontece:**
  - `base.html` renderiza `<div class="alert alert-{{ message.tags|default:'info' }} alert-dismissible fade show" role="alert">`.
  - Como `MESSAGE_TAGS` não está configurado em `src/config/settings/base.py`, o Django emite a tag `'error'` para `messages.error(...)`, gerando `class="alert alert-error ..."`.
  - O Bootstrap 5 não possui `.alert-error` (usa `.alert-danger`), fazendo mensagens de erro aparecerem sem estilo visual de erro.
- **Como corrigir:**
  1. Configurar `MESSAGE_TAGS` em `src/config/settings/base.py` mapeando `messages.constants.ERROR` para `'danger'` (e opcionalmente `DEBUG` para `'secondary'`):
     ```python
     from django.contrib.messages import constants as message_constants

     MESSAGE_TAGS = {
         message_constants.ERROR: 'danger',
     }
     ```
  2. Adicionar teste `TestCase` verificando que uma view que dispara `messages.error` renderiza `alert-danger` no HTML final.

---

### Bug 4 — `gerar_balancete_sintetico` soma `RASCUNHO`, `REJEITADO` e `CANCELADO` por padrão
- **Severidade:** Média (Regra de Negócio / Contábil)
- **Onde está:**
  - `src/apps/relatorios/services.py` (linhas 192–206)
  - `src/templates/relatorios/balancete.html`
- **O que acontece:**
  - Quando o filtro `status` está vazio (`"Todos"` em `balancete.html`), `gerar_balancete_sintetico` chama `filtrar_despesas_relatorio(...)` sem excluir os status não comprometidos (`RASCUNHO`, `REJEITADO`, `CANCELADO`).
  - Com isso, o `Total de despesas` exibido no balancete diverge do comprometimento orçamentário real (`Coordenacao.total_comprometido`, que considera apenas `ENVIADO`, `APROVADO`, `PAGO`).
- **Como corrigir:**
  1. Alinhar a regra padrão de `gerar_balancete_sintetico` (quando `status` não for informado explicitamente) para contabilizar apenas despesas com status efetivos/comprometidos (`ENVIADO`, `APROVADO`, `PAGO`), ou separar explicitamente no balancete o total comprometido vs. rascunhos/rejeitados/cancelados.
  2. Caso a exportação CSV (`gerar_csv_despesas`) deva seguir o mesmo critério ou manter todos os registros filtrados, documentar claramente na UI e na docstring de `gerar_balancete_sintetico`.
  3. Adicionar testes `TestCase` em `src/apps/relatorios/tests.py` com despesas `RASCUNHO`, `REJEITADO`, `CANCELADO`, `ENVIADO`, `APROVADO` e `PAGO` confirmando que o balancete sem filtro de status não soma os status não comprometidos no total comprometido.

---

### Bug 5 — Link ausente para `financeiro:saldos` e classe `active` estática na navbar (`base.html`)
- **Severidade:** Baixa-Média (UI / Navegação)
- **Onde está:**
  - `src/templates/base.html` (linhas 58–80)
- **O que acontece:**
  - Não existe item de menu na navbar apontando para `{% url 'financeiro:saldos' %}` (funcionalidade da Issue #10 já mergeada na `dev`).
  - Além disso, o link `Painel Geral` possui a classe `active` fixa no HTML (linha 59), permanecendo destacado mesmo quando o usuário navega para outras páginas (`Minhas Despesas`, `Painel de Triagem`, `Prestação de Contas`, etc.).
- **Como corrigir:**
  1. Adicionar o item de navegação para `{% url 'financeiro:saldos' %}` na navbar de `src/templates/base.html` (respeitando a visibilidade por perfil, se aplicável).
  2. Tornar a classe `active` dinâmica usando `request.resolver_match` (ex.: `{% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}` e equivalentes por rota/namespace).
  3. Adicionar teste `TestCase` verificando a presença do link `financeiro:saldos` na navegação e o destaque dinâmico da rota ativa.
