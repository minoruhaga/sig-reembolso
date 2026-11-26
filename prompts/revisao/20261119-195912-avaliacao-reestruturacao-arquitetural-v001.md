---
artifact: decision-analysis
schema_version: "4.0"
artifact_version: "v001"
status: proposed
created_at: "2026-11-19T19:59:12-03:00"
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
    - path: AGENTS.md
      relationship: context
      representation: prose
      function: prompt-instruction
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: src/AGENTS.md
      relationship: context
      representation: prose
      function: prompt-instruction
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: docs/fase-2/divisao_tarefas_equipe.md
      relationship: supporting
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: docs/fase-2/planejamento_fase_2.md
      relationship: supporting
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: .github/CODEOWNERS
      relationship: supporting
      representation: prose
      function: configuration
      format: codeowners
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: src/config/settings.py
      relationship: primary
      representation: source-code
      function: configuration
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: src/apps/despesas/models.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: src/apps/despesas/views.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: src/apps/despesas/tests.py
      relationship: supporting
      representation: source-code
      function: test
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: src/apps/financeiro/models.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: src/apps/usuarios/models.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: src/apps/core/services.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
    - path: prompts/README.md
      relationship: context
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: whole-file
      locator: null
      content_state: commit
      revision: "b75b937"
      availability: available
routing:
  root: prompts
  selected_directory: prompts/revisao
  considered_directories: [prompts/revisao, prompts/ambientes, prompts/requisitos]
  confidence: medium
  rationale: "A demanda é uma revisão arquitetural e decisória de proposta de reestruturação do projeto. A subpasta prompts/backend mencionada em prompts/README.md não existe fisicamente; prompts/revisao é a pasta existente mais aderente ao propósito de revisão arquitetural."
classification:
  sphere: engineering
  concerns: [architecture, delivery, collaboration]
  decision_kind: change
  scope: system
  lifecycle: delivery
  urgency: time-critical
  uncertainty: low
  reversibility: moderate
  risk: high
---

# Análise de decisão — Avaliação da Proposta de Reestruturação Arquitetural e Retomada da Fase 2

## Solicitação original

```markdown
# Role
Atue como sênior em gerenciamento, engenheiro e arquiteto de sistemas.

# Context
Como já havia comentado, o Giovanni queria fazer uma mudança na arquitetura do projeto, porque disse que estava confuso e desorganizado. No entanto, ele ainda não aplicou as mudanças, ou seja, ainda estamos parado desde o dia 3/11 (16 dias parados).
Como estamos parados e eu sou o único proativo, eu quero decidir o que mudar e o que não mudar para dar continuidade ao desenvolvimento do sistema. Então, depois disso, vou perguntar para o Ricardo e a Marina para ver se concordam com as novas mudanças e continuação do projeto para não dependermos do Giovanni.

## Mudanças
Raiz do projeto
manage.py: o comando principal do Django. É por ele que se roda o servidor, os testes e as migrações.
requirements.txt: a lista de bibliotecas do projeto (Django e Pillow, para imagens).
.venv: o ambiente virtual, onde essas bibliotecas ficam instaladas só para este projeto. Não vai para o GitHub.
db.sqlite3: o banco de dados local, um arquivo simples. Também não vai para o GitHub.
.gitignore: diz ao Git o que não versionar (o .venv, o banco, as senhas).
.env.example: modelo das configurações secretas (como a chave de segurança). Cada pessoa cria o seu .env a partir dele.
README.md: o cartão de visita do projeto, com a descrição.
sig_reembolso/: a configuração do projeto
settings/: as configurações, separadas em três: base (comum), dev (no computador) e prod (no servidor de verdade).
urls.py: o mapa de endereços do site. Por enquanto só tem a área de administração.
wsgi.py: o ponto de entrada quando o site vai para um servidor real.
container.py: o "montador". Junta as peças (serviços e repositórios) em um só lugar, como o Program.cs do SmartRules.
__init__.py: arquivo vazio que diz ao Python "esta pasta é um pacote". Aparece em quase toda pasta.
apps/: as funcionalidades, uma pasta para cada assunto
accounts: quem é o usuário e o que ele pode fazer (Coordenador, Tesouraria ou Administrador).
orcamento: as coordenações e o teto de verba de cada uma, com o cálculo do saldo.
despesas: o coração do sistema. Aqui ficam o lançamento, a aprovação, a rejeição, a liquidação e o histórico, com todas as regras.
relatorios: reservada para as exportações (CSV). Por enquanto está só o esqueleto.
Cada app segue as mesmas camadas do SmartRules: models (dados), interfaces (contratos), repositories (acesso ao banco), services (regras de negócio) e tests (testes).

common/: o que é compartilhado por todos
enums.py: listas fixas, como os status da despesa e os perfis de usuário.
exceptions.py: os erros de regra de negócio (por exemplo, "falta o comprovante").
dtos.py: o pacote de dados que viaja do formulário para o serviço.
imagens.py: reservado para a compressão das fotos. Ainda não foi feito.
Telas
templates/: onde ficam as páginas HTML. Ainda está vazia.
static/: onde ficam o CSS, o JavaScript e as imagens do site. Também vazia.

# Task
1. Comente sobre as mudanças do Giovanni. Vale aplicar todas ou alguma das sugestões dele? Se sim, liste-as (criando um documento para implementação das mudanças) e explique por que aplicar e por que não aplicar. Além disso, antes de aplicarmos a mudanças, é ideal entrar em contato com o Ricardo e com a Marina para verem se concordam com a mudança?
```

