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
[Etapa 0: Fundação Compartilhada (AGORA)]
  ├── Configuração do repositório, `.gitignore` e `README.md`
  ├── Setup do Django 5 em `src/` com settings modular
  └── Criação dos models base (`usuarios`, `financeiro`, `despesas`)
            │
            ▼
[Momento da Divisão de Tarefas (Ponto de Ramificação)]
  ├── Branch `feature/rbac-financeiro` (Membro 1)
  ├── Branch `feature/despesas-workflow` (Membro 2)
  ├── Branch `feature/frontend-ui-mobile` (Membro 3)
  └── Branch `feature/qa-testes-manuais` (Membro 4)
            │
            ▼
[Integração Contínua via Pull Requests e Homologação]
```

---

## 2. Matriz de Atribuição por Membro (RACI)

Para cobrir tanto o **código executando** quanto **todos os itens obrigatórios da professora (3.g a 3.l)**, a distribuição sugerida para os 4 integrantes é:

### 👤 Membro 1: Tech Lead & Core Financeiro (Arquitetura & RBAC)
* **Frentes de Código:**
  * Configuração geral do Django, variáveis de ambiente, segurança e banco de dados.
  * Módulo `apps/usuarios`: autenticação e papéis (Coordenador de Área, Tesoureiro, Administrador).
  * Módulo `apps/financeiro`: gestão das 15 coordenações, parametrização dos tetos e cálculo do saldo dinâmico livre.
* **Entregáveis da Disciplina:**
  * **Item 3.h:** Documentação técnica do sistema desenvolvido (programas fontes, dependências, instruções de instalação e execução).
  * Gestão do repositório no GitHub (Code Review e aprovação dos Pull Requests).

### 👤 Membro 2: Engenharia de Despesas & Máquina de Estados (Backend de Negócios)
* **Frentes de Código:**
  * Módulo `apps/despesas`: CRUD de despesas e formulários de submissão.
  * Implementação da Máquina de Estados finita (`RASCUNHO`, `ENVIADO`, `APROVADO`, `REJEITADO`, `PAGO`, `CANCELADO`).
  * Implementação da biblioteca Pillow para compressão automática de fotos de notas fiscais (`RNF02`).
  * Implementação das regras de negócio estritas:
    * `RN01`: Obrigatoriedade do comprovante.
    * `RN02`: Lógica de *soft-block* (flag `excede_teto` e `valor_excedente`).
    * `RN03`: Segregação de funções (tesoureiro impedido de aprovar própria despesa).
    * `RN04`: Exigência de justificativa em reprovações.
    * `RN06`: Gravação automática da trilha de auditoria (`HistoricoTransicaoStatus`).

### 👤 Membro 3: Frontend, UX & Interfaces Responsivas (Item 3.g)
* **Frentes de Código:**
  * Layout base e temas responsivos em Bootstrap 5.3 + Bootstrap Icons.
  * **Telas de Campo (Mobile-First):**
    * Tela inicial do voluntário com extrato e termômetro visual de consumo da verba.
    * Formulário ágil de submissão de despesa com acionamento nativo da câmera do celular.
  * **Painel Administrativo da Tesouraria (Desktop):**
    * Grid/Cards de triagem de notas fiscais pendentes com badges coloridos de status.
    * Modal de conferência em tela cheia com zoom no comprovante.
    * Botões de ação rápida (Aprovar / Rejeitar com formulário modal).
* **Entregáveis da Disciplina:**
  * **Item 3.g:** Documento de definição das interfaces do sistema com base na usabilidade (justificativas ergonômicas, personas, contraste, usabilidade sob sol/chuva e mobile-first).

### 👤 Membro 4: Qualidade, Testes, Manuais e Homologação (Itens 3.i, 3.j, 3.k, 3.l)
* **Frentes de Código:**
  * Criação de dados semente (*fixtures/seeds*) com os dados reais do Acampamento Geral VII (GE Caramuru) e despesas típicas do AG VI para simulações.
  * Implementação da suíte de testes automatizados no Django (`tests/`):
    * Testes unitários de cálculo de saldo e soft-block.
    * Testes de transição de status da máquina de estados.
    * Teste da regra de segregação de funções.
* **Entregáveis da Disciplina:**
  * **Item 3.i:** Procedimentos descritivos de testes do sistema (casos de teste, cobertura e evidências de execução).
  * **Item 3.j:** Manual de operação do sistema (guia do usuário para voluntários em campo).
  * **Item 3.k:** Manual de treinamento do sistema (roteiro de capacitação para a Tesouraria).
  * **Item 3.l:** Procedimentos de homologação e minuta do Termo de Aceite Formal assinado pelo Coordenador do AG VII.

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
