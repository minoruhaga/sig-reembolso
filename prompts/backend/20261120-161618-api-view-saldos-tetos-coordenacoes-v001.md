---
artifact: decision-analysis
schema_version: "4.0"
artifact_version: "v001"
status: proposed
created_at: "2026-11-20T16:16:18-03:00"
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
    - path: src/apps/financeiro/models.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/financeiro/views.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/financeiro/urls.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/usuarios/services.py
      relationship: supporting
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
  rationale: "A Issue #10 foca no cálculo dinâmico contábil em Decimal de saldos, comprometimentos por status e parametrização de tetos (RF02/RF03), com exposição via serviço financeiro, view dedicada e API JSON."
classification:
  sphere: engineering
  concerns: [domain, architecture, performance]
  decision_kind: design
  scope: component
  lifecycle: delivery
  urgency: normal
  uncertainty: low
  reversibility: easy
  risk: low
---

# Análise de decisão — API e View Dinâmica de Saldos e Tetos das 15 Coordenações (Issue #10)

## Solicitação original

```text
# Task
1. Criar plano de execução para issues #9, #10, #11 e #12;
2. Executar planos de execução das issues #9, #10, #11 e #12;
3. Listar meus próximos passos.
```

Contexto da Issue #10 (`docs/fase-2/backlog_issues_github.md` e GitHub Issue #10):
- View dedicada e endpoint de API para cálculo dinâmico do termômetro de consumo de verba das 15 coordenações em tempo real (RF03), garantindo integridade de centavos com `Decimal` e atualização instantânea após submissões, aprovações, reprovações e pagamentos.

## Informações complementares

- `Coordenacao` (`src/apps/financeiro/models.py`) já expõe as propriedades `total_comprometido`, `saldo_disponivel` e `percentual_consumido`, porém faz 1 query de agregação por coordenação (padrão N+1 quando exibidas todas as 15 pastas) e não discrimina o total por status (`PAGO`, `APROVADO`, `ENVIADO`).
- O recorte RBAC centralizado já existe em `apps.usuarios.services.coordenacoes_visiveis`.

## Mudanças desde a versão anterior

| Elemento | Versão anterior | Versão atual | Motivo | Impacto |
|---|---|---|---|---|
| Versão | Nenhuma (versão inicial) | v001 | Análise inicial da Issue #10 | Define camada de serviço financeiro com agregação otimizada em `Decimal` |

## Artefatos analisados

| Caminho | Relação | Representação | Função | Formato | Recorte | Estado/revisão |
|---|---|---|---|---|---|---|
| `src/apps/financeiro/models.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/financeiro/views.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/financeiro/urls.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/usuarios/services.py` | `supporting` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/AGENTS.md` | `context` | `prose` | `prompt-instruction` | `markdown` | `whole-file` | `commit` (`bef9653`) |

### Limites da evidência dos artefatos

- `src/apps/financeiro/views.py` e `src/apps/financeiro/tests.py` estão vazios e `src/apps/financeiro/urls.py` não possui rotas registradas.

## Problema enriquecido

### Resultado desejado

Fornecer uma camada de serviço financeiro (`apps.financeiro.services`), uma view dedicada (`financeiro:saldos`), uma API JSON (`financeiro:api_saldos`) e um endpoint transacional para parametrização de teto pela Tesouraria (`financeiro:atualizar_teto`), respeitando isolamento RBAC (RF01), parametrização de tetos (RF02) e consulta em tempo real com barras percentuais (RF03).

### Atores e interesses

- **Coordenadores de Área:** Visualizam exclusivamente o termômetro e composição do saldo da própria coordenação.
- **Tesouraria / Diretoria:** Visualizam todas as 15 coordenações com detalhamento (`Pago`, `Aprovado`, `Em Triagem`, `Saldo Livre`) e ajustam tetos orçamentários.
- **Frontend Mobile (`Issue #8`) / Dashboard (`Issue #13`):** Consomem a API JSON `financeiro/api/saldos/` para atualização dinâmica sem reload completo.

### Evidências e fatos observados

1. `src/AGENTS.md` proíbe cálculos contábeis dentro de views ou templates HTML, exigindo que a lógica resida em `models.py` ou `services.py`.
2. Todo cálculo monetário deve usar exclusivamente `Decimal` (proibido `float` para valores em R$).
3. Alterações no teto orçamentário devem operar sob `@transaction.atomic`.

### Hipóteses

- A agregação com `Sum('despesas__valor', filter=Q(...))` ou agrupamento por status em uma única query por resumo reduz latência para cumprir RNF05 (< 1,5 s).
- O retorno JSON da API pode manter valores monetários como strings com duas casas decimais (`"1250.50"`) para preservar exatidão de centavos sem imprecisão de ponto flutuante IEEE-754.

### Perguntas em aberto

- Nenhuma pendência bloqueante.

### Escopo

- `src/apps/financeiro/services.py` (`calcular_termometro_coordenacao`, `obter_resumo_orcamentario`, `atualizar_teto_orcamentario`).
- `src/apps/financeiro/views.py` e `src/apps/financeiro/urls.py`.
- `src/templates/financeiro/painel_saldos.html`.
- `src/apps/financeiro/tests.py`.

### Fora do escopo