## Informações complementares

Nenhum identificado.

## Mudanças desde a versão anterior

Nenhum identificado — versão inicial (`v001`).

## Artefatos analisados

| Caminho | Relação | Representação | Função | Formato | Recorte | Estado/revisão |
|---|---|---|---|---|---|---|
| `AGENTS.md` | `context` | `prose` | `prompt-instruction` | `markdown` | `whole-file` | `commit` (`b75b937`) |
| `src/AGENTS.md` | `context` | `prose` | `prompt-instruction` | `markdown` | `whole-file` | `commit` (`b75b937`) |
| `docs/fase-2/divisao_tarefas_equipe.md` | `supporting` | `prose` | `documentation` | `markdown` | `whole-file` | `commit` (`b75b937`) |
| `docs/fase-2/planejamento_fase_2.md` | `supporting` | `prose` | `documentation` | `markdown` | `whole-file` | `commit` (`b75b937`) |
| `.github/CODEOWNERS` | `supporting` | `prose` | `configuration` | `codeowners` | `whole-file` | `commit` (`b75b937`) |
| `src/config/settings.py` | `primary` | `source-code` | `configuration` | `python` | `whole-file` | `commit` (`b75b937`) |
| `src/apps/despesas/models.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`b75b937`) |
| `src/apps/despesas/views.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`b75b937`) |
| `src/apps/despesas/tests.py` | `supporting` | `source-code` | `test` | `python` | `whole-file` | `commit` (`b75b937`) |
| `src/apps/financeiro/models.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`b75b937`) |
| `src/apps/usuarios/models.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`b75b937`) |
| `src/apps/core/services.py` | `primary` | `source-code` | `production` | `python` | `whole-file` | `commit` (`b75b937`) |
| `prompts/README.md` | `context` | `prose` | `documentation` | `markdown` | `whole-file` | `commit` (`b75b937`) |

### Limites da evidência dos artefatos

- A proposta do Giovanni foi fornecida apenas como descrição textual na solicitação do usuário; não existe branch, PR ou código implementado por ele no repositório local (`HEAD` em `b75b937`, de 30/10/2026).
- O projeto "SmartRules" citado na proposta é uma referência externa não presente neste repositório; sua menção (`Program.cs`, `interfaces`, `repositories`, `dtos`, `container.py`) indica convenções arquiteturais típicas de .NET/C# (Clean Architecture / Dependency Injection explícita).
- Não foram inspecionados os conteúdos de `src/templates/base.html`, `src/templates/dashboard.html`, `src/apps/financeiro/views.py`, `src/apps/usuarios/views.py` ou `.github/workflows/`, apenas sua existência no diretório.

## Problema enriquecido

### Resultado desejado
Destravar imediatamente o desenvolvimento do **SIG-Reembolso** (parado há 16 dias), decidindo com critério técnico quais elementos da proposta arquitetural do Giovanni agregam valor real e quais devem ser rejeitados, produzindo um roteiro objetivo de implementação das melhorias selecionadas e definindo a estratégia ideal de alinhamento com Ricardo e Marina para garantir a entrega da 2ª Fase no prazo.

