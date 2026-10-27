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
  ├── Branch `feature/rbac-relatorios` (Marina)
  ├── Branch `feature/frontend-ui-ux` (@ricardosakugawa - Ricardo)
  └── Branch `feature/qa-testes-fixtures` (@xixinho - Giovanni)
            │
            ▼
[Integração Contínua via Pull Requests e Homologação]
```

---

## 2. Matriz de Atribuição por Membro (RACI)

Para cobrir tanto o **código executando** quanto **todos os itens obrigatórios da professora (3.g a 3.l)** sem sobrecarregar nenhum integrante e respeitando a governança do caso real (AG VII - GE Caramuru), a distribuição oficial para os 4 integrantes é:

### 👤 Membro 1: Gustavo Minoru Haga (`@minoruhaga` — Tech Lead, Product Owner & Backend Core)
* **Frentes de Código:**
  * Modelagem do Banco de Dados Relacional (PostgreSQL / SQLite) e integridade referencial.
  * Módulo `apps/financeiro`: gestão das 15 coordenações, parametrização dos tetos e cálculo do saldo dinâmico livre.
  * Módulo `apps/despesas`: CRUD de despesas, formulários de submissão e máquina de estados finita.
  * Integração com Pillow para compactação automática de notas fiscais (`RNF02`).
  * Implementação das regras de negócio estritas:
    * `RN01`: Obrigatoriedade de comprovante fiscal legível.
    * `RN02`: Lógica de *soft-block* (flag `excede_teto` e `valor_excedente`).
    * `RN03`: Segregação de funções (membros do financeiro impedidos de aprovar própria despesa).
    * `RN04`: Parecer obrigatório em rejeições.
    * `RN06`: Gravação automática da trilha de auditoria (`HistoricoTransicaoStatus`).
* **Entregáveis da Disciplina (FATEC):**
  * **Item 3.h:** Documentação técnica do sistema desenvolvido (programas fontes, dependências e ambiente de execução).
  * **Itens 3.j e 3.k:** Manuais de Campo (Manual de Operação do Voluntário e Treinamento da Tesouraria, alinhados à prática real).
  * **Item 3.l:** Homologação formal e minuta do Termo de Aceite assinado pelo cliente (Coordenação Executiva do AG VII).
  * Gestão do repositório no GitHub (Code Review e aprovação dos Pull Requests).

### 👤 Membro 2: Marina (Backend de Acesso, Autenticação & Relatórios)
* **Frentes de Código:**
  * Módulo `apps/usuarios`: Custom User Model, login, logout e controle por papel (RBAC: Coordenador de Área, Tesoureiro, Administrador).
  * Proteção de rotas restritas via middleware e decoradores do Django.
  * Módulo `apps/relatorios`: rotinas de exportação de dados para prestação de contas (geração de planilhas CSV e relatórios contábeis para o GE Caramuru).
  * Apoio na infraestrutura de ambiente (`settings.py`, variáveis `.env` e PostgreSQL).
* **Entregáveis da Disciplina (FATEC):**
  * Apoio no **Item 3.h:** Seção de segurança, autenticação, controle de permissões e exportação de dados.

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

### 👤 Membro 4: Giovanni (`@xixinho` — QA, Testes Automatizados & Confiabilidade)
* **Frentes de Código:**
  * Criação de dados semente (*fixtures/seeds*) com os dados reais do Acampamento Geral VII (GE Caramuru) e despesas típicas do AG VI para simulações realistas.
  * Implementação da suíte de testes automatizados no Django (`tests/`):
    * Testes unitários do cálculo dinâmico de saldo e soft-block de teto (`RN02`).
    * Testes de transição de status da máquina de estados (fluxos válidos e bloqueios inválidos).
    * Testes da regra de segregação de funções (`RN03`) e obrigatoriedade de anexo (`RN01`).
    * Testes de compressão de imagens via Pillow.
* **Entregáveis da Disciplina (FATEC):**
  * **Item 3.i:** Procedimentos descritivos de testes do sistema (matriz de rastreabilidade, casos de teste automatizados e evidências de execução com cobertura).

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
