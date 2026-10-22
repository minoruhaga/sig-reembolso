# Requisitos Funcionais (RF) - SIG-Reembolso

**Projeto:** SIG-Reembolso (Acampamento Geral VII - Grupo Escoteiro Caramuru)  
**Disciplina:** Laboratório de Engenharia de Software (LES) - FATEC-SP  
**Referência:** Item 3.d da especificação

---

### [RF01] Autenticação e Controle de Acesso Baseado em Papéis (RBAC)
* **Descrição:** O sistema deve autenticar usuários e restringir acessos de acordo com os seguintes perfis:
  * **Coordenador de Área:** Pode lançar despesas de sua coordenação, anexar comprovantes, salvar rascunhos e acompanhar o saldo e histórico de sua pasta.
  * **Tesoureiro / Gestor Financeiro:** Pode visualizar todas as coordenações, alterar tetos orçamentários, aprovar/rejeitar despesas em fila de triagem e liquidar pagamentos.
  * **Administrador Geral:** Acesso total à administração, configuração e usuários.

### [RF02] Parametrização e Gestão de Coordenações
* **Descrição:** A Tesouraria deve poder cadastrar, editar e desativar coordenações operacionais (as 15 pastas do evento), definindo e ajustando seus limites orçamentários (*teto orçamentário* em R$).

### [RF03] Consulta Dinâmica de Saldos e Termômetro de Verba
* **Descrição:** O sistema deve calcular em tempo real e exibir na tela inicial do coordenador e no painel da tesouraria:
  * Total alocado (teto).
  * Valor comprometido ($\sum \text{PAGO} + \sum \text{APROVADO} + \sum \text{ENVIADO}$).
  * Saldo financeiro livre disponível.
  * Indicador visual percentual (barra de progresso / termômetro de consumo).

### [RF04] Lançamento e Submissão de Despesa
* **Descrição:** O usuário autenticado pode cadastrar uma nova despesa informando:
  * Título / Descrição concisa.
  * Coordenação de origem.
  * Categoria contábil (Alimentação, Combustível, Saúde/Farmácia, Programa, Infraestrutura, Locação, Outros).
  * Tipo de despesa (Reembolso, Fundo de Caixa, Pagamento Direto).
  * Forma de pagamento original (PIX, Cartão Débito, Cartão Crédito, Espécie, Boleto).
  * Valor monetário (R$).
  * Data da despesa (conforme nota/recibo).
  * Upload obrigatório do arquivo do cupom/nota fiscal (imagem da câmera ou PDF).

### [RF05] Gestão de Rascunhos
* **Descrição:** O solicitante pode salvar despesas parciais no estado `RASCUNHO`, permitindo editar dados e complementar arquivos antes da transmissão formal para a Tesouraria.

### [RF06] Painel de Triagem da Tesouraria
* **Descrição:** Interface centralizada para os tesoureiros que lista todas as solicitações no estado `ENVIADO`. Permite:
  * Visualização do comprovante fiscal em alta resolução (modal/zoom).
  * Destaque visual em caso de estouro de teto (`excede_teto = True`).
  * Ação rápida de **Aprovação** (promove para `APROVADO` e debita orçamento).
  * Ação de **Rejeição** (exige motivo obrigatório e retorna ao solicitante como `REJEITADO`).

### [RF07] Liquidação de Reembolso
* **Descrição:** A Tesouraria pode registrar o pagamento efetivo de despesas aprovadas (feitas via internet banking Cora), promovendo o status para `PAGO`, com registro de data/hora, tesoureiro responsável e anexo opcional do comprovante de transferência.

### [RF08] Relatório de Prestação de Contas Consolidado
* **Descrição:** O sistema deve gerar relatórios consolidados e analíticos por coordenação e categoria contábil, permitindo exportação nos formatos:
  * Planilha estruturada (CSV / Excel).
  * Relatório sintético formatado para impressão/apresentação (PDF).
