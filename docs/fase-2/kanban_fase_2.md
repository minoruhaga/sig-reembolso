# Quadro Kanban e Sequenciamento de Entregas - Fase 2

Este documento estabelece o **Quadro Kanban** do SIG-Reembolso para a Fase 2 (Desenvolvimento), sincronizado diretamente com o **[GitHub Project #1 (SIG-Reembolso - Fase 2 Kanban)](https://github.com/users/minoruhaga/projects/1)** e organizado por **Fatias Verticais** e **Ondas de Entrega (Milestones)** para garantir que a equipe trabalhe em paralelo sem conflitos de merge no Django e com foco nas datas do edital de LES da FATEC-SP.

---

## 🧭 Estrutura do Quadro (Colunas de Fluxo)

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   📋 Todo       │──►│ ⚙️ In Progress  │──►│  🔍 Review      │──►│  ✅ Done        │
│   (A Fazer)     │   │ (Codificando)   │   │  (PR Aberto/QA) │   │  (Concluído)    │
└─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## 🌊 Sequenciamento por Ondas de Desenvolvimento (Fatias Verticais)

### 🟢 Onda 0: Fundação, DevOps e Governança (Concluída)
*Objetivo: Estabelecer a base estável, regras de IA, CI/CD e guias para que a equipe possa trabalhar sem fricção.*

| ID GitHub | Issue / Card | Responsável | Área | Status |
| :-: | :--- | :---: | :---: | :---: |
| **[#1](https://github.com/minoruhaga/sig-reembolso/issues/1)** | `[Docs] Elaborar README.md completo e Onboarding de Desenvolvedores` | `@minoruhaga` | Docs / Infra | **[CONCLUÍDO]** |
| **[#2](https://github.com/minoruhaga/sig-reembolso/issues/2)** | `[Gov] Definir Governança de IA, AGENTS.md e Prompts` | `@minoruhaga` | Governança | **[CONCLUÍDO]** |
| **[#3](https://github.com/minoruhaga/sig-reembolso/issues/3)** | `[DevOps] Pipeline de CI/CD com GitHub Actions + Nix` | `@minoruhaga` | DevOps / CI | **[CONCLUÍDO]** |
| **[#4](https://github.com/minoruhaga/sig-reembolso/issues/4)** | `[Gov] CONTRIBUTING.md, .env.example e Templates de Pull Request` | `@minoruhaga` | Governança | **[CONCLUÍDO]** |
| **[#5](https://github.com/minoruhaga/sig-reembolso/issues/5)** | `[Docs] Guia Completo de Configuração do Ambiente (WSL, Nix, Flakes e venv)` | `@minoruhaga` | Docs / Infra | **[CONCLUÍDO]** |

---

### 🟡 Onda 1: MVP Mobile e Dados Reais (Milestone 1 — Prazo: 04/11/2026)
*Objetivo: Entregar a jornada ponta a ponta básica (Coordenador fotografa cupom no celular $\rightarrow$ Despesa cai no banco $\rightarrow$ Tesoureiro visualiza).*

| ID GitHub | Issue / Card | Responsável | Branch Sugerida | Status |
| :-: | :--- | :---: | :--- | :---: |
| **[#6](https://github.com/minoruhaga/sig-reembolso/issues/6)** | `[RBAC] Telas de Login, Logout e Controle por Papel (Usuario)` | `@Mah-Rod` (Marina) | `feature/#6-login-rbac` | ✅ Concluído (PR #29) |
| **[#7](https://github.com/minoruhaga/sig-reembolso/issues/7)** | `[Despesas] Formulário de Submissão com Pillow (RNF02 e RN01)` | `@minoruhaga` (Minoru) | `feature/#7-formulario-despesa` | ✅ Concluído (PR #31) |
| **[#32](https://github.com/minoruhaga/sig-reembolso/issues/32)** | `[Fix] Correções de Integridade Contábil (RN01-RN06), Segurança, Demonstração e Configurações` | `@minoruhaga` (Minoru) | `fix/#32-correcoes-integridade-dominio-e-infra` | ✅ Concluído (PR #33) |
| **[#8](https://github.com/minoruhaga/sig-reembolso/issues/8)** | `[UI/UX] Interface Mobile-First com Câmera Nativa (RNF01)` | `@ricardosakugawa` (Ricardo) | `feature/#8-tela-mobile-camera` | ✅ Concluído (PR #41) |
| **[#9](https://github.com/minoruhaga/sig-reembolso/issues/9)** | `[Dados] Carga de Dados Reais do AG VI e Coordenadores do AG VII` | `@minoruhaga` *(era de `@xixinho`)* | `feature/#9-fixture-ag6-ag7` | ✅ Concluído (PR #37) |

---

### 🟠 Onda 2: Regras Financeiras e 1ª Banca (Milestone 2 — Prazo: 13/11/2026)
*Objetivo: Integrar as regras estritas de domínio contábil antes da 1ª rodada de apresentações da banca.*

| ID GitHub | Issue / Card | Responsável | Branch Sugerida | Status |
| :-: | :--- | :---: | :--- | :---: |
| **[#10](https://github.com/minoruhaga/sig-reembolso/issues/10)** | `[Financeiro] API e View dinâmica de saldos e tetos das 15 coordenações (RF03)` | `@minoruhaga` (Minoru) | `feature/#10-saldos-tetos` | ✅ Concluído (PR #38) |
| **[#11](https://github.com/minoruhaga/sig-reembolso/issues/11)** | `[Workflow] Ações de Triagem da Tesouraria: Aprovar, Rejeitar com Justificativa e Liquidar` | `@minoruhaga` (Minoru) | `feature/#11-acoes-triagem` | ✅ Concluído (PR #39) |
| **[#12](https://github.com/minoruhaga/sig-reembolso/issues/12)** | `[Regras] Soft-block de estouro com alerta e Segregação de Funções (RN02 e RN03)` | `@minoruhaga` (Minoru) | `feature/#12-regras-dominio` | ✅ Concluído (PR #40) |
| **[#13](https://github.com/minoruhaga/sig-reembolso/issues/13)** | `[UI/UX] Painel Desktop da Tesouraria com Modal de Zoom para Notas Fiscais` | `@ricardosakugawa` (Ricardo) | `feature/#13-painel-triagem` | ✅ Concluído (PR #50) |
| **[#34](https://github.com/minoruhaga/sig-reembolso/issues/34)** | `[Relatórios] Módulo de Exportação de Prestação de Contas (CSV e Balancete)` | `@Mah-Rod` (Marina) | `feature/#34-relatorios-exportacao` | ✅ Concluído (PR #43/PR #46) |

---

### 🔴 Onda 3: Qualidade e Entrega Final Teams (Milestone 3 — Prazo: 27/11 a 28/11/2026 às 23:59)
*Objetivo: Produzir os artefatos formais exigidos pela professora (Itens 3.g a 3.l), consolidar testes e homologação final.*

| ID GitHub | Issue / Card | Responsável | Entregável Oficial | Prazo Limite | Status |
| :-: | :--- | :---: | :---: | :---: | :---: |
| **[#14](https://github.com/minoruhaga/sig-reembolso/issues/14)** | `[Docs] Item 3.h - Documentação técnica do sistema desenvolvido` | `@Mah-Rod` / `@minoruhaga` | **Item 3.h** (`3h_documentacao_sistema.md`) | **26/11 às 23:59** | ✅ Concluído (PR #53) |
| **[#16](https://github.com/minoruhaga/sig-reembolso/issues/16)** | `[Docs] Item 3.g - Definição e justificativa das interfaces com base na usabilidade` | `@ricardosakugawa` (Ricardo) | **Item 3.g** (`3g_interfaces_usabilidade.md`) | **26/11 às 23:59** | ✅ Concluído (PR #52) |
| **[#17](https://github.com/minoruhaga/sig-reembolso/issues/17)** | `[Testes] Item 3.i - Procedimentos descritivos de testes e evidências de execução` | `@xixinho` (Giovanni) | **Item 3.i** (`3i_procedimentos_testes.md`) | **26/11 às 23:59** | ⏳ A Fazer |
| **[#48](https://github.com/minoruhaga/sig-reembolso/issues/48)** | `[Docs] Item 3.k - Manual de Treinamento da Tesouraria` | `@Mah-Rod` (Marina) | **Item 3.k** (`3k_manual_treinamento.md`) | **27/11 às 18:00** | ⏳ A Fazer |
| **[#19](https://github.com/minoruhaga/sig-reembolso/issues/19)** | `[Docs] Item 3.j - Manual de Operação do Sistema (Guia dos Voluntários de Campo)` | `@minoruhaga` (Minoru - PO) | **Item 3.j** (`3j_manual_operacao.md`) | **27/11 às 18:00** | ⏳ A Fazer |
| **[#20](https://github.com/minoruhaga/sig-reembolso/issues/20)** | `[Docs] Item 3.l - Procedimentos de Homologação e Aprovação do Sistema` | `@minoruhaga` (Minoru - PO) | **Item 3.l** (`3l_homologacao_sistema.md`) | **27/11 às 18:00** | ⏳ A Fazer |

---

## 🛠️ Acesso Direto ao GitHub Projects da Equipe

O quadro interativo oficial já está público e vinculado ao repositório:
* **Quadro Kanban (Project #1):** [https://github.com/users/minoruhaga/projects/1](https://github.com/users/minoruhaga/projects/1)
* **Milestones (Ondas 1, 2 e 3):** [https://github.com/minoruhaga/sig-reembolso/milestones](https://github.com/minoruhaga/sig-reembolso/milestones)
