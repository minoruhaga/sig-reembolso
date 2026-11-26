---
artifact: decision-analysis
schema_version: "4.0"
artifact_version: "v001"
status: proposed
created_at: "2026-11-20T16:24:58-03:00"
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
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/core/exceptions.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/despesas/tests.py
      relationship: supporting
      representation: source-code
      function: test
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
  considered_directories: [prompts/backend, prompts/requisitos, prompts/revisao]
  confidence: high
  rationale: "A Issue #12 formaliza o motor de regras de domínio para Soft-block de estouro orçamentário (RN02) e Segregação de Funções (RN03), integrando exceções semânticas de domínio e testes unitários dedicados."
classification:
  sphere: engineering
  concerns: [domain, compliance, architecture]
  decision_kind: design
  scope: component
  lifecycle: delivery
  urgency: normal
  uncertainty: low
  reversibility: easy
  risk: medium
---

# Análise de decisão — Motor de Regras RN02 (Soft-Block) e RN03 (Segregação de Funções) (Issue #12)

## Solicitação original

```text
# Task
1. Criar plano de execução para issues #9, #10, #11 e #12;
2. Executar planos de execução das issues #9, #10, #11 e #12;
3. Listar meus próximos passos.
```

Contexto da Issue #12 (`docs/fase-2/backlog_issues_github.md` e GitHub Issue #12):
- Flag automática `excede_teto = True` e cálculo de `valor_excedente` (RN02).
- Impedir que membros do Financeiro aprovem, rejeitem ou liquidem reembolsos de compras solicitadas por eles mesmos (RN03).
- Fornecer metadados estruturados de destaque visual vermelho em caso de estouro e mensagens claras no bloqueio transacional.

## Informações complementares

- `src/apps/core/exceptions.py` já foi criado na revisão arquitetural com as classes `ComprovanteObrigatorioError`, `TransicaoStatusInvalidaError`, `SegregacaoFuncoesError`, `JustificativaRejeicaoObrigatoriaError`, `ImutabilidadeDespesaError` e `PermissaoNegadaDominioError` (todas herdando de `ValidationError`), mas `Despesa` ainda lança `ValidationError` genérico.
- A extração das funções puras de regra de negócio para `src/apps/despesas/regras.py` isola e documenta explicitamente `RN02` e `RN03` e evita acoplamento nas views/templates.

## Mudanças desde a versão anterior

| Elemento | Versão anterior | Versão atual | Motivo | Impacto |
|---|---|---|---|---|
| Versão | Nenhuma (versão inicial) | v001 | Análise inicial da Issue #12 | Modulariza RN02/RN03 em `regras.py` e adota exceções tipadas de domínio |

## Artefatos analisados

| Caminho | Relação | Representação | Função | Formato | Recorte | Estado/revisão |
|---|---|---|---|---|---|---|
| `src/apps/despesas/models.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/core/exceptions.py` | `supporting` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/despesas/tests.py` | `supporting` | `source-code` | `test` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/AGENTS.md` | `context` | `prose` | `prompt-instruction` | `markdown` | `whole-file` | `commit` (`bef9653`) |

### Limites da evidência dos artefatos

- Os testes clássicos em `src/apps/despesas/tests.py` esperam `ValidationError` (`with self.assertRaises(ValidationError):`). Como `SigReembolsoDomainError` herda de `ValidationError`, adotar as exceções semânticas mantém 100% de retrocompatibilidade.

## Problema enriquecido

### Resultado desejado

Consolidar um módulo dedicado de regras de domínio (`apps.despesas.regras`) integrado ao modelo `Despesa` que:
1. Calcule `excede_teto` e `valor_excedente` em `Decimal` (inclusive quando o saldo livre já está zerado ou negativo).
2. Exponha metadados visuais determinísticos (`alerta_estouro`) para que qualquer template (Dashboard, Triagem desktop, Relatórios) destaque em vermelho (`bg-danger`) gastos que excedem o teto sem duplicar lógica.
3. Valide a segregação de funções (RN03) de forma uniforme nas ações `aprovar`, `rejeitar` e `liquidar`, disparando `SegregacaoFuncoesError` / `PermissaoNegadaDominioError`.

