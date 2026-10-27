# Catálogo de Issues no GitHub Projects - Fase 2

Este documento reúne a lista oficial das 18 Issues abertas e concluídas no GitHub da equipe ([minoruhaga/sig-reembolso/issues](https://github.com/minoruhaga/sig-reembolso/issues)), distribuídas entre os 4 integrantes para cobrir tanto o sistema funcionando quanto os itens avaliativos da 2ª Fase (**Itens 3.g a 3.l do edital**).

---

## 📌 Onda 0: Fundação, DevOps e Governança (`@minoruhaga` / Tech Lead)

### [Issue #1](https://github.com/minoruhaga/sig-reembolso/issues/1): `[Docs] Elaborar README.md completo e Onboarding de Desenvolvedores`
* **Assignee:** `@minoruhaga`
* **Labels:** `documentation`, `onda-0`, `fase-2`
* **Status:** Concluída (`Closed`)
* **Descrição:**
  * Documentar visão geral do sistema e contexto real do AG VII (Grupo Escoteiro Caramuru).
  * Instruções passo a passo de setup multiplataforma (Linux via Nix e Windows via `venv + pip`).
  * Comandos de carga de dados (`popular_dados_demo`) e tabela de credenciais de teste.

### [Issue #2](https://github.com/minoruhaga/sig-reembolso/issues/2): `[Gov] Definir Governança de IA, AGENTS.md e Prompts`
* **Assignee:** `@minoruhaga`
* **Labels:** `governance`, `onda-0`, `fase-2`
* **Status:** Concluída (`Closed`)
* **Descrição:**
  * Criar `AGENTS.md` na raiz e `src/AGENTS.md` com as regras arquiteturais invioláveis.
  * Configurar a skill `$decision-analysis-v4` e a estrutura de pastas em `prompts/`.
  * Elaborar o Guia de Governança de IA (`docs/guia-uso-ia-e-skills.md`).

### [Issue #3](https://github.com/minoruhaga/sig-reembolso/issues/3): `[DevOps] Pipeline de CI/CD com GitHub Actions + Nix`
* **Assignee:** `@minoruhaga`
* **Labels:** `devops`, `onda-0`, `fase-2`
* **Status:** Concluída (`Closed`)
* **Descrição:**
  * Criar workflow `.github/workflows/ci.yml`.
  * Executar linter Ruff, checagens do Django, ausência de migrações pendentes e suíte de testes.
  * Executar Gitleaks no histórico para impedir vazamento de credenciais.

### [Issue #4](https://github.com/minoruhaga/sig-reembolso/issues/4): `[Gov] CONTRIBUTING.md, .env.example e Templates de Pull Request`
* **Assignee:** `@minoruhaga`
* **Labels:** `governance`, `onda-0`, `fase-2`
* **Status:** Concluída (`Closed`)
* **Descrição:**
  * Criar `.env.example` com as variáveis necessárias.
  * Criar `CONTRIBUTING.md` e `docs/manual-git.md` com fluxo de branches e prevenção de conflitos de migração.
  * Criar `.github/PULL_REQUEST_TEMPLATE.md` e template de Issue.

### [Issue #5](https://github.com/minoruhaga/sig-reembolso/issues/5): `[Docs] Guia Completo de Configuração do Ambiente (WSL, Nix, Flakes e venv)`
* **Assignee:** `@minoruhaga`
* **Labels:** `documentation`, `onda-0`, `fase-2`
* **Status:** Concluída (`Closed`)
* **Descrição:**
  * Elaborar tutorial passo a passo (`docs/configuracao-ambiente.md`) cobrindo WSL, Nix, Flakes, GitHub CLI (`gh`) e alternativa `venv + pip`.

---

## 📌 Ondas 1 a 3: Backlog de Desenvolvimento e Entregas (Distribuído entre os 4 Integrantes)

### 👤 Membro 1: Gustavo Minoru Haga (`@minoruhaga` — Tech Lead, Product Owner & Backend Core)
* **[Issue #7](https://github.com/minoruhaga/sig-reembolso/issues/7): `[Despesas] Formulário de Submissão com Pillow (RNF02 e RN01)`** *(Milestone: Onda 1 - 04/11/2026)*
  * Formulário web e endpoint para lançamento de despesa em campo com anexo obrigatório de cupom fiscal (**RN01**).
  * Integração com Pillow para compactar automaticamente imagens pesadas de celular (`RNF02`).
* **[Issue #10](https://github.com/minoruhaga/sig-reembolso/issues/10): `[Financeiro] API e View dinâmica de saldos e tetos das 15 coordenações (RF03)`** *(Milestone: Onda 2 - 13/11/2026)*
  * Modelagem e cálculo do saldo dinâmico livre em tempo real com `Sum()` e precisão `Decimal`.
* **[Issue #11](https://github.com/minoruhaga/sig-reembolso/issues/11): `[Workflow] Ações de Triagem da Tesouraria: Aprovar, Rejeitar com Justificativa e Liquidar`** *(Milestone: Onda 2 - 13/11/2026)*
  * Máquina de estados atômica (`@transaction.atomic`) para Aprovar, Rejeitar com Justificativa (**RN04**) e Liquidar Reembolso com anexo do comprovante Cora PJ.
* **[Issue #12](https://github.com/minoruhaga/sig-reembolso/issues/12): `[Regras] Soft-block de estouro com alerta e Segregação de Funções (RN02 e RN03)`** *(Milestone: Onda 2 - 13/11/2026)*
  * Lógica de validação contábil: flag automática `excede_teto = True` e cálculo de `valor_excedente`.
  * Impedir que membros do Financeiro aprovem reembolsos de compras solicitadas por eles mesmos (**RN03**).
* **[Issue #14](https://github.com/minoruhaga/sig-reembolso/issues/14): `[Docs] Item 3.h - Documentação técnica do sistema desenvolvido`** *(Milestone: Onda 3 - 27/11/2026)*
  * Elaborar o documento formal exigido pela professora descrevendo os programas fontes, dependências e ambiente de execução.
* **[Issue #19](https://github.com/minoruhaga/sig-reembolso/issues/19): `[Docs] Item 3.j - Manual de Operação do Sistema (Guia dos Voluntários de Campo)`** *(Milestone: Onda 3 - 27/11/2026)*
  * Guia ilustrado passo a passo ensinando os coordenadores a tirar fotos legíveis e enviar despesas.
* **[Issue #20](https://github.com/minoruhaga/sig-reembolso/issues/20): `[Docs] Itens 3.k e 3.l - Manual de Treinamento da Tesouraria e Homologação Formal`** *(Milestone: Onda 3 - 27/11/2026)*
  * Manual de operação da triagem financeira e minuta do Termo de Homologação formal com o cliente (Coordenação do AG VII - GE Caramuru).

### 👤 Membro 2: Marina (Backend de Acesso, Autenticação & Relatórios)
* **[Issue #6](https://github.com/minoruhaga/sig-reembolso/issues/6): `[RBAC] Telas de Login, Logout e Controle por Papel (Usuario)`** *(Milestone: Onda 1 - 04/11/2026)*
  * Implementar telas de login/logout customizadas no Django utilizando o modelo `Usuario`.
  * Restringir visualizações: Coordenador só vê sua área; Tesoureiro e Admin visualizam todas as 15 coordenações.
* **[Issue #15](https://github.com/minoruhaga/sig-reembolso/issues/15): `[Relatórios] Módulo de Exportação de Prestação de Contas (CSV e Balancete)`** *(Milestone: Onda 2 - 13/11/2026)*
  * Criação de rotinas para exportação de dados contábeis em CSV e relatórios sintéticos de prestação de contas.
  * Suporte no setup de ambiente (`settings.py`, `.env` e PostgreSQL) e apoio na documentação técnica (Item 3.h).

### 👤 Membro 3: Ricardo Sakugawa (`@ricardosakugawa` — Frontend & UI/UX Completo)
* **[Issue #8](https://github.com/minoruhaga/sig-reembolso/issues/8): `[UI/UX] Interface Mobile-First com Câmera Nativa (RNF01)`** *(Milestone: Onda 1 - 04/11/2026)*
  * Tela de submissão otimizada para smartphones (360px–430px) com botão direto `<input type="file" accept="image/*" capture="environment">`.
  * Termômetro visual de consumo da verba por coordenação em tempo real.
* **[Issue #13](https://github.com/minoruhaga/sig-reembolso/issues/13): `[UI/UX] Painel Desktop da Tesouraria com Modal de Zoom para Notas Fiscais`** *(Milestone: Onda 2 - 13/11/2026)*
  * Painel com cards de despesas pendentes, badges coloridos de status e modal em alta resolução para auditoria de comprovantes fiscais.
* **[Issue #16](https://github.com/minoruhaga/sig-reembolso/issues/16): `[Docs] Item 3.g - Definição e justificativa das interfaces com base na usabilidade`** *(Milestone: Onda 3 - 27/11/2026)*
  * Redigir documento acadêmico justificando as decisões ergonômicas, acessibilidade, contraste para uso sob luz solar no campo e facilidade em conexões lentas (Starlink).

### 👤 Membro 4: Giovanni (`@xixinho` — QA, Testes Automatizados & Confiabilidade)
* **[Issue #9](https://github.com/minoruhaga/sig-reembolso/issues/9): `[Dados] Carga de Dados Reais do AG VI e Coordenadores do AG VII`** *(Milestone: Onda 1 - 04/11/2026)*
  * Criar comando ou fixture para carregar os dados anonimizados de `docs/referencias/coordenadores_ag7.csv` e `gastos_historicos_ag6/alimentacao_gastos_ag6.csv`.
* **[Issue #17](https://github.com/minoruhaga/sig-reembolso/issues/17): `[Testes] Item 3.i - Procedimentos descritivos de testes e expansão de casos no Django`** *(Milestone: Onda 3 - 27/11/2026)*
  * Documentar os procedimentos descritivos de testes (Item 3.i) e implementar a suíte completa de testes automatizados (`TestCase`) cobrindo as regras de negócio críticas (RN01 a RN06).