### Atores e interesses
- **Gustavo Minoru Haga (`@minoruhaga`, Tech Lead / PO / Backend Core):** Precisa retomar o ritmo, proteger o núcleo de domínio já validado e garantir entrega funcional e documentada até 27/11/2026.
- **Marina (`@Mah-Rod`, Backend de Acesso & Relatórios):** Depende de clareza na estrutura de `apps/usuarios` e `apps/relatorios` para implementar RBAC nas rotas e exportação CSV sem retrabalho.
- **Ricardo Sakugawa (`@ricardosakugawa`, Frontend & UI/UX):** Depende de estabilidade em `src/templates/`, `src/static/` e nos contratos das views para construir as telas Mobile-First e Desktop (Item 3.g).
- **Giovanni (`@xixinho`, QA / Testes / Co-aprovador em CODEOWNERS):** Propôs reestruturação inspirada em .NET ("SmartRules"), mas não executou alterações em 16 dias; sua ausência representa risco operacional e de governança no fluxo de PRs.
- **Banca Avaliadora (FATEC-SP / LES) e Cliente (AG VII — GE Caramuru):** Exigem software executando ponta a ponta e entregas `3.g` a `3.l` no Teams até **27/11/2026** (com apresentação final até **04/12/2026**).

### Evidências e fatos observados
1. **Prazo crítico:** A data atual é **19/11/2026**. Segundo `docs/fase-2/planejamento_fase_2.md` e `docs/fase-2/divisao_tarefas_equipe.md`, a entrega oficial da documentação no Teams é **27/11/2026** (8 dias restantes) e a apresentação final é **04/12/2026** (15 dias restantes).
2. **Repositório parado:** O último commit em `dev` é `b75b937` de **30/10/2026**. O usuário relata 16 dias de paralisação desde 03/11.
3. **Fundação Django já implementada e testada em `src/`:**
   - `src/apps/usuarios/models.py`: Custom User Model `Usuario` e `PapelUsuario` já implementados com docstrings e migrations.
   - `src/apps/financeiro/models.py`: `Coordenacao` com `teto_orcamentario`, `total_comprometido`, `saldo_disponivel` e `percentual_consumido` em `Decimal`.
   - `src/apps/despesas/models.py`: `Despesa` e `HistoricoTransicaoStatus` com todas as regras **RN01 a RN06** implementadas sob `@transaction.atomic`.
   - `src/apps/despesas/tests.py`: Suíte unitária cobrindo RN01 a RN06 já escrita.
   - `src/apps/core/services.py`: Função `otimizar_comprovante_fiscal` com Pillow, correção EXIF e anonimização UUID v4 já implementada (apesar de a proposta afirmar que `imagens.py` "ainda não foi feito").
   - `.gitignore`, `.env.example`, `README.md`, `src/manage.py`, `src/requirements.txt`, `src/templates/`, `src/static/` e `src/fixtures/coordenacoes_iniciais.json` já existem no repositório.
4. **Lacunas reais para entrega funcional:**
   - `src/apps/despesas/views.py` está vazio (apenas comentário padrão do Django).
   - O app `apps/relatorios` (atribuído à Marina em `divisao_tarefas_equipe.md`) ainda não foi criado em `src/apps/`.
   - `src/config/settings.py` é um único arquivo (já parametrizado com `os.getenv`, porém sem separação `base`/`dev`/`prod`).
5. **Gargalo oculto de governança:** `.github/CODEOWNERS` exige aprovação de `* @minoruhaga @xixinho`, o que pode bloquear merges caso haja regra de proteção de branch exigindo todos os codeowners.

### Hipóteses
- **H1:** Ricardo e Marina estão disponíveis para retomar o desenvolvimento se receberem uma estrutura estável e tarefas claras, sem precisar aprender padrões de .NET em Django.
- **H2:** Giovanni continuará indisponível ou sem capacidade de entregar uma refatoração estrutural antes de 27/11/2026.
- **H3:** A banca da FATEC-SP valorizará muito mais o sistema funcionando ponta a ponta com testes, RN01–RN06 íntegras e itens `3.g`–`3.l` completos do que uma arquitetura multi-camadas artificial com container de DI.

### Perguntas em aberto
- Ricardo e Marina concordam em manter a base atual em `src/` aplicando apenas as 3 melhorias incrementais selecionadas?
- A proteção de branch no GitHub bloqueia merges sem a aprovação de `@xixinho` (por causa de `.github/CODEOWNERS`)?
- Quem absorverá o entregável `3.i` (Procedimentos descritivos de testes) e testes de integração caso Giovanni não retorne nos próximos dias?

### Escopo
- Avaliação técnica item a item das mudanças propostas pelo Giovanni.
- Decisão sobre o que adotar, o que descartar e a justificativa arquitetural e gerencial.
- Roteiro de implementação das mudanças aprovadas (especificação para execução posterior).
- Recomendação de governança e alinhamento com Ricardo e Marina antes da execução.

