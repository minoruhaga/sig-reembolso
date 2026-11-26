# Estratégia de Divisão de Tarefas (Equipe de 4 Integrantes) - Fase 2

**Projeto:** SIG-Reembolso  
**Disciplina:** Laboratório de Engenharia de Software (LES) – FATEC-SP  
**Contexto Operacional:** Acampamento Geral VII – Grupo Escoteiro Caramuru  
**Tamanho da Equipe:** 4 membros  
**Data Limite de Entrega Final:** 27/11/2026 (Apresentações: 13/11, 27/11 e 04/12)

---

## 1. Quando Ocorre a Divisão de Tarefas?

Em Engenharia de Software e boas práticas de desenvolvimento em equipe, a divisão de tarefas **não** deve acontecer antes do alinhamento do ecossistema base. Se os 4 integrantes começarem a codificar simultaneamente sem um esqueleto pronto, ocorrem:
* Conflitos de migrações no banco de dados (`django migrations`).
* Padrões de código e rotas incompatíveis.
* Retrabalho na integração do backend com o frontend.

O momento ideal de divisão segue o fluxo:

```
[Etapa 0: Fundação Compartilhada (CONCLUÍDA)]
  ├── Configuração do repositório, `.gitignore` e `README.md`
  ├── Setup do Django 5 em `src/` com settings modular
  └── Criação dos models base (`usuarios`, `financeiro`, `despesas`)
            │
            ▼
[Momento da Divisão de Tarefas (Ponto de Ramificação)]
  ├── Branch `feature/despesas-financeiro-core` (@minoruhaga - Minoru)
  ├── Branch `feature/rbac-relatorios` (@Mah-Rod - Marina)
  ├── Branch `feature/frontend-ui-ux` (@ricardosakugawa - Ricardo)
  └── Branch `feature/qa-testes-fixtures` (@xixinho - Giovanni)
            │
            ▼
[Integração Contínua via Pull Requests e Homologação]
```

---

## 2. Matriz de Atribuição por Membro (RACI)

Para cobrir tanto o **código executando** quanto **todos os itens obrigatórios da professora (3.g a 3.l)** sem sobrecarregar nenhum integrante e respeitando a governança do caso real (AG VII - GE Caramuru), a distribuição oficial para os 4 integrantes é:

### 👤 Membro 1: Gustavo Minoru Haga (`@minoruhaga` — Tech Lead, Product Owner, Backend Core & QA Absorvido)
* **Frentes de Código:**
  * Modelagem do Banco de Dados Relacional (PostgreSQL / SQLite) e integridade referencial.
  * Módulo `apps/financeiro`: gestão das 15 coordenações, parametrização dos tetos e cálculo do saldo dinâmico livre.
  * Módulo `apps/despesas`: CRUD de despesas, formulários de submissão e máquina de estados finita.
  * Integração com Pillow para compactação automática de notas fiscais (`RNF02`).
  * Implementação das regras de negócio estritas (`RN01` a `RN06`).
  * **Frente absorvida *(era de `@xixinho`)*:**
    * **Issue #9 (Concluída — PR #37):** Carga de dados semente com dados reais do AG VII e despesas históricas do AG VI (`carregar_dados_ag6_ag7`).
* **Entregáveis da Disciplina (FATEC):**
  * **Item 3.h:** Documentação técnica do sistema desenvolvido (programas fontes, dependências, arquitetura e ambiente de execução).
  * **Item 3.j:** Manual de Operação do Sistema (Guia dos Voluntários e Coordenadores de Campo).
  * **Item 3.l:** Homologação formal e minuta do Termo de Aceite assinado pelo cliente (Coordenação Executiva do AG VII).
  * Gestão do repositório no GitHub (Code Review e aprovação dos Pull Requests).

