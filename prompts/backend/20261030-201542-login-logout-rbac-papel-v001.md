---
artifact: decision-analysis
schema_version: "4.0"
artifact_version: "v001"
status: proposed
created_at: "2026-10-30T20:15:42-03:00"
lineage:
  mode: initial
  root: null
  supersedes: null
  change_type: initial
  secondary_change_types: []
  decision_impact: initial
subjects:
  kind: mixed
  files:
    - path: docs/fase-2/backlog_issues_github.md
      relationship: primary
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: selected-section
      locator: "Issue #6 linhas 56-59"
      content_state: working-tree
      revision: null
      availability: available
    - path: src/apps/usuarios/models.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
    - path: src/apps/core/views.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
    - path: src/config/urls.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
    - path: src/config/settings.py
      relationship: supporting
      representation: source-code
      function: configuration
      format: python
      analysis_scope: selected-section
      locator: "AUTH_USER_MODEL, LOGIN_URL linhas 21-22 e 113-116"
      content_state: working-tree
      revision: null
      availability: available
    - path: src/apps/usuarios/urls.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
    - path: src/templates/base.html
      relationship: supporting
      representation: markup
      function: production
      format: html
      analysis_scope: selected-section
      locator: "navbar login/logout via /admin/"
      content_state: working-tree
      revision: null
      availability: available
    - path: src/templates/dashboard.html
      relationship: supporting
      representation: markup
      function: production
      format: html
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
    - path: src/apps/financeiro/models.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: selected-section
      locator: "classe Coordenacao — ausência de vínculo com Usuario"
      content_state: working-tree
      revision: null
      availability: available
    - path: src/apps/core/management/commands/popular_dados_demo.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
    - path: docs/requisitos/requisitos_funcionais.md
      relationship: context
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: selected-section
      locator: "RF01"
      content_state: working-tree
      revision: null
      availability: available
    - path: docs/arquitetura/modelo_dados.md
      relationship: context
      representation: diagram-model
      function: schema-contract
      format: markdown
      analysis_scope: selected-section
      locator: "ER USUARIO / COORDENACAO"
      content_state: working-tree
      revision: null
      availability: available
    - path: AGENTS.md
      relationship: context
      representation: prose
      function: prompt-instruction
      format: markdown
      analysis_scope: selected-section
      locator: "testes, docstrings, ambiente isolado"
      content_state: working-tree
      revision: null
      availability: available
    - path: src/AGENTS.md
      relationship: context
      representation: prose
      function: prompt-instruction
      format: markdown
      analysis_scope: selected-section
      locator: "RN em models/services; views como orquestradoras"
      content_state: working-tree
      revision: null
      availability: available
routing:
  root: prompts
  selected_directory: prompts/backend
  considered_directories: [prompts/backend, prompts/frontend, prompts/requisitos]
  confidence: high
  rationale: "A decisão central é RBAC no modelo Usuario, serviço de escopo e proteção de rotas; o template de login é consequência, não o objeto da decisão."
classification:
  sphere: engineering
  concerns: [security, architecture, user-experience]
  decision_kind: design
  scope: component
  lifecycle: delivery
  urgency: normal
  uncertainty: low
  reversibility: moderate
  risk: medium
---

# Análise de decisão — Login, logout e controle de visão por papel (Issue #6)

## Solicitação original

Implementar telas de login/logout customizadas no Django utilizando o modelo Usuario.
Restringir visualizações: Coordenador só vê sua área; Tesoureiro e Admin visualizam todas as 15 coordenações.

Critérios de Aceitação:

1. View de login com redirecionamento de acordo com o papel.
2. Bloqueio de rotas administrativas para coordenadores de campo.

## Informações complementares

A pasta `prompts/` no working tree continha apenas `README.md`; as subpastas documentadas no README (`backend/`, `frontend/`, `requisitos/`, etc.) não existiam ainda. A subpasta `prompts/backend/` foi criada para receber este artefato, alinhada à organização já descrita em `prompts/README.md`.

O usuário pediu plano e implementação na mesma conversa. Esta análise não implementa código; o handoff descreve a execução posterior.

## Mudanças desde a versão anterior

