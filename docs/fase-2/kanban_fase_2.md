# Quadro Kanban e Sequenciamento de Entregas - Fase 2

Este documento estabelece o **Quadro Kanban** do SIG-Reembolso para a Fase 2 (Desenvolvimento), organizado por **Fatias Verticais** e **Ondas de Entrega** para garantir que os 4 integrantes trabalhem em paralelo sem conflitos de merge no Django e com foco nas datas do edital de LES da FATEC-SP.

---

## 🧭 Estrutura do Quadro (Colunas de Fluxo)

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   📋 BACKLOG    │──►│ ⏳ A FAZER      │──►│ ⚙️ EM PROGRESSO │──►│ 🔍 EM REVISÃO   │──►│  ✅ CONCLUÍDO   │
│                 │   │    (To Do)      │   │                 │   │    (PR Aberto)  │   │     (Done)      │
└─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## 🌊 Sequenciamento por Ondas de Desenvolvimento (Fatias Verticais)

### 🟢 Onda 0: Fundação, DevOps e Governança (Concluída)
*Objetivo: Estabelecer a base estável, regras de IA, CI/CD e guias para que a equipe possa trabalhar sem fricção.*

| ID | Issue / Card | Responsável | Área | Status |
| :-: | :--- | :---: | :---: | :---: |
| **#01** | `[Docs] Elaborar README.md completo e Onboarding` | `@minoru` | Docs / Infra | **[CONCLUÍDO]** |
| **#02** | `[Gov] Definir Governança de IA, AGENTS.md e Prompts` | `@minoru` | Governança | **[CONCLUÍDO]** |
| **#03** | `[DevOps] Pipeline de CI/CD com GitHub Actions + Nix` | `@minoru` | DevOps / CI | **[CONCLUÍDO]** |
| **#04** | `[Gov] CONTRIBUTING.md, .env.example e Templates` | `@minoru` | Governança | **[CONCLUÍDO]** |
| **#18** | `[Docs] Guia de Instalação WSL, Nix e Flakes` | `@minoru` | Docs / Infra | **[CONCLUÍDO]** |

---

### 🟡 Onda 1: Fila de Triagem, Submissão Mobile e Dados Reais (Semana 1: 27/10 a 04/11)
*Objetivo: Entregar a jornada ponta a ponta básica (Coordenador fotografa cupom no celular $\rightarrow$ Despesa cai no banco $\rightarrow$ Tesoureiro visualiza).*

| ID | Issue / Card | Responsável | Branch Sugerida | Status |
| :-: | :--- | :---: | :--- | :---: |
| **#05** | `[RBAC] Telas de Login, Logout e Controle por Papel` | **Membro 1** | `feature/#05-login-rbac` | ⏳ A Fazer |
| **#08** | `[Despesas] Formulário de Submissão com Pillow (RNF02/RN01)` | **Membro 2** | `feature/#08-formulario-despesa` | ⏳ A Fazer |
| **#11** | `[UI/UX] Interface Mobile-First com Câmera Nativa (RNF01)` | **Membro 3** | `feature/#11-tela-mobile-camera` | ⏳ A Fazer |
| **#14** | `[Dados] Carga de dados reais do AG VI e Coordenadores AG VII` | **Membro 4** | `feature/#14-fixture-ag6-ag7` | ⏳ A Fazer |

---

### 🟠 Onda 2: Motor de Regras Financeiras e Painel da Tesouraria (Semana 2: 05/11 a 12/11)
*Objetivo: Integrar as regras estritas de domínio contábil antes da 1ª rodada de apresentações da banca.*

| ID | Issue / Card | Responsável | Branch Sugerida | Status |
| :-: | :--- | :---: | :--- | :---: |
| **#06** | `[Financeiro] API e View dinâmica de saldos e tetos (RF03)` | **Membro 1** | `feature/#06-saldos-tetos` | 📋 Backlog |
| **#09** | `[Workflow] Ações de Triagem: Aprovar, Rejeitar e Liquidar` | **Membro 2** | `feature/#09-acoes-triagem` | 📋 Backlog |
| **#10** | `[Regras] Soft-block de estouro e Segregação de Funções (RN02/RN03)` | **Membro 2** | `feature/#10-regras-dominio` | 📋 Backlog |
| **#12** | `[UI/UX] Painel Desktop da Tesouraria com Modal de Zoom` | **Membro 3** | `feature/#12-painel-triagem` | 📋 Backlog |

---

### 🔴 Onda 3: Qualidade, Relatórios e Entregáveis Formais (Semana 3 e 4: 13/11 a 27/11)
*Objetivo: Fechar os relatórios de exportação e produzir os artefatos formais exigidos pela professora (Itens 3.g a 3.l).*

| ID | Issue / Card | Responsável | Entregável Oficial | Status |
| :-: | :--- | :---: | :---: | :---: |
| **#07** | `[Docs] Documentação técnica do sistema desenvolvido` | **Membro 1** | **Item 3.h** | 📋 Backlog |
| **#13** | `[Docs] Definição e justificativa das interfaces (Usabilidade)` | **Membro 3** | **Item 3.g** | 📋 Backlog |
| **#15** | `[Testes] Procedimentos descritivos de testes e expansão TestCase` | **Membro 4** | **Item 3.i** | 📋 Backlog |
| **#16** | `[Docs] Manual de Operação do Sistema (Guia de Campo)` | **Membro 4** | **Item 3.j** | 📋 Backlog |
| **#17** | `[Docs] Manual de Treinamento da Tesouraria e Homologação` | **Membro 4** | **Itens 3.k e 3.l** | 📋 Backlog |

---

## 🛠️ Como Configurar o GitHub Projects da Equipe

Para espelhar este Kanban diretamente no GitHub:

1. Acesse a aba **Projects** no repositório do GitHub.
2. Clique em **New project** e selecione o template **Board**.
3. Crie as 5 colunas:
   * `📋 Backlog`
   * `⏳ To Do`
   * `⚙️ In Progress`
   * `🔍 In Review (PR Aberto)`
   * `✅ Done`
4. Habilite os workflows automáticos do GitHub Projects:
   * *Item added to project* $\rightarrow$ Move para `To Do`.
   * *Pull request opened* $\rightarrow$ Move o card para `In Review`.
   * *Pull request merged* $\rightarrow$ Move o card para `Done`.
