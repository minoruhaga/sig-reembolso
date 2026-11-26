---
artifact: decision-analysis
schema_version: "4.0"
artifact_version: "v001"
status: proposed
created_at: "2026-10-30T12:05:17-03:00"
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
      content_state: working-tree
      revision: "working-tree based on fe5331c"
      availability: available
    - path: src/apps/core/services.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: "working-tree based on fe5331c"
      availability: available
    - path: src/apps/despesas/views.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: "working-tree based on fe5331c"
      availability: available
    - path: src/AGENTS.md
      relationship: context
      representation: prose
      function: prompt-instruction
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: "working-tree based on fe5331c"
      availability: available
    - path: docs/requisitos/regras_de_negocio.md
      relationship: supporting
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: "working-tree based on fe5331c"
      availability: available
    - path: docs/requisitos/requisitos_nao_funcionais.md
      relationship: supporting
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: "working-tree based on fe5331c"
      availability: available
routing:
  root: prompts
  selected_directory: prompts/backend
  considered_directories: [prompts/backend, prompts/frontend, prompts/requisitos]
  confidence: high
  rationale: "A Issue #7 trata da arquitetura de backend, camada de domínio contábil, integração do serviço de otimização Pillow (RNF02), transições atômicas de despesas e endpoints/formulários Django, sendo o app de backend o núcleo da decisão."
classification:
  sphere: engineering
  concerns: [architecture, implementation, domain]
  decision_kind: design
  scope: component
  lifecycle: delivery
  urgency: normal
  uncertainty: low
  reversibility: moderate
  risk: medium
---

# Análise de decisão — Arquitetura de Formulário de Submissão de Despesas com Otimização Pillow (RNF02 e RN01)

## Solicitação original

```text
# Role
Atue como sênior em AI Software Engineer.

# Task
/plan Criar plano de execução da issue #7

# Constraint
Usar boas práticas de engenharia de software e respeitar as limitações e restrições (SKILL.md, analysis_decision, etc.)
```

Entrada complementar do usuário:
```text
Executar até atingir o Marco 1
```

## Informações complementares

- **Issue #7 no Backlog oficial (`docs/fase-2/backlog_issues_github.md`):** `[Despesas] Formulário de Submissão com Pillow (RNF02 e RN01)`.
- **Atribuição:** Membro 1 (`@minoruhaga` — Tech Lead & Backend Core).
- **Milestone:** Onda 1 (MVP Mobile e Dados Reais — Prazo: 04/11/2026).
- **Fronteira com a Issue #8 (`@ricardosakugawa`):** A Issue #7 estabelece o contrato de dados, formulário Django, serviços de domínio, otimização de imagem Pillow e endpoints REST/HTML, enquanto a Issue #8 concentra o refinamento visual da interface mobile com botão direto de acionamento de câmera nativa.

## Mudanças desde a versão anterior

| Elemento | Versão anterior | Versão atual | Motivo | Impacto |
|---|---|---|---|---|
| Versão | Nenhuma (versão inicial) | v001 | Criação inicial do artefato de decisão para a Issue #7 | Estabelece o padrão de arquitetura para submissão de despesas e tratamento de mídia |

## Artefatos analisados