| Elemento | Versão anterior | Versão atual | Motivo | Impacto |
|---|---|---|---|---|
| N/A | Nenhum identificado | v001 inicial | Primeira análise | Decisão inaugural |

## Artefatos analisados

| Caminho | Relação | Representação | Função | Formato | Recorte | Estado/revisão |
|---|---|---|---|---|---|---|
| docs/fase-2/backlog_issues_github.md | primary | prose | documentation | markdown | Issue #6 | working-tree |
| src/apps/usuarios/models.py | primary | source-code | production | python | arquivo inteiro | working-tree |
| src/apps/core/views.py | supporting | source-code | production | python | arquivo inteiro | working-tree |
| src/config/urls.py | supporting | source-code | production | python | arquivo inteiro | working-tree |
| src/config/settings.py | supporting | source-code | configuration | python | AUTH/LOGIN | working-tree |
| src/apps/usuarios/urls.py | supporting | source-code | production | python | arquivo inteiro | working-tree |
| src/templates/base.html | supporting | markup | production | html | navbar | working-tree |
| src/templates/dashboard.html | supporting | markup | production | html | arquivo inteiro | working-tree |
| src/apps/financeiro/models.py | supporting | source-code | production | python | Coordenacao | working-tree |
| src/apps/core/management/commands/popular_dados_demo.py | supporting | source-code | production | python | arquivo inteiro | working-tree |
| docs/requisitos/requisitos_funcionais.md | context | prose | documentation | markdown | RF01 | working-tree |
| docs/arquitetura/modelo_dados.md | context | diagram-model | schema-contract | markdown | ER | working-tree |
| AGENTS.md | context | prose | prompt-instruction | markdown | testes/docstrings | working-tree |
| src/AGENTS.md | context | prose | prompt-instruction | markdown | RN em services | working-tree |

### Limites da evidência dos artefatos

Não há commit hash disponível neste ambiente (binário `git` ausente no PATH da sessão). O conteúdo analisado é o working tree local. `Usuario` não possui FK para `Coordenacao`; o DER em `modelo_dados.md` também não registra esse vínculo. A issue #6 exige “sua área”, o que não é implementável de forma estável só com `Despesa.solicitante`.

## Problema enriquecido

### Resultado desejado

Voluntários autenticam-se em tela própria (não no Django Admin), caem em destino conforme o papel e, no painel, o coordenador vê apenas a pasta dele; tesoureiro e admin veem as 15. Coordenador de campo não usa rotas `/admin/`.

### Atores e interesses

- Coordenador de área: login simples no celular, saldo só da sua pasta.
- Tesoureiro: visão consolidada das 15 pastas; acesso a ferramentas administrativas quando `is_staff`.
- Admin geral: governança e `/admin/`.
- Banca LES / RF01: evidência de RBAC real, não só `is_staff`.

### Evidências e fatos observados