### Atores e interesses

- **Conselho Fiscal / Diretoria do GE Caramuru:** Exigem garantia de que tesoureiros nunca auto-aprovem ou auto-liquideem seus reembolsos (RN03) e que todo estouro de teto seja sinalizado visivelmente (RN02).
- **Equipe de Frontend (`Issue #13`):** Recebe a propriedade `despesa.alerta_estouro` pronta para renderização sem lógica contábil no HTML.

### Evidências e fatos observados

1. `Despesa.submeter()`, `aprovar()`, `rejeitar()` e `liquidar()` operam sob `@transaction.atomic` em `models.py`.
2. `src/AGENTS.md` proíbe lógica contábil ou cálculo de estouro em templates/views.

### Hipóteses

- Nenhuma alteração de campo de banco (`models.Field`) é necessária, portanto não serão geradas novas migrations, evitando conflitos com as demais branches em andamento.

### Perguntas em aberto

- Nenhuma pendência bloqueante.

### Escopo

- `src/apps/despesas/regras.py` (`calcular_soft_block_rn02`, `avaliar_alerta_estouro_rn02`, `validar_segregacao_funcoes_rn03`, `verificar_impedimento_rn03`).
- Integração em `src/apps/despesas/models.py` (usando `apps.despesas.regras` e `apps.core.exceptions` + propriedade `alerta_estouro`).
- Suíte de testes `src/apps/despesas/test_regras_rn02_rn03.py`.

### Fora do escopo

