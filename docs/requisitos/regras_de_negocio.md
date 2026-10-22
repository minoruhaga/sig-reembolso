# Regras de Negócio e Requisitos de Domínio (RN / RD) - SIG-Reembolso

**Projeto:** SIG-Reembolso (Acampamento Geral VII - Grupo Escoteiro Caramuru)  
**Disciplina:** Laboratório de Engenharia de Software (LES) - FATEC-SP  
**Referência:** Item 3.f da especificação

---

### [RN01 / RD01] Obrigatoriedade do Comprovante Fiscal
* **Regra:** Nenhuma despesa pode transitar para o estado `ENVIADO` sem a anexação de ao menos um arquivo comprobatório válido (imagem JPEG, PNG ou documento PDF legível).
* **Comportamento:** O sistema valida a presença do arquivo antes de submeter à Tesouraria. Em modo `RASCUNHO`, o anexo é opcional para permitir preenchimento preliminar.

### [RN02 / RD02] Tratamento de Estouro Orçamentário (*Soft-block* com Alerta)
* **Regra:** O sistema **não** deve impedir ou bloquear o envio de despesas essenciais em campo caso o valor supere o saldo disponível da coordenação.
* **Comportamento:**
  * Se $\text{valor} > \text{saldo\_disponivel}$, a despesa é gravada com `excede_teto = True` e `valor_excedente = valor - saldo_disponivel`.
  * Na triagem da Tesouraria, a solicitação recebe destaque em vermelho (`ESTOURO DE TETO`).
  * A aprovação requer confirmação explícita do tesoureiro para liberação da verba extraordinária.

### [RN03 / RD03] Segregação de Funções (*Duty Segregation*)
* **Regra:** Um voluntário com perfil de Tesoureiro que realize compras operacionais em nome de uma coordenação fica **impedido** pelo sistema de aprovar, rejeitar ou liquidar suas próprias solicitações de reembolso.
* **Comportamento:** Apenas outro membro com perfil de Tesoureiro poderá atuar na análise e liquidação dessa despesa.

### [RN04 / RD04] Parecer Obrigatório em Reprovações
* **Regra:** A Tesouraria não pode alterar o status de uma despesa para `REJEITADO` sem fornecer uma justificativa formal.
* **Comportamento:** O campo de motivo é obrigatório na modal de rejeição (ex: "Comprovante ilegível", "CNPJ divergente", "Item não autorizado"). O solicitante recebe a justificativa para providenciar a correção.

### [RN05 / RD05] Imutabilidade Pós-Decisão
* **Regra:** Despesas nos estados `APROVADO` e `PAGO` tornam-se estritamente imutáveis.
* **Comportamento:** Valores, coordenação, data e anexos são travados contra edição ou exclusão, resguardando a integridade fiscal e contábil.

### [RN06 / RD06] Trilha de Auditoria Imutável
* **Regra:** Toda e qualquer transição de estado no ciclo de vida de uma despesa deve registrar uma entrada na tabela de auditoria (`HistoricoTransicaoStatus`).
* **Comportamento:** Registra obrigatoriamente: ID da despesa, estado de origem, estado de destino, usuário responsável, data/hora exata (UTC) e observação/motivo.
