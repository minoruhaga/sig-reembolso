# Catálogo de Issues para o GitHub Projects - Fase 2

Este documento reúne a lista pronta de Issues para serem criadas no GitHub da equipe, distribuídas entre os 4 integrantes para cobrir tanto o sistema funcionando quanto os itens avaliativos da 2ª Fase (**Itens 3.g a 3.l do edital**).

---

## 📌 Sprint 0: Fundação, DevOps e Governança (Minoru / Tech Lead)

### Issue #01: `[Docs] Elaborar README.md completo e Onboarding de Desenvolvedores`
* **Assignee:** `@minoru`
* **Labels:** `documentation`, `onboarding`
* **Descrição:**
  * Documentar visão geral do sistema e contexto real do AG VII (Grupo Escoteiro Caramuru).
  * Instruções passo a passo de setup multiplataforma (Linux via Nix e Windows via `venv + pip`).
  * Comandos de carga de dados (`popular_dados_demo`) e tabela de credenciais de teste.
* **Critérios de Aceitação:**
  - [x] README.md atualizado com setup reproduzível.
  - [x] Comandos de execução testados em Nix e venv.

### Issue #02: `[Gov] Definir Governança de IA, Diretrizes de Agentes e Decision Analysis`
* **Assignee:** `@minoru`
* **Labels:** `governance`, `ai-workflow`, `documentation`
* **Descrição:**
  * Criar `AGENTS.md` na raiz e `src/AGENTS.md` com as regras arquiteturais invioláveis.
  * Configurar a skill `$decision-analysis-v4` e a estrutura de pastas em `prompts/`.
  * Elaborar o Guia de Governança de IA (`docs/guia-uso-ia-e-skills.md`).
* **Critérios de Aceitação:**
  - [x] `AGENTS.md` e `src/AGENTS.md` criados e integrados.
  - [x] Skill `$decision-analysis-v4` funcional.

### Issue #03: `[DevOps] Configurar Pipeline de CI/CD com GitHub Actions`
* **Assignee:** `@minoru`
* **Labels:** `devops`, `ci-cd`, `quality`
* **Descrição:**
  * Criar workflow `.github/workflows/ci.yml`.
  * Executar linter Ruff, checagens do Django, ausência de migrações pendentes e suíte de testes.
  * Executar Gitleaks no histórico para impedir vazamento de credenciais.
* **Critérios de Aceitação:**
  - [x] Workflow `.github/workflows/ci.yml` criado.
  - [x] Gates de qualidade validados localmente.

### Issue #04: `[Gov] Criar CONTRIBUTING.md, .env.example e Templates de Pull Request`
* **Assignee:** `@minoru`
* **Labels:** `governance`, `git-flow`
* **Descrição:**
  * Criar `.env.example` com as variáveis necessárias.
  * Criar `CONTRIBUTING.md` e `docs/manual-git.md` com fluxo de branches e prevenção de conflitos de migração.
  * Criar `.github/PULL_REQUEST_TEMPLATE.md` e template de Issue.
* **Critérios de Aceitação:**
  - [x] Arquivos criados e vinculados na documentação.

---

## 📌 Sprint 1: Backlog de Desenvolvimento e Entregas (Distribuído entre os 4 Integrantes)

### 👤 Membro 1: Minoru (Tech Lead / Core Backend & RBAC)
* **Issue #05: `[RBAC] Integrar views de login, autenticação customizada e controle de acesso por papel`**
  * Implementar telas de login/logout customizadas no Django utilizando o modelo `Usuario`.
  * Restringir visualizações: Coordenador só vê sua área; Tesoureiro e Admin visualizam todas as 15 coordenações.
* **Issue #06: `[Financeiro] View e API de consulta dinâmica de saldos e tetos das 15 coordenações (RF03)`**
  * View dedicada para cálculo do termômetro de consumo de verba em tempo real.
  * Garantir integridade de centavos com `Decimal`.
* **Issue #07: `[Docs] Item 3.h - Documentação técnica do sistema desenvolvido`**
  * Elaborar o documento formal exigido pela professora descrevendo os programas fontes, dependências e ambiente de execução.

### 👤 Membro 2: Backend de Despesas & Máquina de Estados
* **Issue #08: `[Despesas] Implementar formulário de submissão de despesa com compressão Pillow (RF04 / RNF02)`**
  * Formulário web para lançamento de despesa em campo com anexo obrigatório de cupom fiscal (**RN01**).
  * Integração com `apps.core.services.otimizar_comprovante_fiscal` para compactar imagens pesadas de celular.
* **Issue #09: `[Workflow] Implementar ações da Tesouraria na Triagem (RF06 / RF07)`**
  * Endpoints e botões de ação para Aprovar, Rejeitar com Justificativa (**RN04**) e Liquidar Reembolso com anexo do comprovante Cora PJ.
* **Issue #10: `[Regras] Validar soft-block com alerta de estouro e segregação de funções (RN02 / RN03)`**
  * Flag automática `excede_teto = True` e cálculo de `valor_excedente`.
  * Impedir que membros do Financeiro aprovem reembolsos de compras solicitadas por eles mesmos.

### 👤 Membro 3: Frontend, UX & Interfaces Mobile-First (Item 3.g)
* **Issue #11: `[UI/UX] Desenvolver tela mobile-first de submissão rápida com câmera nativa (RNF01)`**
  * Tela de submissão otimizada para smartphones (360px–430px) com botão direto `<input type="file" accept="image/*" capture="environment">`.
* **Issue #12: `[UI/UX] Desenvolver tela desktop da Tesouraria com cards de triagem e modal de zoom`**
  * Painel com cards de despesas pendentes, badges de status e modal em alta resolução para auditoria de comprovantes fiscais.
* **Issue #13: `[Docs] Item 3.g - Definição e justificativa das interfaces com base na usabilidade`**
  * Redigir documento acadêmico justificando as decisões ergonômicas, acessibilidade, contraste para uso sob luz solar no campo e facilidade em conexões lentas (Starlink).

### 👤 Membro 4: QA, Testes, Manuais e Homologação (Itens 3.i a 3.l)
* **Issue #14: `[Dados] Criar carga de dados com gastos históricos do AG VI e coordenadores do AG VII`**
  * Criar comando ou fixture para carregar os dados reais de `docs/referencias/coordenadores_ag7.csv` e `gastos_historicos_ag6/alimentacao_gastos_ag6.csv`.
* **Issue #15: `[Testes] Item 3.i - Procedimentos descritivos de testes e expansão de casos no Django`**
  * Documentar os procedimentos descritivos de testes (Item 3.i) e expandir a cobertura automatizada (`TestCase`).
* **Issue #16: `[Docs] Item 3.j - Manual de Operação do Sistema (Guia dos Voluntários de Campo)`**
  * Guia ilustrado passo a passo ensinando os coordenadores a tirar fotos legíveis e enviar despesas.
* **Issue #17: `[Docs] Itens 3.k e 3.l - Manual de Treinamento da Tesouraria e Homologação Formal`**
  * Manual de operação da triagem financeira e minuta do Termo de Homologação com a Diretoria do GE Caramuru.
