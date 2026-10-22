# Modelo de Dados Relacional (DER) - SIG-Reembolso

**Projeto:** SIG-Reembolso (Acampamento Geral VII - Grupo Escoteiro Caramuru)  
**Disciplina:** Laboratório de Engenharia de Software (LES) - FATEC-SP  
**Referência:** Item 5.3 da especificação

---

## 1. Diagrama de Entidade-Relacionamento (Mermaid)

```mermaid
erDiagram
    USUARIO ||--o{ DESPESA : "solicita"
    USUARIO ||--o{ DESPESA : "analisa"
    USUARIO ||--o{ DESPESA : "liquida"
    USUARIO ||--o{ HISTORICO_TRANSICAO : "executa"
    COORDENACAO ||--o{ DESPESA : "onera"
    DESPESA ||--o{ HISTORICO_TRANSICAO : "possui trilha"

    USUARIO {
        int id PK
        string username
        string email
        string first_name
        string last_name
        string papel "COORDENADOR | TESOUREIRO | ADMIN"
        string chave_pix "Chave para recebimento"
        string telefone
        boolean is_active
    }

    COORDENACAO {
        int id PK
        string nome "ex: Alimentação e Cozinha"
        string sigla "ex: ALIM"
        text descricao
        decimal teto_orcamentario "ex: 65000.00"
        boolean ativo
        datetime criado_em
    }

    DESPESA {
        int id PK
        int coordenacao_id FK
        int solicitante_id FK
        string titulo
        text descricao
        string categoria "ALIMENTACAO, COMBUSTIVEL, SAUDE, etc"
        string tipo "REEMBOLSO, FUNDO_CAIXA, PAGAMENTO_DIRETO"
        string forma_pagamento_original "PIX, CARTAO_DEBITO, CARTAO_CREDITO, ESPECIE"
        decimal valor "Valor em R$"
        date data_despesa
        string comprovante "Caminho do arquivo UUID"
        string status "RASCUNHO, ENVIADO, APROVADO, REJEITADO, PAGO, CANCELADO"
        boolean excede_teto "Flag soft-block"
        decimal valor_excedente "Valor acima do teto"
        int analisado_por_id FK "Null se não analisado"
        datetime analisado_em
        text motivo_rejeicao "Obrigatório se REJEITADO"
        int pago_por_id FK "Null se não pago"
        datetime pago_em
        string comprovante_pagamento "Comprovante Banco Cora"
        datetime criado_em
        datetime atualizado_em
    }

    HISTORICO_TRANSICAO {
        int id PK
        int despesa_id FK
        string status_anterior
        string novo_status
        int alterado_por_id FK
        datetime data_hora
        text observacao
    }
```

---

## 2. Fórmulas e Propriedades Calculadas (`Coordenacao`)

No modelo de negócios, o teto e o saldo de cada uma das 15 coordenações são apurados dinamicamente:

$$\text{Total Comprometido} = \sum \text{Despesas}(\text{PAGO}) + \sum \text{Despesas}(\text{APROVADO}) + \sum \text{Despesas}(\text{ENVIADO})$$

$$\text{Saldo Disponível} = \text{Teto Orçamentário} - \text{Total Comprometido}$$

$$\text{Percentual Consumido (\%)} = \left( \frac{\text{Total Comprometido}}{\text{Teto Orçamentário}} \right) \times 100$$