- `AUTH_USER_MODEL = 'usuarios.Usuario'` com `PapelUsuario` e propriedades `is_coordenador`, `is_tesoureiro`, `is_admin_geral`.
- `apps.usuarios.urls` está vazio (placeholder da Issue #6). `views.py` e `tests.py` de usuários estão vazios.
- `LOGIN_URL = 'login'` aponta para nome de rota inexistente.
- Dashboard em `/` é público e lista todas as coordenações ativas.
- Navbar entra e sai por `/admin/login/` e `/admin/logout/`.
- Demo: `coord_cozinha` e `coord_infra` sem `is_staff`; `admin` e `tesoureiro` com `is_staff`.
- Não existe vínculo persistido usuário–coordenação.

### Hipóteses

- “Rotas administrativas” = prefixo `/admin/` (Django Admin), não um futuro painel de tesouraria em `/despesas/`.
- Um coordenador atua em no máximo uma coordenação no piloto AG VII.
- Admin deve ser redirecionado ao Admin; tesoureiro e coordenador ao dashboard (com recortes diferentes).

### Perguntas em aberto

Nenhuma que altere a decisão de desenho: o critério de aceite já fixa login customizado, redirect por papel e bloqueio de admin para coordenador.

### Escopo

- Telas login/logout Bootstrap 5 usando `Usuario`.
- Redirect pós-login por papel.
- Login obrigatório no dashboard.
- Escopo de coordenações e despesas recentes por papel.
- Bloqueio de `/admin/` para coordenador autenticado.
- Testes `TestCase`.
- FK opcional `Usuario.coordenacao` + ajuste da carga demo.

### Fora do escopo

- Formulário de submissão de despesa (Issue #7/#8).
- Aprovar/rejeitar/liquidar (Issue #11).
- Alterar tetos (Issue #10 / RF02).
- Relatórios RF08.
- Substituição completa do Django Admin por um backoffice próprio.

### Critérios de sucesso

1. Login autenticando `Usuario` redireciona Admin → `/admin/`; Tesoureiro e Coordenador → dashboard.
2. Coordenador autenticado em `/admin/` não permanece na área administrativa.
3. Dashboard do coordenador mostra só a coordenação vinculada; tesoureiro/admin veem todas as ativas.
4. Visitante anônimo em `/` é enviado ao login.

## Restrições aplicáveis

- [CRITICAL] Regras de domínio em models/services; views só orquestram (`src/AGENTS.md`).
- [REQUIRED] Docstrings o quê / como / finalidade.
- [REQUIRED] Teste automatizado Django para funcionalidade nova.
- [FORBIDDEN] Instalar Python/deps globais; executar no `.venv`.
- Data contract: o DER atual não tem FK; a FK é extensão mínima justificada por RF01 (“sua coordenação”), sem lógica contábil nova.
- Não usar `float` em dinheiro (já respeitado nas views de dashboard via `Decimal` dos models).

## Classificação comentada

Esfera `engineering` porque o núcleo é autenticação, autorização e contrato de dados. Preocupações `security` (admin e rotas), `architecture` (onde vive o escopo) e `user-experience` (login mobile-first). Risco `medium`: vazamento de tetos de outras pastas para coordenador de campo.

## Decisão de roteamento

`prompts/backend/` — a decisão é o serviço de escopo e o vínculo `Usuario`–`Coordenacao`. `frontend` seria adequado só se a dúvida fosse layout. `requisitos` já está fechado em RF01/Issue #6.

## Dimensões de decisão

| Dimensão | Prioridade | Limiar ou direção | Por que importa |
|---|---|---|---|
| security | high | Coordenador não opera `/admin/` nem vê outras pastas | RF01 e critério 2 |
| correctness | high | Escopo derivado do papel e da FK, não de heurística de username | Evita “área” fantasma |
| simplicity | high | Reusar `LoginView`/`LogoutView` do Django | Menos código, CSRF e sessão nativos |
| user-value | medium | Tela própria, não Admin | Campo / mobile |
| modifiability | medium | Serviço único de visibilidade | Issue #7 reusa o mesmo recorte |
| time-to-value | medium | Sem painel tesouraria paralelo nesta onda | Fora do escopo #11/#13 |

## Alternativas consideradas

### A — Auth views Django + serviço de escopo + FK `Usuario.coordenacao` + middleware em `/admin/`

Login/logout oficiais, `get_success_url` por papel, dashboard com `login_required` filtrando via serviço, middleware após `AuthenticationMiddleware`.

### B — Apenas `is_staff` e inferir área pelas despesas do solicitante

Sem migração. Coordenador novo vê zero pastas; coordenador que lançou em duas pastas (erro operacional) vazaria dados. Admin continua o login padrão se a navbar não mudar de fato.

### C — AdminSite customizado e grupos Django (`Permission`) sem FK

Mais cerimônia que o enum `papel` já existente; ainda não resolve “sua área”.

## Perfil de pagamento comparativo

| Dimensão | Prioridade | Alternativa A | Alternativa B | Alternativa C | Confiança | Base |
|---|---:|---:|---:|---:|---|---|
| security | high | +2 | -1 | +1 | high | B deixa `/` público e área ambígua |
| correctness | high | +2 | -2 | 0 | high | Só A identifica a pasta sem chute |
| simplicity | high | +1 | +1 | -1 | high | C duplica RBAC já modelado |
| user-value | medium | +2 | 0 | 0 | medium | Tela própria só em A se navbar mudar |
| modifiability | medium | +2 | -1 | 0 | high | Serviço reutilizável |
| time-to-value | medium | +1 | +2 | -1 | medium | B é mais curto e errado |

## Histórico e decisão atual

### Decisão da versão anterior

Nenhum identificado.

### Decisão recomendada nesta versão

Adotar a **alternativa A**.

1. `Usuario.coordenacao` FK anulável para `financeiro.Coordenacao` (`PROTECT`).
2. `apps.usuarios.services` com `coordenacoes_visiveis`, `despesas_visiveis`, `url_pos_login`, `usuario_pode_acessar_admin`.
3. `LoginView`/`LogoutView` em `usuarios`, template Bootstrap, `LOGIN_URL = 'usuarios:login'`.
4. Redirect: `ADMIN` → `admin:index`; demais papéis → `dashboard`.
5. Dashboard exige login e usa o serviço (totais só do recorte visível).
6. Middleware bloqueia `/admin/` para quem não for tesoureiro nem admin (inclui anônimo redirecionado ao login customizado).
7. Demo vincula `coord_cozinha`→ALIM e `coord_infra`→INFRA.
8. Testes de login, redirect, bloqueio e recorte de dashboard.

### Impacto da revisão

Decisão inicial.

### Dimensões maximizadas ou priorizadas

| Dimensão | Estado | Ganho esperado | Evidência ou hipótese |
|---|---|---|---|
| security | prioritized | Coordenador não usa Admin nem vê 15 pastas | Middleware + queryset filtrado |
| correctness | prioritized | Área vem do cadastro, não do histórico de despesas | FK no model |

### Dimensões satisfeitas por limiar

| Dimensão | Limiar aceito | Como a decisão atende |
|---|---|---|
| simplicity | Auth views Django, sem JWT/SPA | LoginView/LogoutView |
| time-to-value | Sem backoffice próprio nesta issue | Admin permanece para gestor |

## Perdas e trade-offs

### Perdas se as prioridades não forem atendidas

| Dimensão | Perda esperada | Severidade | Afetados |
|---|---|---|---|
| security | Coordenador vê tetos de outras pastas ou entra no Admin | alta | Tesouraria, banca RF01 |
| correctness | “Sua área” indefinida | alta | Coordenador sem despesas |

### Custos aceitos para priorizá-las

| Dimensão favorecida | Custo ou oportunidade | Dimensão prejudicada | Aceitabilidade |
|---|---|---|---|
| correctness | Migração e DER informalmente à frente do doc | documentação do modelo | aceitável nesta onda; doc pode seguir depois |
| security | Tesoureiro deixa de usar `/admin/login/` nativo | hábito Django | aceitável: um login só |

## Riscos e efeitos de segunda ordem

- Coordenador sem FK vê dashboard vazio: tratar com mensagem, não 500.
- `is_tesoureiro` hoje inclui `is_superuser`; superuser com papel COORDENADOR passaria no admin — aceitável para conta `admin` de demo.
- Issues #7/#10 devem reutilizar o mesmo serviço, senão o recorte diverge.

## Validação da decisão

| Hipótese ou resultado | Evidência necessária | Método | Sinal para revisar |
|---|---|---|---|
| Redirect por papel | 302 distintos Admin vs demais | TestCase client | Product owner quiser tesoureiro no Admin |
| Bloqueio admin | Coordenador autenticado não obtém 200 em `/admin/` | TestCase | Existir outro “admin” fora de `/admin/` |
| Recorte de área | Dashboard coordenador: 1 linha; tesoureiro: N | TestCase | Coordenador multi-pasta no AG VII |

## Handoffs e atividades posteriores

- Implementar no código (solicitado pelo usuário após esta análise).
- Atualizar `modelo_dados.md` em issue de documentação (não nesta entrega, salvo pedido).
- Issues #7 e #10 devem importar o serviço de visibilidade.

## Síntese

O login customizado sozinho não cumpre a issue: o dashboard hoje é público e o usuário não tem “área”. A correção mínima correta é FK opcional + serviço de escopo + auth views Django + middleware no `/admin/`. Inferir pasta pelas despesas ou confiar só em `is_staff` falha RF01.