| Caminho | Relação | Representação | Função | Formato | Recorte | Estado/revisão |
|---|---|---|---|---|---|---|
| `src/apps/despesas/models.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `working-tree based on fe5331c` |
| `src/apps/core/services.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `working-tree based on fe5331c` |
| `src/apps/despesas/views.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `working-tree based on fe5331c` |
| `src/AGENTS.md` | `context` | `prose` | `prompt-instruction` | `markdown` | `whole-file` | `working-tree based on fe5331c` |
| `docs/requisitos/regras_de_negocio.md` | `supporting` | `prose` | `documentation` | `markdown` | `whole-file` | `working-tree based on fe5331c` |
| `docs/requisitos/requisitos_nao_funcionais.md` | `supporting` | `prose` | `documentation` | `markdown` | `whole-file` | `working-tree based on fe5331c` |

### Limites da evidência dos artefatos

- O modelo `Despesa` em `src/apps/despesas/models.py` já implementa métodos de transição (`submeter`, `aprovar`, `rejeitar`, `liquidar`) e validação de invariantes contábeis (`RN01` a `RN06`).
- O serviço `otimizar_comprovante_fiscal` em `src/apps/core/services.py` possui protótipo inicial com redimensionamento para 1920px e renomeação UUID v4, mas carece de validação estrita de tipos permitidos (`RN01`), rejeição de imagens corrompidas e compressão adaptativa garantida para cumprir o teto de 350KB (`RNF02`).
- As views em `src/apps/despesas/views.py` e rotas em `src/apps/despesas/urls.py` estão atualmente vazias, dependendo da definição desta decisão de engenharia.

## Problema enriquecido

### Resultado desejado

Permitir que coordenadores e voluntários em campo registrem despesas operacionais com anexação de cupom/nota fiscal através de formulário web, garantindo:
1. Validação estrita da presença de comprovante no ato da submissão formal (**RN01**).
2. Possibilidade de salvamento provisório sem comprovante como rascunho (**RF05**).
3. Otimização e compressão automática de fotos de celulares para arquivos JPEG $< 350\text{ KB}$ com anonimização UUID v4 (**RNF02**, **RNF04**).
4. Preservação da integridade contábil sob transações atômicas (**RNF03**) e registro auditável de transição (**RN06**).

### Atores e interesses

- **Coordenador de Área / Voluntário de Campo:** Necessita de agilidade para enviar despesas pelo celular sem travamentos ou falhas de upload na rede Starlink limitada.
- **Tesouraria / Gestores Financeiros:** Exigem notas fiscais legíveis, com data, CNPJ e valores nítidos, vinculados de forma auditável ao orçamento da coordenação correta.
- **Desenvolvedores / Tech Lead:** Necessitam de código limpo, sem vazamento de regras de domínio contábil para views ou templates, com testes automatizados cobrindo regressões.

### Evidências e fatos observados

1. O acampamento em Juquitiba opera sob conectividade satelital (Starlink) compartilhada por dezenas de voluntários. Uploads desnecessários de 5MB por foto causam saturação de banda e *timeouts* no navegador mobile.
2. `src/AGENTS.md` proíbe expressamente lógica contábil, cálculos orçamentários ou validações primárias de estado dentro de views ou templates HTML.
3. Fotos tiradas diretamente de smartphones Android/iOS frequentemente contêm metadados de orientação EXIF que causam rotação incorreta caso não sejam normalizados (`ImageOps.exif_transpose`).

### Hipóteses

- A conversão de imagens coloridas pesadas para JPEG progressivo com qualidade adaptativa (entre 75 e 40) e largura máxima de 1920px é suficiente para reduzir 100% das fotos de notas fiscais comuns para menos de 350KB mantendo a legibilidade contábil.
- Arquivos em PDF não necessitam de compressão raster via Pillow, devendo ser validados quanto à extensão e renomeados com UUID v4.

### Perguntas em aberto

- Nenhuma pendência impeditiva. O modelo de usuários e de coordenações suporta plenamente o relacionamento necessário.

### Escopo

- Definição do formulário Django (`DespesaForm` em `forms.py`).
- Implementação da camada de serviço de domínio em `apps.despesas.services`.
- Aprimoramento da rotina `otimizar_comprovante_fiscal` em `apps.core.services` para garantia de $< 350\text{ KB}$ e rejeição de arquivos inválidos.
- Implementação das views e endpoints em `apps.despesas.views` e `apps.despesas.urls`.
- Templates HTML funcionais em Bootstrap 5 (`despesa_form.html` e `minhas_despesas.html`).
- Suíte de testes automatizados unitários e de integração (`core/tests.py` e `despesas/tests.py`).

### Fora do escopo

- Refinamento avançado de ergonomia UI/UX mobile camera (atribuído à Issue #8).
- Telas de triagem, aprovação e liquidação da Tesouraria (atribuídas às Issues #11 e #13).
- Integração bancária direta via API Cora (Out-of-Scope do projeto).

### Critérios de sucesso

- Todo envio com `acao='submeter'` sem anexo é rejeitado conforme RN01.
- Todo salvamento com `acao='rascunho'` sem anexo é aceito em estado `RASCUNHO` conforme RF05.
- Toda foto de nota fiscal é processada pelo Pillow, resultando em arquivo persistido com nome UUID v4 `.jpg` de tamanho estritamente inferior a $350\text{ KB}$ (358.400 bytes).
- Submissão acima do teto orçamentário sensibiliza automaticamente o *soft-block* (`excede_teto = True` e `valor_excedente` correto em `Decimal`).
- Todas as operações de persistência e transição ocorrem sob `@transaction.atomic`.
- 100% dos testes unitários e linters (`ruff`) executam com sucesso no ambiente Nix.

## Restrições aplicáveis

- **`[CRITICAL]` Localização de Regras de Negócio (`src/AGENTS.md`):** Regras residem estritamente nos modelos ou em serviços de domínio. Views atuam apenas como orquestradoras.
- **`[CRITICAL]` Atomicidade e Precisão Monetária (`src/AGENTS.md`):** `@transaction.atomic` obrigatório em alterações de estado/saldo; proibição estrita de `float` para moeda, usando `Decimal`.
- **`[REQUIRED]` Otimização com Pillow (`src/AGENTS.md`):** Todo upload de imagem deve ser processado por `otimizar_comprovante_fiscal` e anonimizado com UUID v4.
- **`[REQUIRED]` Docstrings estruturadas:** Toda função/classe/view deve conter docstring com "O que faz", "Como faz" e "Qual finalidade atende".

## Classificação comentada

- **Esfera `engineering`:** Trata-se de implementação de componentes de software, modelagem de serviços e pipeline de manipulação de mídia.
- **Preocupações `[architecture, implementation, domain]`:** Foco em separação de camadas (View -> Service -> Domain), implementação da integração Pillow e garantia das regras contábeis RN01 e RN02.
- **Risco `medium`:** Falha na compressão ou no isolamento transacional pode resultar em estouro de armazenamento, lentidão em campo ou inconsistência contábil.

## Decisão de roteamento

- Diretório selecionado: `prompts/backend`.
- Justificativa: A decisão trata primariamente de arquitetura de backend, integridade de domínio contábil, services do Django e processamento de mídia no servidor.

## Dimensões de decisão

| Dimensão | Prioridade | Limiar ou direção | Por que importa |
|---|---|---|---|
| `correctness` | Alta | 100% de conformidade com RN01 a RN06 | Garante a integridade dos dados fiscais do evento |
| `reliability` | Alta | Resiliência a falhas de upload e imagens corrompidas | Previne erros 500 para coordenadores em campo |
| `performance` | Média | Compressão $< 350\text{ KB}$ em $< 1{,}5\text{ s}$ | Viabiliza tráfego no link Starlink |
| `simplicity` | Alta | Código síncrono nativo sem filas externas (Celery) | Mantém o stack aderente ao escopo acadêmico |
| `modifiability` | Média | Desacoplamento entre View, Form e Serviço | Facilita a integração do frontend mobile da Issue #8 |

## Alternativas consideradas

### Alternativa A: Processamento direto acoplado na View do Django
- A view recebe o request multipart, valida o formulário, invoca Pillow diretamente e executa os `.save()` e `.submeter()`.
- **Inviabilidade:** Viola diretamente a regra `[CRITICAL]` de `src/AGENTS.md` (views não devem conter lógica de domínio ou orquestração contábil). Dificulta reuso em APIs ou comandos CLI.

### Alternativa B: Camada de Serviço de Domínio Dedicada (`apps.despesas.services`) + Otimização em `apps.core.services` (Recomendada)
- O formulário valida tipos de dados de entrada (`forms.ModelForm`).
- A view orquestra autenticação e delega para `criar_ou_atualizar_despesa(...)` em `apps.despesas.services`.
- O serviço opera sob `@transaction.atomic`, invoca `otimizar_comprovante_fiscal` do app core, persiste em rascunho e delega a transição para `despesa.submeter(usuario)`.
- **Vantagens:** Atende integralmente `src/AGENTS.md`, isola transações, centraliza a regra de negócio no domínio e permite testar cada camada isoladamente via `TestCase`.

### Alternativa C: Processamento Assíncrono com Background Workers (Celery / Redis)
- O arquivo bruto é salvo temporariamente e uma tarefa assíncrona comprime e move para o storage final.
- **Inviabilidade:** Adiciona complexidade desproporcional de infraestrutura (broker Redis, worker daemon), cria estado inconsistente intermediário (despesa criada sem comprovante pronto para triagem imediata) e viola o princípio de simplicidade do projeto.

## Perfil de pagamento comparativo

| Dimensão | Prioridade | Alternativa A (View Direta) | Alternativa B (Service Dedicado) | Alternativa C (Celery/Async) | Confiança | Base |
|---|---:|---:|---:|---:|---|---|
| `correctness` | Alta | -1 (risco de vazamento) | +2 (estrita separação) | +1 (complexidade de sincronismo) | Alta | Regras de `src/AGENTS.md` |
| `reliability` | Alta | 0 (sem fallback limpo) | +2 (transações atômicas) | -1 (risco de falha no broker) | Alta | Arquitetura ACID Django |
| `performance` | Média | +1 (síncrono rápido) | +1 (síncrono com Pillow otimizado) | +2 (não bloqueia request) | Alta | Testes de benchmark Pillow |
| `simplicity` | Alta | +1 (poucos arquivos) | +2 (padrão Django coeso) | -2 (infraestrutura pesada) | Alta | Escopo acadêmico e SLA |
| `modifiability` | Média | -1 (alto acoplamento) | +2 (fácil testabilidade) | 0 (complexidade distribuída) | Alta | Manutenibilidade da equipe |

## Histórico e decisão atual

### Decisão da versão anterior
Nenhuma (versão inicial).

### Decisão recomendada nesta versão
Adotar a **Alternativa B**:
1. Otimização Pillow encapsulada em `apps.core.services.otimizar_comprovante_fiscal` com algoritmo adaptativo para garantir teto $< 350\text{ KB}$ e rejeição estrita de arquivos corrompidos.
2. Criação de `apps.despesas.services.criar_ou_atualizar_despesa` com proteção `@transaction.atomic`.
3. Formulário `DespesaForm` em `apps.despesas.forms` responsável pela validação sintática e interface Bootstrap.
4. Views orquestradoras em `apps.despesas.views` (`nova_despesa_view`, `editar_despesa_view`, `submeter_despesa_view`, `minhas_despesas_view`).

### Impacto da revisão
Decisão inicial que desbloqueia a implementação do Marco 2 da Issue #7 e fornece as bases sólidas para a Issue #8 (UI/UX).

### Dimensões maximizadas ou priorizadas

| Dimensão | Estado | Ganho esperado | Evidência ou hipótese |
|---|---|---|---|
| `correctness` | `maximized` | Conformidade 100% com regras RN01 a RN06 | Validação centralizada no modelo e service |
| `simplicity` | `prioritized` | Entrega rápida sem dependências de infraestrutura externa | Ausência de Redis/Celery no ambiente Nix |
| `reliability` | `prioritized` | Uploads estáveis e sem perda de transação | Execução sob `@transaction.atomic` |

### Dimensões satisfeitas por limiar

| Dimensão | Limiar aceito | Como a decisão atende |
|---|---|---|
| `performance` | Tempo de resposta $< 1{,}5\text{ s}$ e imagem $< 350\text{ KB}$ | Redimensionamento para 1920px e compressão JPEG adaptativa em milissegundos |
| `modifiability` | Isolamento limpo entre backend e UI mobile | Formulário e views desacoplados de estilos rígidos |

## Perdas e trade-offs

### Perdas se as prioridades não forem atendidas

| Dimensão | Perda esperada | Severidade | Afetados |
|---|---|---|---|
| `performance` | Esgotamento do link Starlink e lentidão generalizada | Alta | Todos os voluntários em Juquitiba |
| `correctness` | Despesas sem anexo aprovadas por engano | Crítica | Tesouraria e prestação de contas |

### Custos aceitos para priorizá-las

| Dimensão favorecida | Custo ou oportunidade | Dimensão prejudicada | Aceitabilidade |
|---|---|---|---|
| `simplicity` | Compressão no mesmo ciclo de request HTTP | `performance` de pico da thread | Plenamente aceitável (compressão leva $< 200\text{ ms}$) |
| `correctness` | Bloqueio de arquivos não-imagem / não-PDF | `optionality` de formatos exóticos | Plenamente aceitável (norma fiscal padrão) |

## Riscos e efeitos de segunda ordem

- **Risco:** Celulares modernos com fotos de alta resolução (48MP+) consumirem muita memória RAM durante a descompressão inicial do Pillow.
  - **Mitigação:** Fixar limite de upload em 10MB e processar através de `Image.open` com descarte de streams em caso de exceção.
- **Risco:** Arquivo com extensão renomeada maliciosamente (ex: `.exe` renomeado para `.jpg`).
  - **Mitigação:** O Pillow valida a assinatura interna dos bytes da imagem ao executar `Image.open()`. Se for corrompido ou falso, dispara `ValidationError` formal.

## Validação da decisão

| Hipótese ou resultado | Evidência necessária | Método | Sinal para revisar |
|---|---|---|---|
| Imagens brutas $\le 5\text{ MB}$ comprimidas para $< 350\text{ KB}$ | Arquivo final persistido $\le 358.400\text{ bytes}$ | Teste unitário automatizado com imagem sintética de alta densidade | Qualquer imagem gerada $> 350\text{ KB}$ |
| Submissão sem comprovante bloqueada | Disparo de `ValidationError` em `submeter()` | Teste unitário de domínio | Despesa transicionar para `ENVIADO` sem anexo |
| Rascunho salvo sem comprovante | Despesa persistida com status `RASCUNHO` | Teste de view/form via client de teste do Django | Erro impeditivo de formulário ao salvar rascunho |

## Handoffs e atividades posteriores

1. **Marco 2 da Issue #7 (Implementação de Código):**
   - Aprimorar `otimizar_comprovante_fiscal` em `apps.core.services` e testes em `apps.core.tests`.
   - Implementar `apps.despesas.services` e `apps.despesas.forms`.
   - Implementar `apps.despesas.views`, `apps.despesas.urls` e templates em `src/templates/despesas/`.
   - Executar suíte de testes do Django e verificação de linters (`ruff`).
2. **Handoff para a Issue #8 (`@ricardosakugawa`):**
   - Disponibilização dos endpoints funcionais para aplicação do layout mobile com câmera nativa.

## Síntese

A análise conclui que a **Alternativa B** (camada de serviço transacional dedicada combinada com aprimoramento adaptativo do motor Pillow do app core) é a solução que atende com rigor máximo às restrições arquiteturais (`src/AGENTS.md`), às regras de negócio contábeis (**RN01**, **RN02**, **RN05**, **RN06**) e aos critérios de aceitação de desempenho e legibilidade (**RNF01**, **RNF02**, **RNF04**).

Arquivo criado em prompts/backend/20261030-120517-formulario-submissao-despesas-pillow-v001.md. Avalie se o local escolhido é de fato o mais adequado.
