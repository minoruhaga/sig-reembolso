---
artifact: decision-analysis
schema_version: "4.0"
artifact_version: "v001"
status: proposed
created_at: "2026-11-20T16:19:41-03:00"
lineage:
  mode: initial
  root: null
  supersedes: null
  change_type: initial
  secondary_change_types: []
  decision_impact: initial
subjects:
  kind: file-set
  files:
    - path: src/apps/despesas/models.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/despesas/services.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/despesas/forms.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/despesas/views.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/despesas/urls.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/AGENTS.md
      relationship: context
      representation: prose
      function: prompt-instruction
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
routing:
  root: prompts
  selected_directory: prompts/backend
  considered_directories: [prompts/backend, prompts/frontend, prompts/requisitos]
  confidence: high
  rationale: "A Issue #11 define os endpoints POST transacionais de aprovação, rejeição com justificativa obrigatória (RN04) e liquidação bancária com anexo Cora PJ (RF06/RF07), além da orquestração de serviços e formulários."
classification:
  sphere: engineering
  concerns: [domain, security, architecture]
  decision_kind: design
  scope: component
  lifecycle: delivery
  urgency: normal
  uncertainty: low
  reversibility: easy
  risk: medium
---

# Análise de decisão — Workflow e Endpoints de Triagem da Tesouraria (Issue #11)

## Solicitação original

```text
# Task
1. Criar plano de execução para issues #9, #10, #11 e #12;
2. Executar planos de execução das issues #9, #10, #11 e #12;
3. Listar meus próximos passos.
```

Contexto da Issue #11 (`docs/fase-2/backlog_issues_github.md` e GitHub Issue #11):
- Endpoints e botões de ação para **Aprovar**, **Rejeitar com Justificativa (RN04)** e **Liquidar Reembolso** com anexo do comprovante Cora PJ (RF06 e RF07).

## Informações complementares

- A entidade `Despesa` (`src/apps/despesas/models.py`) já possui os métodos transacionais `aprovar()`, `rejeitar()` e `liquidar()`, protegidos por `@transaction.atomic`, validação de papel Tesoureiro, segregação de funções (RN03), justificativa obrigatória (RN04) e auditoria (RN06).
- A Issue #13 (`@ricardosakugawa`) fará o refinamento visual avançado do painel desktop da Tesouraria; a Issue #11 entrega todos os serviços, formulários, endpoints POST, painel funcional de triagem com modais Bootstrap 5 (rejeição, liquidação e visualização do cupom) e testes integrados.

## Mudanças desde a versão anterior

| Elemento | Versão anterior | Versão atual | Motivo | Impacto |
|---|---|---|---|---|
| Versão | Nenhuma (versão inicial) | v001 | Análise inicial da Issue #11 | Define camada de serviço de triagem e endpoints HTTP POST protegidos |

## Artefatos analisados