### Fora do escopo
- Alteração direta de código-fonte, migrations, settings ou `.github/CODEOWNERS` neste artefato.
- Implementação de views, templates ou relatórios (atividades posteriores à decisão).

### Critérios de sucesso
1. Zero regressão nos modelos, migrations e testes de RN01–RN06 já existentes.
2. Tempo de aplicação das melhorias arquiteturais selecionadas inferior a 2 horas no total.
3. Desbloqueio imediato das frentes de Marina (`apps/usuarios`, `apps/relatorios`) e Ricardo (`templates/`, `static/`).
4. Alinhamento documentado com Ricardo e Marina em até 24 horas (sem abrir novo ciclo de paralisação).

## Restrições aplicáveis

1. **Prazo rígido (Hard Constraint):** Entrega no Teams em **27/11/2026** (8 dias) e apresentação final em **04/12/2026**. Qualquer refatoração que consuma múltiplos dias reescrevendo código funcional coloca a entrega em risco crítico.
2. **Integridade de domínio (`src/AGENTS.md`):** Regras de negócio RN01–RN06 devem permanecer em `models.py` ou `services.py`, com `@transaction.atomic` e `Decimal`. Views não podem conter lógica contábil.
3. **Code First / Migrations (`src/AGENTS.md`):** É proibido apagar ou editar migrations já integradas em `dev`/`main`. Renomear apps (`usuarios` → `accounts`, `financeiro` → `orcamento`) quebra a história de migrations e o `AUTH_USER_MODEL = 'usuarios.Usuario'`.
4. **RNF02 (`src/AGENTS.md`):** O serviço obrigatório de compressão de comprovantes está formalmente referenciado como `apps.core.services.otimizar_comprovante_fiscal`.
5. **Padrão de Docstrings (`AGENTS.md`):** Todo novo módulo, classe ou função exige docstring completa (*O que faz*, *Como faz*, *Qual finalidade atende*).

## Classificação comentada

- **Esfera (`engineering`):** O núcleo da decisão é arquitetura de software Django vs. portabilidade de padrões .NET, diretamente acoplada à entrega.
- **Preocupações (`architecture`, `delivery`, `collaboration`):** Equilibra qualidade estrutural, prazo crítico de 8 dias e coordenação da equipe reduzida/assíncrona.
- **Urgência (`time-critical`) e Risco (`high`):** Com 8 dias até a entrega no Teams e 16 dias já perdidos, uma decisão equivocada (como reescrever tudo) torna a entrega da Fase 2 inviável.

## Decisão de roteamento

Inventário real de subpastas em `prompts/`: `ambientes`, `frontend`, `requisitos`, `revisao`, `templates`, `testes`.
- `prompts/backend` consta na documentação `prompts/README.md`, mas não existe no sistema de arquivos (e a skill veda criar subpasta nova).
- `prompts/revisao` é definida em `prompts/README.md` para revisões arquiteturais e auditorias, sendo a pasta existente mais aderente ao propósito principal desta análise.
- `prompts/ambientes` foi considerada por envolver `settings/`, mas descartada como destino principal porque a decisão abrange estrutura de apps, camadas de domínio e governança da equipe.

## Dimensões de decisão

| Dimensão | Prioridade | Limiar ou direção | Por que importa |
|---|---|---|---|
| `delivery-speed` | Alta (1) | Maximizar | Faltam apenas 8 dias para a entrega no Teams após 16 dias parados; o sistema ainda precisa de views, telas, relatórios e manuais. |
| `correctness` | Alta (2) | Limiar mínimo: 100% das RN01–RN06 e testes existentes preservados | Quebrar migrations, `AUTH_USER_MODEL` ou testes contábeis compromete a nota e o uso real no AG VII. |
| `simplicity` | Alta (3) | Maximizar aderência idiomática ao Django | Equipe de 3–4 estudantes; arquitetura simples e idiomática acelera onboarding de Ricardo e Marina e reduz bugs. |
| `cognitive-load` | Média (4) | Minimizar | Introduzir DI Container (`container.py`), ABCs (`interfaces`), `repositories` e `dtos` sobre o Django ORM aumenta drasticamente a fricção para o time. |
| `modifiability` | Média (5) | Limiar aceito: modularidade limpa por app + `services.py` + `settings/` modular | Garante organização clara para a banca (Item 3.h) sem over-engineering. |
| `team-autonomy` | Média (6) | Maximizar desacoplamento entre frentes | Permite que Minoru, Marina e Ricardo avancem em paralelo sem depender do Giovanni. |

