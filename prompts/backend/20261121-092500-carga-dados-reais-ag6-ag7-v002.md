---
artifact: decision-analysis
schema_version: "4.0"
artifact_version: "v002"
status: accepted
created_at: "2026-11-21T09:25:00-03:00"
lineage:
  mode: revision
  root: prompts/backend/20261120-161259-carga-dados-reais-ag6-ag7-v001.md
  supersedes: prompts/backend/20261120-161259-carga-dados-reais-ag6-ag7-v001.md
  change_type: correction
  secondary_change_types: [scope-adjustment]
  decision_impact: material
subjects:
  kind: file-set
  files:
    - path: src/fixtures/coordenacoes_iniciais.json
      relationship: primary
      representation: structured-data
      function: data-fixture
      format: json
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
    - path: src/apps/core/management/commands/carregar_dados_ag6_ag7.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
    - path: src/apps/core/test_carga_ag6_ag7.py
      relationship: supporting
      representation: source-code
      function: test
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
    - path: docs/arquitetura/distribuicao_orcamentaria_coordenacoes.md
      relationship: supporting
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: null
      availability: available
routing:
  root: prompts
  selected_directory: prompts/backend
  considered_directories: [prompts/backend]
  confidence: high
  rationale: "Revisão incremental da análise v001 do PR #37 / Issue #9 mantendo continuidade na mesma pasta."
classification:
  sphere: engineering
  concerns: [data, domain, correctness]
  decision_kind: design
  scope: component
  lifecycle: delivery
  urgency: normal
  uncertainty: low
  reversibility: easy
  risk: low
---

# Análise de decisão — Correção das 15 Coordenações Reais e Siglas do AG VII (PR #37 / Issue #9)

## Solicitação original

Validação do PR #37 solicitando eliminação de coordenações fictícias/alucinadas (`SEG`, `SEC`, `CANT`, `ALMOX`, `ALOJ`, `LIMP`, `ESPIR`, `TES`), atualização das descrições reais, remoção de colisão em `MAPA_AREA_SIGLA` e alinhamento dos tetos à Tabela 1 (`1. ORÇAMENTO POR COORDENAÇÃO`) da aba `3_CUSTOS_COORDENACOES` da planilha oficial *AG VII - Modelagem de Precificação e Cenários*.

## Mudanças desde a versão anterior

| Elemento | Versão anterior (`v001`) | Versão atual (`v002`) | Motivo | Impacto |
|---|---|---|---|---|
| Coordenações da fixture (`coordenacoes_iniciais.json`) | 15 áreas herdadas da modelagem inicial (incluía `SEG`, `SEC`, `CANT`, `ALMOX`, `ALOJ`, `LIMP`, `ESPIR`, `TES`) | 15 coordenações reais do `coordenadores_ag7.csv` com `Geral e Programação` unificada (`ALIM`, `INFRA`, `TRANS`, `ATIV`, `SOM`, `SAUDE`, `DECO`, `LOG`, `SUST`, `DIV`, `CAPT`, `FIN`, `GERAL`, `INSC`, `MUS`) | Eliminar áreas inexistentes no evento real e corrigir nomes/descrições | Alinha 100% do domínio de `Coordenacao` ao evento real |
| Tetos orçamentários | Teto inicial estimado de R$ 180.000,00 | Coluna K `OTIMISTA (271)` + 10% arredondado (total R$ 193.320,00), com `SAUDE` fixado em R$ 1.500,00 e `SOM` = R$ 0,00 | Alinhamento com a planilha oficial de precificação do AG VII | Reflete custos reais e reservas de +10% |
| `MAPA_AREA_SIGLA` | Reaproveitava siglas fictícias e colidia `Música`/`Som` em `MULT` e `Geral/Programação`/`Atividades` em `PROG` | Mapeamento 1:1 exclusivo para cada uma das 15 áreas (`FIN` para Financeiro, `GERAL` para Geral/Programação, `MUS` vs `SOM`, etc.) | Evitar mistura de despesas e usuários entre coordenações distintas | Isolamento RBAC preciso no dashboard e nos relatórios |

## Decisão adotada

1. Substituir as entradas da fixture [`src/fixtures/coordenacoes_iniciais.json`](../../src/fixtures/coordenacoes_iniciais.json) mantendo os mesmos PKs (`1` a `15`) sem sobreposição de `sigla`/`nome` entre PKs distintos para evitar violação de `UNIQUE` ao rodar `loaddata` em bancos pré-populados.
2. Atualizar `MAPA_AREA_SIGLA` e a verificação de perfil financeiro (`sigla == 'FIN'`) em [`carregar_dados_ag6_ag7.py`](../../src/apps/core/management/commands/carregar_dados_ag6_ag7.py), garantindo recarga da fixture se `sigla='FIN'` ainda não existir no banco.
3. Atualizar a suíte [`test_carga_ag6_ag7.py`](../../src/apps/core/test_carga_ag6_ag7.py) e a documentação [`distribuicao_orcamentaria_coordenacoes.md`](../../docs/arquitetura/distribuicao_orcamentaria_coordenacoes.md).