| Caminho | Relação | Representação | Função | Formato | Recorte | Estado/revisão |
|---|---|---|---|---|---|---|
| `src/apps/despesas/models.py` | `supporting` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/despesas/services.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/despesas/forms.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/despesas/views.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/despesas/urls.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/AGENTS.md` | `context` | `prose` | `prompt-instruction` | `markdown` | `whole-file` | `commit` (`bef9653`) |

### Limites da evidência dos artefatos

- `Despesa.liquidar()` aceita `comprovante_pagamento=None` no nível do model (para manter compatibilidade com testes clássicos), mas o critério de aceitação da Issue #11 e o fluxo da Tesouraria exigem anexo do comprovante bancário Cora PJ na liquidação via endpoint.

## Problema enriquecido

### Resultado desejado

Disponibilizar o fluxo completo de triagem financeira web para a Tesouraria:
1. Listagem filtrável de despesas na fila de triagem (`ENVIADO`) e fila de pagamento (`APROVADO`) em `despesas:triagem`, bloqueada para coordenadores comuns (`PermissionDenied` HTTP 403).
2. Ação de **Aprovar** via POST (`despesas:aprovar`).
3. Ação de **Rejeitar** via POST (`despesas:rejeitar`) com formulário/modal exigindo justificativa textual obrigatória (`RN04`).
4. Ação de **Liquidar** via POST multipart (`despesas:liquidar`) exigindo comprovante bancário Cora PJ, otimizado com Pillow (`RNF02`/`RNF04`).

### Atores e interesses

- **Tesoureiro / Gestor Financeiro:** Precisa conferir rapidamente notas pendentes, visualizar chave PIX do solicitante, rejeitar com parecer claro ou liquidar com comprovante Cora PJ.
- **Coordenador de Área:** Não pode acessar a fila de triagem global nem acionar endpoints de aprovação/rejeição/liquidação.

### Evidências e fatos observados

1. `src/AGENTS.md` exige que todo upload de imagem passe por `otimizar_comprovante_fiscal` e receba UUID v4 antes de ser salvo no storage.
2. `src/AGENTS.md` exige `@transaction.atomic` em toda transição de estado e proíbe lógica contábil nas views.

### Hipóteses

- Exigir `comprovante_pagamento` obrigatório no `LiquidacaoDespesaForm` e em `liquidar_despesa_triagem` atende diretamente ao critério de aceitação da Issue #11 sem quebrar `Despesa.liquidar()` nos testes existentes em `apps/despesas/tests.py`.

### Perguntas em aberto

- Nenhuma pendência bloqueante.

### Escopo

- `RejeicaoDespesaForm` e `LiquidacaoDespesaForm` em `src/apps/despesas/forms.py`.
- Serviços `aprovar_despesa_triagem`, `rejeitar_despesa_triagem`, `liquidar_despesa_triagem` em `src/apps/despesas/services.py`.
- Views e rotas `triagem/`, `<int:pk>/aprovar/`, `<int:pk>/rejeitar/`, `<int:pk>/liquidar/`.
- Template `src/templates/despesas/painel_triagem.html` + links em `base.html` e `dashboard.html`.
- Suíte de testes `src/apps/despesas/test_triagem_workflow.py`.

### Fora do escopo

- Alterar `src/apps/despesas/models.py` (evita conflito de merge com a Issue #12).
- Estilização avançada de lupa/zoom em alta resolução (Issue #13).

### Critérios de sucesso

- Coordenador recebe HTTP 403 ao tentar acessar ou postar nos endpoints de triagem.
- Tesoureiro aprova, rejeita (falhando quando motivo está vazio - RN04) e liquida com anexo Cora PJ comprimido/UUID v4 (RNF02/RNF04).
- Segregação de funções (RN03) impede que tesoureiro aprove, rejeite ou liquide despesa própria pelos endpoints.

## Restrições aplicáveis

- **`[CRITICAL]` Regras e otimização fora das views (`src/AGENTS.md`)**
- **`[CRITICAL]` `@transaction.atomic` e `Decimal` (`src/AGENTS.md`)**
- **`[REQUIRED]` Docstrings em 3 partes (`AGENTS.md`)**
- **`[REQUIRED]` Zero alterações em `models.py` nesta branch** para manter isolamento limpo com a Issue #12.

## Classificação comentada

- **Esfera `engineering` / Preocupações `[domain, security, architecture]`:** Construção de endpoints seguros de transição de estados e upload bancário.

## Decisão de roteamento

- Pasta escolhida: `prompts/backend`.

## Dimensões de decisão

| Dimensão | Prioridade | Limiar ou direção | Por que importa |
|---|---|---|---|
| `security` | Alta | 100% de bloqueio RBAC e CSRF POST-only | Impede ações não autorizadas na fila financeira |
| `correctness` | Alta | Conformidade RN02, RN03, RN04, RN05 e RN06 | Garante rastreabilidade e lastro bancário |
| `modifiability` | Média | Desacoplar templates de triagem das regras de serviço | Facilita evolução visual na Issue #13 |

## Alternativas consideradas

### Alternativa A: Chamar métodos do model direto na view sem forms/services de triagem
- **Desvantagem:** Espalha validação de justificativa e chamada de `otimizar_comprovante_fiscal` na camada HTTP.

### Alternativa B: Formulários dedicados (`RejeicaoDespesaForm`, `LiquidacaoDespesaForm`) + Serviços transacionais em `services.py` (Recomendada)
- Isola validação de entrada nos forms, garante `@transaction.atomic` e `otimizar_comprovante_fiscal` nos services, e deixa as views exclusivamente como orquestradoras HTTP.

## Perfil de pagamento comparativo

| Dimensão | Prioridade | Alternativa A | Alternativa B | Confiança | Base |
|---|---:|---:|---:|---|---|
| `security` | Alta | +1 | +2 | Alta | Validação de formulário + RBAC + POST-only |
| `correctness` | Alta | +1 | +2 | Alta | Garantia de `otimizar_comprovante_fiscal` e atomicidade |
| `modifiability` | Média | 0 | +2 | Alta | Reutilizável pela Issue #13 sem reescrever lógica |

## Histórico e decisão atual

### Decisão da versão anterior
Nenhuma (versão inicial).

### Decisão recomendada nesta versão
Adotar a **Alternativa B**: adicionar `RejeicaoDespesaForm` e `LiquidacaoDespesaForm`, os 3 serviços transacionais em `apps.despesas.services`, as 4 views em `apps.despesas.views`, o template `painel_triagem.html` e os testes em `test_triagem_workflow.py`.

### Impacto da revisão
Decisão inicial que habilita a implementação da Issue #11.

### Dimensões maximizadas ou priorizadas

| Dimensão | Estado | Ganho esperado | Evidência ou hipótese |
|---|---|---|---|
| `security` | `maximized` | Proteção total contra CSRF, RBAC indevido e auto-aprovação | Decorators `@require_POST` + checagem de papel + RN03 |
| `correctness` | `maximized` | Auditoria completa e comprovante Cora PJ otimizado | `HistoricoTransicaoStatus` + `otimizar_comprovante_fiscal` |

### Dimensões satisfeitas por limiar

| Dimensão | Limiar aceito | Como a decisão atende |
|---|---|---|
| `modifiability` | Código da UI desacoplado do domínio | Views chamam funções de serviço em `services.py` |

## Perdas e trade-offs

### Perdas se as prioridades não forem atendidas

| Dimensão | Perda esperada | Severidade | Afetados |
|---|---|---|---|
| `security` | Coordenador aprovar própria despesa via POST forjado | Crítica | Caixa do Grupo Escoteiro Caramuru |

### Custos aceitos para priorizá-las

| Dimensão favorecida | Custo ou oportunidade | Dimensão prejudicada | Aceitabilidade |
|---|---|---|---|
| `correctness` | Exigir comprovante bancário em toda liquidação via painel | Flexibilidade para liquidar sem PDF/foto na UI | Alta — critério explícito da Issue #11 |

## Riscos e efeitos de segunda ordem

- **Risco:** Falha de envio de arquivo corrompido na liquidação causar erro 500.
  - **Mitigação:** Capturar `ValidationError` na view de liquidação, exibir `messages.error` claro e manter a despesa em `APROVADO`.

## Validação da decisão

| Hipótese ou resultado | Evidência necessária | Método | Sinal para revisar |
|---|---|---|---|
| Fluxo completo Aprovar, Rejeitar (RN04) e Liquidar (Cora PJ) funciona com RBAC e RN03 | Todos os casos de `test_triagem_workflow.py` passando | `manage.py test` | Qualquer transição não autorizada ou sem auditoria |

## Handoffs e atividades posteriores

1. Implementar alterações da Issue #11 na branch `feature/#11-acoes-triagem`.
2. Handoff visual dos cards/zoom em alta resolução para a Issue #13 (`@ricardosakugawa`).

## Síntese

A **Alternativa B** entrega as ações completas da Tesouraria com segurança RBAC, atomicidade transacional e desacoplamento limpo para o refinamento visual futuro.

Arquivo criado em prompts/backend/20261120-161941-workflow-acoes-triagem-tesouraria-v001.md. Avalie se o local escolhido é de fato o mais adequado.
