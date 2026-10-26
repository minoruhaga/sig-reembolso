# Backend e Domínio (Django) — Regras para Agentes e Desenvolvedores

Estas instruções aplicam-se a todo o código-fonte em `src/` e complementam o `AGENTS.md` da raiz.

---

## 1. Arquitetura e Integridade de Domínio

### CRITICAL — Localização das Regras de Negócio (RN01 a RN06)
[CRITICAL] As regras de negócio e restrições de domínio contábil do SIG-Reembolso DEVEM residir estritamente nos modelos (`models.py`) ou em serviços de domínio (`services.py`).

[FORBIDDEN] Views, templates HTML ou formulários front-end NÃO DEVEM conter lógica contábil, cálculos de rateio orçamentário ou validações primárias de estado. A view atua apenas como orquestradora de entrada/saída.

### CRITICAL — Atomicidade Transacional e Precisão Monetária
[CRITICAL] Toda operação que altere o saldo de uma coordenação, debite orçamento, transicione estados de despesa ou execute uploads DEVE estar protegida por transação atômica (`@transaction.atomic`).

[CRITICAL] Todo cálculo monetário DEVE utilizar estritamente o tipo `Decimal` (`DecimalField` do Django e `decimal.Decimal` do Python). É TERMINANTEMENTE PROIBIDO utilizar `float` para armazenar ou calcular valores em Reais (R$).

---

## 2. Máquina de Estados e Auditoria

### REQUIRED — Transições Controladas da Despesa
[REQUIRED] O ciclo de vida da entidade `Despesa` DEVE respeitar rigorosamente a máquina de estados finita:
* `RASCUNHO` $\rightarrow$ `ENVIADO` (requer anexo obrigatório - **RN01**, calcula soft-block - **RN02**)
* `ENVIADO` $\rightarrow$ `APROVADO` (requer aprovação da Tesouraria com segregação de funções - **RN03**)
* `ENVIADO` $\rightarrow$ `REJEITADO` (requer justificativa textual obrigatória - **RN04**)
* `APROVADO` $\rightarrow$ `PAGO` (liquidação com anexo de comprovante bancário Cora PJ)
* `RASCUNHO` / `ENVIADO` $\rightarrow$ `CANCELADO`

[REQUIRED] Toda transição de estado DEVE gravar automaticamente uma linha na tabela de auditoria imutável `HistoricoTransicaoStatus` (**RN06**).

[CRITICAL] Despesas nos estados `APROVADO` ou `PAGO` tornam-se estritamente imutáveis em valores, coordenação e datas (**RN05**).

---

## 3. Banco de Dados e Migrações (Code First)

### REQUIRED — Fonte da Verdade no ORM
[REQUIRED] O schema do banco de dados relacional DEVE ser evoluído exclusivamente via migrações do Django (`makemigrations` e `migrate`).

[FORBIDDEN] NUNCA crie, altere ou remova tabelas manualmente via scripts SQL no banco de produção ou desenvolvimento sem a respectiva migration do Django.

[FORBIDDEN] NUNCA edite ou apague arquivos de migração que já tenham sido integrados nas branches `main` ou `dev` compartilhadas da equipe.

---

## 4. Otimização de Comprovantes (RNF02)

### REQUIRED — Compressão Prévia com Pillow
[REQUIRED] Todo upload de arquivo de imagem de nota fiscal ou cupom DEVE ser processado pelo serviço `apps.core.services.otimizar_comprovante_fiscal` antes de ser salvo no disco/storage.
[REQUIRED] O nome final do arquivo físico persistido DEVE ser anonimizado com identificador único UUID v4 (`uuid.uuid4().hex`) para evitar colisões e enumeração direta.
