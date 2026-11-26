---
artifact: decision-analysis
schema_version: "4.0"
artifact_version: "v001"
status: proposed
created_at: "2026-11-20T16:12:59-03:00"
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
    - path: docs/referencias/coordenadores_ag7.csv
      relationship: primary
      representation: structured-data
      function: data-fixture
      format: csv
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: docs/referencias/gastos_historicos_ag6/alimentacao_gastos_ag6.csv
      relationship: primary
      representation: structured-data
      function: data-fixture
      format: csv
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: docs/referencias/gastos_historicos_ag6/saude_e_bem_estar_caixa_medica_ag6.csv
      relationship: primary
      representation: structured-data
      function: data-fixture
      format: csv
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/apps/core/management/commands/popular_dados_demo.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "bef9653"
      availability: available
    - path: src/fixtures/coordenacoes_iniciais.json
      relationship: supporting
      representation: structured-data
      function: data-fixture
      format: json
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
  considered_directories: [prompts/backend, prompts/testes, prompts/requisitos]
  confidence: high
  rationale: "A Issue #9 trata de um management command Django para parsing de CSVs reais, criação idempotente de registros de domínio (Usuario, Coordenacao, Despesa, HistoricoTransicaoStatus) e conformidade com Decimal e RN01-RN06."
classification:
  sphere: engineering
  concerns: [data, implementation, domain]
  decision_kind: design
  scope: component
  lifecycle: delivery
  urgency: normal
  uncertainty: low
  reversibility: easy
  risk: low
---

# Análise de decisão — Carga Idempotente de Dados Reais do AG VI e Coordenadores do AG VII (Issue #9)

## Solicitação original

```text
# Task
1. Criar plano de execução para issues #9, #10, #11 e #12;
2. Executar planos de execução das issues #9, #10, #11 e #12;
3. Listar meus próximos passos.
```

Contexto da Issue #9 (`docs/fase-2/backlog_issues_github.md` e GitHub Issue #9):
- Criar comando de carga de dados populando o banco com a massa histórica de despesas de Alimentação e Saúde do AG VI e com a lista nominal dos coordenadores do AG VII (`docs/referencias/coordenadores_ag7.csv`, `alimentacao_gastos_ag6.csv` e `saude_e_bem_estar_caixa_medica_ag6.csv`).

## Informações complementares

- A Issue #9 foi redistribuída de `@xixinho` para `@minoruhaga` na reta final da Fase 2.
- O comando existente `popular_dados_demo` cria apenas os 4 usuários de demonstração (`admin`, `tesoureiro`, `coord_cozinha`, `coord_infra`) e 2 despesas sintéticas.

## Mudanças desde a versão anterior

| Elemento | Versão anterior | Versão atual | Motivo | Impacto |
|---|---|---|---|---|
| Versão | Nenhuma (versão inicial) | v001 | Análise inicial da Issue #9 | Define estratégia de parsing idempotente e carga transacional |

## Artefatos analisados

| Caminho | Relação | Representação | Função | Formato | Recorte | Estado/revisão |
|---|---|---|---|---|---|---|
| `docs/referencias/coordenadores_ag7.csv` | `primary` | `structured-data` | `data-fixture` | `csv` | `whole-file` | `commit` (`bef9653`) |
| `docs/referencias/gastos_historicos_ag6/alimentacao_gastos_ag6.csv` | `primary` | `structured-data` | `data-fixture` | `csv` | `whole-file` | `commit` (`bef9653`) |
| `docs/referencias/gastos_historicos_ag6/saude_e_bem_estar_caixa_medica_ag6.csv` | `primary` | `structured-data` | `data-fixture` | `csv` | `whole-file` | `commit` (`bef9653`) |
| `src/apps/core/management/commands/popular_dados_demo.py` | `supporting` | `source-code` | `production` | `python` | `whole-file` | `commit` (`bef9653`) |
| `src/fixtures/coordenacoes_iniciais.json` | `supporting` | `structured-data` | `data-fixture` | `json` | `whole-file` | `commit` (`bef9653`) |
| `src/AGENTS.md` | `context` | `prose` | `prompt-instruction` | `markdown` | `whole-file` | `commit` (`bef9653`) |

### Limites da evidência dos artefatos

- Os CSVs históricos apresentam layout tabular com múltiplas tabelas lado a lado (`coordenadores_ag7.csv` tem 3 blocos de pilares; `saude_e_bem_estar_caixa_medica_ag6.csv` tem 2 blocos paralelos: Itens e Medicamentos), linhas de cabeçalho deslocadas e valores formatados em pt-BR (`"R$ 1.557,22"`).
- Alguns registros de `alimentacao_gastos_ag6.csv` possuem campos vazios (ex.: ID 26 sem valor ou linhas 15/16 sem descrição explícita), exigindo tratamento defensivo no parser.