## Alternativas consideradas

1. **Alternativa A — Adoção integral da proposta do Giovanni (Reestruturação estilo SmartRules/.NET):**
   Mover o projeto Django para a raiz, renomear `config/` → `sig_reembolso/`, `usuarios` → `accounts`, `financeiro` → `orcamento`, `core` → `common`, e reescrever todos os apps com camadas `models`, `interfaces`, `repositories`, `services`, `dtos`, `container.py` e `common/enums.py`.
   *Nota:* Viola parcialmente a restrição de não quebrar migrations já integradas em `dev` e compromete diretamente a restrição dura de prazo (8 dias).

2. **Alternativa B — Adoção seletiva e incremental mantendo a base Django em `src/` (Recomendada):**
   Manter a estrutura atual já validada em `src/` (`config/`, `apps/core`, `apps/usuarios`, `apps/financeiro`, `apps/despesas`, `templates/`, `static/`) e incorporar **apenas** os pontos genuinamente benéficos e de baixo custo:
   - Criar o app `src/apps/relatorios/` (previsto no planejamento da Marina).
   - Modularizar `src/config/settings/` em `base.py`, `dev.py` e `prod.py` (opcional/rápido, mantendo compatibilidade total).
   - Criar `src/apps/core/exceptions.py` com exceções de domínio nomeadas (herdando de `ValidationError` para retrocompatibilidade) e usar `services.py` nos apps conforme as views/orquestrações forem criadas.

3. **Alternativa C — Manutenção estrita do estado atual (Zero mudanças estruturais):**
   Não aplicar nenhuma sugestão do Giovanni (nem `settings/` modular, nem `exceptions.py`), criando apenas `apps/relatorios` quando a Marina iniciar a exportação CSV.

## Perfil de pagamento comparativo

| Dimensão | Prioridade | Alternativa A (Integral Giovanni) | Alternativa B (Seletiva Incremental) | Alternativa C (Zero Mudanças) | Confiança | Base |
|---|---:|---:|---:|---:|---|---|
| `delivery-speed` | Alta (1) | `-2` | `+2` | `+2` | Alta | Evidência do prazo (8 dias) e volume de reescrita da Alt. A |
| `correctness` | Alta (2) | `-2` | `+2` | `+1` | Alta | Migrations, `AUTH_USER_MODEL` e testes RN01–RN06 já passando em `src/` |
| `simplicity` | Alta (3) | `-2` | `+2` | `+2` | Alta | Django idiomático vs. boilerplate .NET (`container.py`, `interfaces`, `repositories`, `dtos`) |
| `cognitive-load` | Média (4) | `-2` | `+1` | `+2` | Alta | Curva de aprendizado desnecessária para Ricardo e Marina na Alt. A |
| `modifiability` | Média (5) | `+1` | `+2` | `0` | Média | `settings/` separado + `apps/relatorios` + `exceptions.py` atendem bem sem over-engineering |
| `team-autonomy` | Média (6) | `-2` | `+2` | `+1` | Alta | Alt. B cria `apps/relatorios` e destrava imediatamente Marina e Ricardo |

## Histórico e decisão atual

### Decisão da versão anterior
Nenhum identificado — versão inicial (`v001`).

### Decisão recomendada nesta versão
**Adotar a Alternativa B (Adoção seletiva e incremental mantendo a base Django em `src/`), validada via alinhamento ágil (prazo máximo de 24h) com Ricardo e Marina antes da execução.**

#### Matriz de Decisão — O que Aplicar vs. O que NÃO Aplicar