### 👤 Membro 2: Marina (`@Mah-Rod` — Backend de Acesso, Autenticação, Relatórios & Manual 3.k)
* **Frentes de Código:**
  * Módulo `apps/usuarios`: Custom User Model, login, logout e controle por papel (RBAC: Coordenador de Área, Tesoureiro, Administrador) — ✅ Concluído (PR #29).
  * Módulo `apps/relatorios`: rotinas de exportação de dados para prestação de contas (geração de planilhas CSV e relatórios contábeis para o GE Caramuru) — ✅ Concluído (PR #43 e PR #46).
* **Entregáveis da Disciplina (FATEC):**
  * **Item 3.k ([Issue #48](https://github.com/minoruhaga/sig-reembolso/issues/48)):** Manual de Treinamento da Tesouraria (`docs/fase-2/3k_manual_treinamento.md`), cobrindo a operação do painel de triagem, modal de conferência de notas, aprovação, reprovação justificada (RN04), liquidação Cora PJ (RF07) e exportação do balancete/CSV (RF08).
  * Apoio no **Item 3.h:** Seção de segurança, autenticação e controle de permissões.

### 👤 Membro 3: Ricardo Sakugawa (`@ricardosakugawa` — Frontend & UI/UX Completo)
* **Frentes de Código:**
  * Identidade visual unificada e temas responsivos em Bootstrap 5.3 + Bootstrap Icons.
  * **Telas de Campo (Mobile-First):**
    * Tela inicial do voluntário com extrato e termômetro visual de consumo da verba da sua coordenação.
    * Formulário ágil de submissão de despesa com acionamento nativo da câmera do celular.
  * **Painel Administrativo da Tesouraria (Desktop):**
    * Grid/Cards de triagem de notas fiscais pendentes com badges coloridos de status.
    * Modal de conferência em tela cheia com zoom no comprovante.
    * Botões de ação rápida (Aprovar / Rejeitar com formulário modal / Liquidar com comprovante Cora).
* **Entregáveis da Disciplina (FATEC):**
  * **Item 3.g:** Documento de definição das interfaces do sistema com base na usabilidade (justificativas ergonômicas, personas, contraste sob sol/chuva, navegação mobile-first e eficiência desktop).

### 👤 Membro 4: Giovanni (`@xixinho` — QA, Validação Ponta a Ponta & Item 3.i)
* *Nota de Alinhamento (23/11/2026):* Após alinhamento com a equipe, o repositório paralelo foi descartado e `@xixinho` passa a atuar diretamente sobre a base oficial em `minoruhaga/sig-reembolso` (branch `dev`), com foco exclusivo em QA e na entrega do **Item 3.i** até **27/11/2026**, sem alterar `models`, `migrations` ou arquitetura de `src/`.
* **O que deve ser feito (passo a passo):**
  1. **Setup e Execução Local:** Clonar a branch `dev`, configurar o ambiente (`nix develop` ou `.venv`), carregar os dados reais (`python manage.py carregar_dados_ag6_ag7`) e executar toda a suíte existente (`python manage.py test`) registrando os logs de aprovação dos 72 testes atuais.
  2. **Entregável Obrigatório — Item 3.i (`docs/fase-2/3i_procedimentos_testes.md`):** Redigir o documento formal de procedimentos descritivos de testes exigido pelo edital, contendo:
     * Inventário e resultados da execução da suíte automatizada (`src/apps/*/tests.py` e `test_*.py`).
     * Roteiro de testes funcionais descritivos (ID do caso, pré-condição, passos de execução, resultado esperado, resultado obtido e evidências/prints das telas) cobrindo: login/RBAC, submissão mobile com câmera e compressão Pillow (`RNF02`), regras **RN01 a RN06**, triagem da Tesouraria, liquidação Cora PJ e exportação CSV/Balancete.
  3. **Testes Extras de QA (Opcional, sem alterar produção):** Caso adicione novos testes em Python (ex.: fluxo ponta a ponta via `Client()` ou acesso cruzado entre coordenações), criar branch própria a partir de `dev` (`test/#17-procedimentos-testes-e2e`) tocando apenas arquivos `test_*.py` e abrir PR para `dev`.

---

## 3. Cronograma Semanal de Integração (Até a Apresentação)

| Semana | Período | Foco da Equipe | Marco de Entrega |
| :---: | :---: | :--- | :--- |
| **S1** | 22/10 a 31/10 | Setup do Django, models base, templates iniciais e divisão formal das branches | **Esqueleto Funcional Integrado** |
| **S2** | 01/11 a 07/11 | Conexão do fluxo de submissão (upload + compressão Pillow) com o painel da tesouraria | **Fluxo Ponta a Ponta Operando** |
| **S3** | 08/11 a 14/11 | Testes automatizados, relatórios de prestação de contas e 1ª Rodada de Apresentações | **Apresentação Prévia (13/11)** |
| **S4** | 15/11 a 21/11 | Redação dos Manuais (Operação e Treinamento) e homologação com dados reais do AG VII | **Documentação Completa** |
| **S5** | 22/11 a 27/11 | Revisão final, ensaio de apresentação e envio de todo o material no Teams | **Entrega Oficial Teams (27/11)** |
| **S6** | 28/11 a 04/12 | Defesa do software funcionando perante a banca examinadora | **Apresentação Final da Fase 2** |