- Alterar `forms.py`, `services.py`, `views.py`, `urls.py` ou templates (mantendo isolamento total de arquivos com a Issue #11).

### Critérios de sucesso

- `calcular_soft_block_rn02` retorna resultados exatos em `Decimal` para saldo positivo, limite exato, estouro positivo e saldo já negativo.
- `SegregacaoFuncoesError` (subclasse de `ValidationError`) é disparada em tentativas de auto-aprovação, auto-rejeição e auto-liquidação por tesoureiros.
- Outro tesoureiro consegue aprovar, rejeitar e liquidar normalmente a despesa solicitada por um colega de Tesouraria.
- 100% dos testes pré-existentes continuam passando sem regressões.

## Restrições aplicáveis

- **`[CRITICAL]` Regras estritas em `models.py` ou camada de domínio (`src/AGENTS.md`)**
- **`[CRITICAL]` `Decimal` e `@transaction.atomic` (`src/AGENTS.md`)**
- **`[REQUIRED]` Docstrings em 3 partes (`AGENTS.md`)**
- **`[REQUIRED]` Não gerar migrations nem editar arquivos da Issue #11.**

## Classificação comentada

- **Esfera `engineering` / Preocupações `[domain, compliance, architecture]`:** Isolamento de regras contábeis e governança de segregação de funções.

## Decisão de roteamento

- Pasta escolhida: `prompts/backend`.

## Dimensões de decisão

| Dimensão | Prioridade | Limiar ou direção | Por que importa |
|---|---|---|---|
| `correctness` | Alta | 100% de precisão `Decimal` em estouros e segregação | Evita fraude e erro contábil |
| `modifiability` | Alta | Regras puras em `regras.py` + exceções tipadas | Facilita manutenção e cobertura de testes unitários (Item 3.i) |
| `simplicity` | Média | Sem migrations extras | Mantém compatibilidade imediata com `dev` e PRs paralelos |

## Alternativas consideradas

### Alternativa A: Manter lógica inline duplicada em `models.py` com `ValidationError` genérico
- **Desvantagem:** Duplica verificação de perfil/segregação em `aprovar`, `rejeitar` e `liquidar`, e não utiliza as exceções criadas em `apps.core.exceptions`.

### Alternativa B: Módulo de regras puras `apps.despesas.regras` + exceções semânticas integradas em `Despesa` (Recomendada)
- Centraliza `RN02` e `RN03` em `regras.py`, conecta os métodos atômicos de `Despesa` a esse módulo e às exceções de `apps.core.exceptions`, e expõe `alerta_estouro` para a UI.

## Perfil de pagamento comparativo

| Dimensão | Prioridade | Alternativa A | Alternativa B | Confiança | Base |
|---|---:|---:|---:|---|---|
| `correctness` | Alta | +1 | +2 | Alta | Regra única centralizada sem divergência entre métodos |
| `modifiability` | Alta | 0 | +2 | Alta | Uso efetivo de `apps.core.exceptions` e testes unitários puros |
| `simplicity` | Média | +2 | +2 | Alta | Zero alterações de schema/migrations |

## Histórico e decisão atual

### Decisão da versão anterior
Nenhuma (versão inicial).

### Decisão recomendada nesta versão
Adotar a **Alternativa B**: implementar `src/apps/despesas/regras.py`, integrar com `src/apps/despesas/models.py` usando `apps.core.exceptions` e criar a suíte `src/apps/despesas/test_regras_rn02_rn03.py`.

### Impacto da revisão
Decisão inicial que habilita a implementação da Issue #12.

### Dimensões maximizadas ou priorizadas

| Dimensão | Estado | Ganho esperado | Evidência ou hipótese |
|---|---|---|---|
| `correctness` | `maximized` | Zero duplicação da regra RN03 e cálculo exato RN02 | Funções puras testadas isoladamente e via ORM |
| `modifiability` | `maximized` | Diagnóstico claro de exceções de domínio | Adoção de `SegregacaoFuncoesError`, `ImutabilidadeDespesaError`, etc. |

### Dimensões satisfeitas por limiar

| Dimensão | Limiar aceito | Como a decisão atende |
|---|---|---|
| `simplicity` | Nenhuma migration gerada | Apenas lógica Python e propriedade calculada em `Despesa` |

## Perdas e trade-offs

### Perdas se as prioridades não forem atendidas

| Dimensão | Perda esperada | Severidade | Afetados |
|---|---|---|---|
| `correctness` | Cálculo incorreto de excedente em saldos negativos ou falha de RN03 na liquidação | Crítica | Prestação de contas do AG VII |

### Custos aceitos para priorizá-las

| Dimensão favorecida | Custo ou oportunidade | Dimensão prejudicada | Aceitabilidade |
|---|---|---|---|
| `modifiability` | Um módulo adicional (`regras.py`) além de `models.py` e `services.py` | Minimalismo extremo de arquivos | Alta — reduz duplicação dentro de `models.py` |

## Riscos e efeitos de segunda ordem

- **Risco:** Algum código ou teste externo verificar texto literal antigo de `ValidationError`.
  - **Mitigação:** Manter as mensagens originais claras contendo as expressões `"Segregação de Funções"`, `"RN05"`, `"comprovante fiscal"` e herdar de `ValidationError`.

## Validação da decisão

| Hipótese ou resultado | Evidência necessária | Método | Sinal para revisar |
|---|---|---|---|
| Retrocompatibilidade + novos cenários RN02/RN03 | 100% dos testes antigos e novos passando | `manage.py test src/apps` | Qualquer regressão em `DespesaRegrasNegocioTestCase` |

## Handoffs e atividades posteriores

1. Implementar `regras.py`, atualizar `models.py` e criar `test_regras_rn02_rn03.py`.
2. Abrir Pull Request da branch `feature/#12-regras-dominio` apontando para `dev`.

## Síntese

A **Alternativa B** elimina duplicação de regras no modelo `Despesa`, ativa a hierarquia de exceções de `apps.core.exceptions` e entrega cobertura completa de testes para RN02 e RN03 sem conflitar com nenhuma outra issue.

Arquivo criado em prompts/backend/20261120-162458-regras-softblock-segregacao-rn02-rn03-v001.md. Avalie se o local escolhido é de fato o mais adequado.