| Item proposto pelo Giovanni | Decisão | Justificativa técnica e gerencial |
|---|---|---|
| **Criar app `apps/relatorios/`** | **APLICAR** (em `src/apps/relatorios/`) | Requisito real da Fase 2 (exportação CSV), atribuído à Marina em `divisao_tarefas_equipe.md`, e ainda ausente no código. Custo mínimo (~15 min). |
| **Separar `settings/` em `base.py`, `dev.py`, `prod.py`** | **APLICAR** (em `src/config/settings/`) | Boa prática idiomática de Django para isolar configuração local (SQLite/`DEBUG=True`) de produção (PostgreSQL/`DEBUG=False`). Baixo custo (~20–30 min) e valoriza o Item 3.h, desde que `manage.py` e `wsgi.py` mantenham default funcional (`config.settings.dev`). |
| **Criar `exceptions.py` para erros de negócio** | **APLICAR** (em `src/apps/core/exceptions.py`) | Melhora clareza semântica dos erros de domínio (ex.: `ComprovanteObrigatorioError`, `SegregacaoFuncoesError`, `ImutabilidadeDespesaError`). Herdando de `django.core.exceptions.ValidationError`, mantém 100% de compatibilidade com os testes e forms existentes. |
| **Usar `services.py` por app** | **APLICAR SOB DEMANDA** | `src/AGENTS.md` já prevê regras em `models.py` ou `services.py`. Manter as transições atuais em `Despesa` (já testadas) e criar `apps/despesas/services.py` apenas para orquestração de casos de uso que envolvam múltiplos componentes (ex.: compressão Pillow + criação/submissão). |
| **Mover `src/` para a raiz do projeto** | **NÃO APLICAR** | `manage.py`, `requirements.txt`, `templates/`, `static/` já existem e ficam organizados dentro de `src/` para isolar código-fonte de `docs/`, `prompts/`, `flake.nix` e arquivos de governança. Mover gera quebra de paths, CI e documentação sem ganho funcional. |
| **Renomear `config/` → `sig_reembolso/`, `usuarios` → `accounts`, `financeiro` → `orcamento`, `core` → `common`** | **NÃO APLICAR** | Churn puramente cosmético. Quebra `AUTH_USER_MODEL = 'usuarios.Usuario'`, migrations existentes em `dev`, `fixtures/coordenacoes_iniciais.json`, imports, `src/AGENTS.md` e toda a documentação da Fase 2. |
| **`container.py` (DI Container estilo `Program.cs` do .NET)** | **NÃO APLICAR** | Anti-pattern/over-engineering em Django. Python/Django não precisa de container de injeção de dependência para um monólito MVC acadêmico/operacional de 4 apps. |
| **Camadas `interfaces/` + `repositories/` + `dtos.py`** | **NÃO APLICAR** | Transplante de arquitetura C#/.NET ("SmartRules") incompatível com a ergonomia do Django ORM, ModelForms e Django Admin. Multiplica arquivos e boilerplate, aumenta carga cognitiva da equipe e consome dias críticos reescrevendo código que já funciona. |
| **Centralizar `common/enums.py`** | **NÃO APLICAR** | Os enums (`PapelUsuario`, `StatusDespesa`, `CategoriaDespesa`, `TipoDespesa`, `FormaPagamentoOriginal`) já existem coesos junto aos respectivos `models.py`. Movê-los cria acoplamento artificial e risco de imports circulares. |
| **Criar `common/imagens.py` ("ainda não foi feito")** | **NÃO APLICAR (JÁ EXISTE)** | Já está implementado em `src/apps/core/services.py` (`otimizar_comprovante_fiscal`) com Pillow, correção EXIF e UUID v4, exatamente como exigido por `src/AGENTS.md`. |
| **Criar `.gitignore`, `.env.example`, `README.md`, `templates/`, `static/`** | **NÃO APLICAR (JÁ EXISTEM)** | Todos esses arquivos e pastas já existem e estão configurados no repositório. |

#### Sobre consultar Ricardo e Marina antes de aplicar
- **Decisão:** **Sim, consultar antes de aplicar**, mas em formato de **alinhamento rápido por consentimento (janela de 24h)**, levando a proposta fechada (Alternativa B) pronta para aprovação.
- **Motivo:**
  1. Evita que o Tech Lead imponha mudanças unilateralmente e garante adesão real de quem vai codificar frontend (Ricardo) e RBAC/relatórios (Marina).
  2. Elimina o risco de reabrir um debate infinito de arquitetura: em vez de perguntar *"o que vocês acham que devemos fazer?"*, apresenta-se *"estamos parados há 16 dias e faltam 8 dias para a entrega; vamos manter a base atual em `src/` e aplicar apenas estas 3 melhorias rápidas — se ninguém tiver objeção até [horário/amanhã], sigo com isso e destravamos as branches"*.
  3. Serve como ponto de decisão para redistribuir eventuais pendências do Giovanni (especialmente testes/Item 3.i) e revisar `.github/CODEOWNERS`.

### Impacto da revisão
Nenhum identificado — versão inicial (`v001`).

### Dimensões maximizadas ou priorizadas