## Problema enriquecido

### Resultado desejado

Disponibilizar um comando Django idempotente (`carregar_dados_ag6_ag7`) — e integrá-lo opcionalmente ao fluxo de `popular_dados_demo` — capaz de popular o banco com as 15 coordenações, os coordenadores reais do AG VII (com telefones mascarados e papéis RBAC corretos) e os gastos reais do AG VI (Alimentação e Saúde/Farmácia), respeitando todas as regras de domínio (`RN01`–`RN06`, `Decimal`, `@transaction.atomic`).

### Atores e interesses

- **Desenvolvedores / QA / Banca Avaliadora:** Precisam validar telas, saldos, triagem e relatórios com massa realista do AG VI/AG VII em vez de apenas 2 registros sintéticos.
- **Cliente (AG VII - GE Caramuru):** Preservação de privacidade nos telefones mascarados já contidos nos CSVs e fidelidade orçamentária das compras reais (Assaí, CEAGESP, farmácias).

### Evidências e fatos observados

1. `coordenadores_ag7.csv` lista voluntários com nomes duplicados em áreas distintas (ex.: `Carol M.` em Decoração e Transporte; `Minoru` em Financeiro e Transporte; `Vitoria` em Decoração e Divulgação; `Onoe` em Captação e Sustentabilidade), logo o `username` precisa considerar nome + coordenação/sigla ou tratar atualização sem colisão.
2. `Despesa.save()` chama `otimizar_comprovante_fiscal` quando `_otimizado_pillow` não está marcado, e `Despesa.clean()` exige comprovante válido fora de `RASCUNHO` (`RN01`).
3. `src/AGENTS.md` exige precisão `Decimal` e execução sob `@transaction.atomic`.

### Hipóteses

- Os coordenadores mapeados para `Financeiro` devem receber `papel = PapelUsuario.TESOUREIRO` e `is_staff = True`, enquanto os demais recebem `papel = PapelUsuario.COORDENADOR`.
- Como os valores de Alimentação do AG VI somam R$ 39.398,83 (abaixo do teto de R$ 65.000,00 de `ALIM`) e Saúde soma R$ 1.011,57 (abaixo de R$ 8.000,00 de `SAUDE`), as despesas podem ser carregadas como `PAGO` (ou `ENVIADO` se `Reembolso == 'Pendente'`) mantendo saldos livres positivos e realistas.

### Perguntas em aberto

- Nenhuma pendência bloqueante; os mapeamentos das áreas dos CSVs para as 15 siglas de `coordenacoes_iniciais.json` são determinísticos.

### Escopo

- Management command `carregar_dados_ag6_ag7.py`.
- Chamada integrada ao final de `popular_dados_demo.py`.
- Testes automatizados em `src/apps/core/test_carga_ag6_ag7.py`.

### Fora do escopo

- Alteração dos arquivos CSV originais em `docs/referencias/`.
- Geração de migrations ou alteração de schemas de banco.

### Critérios de sucesso

- `python src/manage.py carregar_dados_ag6_ag7` popula as 15 coordenações, coordenadores do AG VII e despesas históricas do Assaí, CEAGESP e Saúde/Farmácia.
- Execução repetida é 100% idempotente (não duplica registros).
- Todas as despesas carregadas passam em `full_clean()` com comprovantes válidos em UUID v4 e trilha de auditoria (`HistoricoTransicaoStatus`).

## Restrições aplicáveis

- **`[CRITICAL]` Precisão Monetária e Atomicidade (`src/AGENTS.md`):** Parsing monetário pt-BR convertido exclusivamente para `Decimal`, sob `@transaction.atomic`.
- **`[REQUIRED]` Docstrings em 3 partes (`AGENTS.md`):** Aplicado ao comando e funções auxiliares.
- **`[REQUIRED]` Testes Automatizados (`AGENTS.md`):** Cobertura via `TestCase` validando carga e idempotência.

## Classificação comentada

- **Esfera `engineering` / Preocupações `[data, implementation, domain]`:** Parsing estruturado de CSVs heterogêneos para modelos de domínio Django sem violar invariantes contábeis.

## Decisão de roteamento

- Pasta escolhida: `prompts/backend` (seguindo continuidade dos artefatos de backend do projeto).

## Dimensões de decisão

| Dimensão | Prioridade | Limiar ou direção | Por que importa |
|---|---|---|---|
| `correctness` | Alta | 100% de conversão `Decimal` exata e validação `full_clean()` | Evita divergência de centavos e registros inválidos |
| `reliability` | Alta | Idempotência garantida em reexecuções | Permite rodar `popular_dados_demo` e o comando múltiplas vezes |
| `simplicity` | Alta | Biblioteca padrão `csv` do Python + Django ORM | Zero dependências extras no `requirements.txt` |

