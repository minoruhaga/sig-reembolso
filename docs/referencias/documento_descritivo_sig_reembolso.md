# SIG-Reembolso: Sistema Integrado de Gestão de Fundo de Caixa, Adiantamentos e Reembolsos

## Documento de Engenharia de Requisitos, Governança e Arquitetura de Software

**Instituição:** Faculdade de Tecnologia de São Paulo (FATEC-SP)

**Departamento:** Departamento de Tecnologia da Informação (DTI)

**Disciplina:** Laboratório de Engenharia de Software (LES) – 2º Semestre de 2026

**Cliente / Contexto Operacional:** Coordenação Executiva do Acampamento Geral VII (AG VII) – Grupo Escoteiro Caramuru

**Versão:** 1.0 (Fase de Planejamento e Especificação Técnica)

## Sumário

1. [Visão Geral do Projeto e Problema de Negócio](#1-visão-geral-do-projeto-e-problema-de-negócio)

2. [Caracterização da Organização Cliente (Itens 1.a a 1.g)](#2-caracterização-da-organização-cliente-itens-1a-a-1g)

   * [1.a Apresentação e Histórico da Organização](#1a-apresentação-e-histórico-da-organização)

   * [1.b Organograma Estrutural e Funcional](#1b-organograma-estrutural-e-funcional)

   * [1.c Missão, Visão e Princípios da Organização](#1c-missão-visão-e-princípios-da-organização)

   * [1.d Funções Terceirizadas da Empresa (Operacionais)](#1d-funções-terceirizadas-da-empresa-operacionais)

   * [1.e Objetivos e Funções das Áreas de Negócio (15 Coordenações)](#1e-objetivos-e-funções-das-áreas-de-negócio-15-coordenações)

   * [1.f Quadro de Colaboradores e Voluntários por Área](#1f-quadro-de-colaboradores-e-voluntários-por-área)

   * [1.g Faturamento Anual e Orçamento do Evento](#1g-faturamento-anual-e-orçamento-do-evento)

3. [Diagnóstico da TI Atual e Governança Operacional (Itens 2.a a 2.d)](#3-diagnóstico-da-ti-atual-e-governança-operacional-itens-2a-a-2d)

   * [2.a Procedimentos Existentes para Manutenção e Requisição de Novos Sistemas](#2a-procedimentos-existentes-para-manutenção-e-requisição-de-novos-sistemas)

   * [2.b Descrição da Infraestrutura Tecnológica Existente](#2b-descrição-da-infraestrutura-tecnológica-existente)

   * [2.c Softwares Existentes (Sistemas Aplicativos, SO e Bancos de Dados)](#2c-softwares-existentes-sistemas-aplicativos-so-e-bancos-de-dados)

   * [2.d Fornecedores de TI, Alinhamento ITIL v4 e Acordo de Nível de Serviço (SLA)](#2d-fornecedores-de-ti-alinhamento-itil-v4-e-acordo-de-nível-de-serviço-sla)

4. [Engenharia do Novo Sistema (Itens 3.a a 3.f)](#4-engenharia-do-novo-sistema-itens-3a-a-3f)

   * [3.a Definição do Escopo do Sistema com base no PMBOK](#3a-definição-do-escopo-do-sistema-com-base-no-pmbok)

   * [3.b Cronograma Físico de Desenvolvimento](#3b-cronograma-físico-de-desenvolvimento)

   * [3.c Elicitação de Requisitos do Sistema e Metodologia](#3c-elicitação-de-requisitos-do-sistema-e-metodologia)

   * [3.d Requisitos Funcionais do Sistema (RF)](#3d-requisitos-funcionais-do-sistema-rf)

   * [3.e Requisitos Não Funcionais do Sistema (RNF)](#3e-requisitos-não-funcionais-do-sistema-rnf)

   * [3.f Requisitos de Domínio e Regras de Negócio Estritas (RD / RN)](#3f-requisitos-de-domínio-e-regras-de-negócio-estritas-rd--rn)

5. [Arquitetura de Dados, Engenharia de Software e Máquina de Estados](#5-arquitetura-de-dados-engenharia-de-software-e-máquina-de-estados)

   * [5.1 Racional da Stack Tecnológica](#51-racional-da-stack-tecnológica)

   * [5.2 Máquina de Estados da Despesa](#52-máquina-de-estados-da-despesa)

   * [5.3 Modelagem Conceitual e Dicionário de Dados Django](#53-modelagem-conceitual-e-dicionário-de-dados-django)

   * [5.4 Distribuição Orçamentária Inicial (Matriz das 15 Coordenações)](#54-distribuição-orçamentária-inicial-matriz-das-15-coordenações)

6. [Fluxo Operacional Ponta a Ponta](#6-fluxo-operacional-ponta-a-ponta)

7. [Guia de Defesa e Argumentos Estratégicos perante a Banca](#7-guia-de-defesa-e-argumentos-estratégicos-perante-a-banca)

8. [Planejamento de Entregas da 2ª Fase (Itens 3.g a 3.l)](#8-planejamento-de-entregas-da-2ª-fase-itens-3g-a-3l)

## 1. Visão Geral do Projeto e Problema de Negócio

O **SIG-Reembolso** (Sistema Integrado de Gestão de Fundo de Caixa, Adiantamentos e Reembolsos) é uma aplicação web concebida para sanar o gargalo financeiro e contábil vivenciado em eventos temporários de grande escala, tendo como piloto oficial o **Acampamento Geral VII (AG VII)** do **Grupo Escoteiro Caramuru**.

### A Dor Crônica

Durante os 7 dias ininterruptos de operação do acampamento no Campo Escola de Juquitiba/SP, cerca de 100 voluntários adultos e seniores/pioneiros precisam realizar dezenas de aquisições de suprimentos emergenciais nas cidades vizinhas (alimentos perecíveis para a cozinha, medicamentos na farmácia de plantão, conexões hidráulicas e combustíveis para geradores elétricos).

Historicamente, essa dinâmica operava sob um modelo descentralizado e informal:

1. **Perda Física de Comprovantes:** Cupons fiscais de papel térmico eram guardados nos bolsos dos uniformes, amassados na chuva ou perdidos no campo, inviabilizando a prestação de contas contábil.

2. **Caos de Canais de Comunicação:** Fotos de recibos sem nitidez, comprovantes cortados e solicitações de PIX eram dispersados em dezenas de conversas privadas e grupos de WhatsApp.

3. **Ausência de Controle do Teto em Tempo Real:** Sem uma ferramenta de abatimento automático, as coordenações operacionais desconheciam o saldo restante de suas dotações, culminando frequentemente em estouros de orçamento sem prévia deliberação da tesouraria.

4. **Morosidade no Pós-Evento:** A equipe financeira despendia semanas após o término do acampamento cobrando recibos originais, transcrevendo dados manualmente para planilhas eletrônicas e tentando conciliar saídas bancárias da conta institucional.

### A Solução Proposta

O SIG-Reembolso substitui esse fluxo por uma solução web focada em mobilidade e controle transacional. Através de um formulário *Mobile-First*, o coordenador em campo informa a compra e anexa a fotografia da nota no instante da aquisição. No ambiente administrativo, a Tesouraria recebe as submissões em uma fila única de triagem, confere os comprovantes em tela cheia e, em um único clique, aprova ou rejeita a solicitação, abatendo o teto orçamentário da coordenação imediatamente e gerando trilhas auditáveis para o fechamento de contas final.

## 2. Caracterização da Organização Cliente (Itens 1.a a 1.g)

### 1.a Apresentação e Histórico da Organização

O **Grupo Escoteiro Caramuru** (fundado em 1927 no município de São Paulo) é uma das unidades escoteiras mais antigas, ativas e tradicionais do Brasil. Vinculado à União dos Escoteiros do Brasil (UEB), congrega centenas de jovens e adultos com atuação ininterrupta de educação não formal.

A principal atividade da organização é o **Acampamento Geral (AG)**, que ocorre rigorosamente a cada 4 anos. O **AG VII** consiste na mobilização simultânea de todos os ramos da instituição (Alcateia/Lobinhos, Tropa Escoteira, Tropa Sênior e Clã Pioneiro), transferindo toda a sua comunidade para o Campo Escola em Juquitiba/SP durante uma semana inteira. No local, estabelece-se uma estrutura autossuficiente e temporária que opera com serviços próprios de refeitório industrial, ambulatório médico, rede elétrica por geradores, saneamento e programação pedagógica contínua.

### 1.b Organograma Estrutural e Funcional

A operação do AG VII conta com uma estrutura organizacional matricial e coordenada em três grandes pilares, congregando 15 coordenações funcionais com atribuições delimitadas:

```
                          ┌──────────────────────────────────────────────┐
                          │    Coordenação Executiva Geral do AG VII     │
                          │        (Diretoria do GE Caramuru)            │
                          └──────────────────────┬───────────────────────┘
                                                 │
         ┌───────────────────────────────────────┼───────────────────────────────────────┐
         │                                       │                                       │
         ▼                                       ▼                                       ▼
┌───────────────────┐                  ┌───────────────────┐                   ┌───────────────────┐
│     PILAR 1:      │                  │     PILAR 2:      │                   │     PILAR 3:      │
│   ADMINISTRATIVO  │                  │     PRODUÇÃO      │                   │      TÉCNICO      │
└────────┬──────────┘                  └────────┬──────────┘                   └────────┬──────────┘
         │                                      │                                       │
         ├─► Financeiro / Tesouraria (*)        ├─► Alimentação / Cozinha               ├─► Infraestrutura e Campo
         ├─► Transporte e Logística             ├─► Atividades / Ramos                  ├─► Saúde e Bem-Estar
         ├─► Inscrições e Secretaria            ├─► Decoração e Ambientação             ├─► Sustentabilidade e Resíduos
         └─► Captação e Recursos                ├─► Música e Animação                   ├─► Logística de Materiais
                                                └─► Divulgação e Mídias                 └─► Som e Iluminação

```

*(*) Ponto de intervenção central do SIG-Reembolso, servindo como polo de conciliação entre o Financeiro e as outras 14 frentes.\*

### 1.c Missão, Visão e Princípios da Organização

* **Missão:** Contribuir para a educação de crianças e jovens mediante a aplicação do Método Escoteiro, fundamentado em valores éticos, fraternidade, contato com a natureza, liderança comunitária e total transparência no uso dos recursos auferidos junto às famílias e benfeitores.

* **Visão:** Consolidar o Acampamento Geral como referência nacional de excelência operacional, segurança e governança administrativa em atividades escoteiras de grande porte.

* **Princípios Operacionais:** Probidade administrativa, responsabilidade orçamentária descentralizada, conformidade fiscal e zelo comunitário.

### 1.d Funções Terceirizadas da Empresa (Operacionais)

O Grupo Escoteiro mantém contratos corporativos centrais, firmados estritamente na modalidade Pessoa Jurídica para Pessoa Jurídica (PJ-PJ), para viabilizar serviços pesados de infraestrutura que fogem ao escopo do reembolso individual:

1. **Transporte Rodoviário Fretado:** Locação de frota de ônibus rodoviários executivos para o transporte dos participantes da capital até Juquitiba/SP.

2. **Locação do Campo Escola:** Contrato de uso e locação do sítio e instalações de acampamento em Juquitiba.

3. **Locação de Geradores de Grande Porte:** Fornecimento e abastecimento contínuo de grupos motogeradores de eletricidade para garantir iluminação e câmaras de refrigeração.

### 1.e Objetivos e Funções das Áreas de Negócio (15 Coordenações)

| Pilar | Coordenação | Objetivo Central | Funções e Atribuições Operacionais | 
| ----- | ----- | ----- | ----- | 
| **Administrativo** | **Financeiro / Tesouraria** | Assegurar higidez financeira, liquidez e conformidade fiscal | Triagem e auditoria de recibos fiscais, liquidação bancária, monitoramento de tetos orçamentários e prestação de contas contábil. | 
| **Administrativo** | **Transporte e Logística** | Garantir mobilidade segura e pontual de pessoas e carga | Gestão de comboios rodoviários, controle de frotas de apoio e combustível de campo. | 
| **Administrativo** | **Inscrições e Secretaria** | Centralizar dados de participantes e atendimento | Credenciamento presencial, conferência de autorizações legais, fichas médicas e kits. | 
| **Administrativo** | **Captação de Recursos** | Ampliar sustentabilidade econômico-financeira | Captação de doações institucionais e relacionamento com parceiros e benfeitores. | 
| **Produção** | **Alimentação / Cozinha** | Prover suporte nutricional seguro para toda a comunidade | Planejamento de cardápios, preparo de 5 refeições diárias para \~400 pessoas e compras de perecíveis de emergência. | 
| **Produção** | **Atividades e Ramos** | Executar o projeto pedagógico escoteiro | Condução de oficinas, gincanas, jogos de campo e vivências por ramo etário. | 
| **Produção** | **Decoração e Ambientação** | Construir a imersão visual e temática do evento | Montagem de portais, sinalizações rústicas, faixas e ambientação das áreas de convivência. | 
| **Produção** | **Música e Animação** | Fomentar engajamento, cerimoniais e entretenimento | Sonoplastia de fogueiras do conselho, cerimônias de abertura e encerramento. | 
| **Produção** | **Divulgação e Mídias** | Registrar a memória institucional e boletins em campo | Cobertura fotográfica, transmissão interna de avisos e boletins diários para as famílias. | 
| **Técnico** | **Infraestrutura e Campo** | Montar e manter serviços vitais do campo escola | Redes de distribuição hidráulica e elétrica temporárias, manutenção de geradores e manutenções emergenciais de ferragens. | 
| **Técnico** | **Saúde e Bem-Estar** | Assegurar prontidão médica e prevenção sanitária | Ambulatório de pronto-atendimento 24h, dispensação controlada de medicamentos e isolamento. | 
| **Técnico** | **Sustentabilidade e Resíduos** | Minimizar impacto ambiental e destinar resíduos | Coleta seletiva, descarte de efluentes, reciclagem e conservação das matas locais. | 
| **Técnico** | **Logística de Materiais** | Controlar o fluxo do almoxarifado técnico | Custódia, guarda, empréstimo e manutenção de machadinhas, pás, cordas e lonas. | 
| **Técnico** | **Som e Iluminação** | Garantir operabilidade técnica de eventos coletivos | Manutenção e operação de mesas de áudio, microfones e refletores em campo aberto. | 
| **Técnico** | **Segurança e Brigada** | Garantir perímetro seguro e resposta a incidentes | Rondas noturnas, monitoramento perimetral, plano de evacuação e combate a princípios de incêndio. | 

### 1.f Quadro de Colaboradores e Voluntários por Área

O Acampamento Geral opera exclusivamente sob o voluntariado qualificado, congregando cerca de 100 adultos e seniores distribuídos nas frentes:

* **Pilar Administrativo (16 voluntários):**

  * Coordenação Geral / Diretoria: 3 líderes

  * Financeiro / Tesouraria: 4 voluntários *(operadores diretos do sistema)*

  * Transporte e Logística: 4 coordenadores

  * Inscrições e Apoio de Secretaria: 2 voluntários

  * Captação de Recursos: 3 voluntários

* **Pilar de Produção (\~45 voluntários):**

  * Alimentação e Cozinha: 3 coordenadores executivos + 22 voluntários na brigada de preparo

  * Atividades e Jogos de Ramos: 4 coordenadores + 10 pioneiros/monitores

  * Decoração e Cenografia: 5 membros

  * Música e Animação: 3 voluntários

  * Divulgação e Mídias: 2 voluntários

* **Pilar Técnico (\~39 voluntários):**

  * Infraestrutura e Manutenção: 4 líderes técnicos + 16 voluntários de montagem/oficinas

  * Saúde e Bem-Estar: 3 profissionais de saúde (médico/enfermeiro) + 5 socorristas de apoio

  * Sustentabilidade e Resíduos: 3 voluntários

  * Almoxarifado e Materiais: 2 voluntários

  * Som e Iluminação: 1 coordenadora

  * Segurança de Campo: 5 voluntários de apoio

* **Público Atendido:** Projeção orçada entre **300 e 390 participantes** ativos (jovens de 6,5 a 21 anos).

### 1.g Faturamento Anual e Orçamento do Evento

Sendo uma associação civil sem fins lucrativos, o conceito contábil de faturamento é traduzido no **Orçamento Global de Receitas e Despesas do Evento**, auditado e fixado em:

* **Orçamento Operacional Global:** **R\$ 180.000,00** (Cento e oitenta mil reais).

* **Parâmetro Histórico:** Calculado com base nas despesas executadas e auditadas do AG VI (R\$ 120.000,00 a R$ 150.000,00), devidamente reajustadas pelos índices inflacionários acumulados (IPCA e IGP-M setoriais de frete e alimentos).

* **Conta de Custódia:** Conta Jurídica Digital PJ aberta em nome do Grupo Escoteiro Caramuru no **Banco Cora**, operando sem tarifas e centralizando todas as entradas (inscrições fracionadas) e saídas (transferências bancárias e PIX).

## 3. Diagnóstico da TI Atual e Governança Operacional (Itens 2.a a 2.d)

### 2.a Procedimentos Existentes para Manutenção e Requisição de Novos Sistemas

O diagnóstico revelou um cenário de **ausência completa de governança formal**:

* **Fluxo Informal:** Demandas de suporte ou requisições de novas funcionalidades não seguiam catálogo de serviços. Voluntários solicitavam alterações de abas em planilhas ou fórmulas via áudios de WhatsApp ou discussões em reuniões presenciais.

* **Ausência de Rastreamento:** Inexistiam ferramentas de chamados (*tickets*), controle de versão de fórmulas ou homologação prévia de alterações, resultando em sobreposições acidentais de dados e fórmulas quebradas às vésperas de fechamento contábil.

### 2.b Descrição da Infraestrutura Tecnológica Existente

* **Dispositivos de Entrada (Campo):** Dispositivos móveis pessoais dos voluntários (*Bring Your Own Device - BYOD*), compreendendo smartphones Android (versões 10+) e iPhones (iOS 15+).

* **Estações da Tesouraria:** Laptops pessoais dos membros da tesouraria executando Windows 10/11, macOS e distribuições Linux.

* **Topologia de Conectividade em Campo (Juquitiba):** Devido à localização geográfica do Campo Escola em área de serra e mata atlântica, **não há cobertura de sinal celular (GSM/4G)** nem provedores locais de fibra óptica. A conectividade integral da base administrativa do evento depende exclusivamente de uma antena de internet satelital de baixa órbita (**Starlink**), cedida e instalada por um voluntário da equipe, gerando rede local Wi-Fi restrita às áreas da Secretaria e Tesouraria.

### 2.c Softwares Existentes (Sistemas Aplicativos, SO e Bancos de Dados)

* **Planilhas e Formulários:** Google Sheets (usado como banco de dados e formulário de fechamento) e Google Forms (coleta de dados cadastrais).

* **Comunicação Operacional:** Aplicativo WhatsApp (grupos temáticos de cada coordenação e conversas privadas).

* **Custódia Bancária:** Internet Banking e aplicativo mobile do Banco Cora PJ.

* **Armazenamento de Arquivos:** Pastas públicas e descentralizadas no Google Drive pessoal de voluntários.

* **Diagnóstico Crítico:** O Google Sheets não oferece integridade referencial, bloqueio de concorrência (*race condition*), trilha de auditoria contra exclusões intencionais nem validação do envio obrigatório de fotos fiscais.

### 2.d Fornecedores de TI, Alinhamento ITIL v4 e Acordo de Nível de Serviço (SLA)

Para garantir operação ininterrupta do novo sistema durante a semana crítica do acampamento, foram formalizados os provedores de computação em nuvem e os modelos operacionais baseados em boas práticas:

#### Provedores de Serviços de TI Externos

1. **Plataforma de Aplicação (PaaS Web):** **Render Cloud / Railway** (ou contêiner AWS Elastic Beanstalk), responsável pela execução do servidor web e runtime da aplicação Django.

2. **Banco de Dados Relacional Gerenciado:** **PostgreSQL** hospedado em nuvem (via **Supabase Database Engine** ou **AWS RDS**), garantindo transações ACID e retenção automatizada de snapshots diários.

3. **Storage de Arquivos e Mídia:** **Cloudflare R2 Object Storage / AWS S3**, destinado ao armazenamento protegido das fotos dos recibos e notas fiscais com redundância global e baixo custo de tráfego de saída.

4. **Controle de Versão e CI/CD:** **GitHub Cloud**, gerenciando o repositório central, automação de testes unitários e esteira de entrega contínua.

#### Acordo de Nível de Serviço (SLA)

* **Disponibilidade (Uptime do Sistema):**

  * *Período Pré-Evento (Planejamento):* $99{,}5\%$ de disponibilidade mensal.

  * *Período do Evento (7 dias contínuos em Juquitiba):* $99{,}9\%$ **de disponibilidade ininterrupta**.

* **Tempo de Atendimento a Incidentes Críticos (P1 - Falha no Upload ou Queda de Banco):**

  * *Tempo de Primeira Resposta (MTTA):* Menor que $30\text{ minutos}$.

  * *Tempo Máximo de Restabelecimento (MTTR):* **Menor que** $2\text{ horas}$.

* **Objetivo de Ponto de Recuperação (RPO):** Máximo de $24\text{ horas}$ no pré-evento e snapshots a cada $6\text{ horas}$ durante a semana do acampamento.

#### Procedimentos Operacionais Alinhados ao ITIL v4

* **Gerenciamento de Incidentes:** Qualquer falha relatada em campo é canalizada para a tesouraria, que abre um chamado formal na ferramenta de triagem técnica (**GitHub Issues**), com atribuição de etiquetas de severidade (*High/Critical, Medium, Low*), impedindo a perda de rastreabilidade do bug.

* **Gerenciamento de Mudanças:** É terminantemente proibido efetuar alterações de código diretamente no ambiente de produção. Toda correção ou novo *patch* deve seguir o fluxo de Pull Request, aprovação de testes automatizados e implantação prévia em ambiente de homologação (*Staging*).

* **Gerenciamento de Liberação (*Release Management*):** *Freezing* de código (congelamento de versões) 72 horas antes do início da montagem de campo do acampamento, permitindo unicamente *hotfixes* emergenciais previamente revisados pelo líder técnico.

## 4. Engenharia do Novo Sistema (Itens 3.a a 3.f)

### 3.a Definição do Escopo do Sistema com base no PMBOK

#### 3.a.1 Justificativa Estratégica do Projeto

Automatizar e centralizar o fluxo de prestações de contas e reembolsos operacionais das 15 coordenações do AG VII, eliminando o extravio de documentos fiscais, reduzindo a zero o risco de descontrole orçamentário por área e assegurando que o fechamento financeiro do acampamento ocorra em menos de 48 horas após o encerramento das atividades.

#### 3.a.2 Declaração de Escopo do Produto (*In-Scope*)

* Módulo Web Responsivo (*Mobile-First*) para submissão ágil de despesas com anexação obrigatória de fotos/arquivos de notas ou cupons fiscais.

* Painel Administrativo da Tesouraria com visualização consolidada de solicitações pendentes, análise de comprovantes fiscais em alta resolução e botões de decisão rápida (Aprovar, Rejeitar com Justificativa, Liquidar Pagamento).

* Módulo de Gestão Orçamentária com parametrização individual dos tetos das 15 coordenações e abatimento em tempo real de saldos comprometidos.

* Mecanismo de Alerta de Estouro Orçamentário (*Soft-block* com autorização especial de verba).

* Mecanismo de Auditoria e Histórico Imutável de Transições de Estado.

* Exportação de Relatórios de Fechamento Contábil nos formatos CSV, Excel e PDF sintético.

#### 3.a.3 Exclusões Explícitas de Escopo (*Out-of-Scope*)

Para assegurar a conclusão rigorosa do software funcional dentro do semestre letivo (mitigando complexidades desnecessárias de integração), **não fazem parte do escopo**:

1. **Transferências Bancárias Automáticas:** O sistema não integrará APIs bancárias abertas (*Open Finance/PIX API*) para débito automático. A liquidação física do dinheiro continua sendo executada pelo tesoureiro dentro do internet banking do Banco Cora PJ.

2. **Gestão de Contratos Estruturais Centrais:** Não gerenciará minutas ou parcelamentos dos contratos de ônibus fretados e locação do sítio.

3. **Módulo de Inscrição e Prontuários Médicos:** Não coletará fichas médicas, laudos ou cadastros nominais de participantes.

#### 3.a.4 Estrutura Analítica do Projeto (EAP / WBS Resumida)

```
1.0 SIG-Reembolso
  ├── 1.1 Gerenciamento do Projeto e Requisitos
  │     ├── 1.1.1 Elicitação e Análise Documental
  │     ├── 1.1.2 Especificação de RF, RNF e Domínio
  │     └── 1.1.3 Defesa de Escopo (Fase 1)
  ├── 1.2 Modelagem e Infraestrutura
  │     ├── 1.2.1 Modelagem Relacional (PostgreSQL)
  │     ├── 1.2.2 Arquitetura Django e Settings
  │     └── 1.2.3 Configuração de Storage de Mídia
  ├── 1.3 Desenvolvimento de Software
  │     ├── 1.3.1 App Usuários e RBAC
  │     ├── 1.3.2 App Financeiro e Controle de Tetos
  │     ├── 1.3.3 App Despesas, Uploads e Máquina de Estados
  │     └── 1.3.4 Telas Responsivas (Bootstrap 5)
  ├── 1.4 Testes e Garantia de Qualidade
  │     ├── 1.4.1 Testes Unitários de Regras de Domínio
  │     └── 1.4.2 Testes Integrados de Carga e Upload
  └── 1.5 Encerramento e Homologação
        ├── 1.5.1 Manuais de Operação e Treinamento
        ├── 1.5.2 Termo de Homologação Assinado
        └── 1.5.3 Apresentação Final (Fase 2)

```

#### 3.a.5 Critérios de Aceitação Formal

* Todo reembolso lançado deve possuir pelo menos um arquivo de cupom/nota fiscal legível atrelado.

* O sistema deve calcular o saldo orçamentário restante da coordenação sem divergência de centavos, respeitando transações ACID.

* O Coordenador Financeiro do AG VII deve assinar o Termo de Aceite Formal e Homologação comprovando que o sistema atende aos padrões contábeis da instituição.

### 3.b Cronograma Físico de Desenvolvimento

O cronograma foi planejado para atender com precisão aos marcos estipulados pelo Departamento de TI da FATEC-SP para o 2º Semestre de 2026:

| Etapa | Período de Execução | Atividades e Entregáveis | Marco Avaliativo | 
| ----- | ----- | ----- | ----- | 
| **Etapa 1** | 01/08/2026 a 16/10/2026 | Levantamento e diagnóstico de TI, elicitação de requisitos, delimitação do escopo PMBOK, elaboração do documento base e dos slides de apresentação. | **Apresentação Oficial da 1ª Fase (16/10/2026)** | 
| **Etapa 2** | 17/10/2026 a 31/10/2026 | Configuração do repositório no GitHub, arquitetura Django, modelagem de dados relacional no PostgreSQL e prototipação de wireframes mobile. | Conclusão do Backlog de Código | 
| **Etapa 3** | 01/11/2026 a 20/11/2026 | Codificação dos modelos, views, controle de RBAC, upload de comprovantes fiscais, máquina de estados e painel administrativo da tesouraria. | Software Funcional em Staging | 
| **Etapa 4** | 21/11/2026 a 27/11/2026 | Execução de testes de unidade automatizados, elaboração dos manuais de operação e treinamento, e submissão da documentação integral via Microsoft Teams. | **Entrega Final da Documentação no Teams (27/11/2026)** | 
| **Etapa 5** | 28/11/2026 a 04/12/2026 | Rodada de validação assistida com o Coordenador Financeiro, assinatura do termo de homologação e defesa pública perante a banca examinadora. | **Apresentação Oficial da 2ª Fase (Até 04/12/2026)** | 

### 3.c Elicitação de Requisitos do Sistema e Metodologia

Para obter requisitos sólidos e blindados contra inconsistências, a equipe combinou três técnicas de engenharia de software:

1. **Análise Documental:**

   * *Procedimento:* Exame aprofundado dos relatórios físicos de prestação de contas, balanços patrimoniais e pastas de recibos fiscais remanescentes do Acampamento Geral VI.

   * *Justificativa:* Identificou as falhas contábeis recorrentes da edição anterior, tais como cupons desbotados, despesas sem classificação e divergências entre extratos bancários e anotações manuais.

2. **Entrevistas Semi-estruturadas com Usuários-Chave:**

   * *Procedimento:* Entrevistas individuais realizadas com o Coordenador Geral, o Coordenador Financeiro/Tesoureiro e os Coordenadores de Infraestrutura e Cozinha do evento.

   * *Justificativa:* Mapeou a jornada do voluntário que sai do campo escola para efetuar compras de emergência, registrando as restrições de tempo, cansaço físico e dificuldades de manuseio de notas em ambientes inóspitos.

3. **Prototipação Rápida de Interfaces (*Wireframing*):**

   * *Procedimento:* Criação de telas navegáveis de baixa fidelidade no celular e validação direta com voluntários em reuniões prévias.

   * *Justificativa:* Assegurou que a submissão de uma despesa fosse concluída em menos de 60 segundos com pouquíssimos toques, prevenindo atritos de adoção sob chuva ou sol intenso.

### 3.d Requisitos Funcionais do Sistema (RF)

* **RF01 - Autenticação e Controle de Acesso Baseado em Papéis (RBAC):** O sistema deve autenticar usuários e restringir acessos de acordo com os perfis cadastrados:

  * *Coordenador de Área:* Lança despesas da sua respectiva coordenação, anexa comprovantes, salva rascunhos e consulta seu extrato de saldo.

  * *Tesoureiro / Gestor Financeiro:* Visualiza todas as coordenações, altera tetos, aprova/rejeita despesas e liquida pagamentos.

  * *Administrador Geral:* Gestão global do sistema.

* **RF02 - Parametrização e Gestão de Coordenações:** A Tesouraria deve poder cadastrar, editar e desativar coordenações operacionais, fixando seus limites orçamentários (*teto* em reais).

* **RF03 - Consulta Dinâmica de Saldos e Termômetro de Verba:** O sistema deve calcular e exibir na tela inicial do coordenador e no painel da tesouraria o total alocado, o valor comprometido (somatória de despesas pagas, aprovadas e em análise) e o saldo financeiro livre restante.

* **RF04 - Lançamento e Submissão de Despesa:** O usuário autenticado deve poder cadastrar uma despesa especificando: Título, Coordenação de Origem, Valor Monetário ($R\$$), Categoria do Gasto, Data da Realização, Tipo de Despesa (Reembolso, Adiantamento, Pagamento Direto) e Forma de Pagamento Original (PIX, Débito, Crédito, Espécie), acompanhado do upload obrigatório do documento fiscal.

* **RF05 - Gestão de Rascunhos:** O solicitante pode salvar lançamentos incompletos no estado *Rascunho*, permitindo correções e complemento de anexos antes da submissão final à Tesouraria.

* **RF06 - Painel de Triagem da Tesouraria:** Interface exclusiva que lista as despesas pendentes de parecer (*status* ENVIADO), permitindo a abertura de pop-up com imagem em alta resolução e botões de ação rápida para Aprovar ou Rejeitar a despesa.

* **RF07 - Liquidação de Reembolso:** A Tesouraria deve poder registrar a efetivação bancária de uma despesa aprovada, alterando seu estado para PAGO, com registro da data e anexo opcional do comprovante de transferência bancária emitido pelo internet banking Cora.

* **RF08 - Relatório de Prestação de Contas Consolidado:** O sistema deve disponibilizar relatórios contábeis sintéticos e analíticos por coordenação e categoria de gasto, exportáveis em formato estruturado (CSV/Excel) e pronto para impressão (PDF).

### 3.e Requisitos Não Funcionais do Sistema (RNF)

* **RNF01 - Usabilidade e Arquitetura *Mobile-First*:** As telas de consulta de saldo e submissão de despesas devem ser desenhadas priorizando visualizações em telas de smartphones comuns (resolução vertical entre 360px e 430px), permitindo acionamento direto da câmera nativa do aparelho para foto do cupom.

* **RNF02 - Otimização e Compressão Automática de Imagens:** O backend deve processar e comprimir automaticamente todas as fotografias enviadas pelos voluntários (reduzindo arquivos brutos de 5MB para versões otimizadas de até 350KB sem perda de legibilidade de texto), viabilizando uploads estáveis mesmo sob link satelital compartilhado e economizando espaço em disco.

* **RNF03 - Integridade e Atomicidade Transacional:** Operações de débito orçamentário, submissão e alteração de status devem operar sob transações atômicas no PostgreSQL (`@transaction.atomic`), prevenindo discrepâncias contábeis ou condições de corrida (*race conditions*) em acessos simultâneos.

* **RNF04 - Segurança da Informação e Criptografia:** Senhas devem ser armazenadas utilizando algoritmos de hashing seguros com salt (PBKDF2/SHA256). Todos os arquivos de comprovantes fiscais devem ser renomeados com chaves UUID únicas no momento da persistência, impedindo acesso indevido ou sobrescrita acidental.

* **RNF05 - Desempenho e Tempo de Resposta:** As operações de consulta de saldos e carregamento de listas de despesas não devem exceder o tempo limite de $1{,}5\text{ segundo}$ sob carga operacional padrão.

### 3.f Requisitos de Domínio e Regras de Negócio Estritas (RD / RN)

* **RD01 / RN01 - Obrigatoriedade do Comprovante Fiscal:** Nenhuma solicitação pode ser transmitida para análise da Tesouraria (transição de RASCUNHO para ENVIADO) sem pelo menos um arquivo válido anexado (formato imagem JPEG, PNG ou PDF). O sistema impede a gravação sem anexo.

* **RD02 / RN02 - Tratamento de Estouro Orçamentário (*Soft-block* com Alerta):** O sistema não deve travar impeditivamente o envio de compras emergenciais em campo. Caso o valor lançado supere o saldo restante da coordenação, a despesa é marcada automaticamente no banco como `excede_teto = True`, calculando o `valor_excedente`. No painel da Tesouraria, a solicitação ganha destaque visual em cor vermelha e exige ciência expressa do tesoureiro para concessão de aprovação especial.

* **RD03 / RN03 - Segregação de Funções (*Duty Segregation*):** Membros cadastrados com perfil de Tesoureiro que também realizem compras para coordenações operacionais ficam terminantemente bloqueados pelo sistema de analisar, aprovar ou liquidar suas próprias solicitações de reembolso.

* **RD04 / RN04 - Parecer Obrigatório em Reprovações:** A Tesouraria fica impedida pelo sistema de assinalar o status REJEITADO sem redigir um motivo claro no campo de justificativa (ex.: "Comprovante fiscal ilegível", "CNPJ do emissor em desacordo", "Despesa não autorizada para esta coordenação").

* **RD05 / RN05 - Imutabilidade Pós-Decisão:** Despesas que atinjam os estados APROVADO ou PAGO não podem ser alteradas em valores, coordenação ou datas por nenhum usuário, garantindo a integridade dos livros fiscais.

* **RD06 / RN06 - Rastreabilidade e Auditoria Imutável:** Todas as transições de estado do sistema devem gerar automaticamente uma linha na tabela de auditoria, registrando o usuário logado, o carimbo de data/hora (timestamp UTC), o estado original, o novo estado e observações.

## 5. Arquitetura de Dados, Engenharia de Software e Máquina de Estados

### 5.1 Racional da Stack Tecnológica

A seleção tecnológica foi guiada pela busca de máxima confiabilidade, facilidade de implementação no prazo acadêmico e baixo custo de implantação:

* **Backend:** **Python 3.12** com framework **Django 5.x**. A escolha fundamenta-se na robustez de seu ORM nativo, segurança pronta contra ataques comuns (CSRF, XSS, SQL Injection), ecossistema unificado de administração e facilidade para tratamento transacional de moedas com `DecimalField`.

* **Banco de Dados:** **PostgreSQL 16**. Provedor relacional padrão da indústria, garantindo conformidade ACID estrita, tipos estruturados e suporte a concorrência sem risco de travamento de tabelas.

* **Frontend:** **Django Templates** com **Bootstrap 5.3** e **Bootstrap Icons**. Elimina a necessidade de pipelines complexos de compilação em frameworks front-end separados, garantindo agilidade de entrega, código unificado e responsividade limpa para navegadores mobile e desktop.

* **Manipulação de Imagens:** Biblioteca **Pillow**, responsável pela compressão dinâmica das fotos enviadas antes da gravação no storage.

### 5.2 Máquina de Estados da Despesa

O ciclo de vida de uma solicitação no SIG-Reembolso respeita um fluxo estrito de máquina de estados finita:

```
    ┌──────────────┐
    │   RASCUNHO   │◄────────────────────────────────┐
    └──────┬───────┘                                 │
           │                                         │
           │ (Submeter com Comprovante Obrigatório)  │ (Corrigir e Reenviar)
           ▼                                         │
    ┌──────────────┐                                 │
    │   ENVIADO    │                                 │
    └──┬────────┬──┘                                 │
       │        │                                    │
       │        └────────────────►┌──────────────┐   │
       │ (Aprovar Tesouraria)     │  REJEITADO   ├───┘
       ▼                          │(Exige Motivo)│
┌──────────────┐                  └──────────────┘
│   APROVADO   │
└──────┬───────┘
       │ (Liquidação Bancária Cora PJ)
       ▼
┌──────────────┐
│     PAGO     │
└──────────────┘

```

*Estados Terminais ou Especiais:* A qualquer momento anterior à aprovação, o solicitante pode assinalar a despesa como `CANCELADO`.

### 5.3 Modelagem Conceitual e Dicionário de Dados Django

Abaixo está o detalhamento estrutural das três entidades centrais que compõem a arquitetura de persistência do sistema:

#### Model: `financeiro.Coordenacao`

Representa as 15 frentes operacionais e gerencia os saldos e tetos alocados.

* `nome` (CharField, max_length=100, unique=True): Nome oficial da área.

* `sigla` (CharField, max_length=10, unique=True): Abreviação mnemônica.

* `descricao` (TextField): Escopo operacional e atribuições da pasta.

* `teto_orcamentario` (DecimalField, max_digits=10, decimal_places=2): Dotação financeira do evento.

* `ativo` (BooleanField, default=True): Sinalizador de coordenação ativa.

* `criado_em` (DateTimeField, auto_now_add=True): Timestamp de criação.

*Propriedades Calculadas (ORM):*

$$
\text{total\_comprometido} = \sum \text{despesas}(\text{PAGO}) + \sum \text{despesas}(\text{APROVADO}) + \sum \text{despesas}(\text{ENVIADO})
$$

$$
\text{saldo\_disponivel} = \text{teto\_orcamentario} - \text{total\_comprometido}
$$

#### Model: `despesas.Despesa`

Entidade central do sistema, agregando as informações financeiras e comprobatórias.

* `coordenacao` (ForeignKey -> `financeiro.Coordenacao`, on_delete=PROTECT): Área onerada.

* `solicitante` (ForeignKey -> `settings.AUTH_USER_MODEL`, on_delete=PROTECT): Usuário que realizou a compra.

* `titulo` (CharField, max_length=150): Identificação concisa do item adquirido.

* `descricao` (TextField, blank=True): Detalhamento operacional da despesa.

* `categoria` (CharField, choices=CategoriaDespesa): Classificação contábil (Alimentação, Combustível, Saúde/Farmácia, Programa, Infraestrutura, Locação, Outros).

* `tipo` (CharField, choices=TipoDespesa): Modalidade (Reembolso, Fundo de Caixa, Pagamento Direto).

* `forma_pagamento_original` (CharField, choices=MetodoPagamentoOriginal): Método utilizado na ponta (PIX, Crédito, Débito, Espécie, Boleto).

* `valor` (DecimalField, max_digits=10, decimal_places=2): Valor nominal da compra.

* `data_despesa` (DateField): Data expressa no documento fiscal.

* `comprovante` (FileField): Foto ou PDF do recibo ou cupom fiscal.

* `status` (CharField, choices=StatusDespesa, default=RASCUNHO, db_index=True): Estado atual no fluxo.

* `excede_teto` (BooleanField, default=False): Flag automática de estouro de verba.

* `valor_excedente` (DecimalField, max_digits=10, decimal_places=2, default=0.00): Valor que excede a dotação.

* `analisado_por` (ForeignKey -> `settings.AUTH_USER_MODEL`, null=True): Tesoureiro responsável pela triagem.

* `analisado_em` (DateTimeField, null=True): Data/hora da decisão.

* `motivo_rejeicao` (TextField, blank=True): Justificativa formal da reprovação.

* `pago_por` (ForeignKey -> `settings.AUTH_USER_MODEL`, null=True): Tesoureiro que efetuou a liquidação.

* `pago_em` (DateTimeField, null=True): Data/hora do pagamento.

* `comprovante_pagamento` (FileField, null=True, blank=True): Comprovante bancário do Banco Cora PJ.

#### Model: `despesas.HistoricoTransicaoStatus`

Tabela imutável dedicada à auditoria e conformidade contábil.

* `despesa` (ForeignKey -> `despesas.Despesa`, on_delete=CASCADE): Despesa auditada.

* `status_anterior` (CharField): Estado prévio.

* `novo_status` (CharField): Estado posterior.

* `alterado_por` (ForeignKey -> `settings.AUTH_USER_MODEL`, on_delete=PROTECT): Autor da transição.

* `data_hora` (DateTimeField, auto_now_add=True): Timestamp exato da ocorrência.

* `observacao` (TextField, blank=True): Notas complementares da transição.

### 5.4 Distribuição Orçamentária Inicial (Matriz das 15 Coordenações)

Para a inicialização do banco de dados (carga via fixture JSON), o orçamento global de **R\$ 180.000,00** foi alocado conforme as necessidades históricas de campo apuradas na elicitação:

| ID | Nome da Coordenação | Sigla | Atribuição Operacional Primária | Teto Alocado (R\$) | % do Orçamento | 
| ----- | ----- | ----- | ----- | ----- | ----- | 
| 1 | Alimentação e Cozinha Central | `ALIM` | 5 refeições diárias para \~400 pessoas por 7 dias | R\$ 65.000,00 | 36,1% | 
| 2 | Infraestrutura e Manutenção | `INFRA` | Rede elétrica, hidráulica, geradores e reparos | R\$ 25.000,00 | 13,9% | 
| 3 | Transporte e Logística | `TRANS` | Vans de apoio, combustível de campo e fretes | R\$ 20.000,00 | 11,1% | 
| 4 | Programa e Atividades Gerais | `PROG` | Oficinas pedagógicas, gincanas e dinâmicas | R\$ 14.000,00 | 7,8% | 
| 5 | Som, Iluminação e Multimídia | `MULT` | Equipamentos de som, iluminação e geradores cênicos | R\$ 12.000,00 | 6,7% | 
| 6 | Saúde e Primeiros Socorros | `SAUDE` | Farmácia de campo, curativos e emergências | R\$ 8.000,00 | 4,4% | 
| 7 | Segurança e Brigada de Campo | `SEG` | Rádios comunicadores, lanternas e vigília | R\$ 6.000,00 | 3,3% | 
| 8 | Secretaria e Recepção | `SEC` | Crachás, pulseiras, kits de boas-vindas e materiais | R\$ 5.000,00 | 2,8% | 
| 9 | Bazar e Cantina Operacional | `CANT` | Suprimentos de apoio contínuo aos voluntários | R\$ 5.000,00 | 2,8% | 
| 10 | Almoxarifado e Compras de Campo | `ALMOX` | Ferramental, cordas, fitas e lonas extras | R\$ 4.000,00 | 2,2% | 
| 11 | Alojamentos e Estrutura de Barracas | `ALOJ` | Estrutura de abrigo e reparos de acantonamento | R\$ 4.000,00 | 2,2% | 
| 12 | Limpeza e Gestão de Resíduos | `LIMP` | Coleta seletiva, desinfecção e destinação de lixo | R\$ 4.000,00 | 2,2% | 
| 13 | Espiritualidade e Capelania | `ESPIR` | Materiais litúrgicos e momentos devocionais | R\$ 3.000,00 | 1,7% | 
| 14 | Comunicação e Mídias | `COM` | Cobertura fotográfica, pilhas e sinalização | R\$ 3.000,00 | 1,7% | 
| 15 | Fundo de Reserva da Tesouraria | `TES` | Reserva técnica para contingências e suplementações | R\$ 6.000,00 | 3,3% | 
| **TOTAL** | **Orçamento Geral Consolidado** | — | — | **R\$ 180.000,00** | **100,0%** | 

## 6. Fluxo Operacional Ponta a Ponta

O funcionamento prático do SIG-Reembolso traduz-se em uma jornada sem fricção entre a ponta de consumo e a tesouraria:

### Passo 1: Aquisição e Captura do Comprovante (Em Campo)

1. O voluntário autorizado da coordenação (ex.: Cozinha) adquire verduras frescas no comércio local de Juquitiba com dinheiro próprio ou cartão.

2. No momento em que recebe a nota fiscal ou cupom SAT, o voluntário saca o celular, acessa a rota web do sistema e clica em **"Nova Despesa"**.

3. O sistema abre a câmera do smartphone; o voluntário enquadra a nota fiscal. O software compacta a imagem em milissegundos.

4. O voluntário digita o valor ($R\$$), seleciona a categoria e clica em **"Submeter para Análise"**. O status é imediatamente promovido a `ENVIADO`.

### Passo 2: Triagem e Auditoria (Na Sede Administrativa / Tesouraria)

1. O tesoureiro, operando em desktop conectado à rede Starlink na sede, acompanha o painel em tempo real.

2. A nova despesa desponta na fila de triagem. Caso a compra tenha superado o saldo livre daquela coordenação, um alerta em vermelho (`ESTOURO DE TETO`) surge na tela.

3. O tesoureiro abre a despesa: o sistema exibe o comprovante fiscal em alta definição em uma modal lateral, confrontando com o valor digitado.

4. Com um clique em **"Aprovar"**, o status avança para `APROVADO`. O saldo orçamentário da coordenação é debitado instantaneamente.

5. Caso o recibo esteja rasurado ou seja ilegível, o tesoureiro clica em **"Rejeitar"**, digita o motivo obrigatório (ex.: "Total ilegível no cupom") e a despesa retorna ao coordenador como `REJEITADO` para reenvio corrigido.

### Passo 3: Liquidação Bancária e Prestação de Contas Final

1. Periodicamente (duas vezes ao dia), o tesoureiro filtra as despesas aprovadas e abre o Internet Banking do Banco Cora PJ.

2. Realiza o PIX de ressarcimento na chave cadastrada do voluntário.

3. No SIG-Reembolso, marca a despesa como `PAGO` e anexa o PDF/comprovante bancário do Banco Cora.

4. Ao término dos 7 dias, a Tesouraria emite o Relatório Consolidado de Prestação de Contas com todos os arquivos fiscais zipados em lote, entregando o balanço formalmente à Diretoria do Grupo Escoteiro.

## 7. Guia de Defesa e Argumentos Estratégicos perante a Banca

Esta seção reúne as respostas conceituais e técnicas para blindar o grupo contra questionamentos rigorosos durante a apresentação:

### Q1: "Por que desenvolver um sistema próprio em Django em vez de usar Google Forms associado a uma planilha do Google Sheets?"

* **Resposta Estratégica:**

  > *"O Google Forms e as planilhas do Sheets carecem de integridade transacional ACID e controle de concorrência com segregação de funções. Em planilhas compartilhadas na nuvem, qualquer usuário pode inadvertidamente apagar fórmulas contábeis ou sobrescrever lançamentos de outras coordenações. Além disso, as planilhas não efetuam a compressão de imagens em tempo real (sobrecarregando o armazenamento), não impedem que um tesoureiro aprove os próprios gastos e não abatem orçamentos de maneira blindada com máquina de estados finita. O SIG-Reembolso amarra a imagem fiscal diretamente à transação do banco relacional, garantindo auditoria e conformidade contábil inquebrável."*

### Q2: "Como o sistema lida com a falta de sinal de celular no Campo Escola em Juquitiba?"

* **Resposta Estratégica:**

  > *"Identificamos essa restrição geográfica na etapa de diagnóstico da infraestrutura (Item 2.b). O sítio conta com conectividade satelital Starlink centralizada na sede administrativa. Como as compras operacionais ocorrem no comércio urbano vizinho (centros de Juquitiba e Miracatu), o voluntário efetua a compra, fotografa o cupom na hora pelo celular e, ao ingressar no raio Wi-Fi da sede do evento, transmite o formulário em segundos graças ao motor de compressão que reduz as imagens para menos de 350KB."*

### Q3: "Por que os contratos de ônibus fretados e locação do sítio não entram no fluxo de reembolso do software?"

* **Resposta Estratégica:**

  > *"Aplicamos com rigor a metodologia do PMBOK (Item 3.a) delimitando o que é Escopo do Produto e o que são Exclusões Explícitas (Out-of-Scope). A frota de ônibus e o sítio são contratos estruturais de grande porte, pactuados diretamente entre a Pessoa Jurídica do Grupo Escoteiro e as fornecedoras, faturados com antecedência e liquidados via conta bancária central da Diretoria. Nenhum voluntário desembolsa R\$ 20.000 do próprio bolso para pedir reembolso em campo. O SIG-Reembolso foi projetado para resolver a dor das compras operacionais e emergenciais descentralizadas nas 15 coordenações."*

### Q4: "Qual o sentido de aplicar ITIL e fixar SLA para um sistema de escopo acadêmico?"

* **Resposta Estratégica:**

  > *"Embora o sistema seja construído como projeto acadêmico de LES, sua implantação atende a uma operação do mundo real com movimentação orçamentária de R\$ 180 mil e cerca de 400 pessoas isoladas em um campo. O SLA de 99,9% durante os 7 dias de acampamento é indispensável para que o software não fique indisponível durante o abastecimento da cozinha ou socorro da enfermagem. Da mesma forma, os preceitos de ITIL v4 (Gestão de Mudanças com staging e Gestão de Incidentes via GitHub Issues) garantem que correções urgentes em campo não quebrem o banco de dados em produção."*

### Q5: "Por que adotar um alerta de estouro de teto (soft-block) em vez de travar impeditivamente o lançamento?"

* **Resposta Estratégica:**

  > *"Em Engenharia de Software voltada ao usuário, os requisitos de domínio devem espelhar a realidade do negócio. Se a equipe de saúde precisar de um medicamento urgente na madrugada e o sistema travar a submissão porque o teto estourou em R\$ 10, o coordenador simplesmente abandonará o sistema e voltará a enviar o cupom solto no WhatsApp do tesoureiro, matando a adoção do software. O soft-block permite o registro tempestivo da despesa, sinaliza a bandeira vermelha no painel e transfere a governança para a alçada de decisão consciente do Tesoureiro."*

## 8. Planejamento de Entregas da 2ª Fase (Itens 3.g a 3.l)

Com a aprovação da documentação da 1ª Fase, os esforços da equipe concentram-se na execução dos artefatos práticos exigidos no edital para o fechamento da disciplina:

* **Item 3.g - Definição das Interfaces do Sistema com Base na Usabilidade:**

  * Telas Mobile-First em Bootstrap 5: tela de login limpa, extrato de saldo com barra percentual e formulário de submissão direta com acionamento de câmera.

  * Painel Desktop da Tesouraria: grid de cartões de triagem, modal com lente de aumento para leitura de cupons fiscais e filtros rápidos por status e área.

* **Item 3.h - Documentação Técnica e Código-Fonte do Sistema:**

  * Repositório oficial no GitHub com branches protegidas, arquivo `requirements.txt` estruturado para execução em ambiente virtual padrão (`venv`), migrações do Django e scripts de inicialização de dados (`fixtures/coordenacoes_iniciais.json`).

* **Item 3.i - Procedimentos Descritivos de Testes do Sistema:**

  * Suíte de testes automatizados unitários e de integração utilizando o test runner nativo do Django (`TestCase`), cobrindo: transições proibidas de estado, integridade de DecimalField monetário, validação de soft-block e testes de upload de arquivos corrompidos.

* **Item 3.j - Manual de Operação do Sistema:**

  * Guia ilustrado passo a passo voltado aos Coordenadores de Campo, orientando o cadastramento de despesas, conferência de fotos nítidas e acompanhamento do parecer da tesouraria.

* **Item 3.k - Manual de Treinamento do Sistema:**

  * Roteiro de capacitação para a equipe da Tesouraria e Coordenadores Gerais, abordando a triagem de despesas, concessão de autorizações especiais de estouro de teto e conciliação bancária de fechamento.

* **Item 3.l - Procedimentos para Homologação do Sistema:**

  * Roteiro formal de testes de aceitação do usuário (UAT) e minuta do Termo de Homologação Formal a ser assinado pelo Coordenador Financeiro do AG VII antes da apresentação final de 2ª Fase.