| Dimensão | Estado | Ganho esperado | Evidência ou hipótese |
|---|---|---|---|
| `delivery-speed` | `prioritized` | Retomada imediata do desenvolvimento funcional (views, telas e relatórios) em menos de 1 dia | Restam 8 dias até 27/11/2026 (`planejamento_fase_2.md`). |
| `correctness` | `prioritized` | Preservação integral de RN01–RN06, migrations e testes unitários existentes | Evidenciado em `src/apps/despesas/models.py` e `tests.py`. |
| `simplicity` | `maximized` | Manutenção de Django idiomático com baixa curva de aprendizado para toda a equipe | Comparação direta entre estrutura atual e boilerplate da Alternativa A. |
| `team-autonomy` | `prioritized` | Marina e Ricardo podem trabalhar em paralelo nas próprias pastas sem depender do Giovanni | Evidenciado em `divisao_tarefas_equipe.md`. |

### Dimensões satisfeitas por limiar

| Dimensão | Limiar aceito | Como a decisão atende |
|---|---|---|
| `modifiability` | Separação clara por app + `settings/` por ambiente + `exceptions.py` + `services.py` sob demanda | Atende às boas práticas de engenharia para o Item 3.h sem reescrever o ORM. |
| `cognitive-load` | Qualquer integrante consegue localizar models, views, services e templates sem aprender padrões de .NET | Mantém convenções padrão da documentação oficial do Django. |

## Perdas e trade-offs

### Perdas se as prioridades não forem atendidas

| Dimensão | Perda esperada | Severidade | Afetados |
|---|---|---|---|
| `delivery-speed` | Não concluir telas, fluxo ponta a ponta e documentação `3.g`–`3.l` até 27/11/2026 | Crítica | Toda a equipe (nota da disciplina LES) e cliente AG VII |
| `correctness` | Quebra de migrations, `AUTH_USER_MODEL` ou regressão nas regras RN01–RN06 | Alta | Backend Core, Tesouraria do AG VII e banca avaliadora |
| `team-autonomy` | Continuidade da paralisação aguardando um integrante inativo há 16 dias | Alta | Minoru, Ricardo e Marina |

### Custos aceitos para priorizá-las

| Dimensão favorecida | Custo ou oportunidade | Dimensão prejudicada | Aceitabilidade |
|---|---|---|---|
| `delivery-speed` / `simplicity` | Não adotar abstração de repositórios/interfaces que permitiria trocar o Django ORM por outra camada de persistência | `modifiability` (hipotética troca de ORM) | Alta — não há requisito de troca de ORM e o Django ORM é a espinha dorsal do projeto. |
| `delivery-speed` | Eventual desconforto interpessoal com Giovanni por descartar a maior parte da sua proposta | `collaboration` (com 1 integrante ausente) | Aceitável — decisão baseada em evidência técnica e prazo real, transparente e documentada. |

## Riscos e efeitos de segunda ordem

1. **Bloqueio de Pull Requests via `.github/CODEOWNERS`:** O arquivo atual exige `@minoruhaga @xixinho`. Se a branch `dev`/`main` tiver proteção exigindo aprovação de todos os codeowners, os PRs de Marina, Ricardo e Minoru ficarão travados. *Mitigação:* Verificar nas configurações do GitHub e, em acordo com Ricardo e Marina, atualizar `CODEOWNERS` para membros ativos.
2. **Descobertura do Item 3.i (QA e Testes):** Giovanni era o responsável pelo Item 3.i e testes integrados em `divisao_tarefas_equipe.md`. *Mitigação:* Já definir no alinhamento com Ricardo e Marina como dividir a cobertura de testes das views/relatórios e a redação do `3i_procedimentos_testes.md`.
3. **Quebra acidental de `DJANGO_SETTINGS_MODULE` ao modularizar `settings/`:** Comandos em `flake.nix`, `manage.py`, `wsgi.py`, `asgi.py` ou `.github/workflows/` podem falhar se o caminho mudar sem compatibilidade. *Mitigação:* Manter `src/config/settings/__init__.py` ou apontar explicitamente para `config.settings.dev` por padrão e rodar `manage.py test` imediatamente após a mudança.

## Validação da decisão

| Hipótese ou resultado | Evidência necessária | Método | Sinal para revisar |
|---|---|---|---|
| Acordo da equipe ativa (H1) | Confirmação explícita de Ricardo e Marina no grupo da equipe | Mensagem objetiva com prazo de 24h | Objeção técnica fundamentada de Ricardo ou Marina |
| Zero regressão após melhorias | Todos os testes passando (`python manage.py test`) e `ruff check` limpo | Execução local dentro do ambiente isolado (`nix develop` / `.venv`) | Falha em migrations, imports ou qualquer teste de RN01–RN06 |
| Retomada real do fluxo de entrega | Primeiras views/templates/rotas integrados em `dev` nos próximos 2–3 dias | Acompanhamento de commits/PRs no GitHub | Novo travamento por conflito de estrutura ou CODEOWNERS |