## Alternativas consideradas

### Alternativa A: Fixture JSON estática gerada manualmente
- Converter os 3 CSVs em um grande arquivo `.json` estático.
- **Desvantagem:** Perde vínculo direto com os CSVs oficiais se atualizados, dificulta criação de hashes de senha de `Usuario` e exige UUIDs hardcoded de mídia.

### Alternativa B: Management Command idempotente lendo os CSVs oficiais diretamente (Recomendada)
- Comando `carregar_dados_ag6_ag7` lê os 3 CSVs em `docs/referencias/`, carrega `coordenacoes_iniciais.json` se necessário, cria usuários e despesas via ORM com `get_or_create` sob `@transaction.atomic`.
- **Vantagens:** Fonte única da verdade nos CSVs, idempotente, testável via `call_command` e integrado a `popular_dados_demo`.

## Perfil de pagamento comparativo

| Dimensão | Prioridade | Alternativa A (Fixture JSON) | Alternativa B (Management Command) | Confiança | Base |
|---|---:|---:|---:|---|---|
| `correctness` | Alta | 0 | +2 | Alta | Validação via `full_clean()` e `Decimal` |
| `reliability` | Alta | -1 | +2 | Alta | Idempotência com `get_or_create` |
| `simplicity` | Alta | +1 | +2 | Alta | Módulo nativo `csv` do Python |

## Histórico e decisão atual

### Decisão da versão anterior
Nenhuma (versão inicial).

### Decisão recomendada nesta versão
Adotar a **Alternativa B**: implementar `src/apps/core/management/commands/carregar_dados_ag6_ag7.py` com parsing `Decimal`, criação idempotente de coordenadores AG VII e despesas AG VI sob `@transaction.atomic`, integrá-lo a `popular_dados_demo.py` e validar via `TestCase`.

### Impacto da revisão
Decisão inicial que habilita a implementação da Issue #9.

### Dimensões maximizadas ou priorizadas

| Dimensão | Estado | Ganho esperado | Evidência ou hipótese |
|---|---|---|---|
| `correctness` | `maximized` | Zero erros de conversão monetária ou violação RN01/RN06 | Parsing `Decimal` + `full_clean()` |
| `reliability` | `prioritized` | Reexecução segura sem duplicatas | Chaves determinísticas em `get_or_create` |

### Dimensões satisfeitas por limiar

| Dimensão | Limiar aceito | Como a decisão atende |
|---|---|---|
| `simplicity` | Sem bibliotecas externas (ex.: pandas) | Uso exclusivo de `csv` e `decimal` da stdlib |

## Perdas e trade-offs

### Perdas se as prioridades não forem atendidas

| Dimensão | Perda esperada | Severidade | Afetados |
|---|---|---|---|
| `correctness` | Totais históricos divergentes dos CSVs do AG VI | Alta | Testes, relatórios e banca |

### Custos aceitos para priorizá-las

| Dimensão favorecida | Custo ou oportunidade | Dimensão prejudicada | Aceitabilidade |
|---|---|---|---|
| `reliability` | Anexar comprovante sintético padrão para despesas históricas sem foto digital local | Fidelidade visual das notas antigas do AG VI | Aceitável — as notas físicas de 2023 não estão versionadas no repo |

## Riscos e efeitos de segunda ordem

- **Risco:** Mudança de caminho do `BASE_DIR` comprometer a localização da pasta `docs/referencias/`.
  - **Mitigação:** Resolver o diretório raiz via `settings.BASE_DIR.parent / 'docs' / 'referencias'` e permitir override opcional via argumento ou fallback.

## Validação da decisão

| Hipótese ou resultado | Evidência necessária | Método | Sinal para revisar |
|---|---|---|---|
| Carga correta de coordenadores e despesas | Assaí, CEAGESP, Farmácia e coordenadores no banco | `TestCase` chamando `call_command('carregar_dados_ag6_ag7')` | Valores diferentes dos CSVs ou exceções de validação |

## Handoffs e atividades posteriores

1. Implementar `carregar_dados_ag6_ag7.py`, atualizar `popular_dados_demo.py` e adicionar `test_carga_ag6_ag7.py`.
2. Abrir Pull Request da branch `feature/#9-fixture-ag6-ag7` apontando para `dev`.

## Síntese

A **Alternativa B** entrega uma carga reprodutível, idempotente e fiel aos CSVs reais do AG VI e AG VII com conformidade estrita às regras contábeis e arquiteturais do projeto.

Arquivo criado em prompts/backend/20261120-161259-carga-dados-reais-ag6-ag7-v001.md. Avalie se o local escolhido é de fato o mais adequado.