- Modificação no `Coordenacao` model (sem migrations necessárias).
- Exportação CSV/PDF (escopo da Issue #34 / `apps.relatorios`).

### Critérios de sucesso

- Saldos e comprometimentos atualizam instantaneamente após transições (`ENVIADO`, `APROVADO`, `PAGO`, `REJEITADO`, `CANCELADO`) com precisão exata de centavos em `Decimal`.
- Coordenador vê somente sua coordenação na view HTML e na API JSON; Tesoureiro/Admin vê todas as ativas.
- Somente Tesoureiro/Admin pode alterar `teto_orcamentario`, rejeitando valores negativos e usuários sem permissão.

## Restrições aplicáveis

- **`[CRITICAL]` Regras e cálculos em `services.py` (`src/AGENTS.md`)**
- **`[CRITICAL]` `@transaction.atomic` e `Decimal` (`src/AGENTS.md`)**
- **`[REQUIRED]` Docstrings em 3 partes (`AGENTS.md`)**

## Classificação comentada

- **Esfera `engineering` / Preocupações `[domain, architecture, performance]`:** Desenho de serviço contábil de leitura agregada e atualização transacional de teto.

## Decisão de roteamento

- Pasta escolhida: `prompts/backend`.

## Dimensões de decisão

| Dimensão | Prioridade | Limiar ou direção | Por que importa |
|---|---|---|---|
| `correctness` | Alta | Zero divergência de centavos em `Decimal` | Garante auditoria financeira do orçamento de R$ 180 mil |
| `security` | Alta | Isolamento estrito RBAC por coordenação | Impede coordenador de consultar tetos de outras pastas ou editar tetos |
| `performance` | Média | Agregação ORM eficiente (< 1,5 s - RNF05) | Evita múltiplas consultas desnecessárias sob link Starlink |

## Alternativas consideradas

### Alternativa A: Calcular diretamente nas views iterando sobre `Coordenacao.objects.all()`
- **Inviabilidade:** Viola `src/AGENTS.md` (lógica contábil na view) e ignora `coordenacoes_visiveis`.

### Alternativa B: Serviço financeiro dedicado (`apps.financeiro.services`) + API JSON e View dedicadas (Recomendada)
- Encapsula cálculo detalhado do termômetro por coordenação e atualização transacional do teto em `services.py`, reutilizando `coordenacoes_visiveis` de `apps.usuarios.services`. Views apenas orquestram entrada/saída HTML e JSON.

## Perfil de pagamento comparativo

| Dimensão | Prioridade | Alternativa A (View Direta) | Alternativa B (Service Dedicado) | Confiança | Base |
|---|---:|---:|---:|---|---|
| `correctness` | Alta | -1 | +2 | Alta | Separação de camadas e uso estrito de `Decimal` |
| `security` | Alta | 0 | +2 | Alta | Uso de `coordenacoes_visiveis` e `PermissaoNegadaDominioError` |
| `performance` | Média | -1 | +2 | Alta | `annotate` em queryset único no resumo |

## Histórico e decisão atual

### Decisão da versão anterior
Nenhuma (versão inicial).

### Decisão recomendada nesta versão
Adotar a **Alternativa B**: implementar `apps.financeiro.services`, expor `financeiro:saldos`, `financeiro:api_saldos` e `financeiro:atualizar_teto`, criar o template `financeiro/painel_saldos.html` e cobrir todos os cenários em `apps/financeiro/tests.py`.

### Impacto da revisão
Decisão inicial que habilita a implementação da Issue #10.

### Dimensões maximizadas ou priorizadas

| Dimensão | Estado | Ganho esperado | Evidência ou hipótese |
|---|---|---|---|
| `correctness` | `maximized` | Precisão absoluta em `Decimal` | Cômputo por status sem `float` |
| `security` | `prioritized` | Isolamento RBAC em HTML e API | Reuso de `coordenacoes_visiveis` |

### Dimensões satisfeitas por limiar

| Dimensão | Limiar aceito | Como a decisão atende |
|---|---|---|
| `performance` | Tempo de resposta < 1,5 s | Agregação SQL com `Sum` e `Q` no queryset |

## Perdas e trade-offs

### Perdas se as prioridades não forem atendidas

| Dimensão | Perda esperada | Severidade | Afetados |
|---|---|---|---|
| `correctness` | Divergência entre termômetro e saldo real | Crítica | Tesouraria e coordenadores |

### Custos aceitos para priorizá-las

| Dimensão favorecida | Custo ou oportunidade | Dimensão prejudicada | Aceitabilidade |
|---|---|---|---|
| `correctness` | Retornar valores monetários formatados como string no JSON (além de percentual numérico) | Simplicidade de parsing numérico direto em JS | Alta — padrão de APIs financeiras para evitar erro de ponto flutuante |

## Riscos e efeitos de segunda ordem

- **Risco:** Usuário digitar vírgula no campo de teto (`"65000,00"`).
  - **Mitigação:** Normalizar string de entrada substituindo `,` por `.` antes de converter para `Decimal` na view/service.

## Validação da decisão

| Hipótese ou resultado | Evidência necessária | Método | Sinal para revisar |
|---|---|---|---|
| Atualização imediata do saldo após submissão/aprovação/pagamento/rejeição | Saldo livre e comprometido exatos na API e View | `TestCase` em `apps/financeiro/tests.py` | Divergência de centavos ou vazamento RBAC |

## Handoffs e atividades posteriores

1. Implementar `services.py`, `views.py`, `urls.py`, `painel_saldos.html` e `tests.py` em `apps/financeiro`.
2. Abrir Pull Request da branch `feature/#10-saldos-tetos` apontando para `dev`.

## Síntese

A **Alternativa B** entrega a API e view dinâmica de saldos e tetos das 15 coordenações com total respeito à arquitetura do projeto, isolamento RBAC e precisão contábil `Decimal`.

Arquivo criado em prompts/backend/20261120-161618-api-view-saldos-tetos-coordenacoes-v001.md. Avalie se o local escolhido é de fato o mais adequado.