## Handoffs e atividades posteriores

### 1. Alinhamento prévio com Ricardo e Marina (Antes de mexer no código)
Enviar mensagem curta e objetiva apresentando:
- O diagnóstico real (16 dias parados, 8 dias até 27/11, fundação Django já pronta e testada em `src/`).
- A proposta fechada: manter a arquitetura atual em `src/` e aplicar apenas as 3 melhorias incrementais abaixo.
- Prazo curto de resposta (ex.: até amanhã ou 24h) para consentimento.
- Pauta rápida adicional: atualizar `.github/CODEOWNERS` (para não depender de aprovação de quem está ausente) e redistribuir os testes/Item 3.i caso Giovanni continue inativo.

### 2. Roteiro de Implementação das Mudanças Aprovadas (Estimativa: ~1h a 1h30)
Após confirmação de Ricardo e Marina (ou decurso do prazo de alinhamento), executar em micro-commits na branch `dev` (ou branch dedicada com PR):

1. **Criar app `src/apps/relatorios/`**
   - Executar `python manage.py startapp relatorios` dentro de `src/apps/` (ou criar estrutura padronizada com `apps.py`, `services.py`, `views.py`, `urls.py`, `tests.py` e docstrings completas).
   - Registrar `'apps.relatorios'` em `INSTALLED_APPS`.
   - Incluir rota base em `src/config/urls.py`.
2. **Criar `src/apps/core/exceptions.py`**
   - Definir exceção base `SigReembolsoDomainError(ValidationError)` e especializações semânticas (`ComprovanteObrigatorioError`, `TransicaoStatusInvalidaError`, `SegregacaoFuncoesError`, `JustificativaRejeicaoObrigatoriaError`, `ImutabilidadeDespesaError`).
   - Opcionalmente adotá-las nos métodos de `Despesa` (mantendo herança de `ValidationError` para preservar 100% dos testes existentes).
3. **Modularizar `src/config/settings/`** *(somente se não houver conflito com CI/workflows)*
   - Converter `src/config/settings.py` em pacote `src/config/settings/`:
     - `base.py`: configurações comuns atuais (com `BASE_DIR = Path(__file__).resolve().parent.parent.parent` — atenção ao nível extra de `.parent`!).
     - `dev.py`: importa `base`, define `DEBUG = True`, SQLite local e `ALLOWED_HOSTS = ['*']`.
     - `prod.py`: importa `base`, força `DEBUG = False`, exige `DJANGO_SECRET_KEY` e `DJANGO_ALLOWED_HOSTS` via ambiente e configura PostgreSQL via variáveis de ambiente.
     - `__init__.py`: pode permanecer vazio se `manage.py`, `wsgi.py`, `asgi.py` e CI apontarem explicitamente para `config.settings.dev` (ou carregar `dev` como fallback seguro).
4. **Verificação obrigatória pós-mudança**
   - Executar `python src/manage.py check`, `python src/manage.py makemigrations --check --dry-run`, `python src/manage.py test` e `ruff check .` dentro do ambiente isolado (`nix develop` ou `.venv`).
5. **Governança**
   - Revisar `.github/CODEOWNERS` para evitar bloqueio de PRs por integrantes inativos.

## Síntese

A proposta do Giovanni mistura elementos que **já existem** no projeto (`.gitignore`, `.env.example`, compressão de imagens com Pillow em `apps/core/services.py`, `templates/`, `static/`) com um **transplante de arquitetura .NET ("SmartRules")** (`container.py`, `interfaces/`, `repositories/`, `dtos.py`) e renomeações destrutivas (`src/` para raiz, `usuarios` → `accounts`, `financeiro` → `orcamento`). Aplicar tudo a **8 dias da entrega oficial (27/11/2026)** seria um erro estratégico grave que quebraria migrations e desperdiçaria o núcleo RN01–RN06 já validado.

A decisão recomendada é **manter a base Django idiomática em `src/`**, incorporar **apenas 3 melhorias cirúrgicas e de baixo custo** (`src/apps/relatorios/`, `src/apps/core/exceptions.py` e `src/config/settings/{base,dev,prod}.py`), e fazer um **alinhamento rápido (janela de 24h) com Ricardo e Marina** antes de aplicar — aproveitando para revisar `.github/CODEOWNERS` e destravar imediatamente as frentes de views, telas e documentação da Fase 2.
