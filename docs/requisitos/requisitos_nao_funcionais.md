# Requisitos Não Funcionais (RNF) - SIG-Reembolso

**Projeto:** SIG-Reembolso (Acampamento Geral VII - Grupo Escoteiro Caramuru)  
**Disciplina:** Laboratório de Engenharia de Software (LES) - FATEC-SP  
**Referência:** Item 3.e da especificação

---

### [RNF01] Usabilidade e Arquitetura *Mobile-First*
* **Descrição:** A interface de submissão de despesas e consulta de saldos deve ser projetada com foco prioritário em dispositivos móveis (*smartphones* Android/iOS entre 360px e 430px de largura).
* **Critério de Aceitação:** Formulário acessível diretamente em campo, permitindo captura nativa através da câmera do aparelho em menos de 3 toques.

### [RNF02] Otimização e Compressão Automática de Imagens
* **Descrição:** O backend deve processar e otimizar todas as fotos de cupons/notas fiscais enviadas pelos voluntários através da biblioteca Pillow.
* **Critério de Aceitação:** Redução de imagens brutas de até 5MB para versões compactadas de até 350KB sem prejuízo à nitidez e legibilidade de valores fiscais e CNPJs, permitindo tráfego eficiente na rede Starlink.

### [RNF03] Integridade e Atomicidade Transacional
* **Descrição:** Todas as operações que envolvem alteração de status de despesas, abatimento ou recálculo de saldos orçamentários devem ser executadas sob transações atômicas no banco de dados (`@transaction.atomic`).
* **Critério de Aceitação:** Prevenção total de condições de corrida (*race conditions*) ou inconsistências de saldo em acessos simultâneos.

### [RNF04] Segurança da Informação e Criptografia
* **Descrição:** 
  * As credenciais de usuários devem ser protegidas por algoritmos de hashing seguros com salt (PBKDF2/SHA256 padrão do Django).
  * Todos os arquivos de mídia (comprovantes fiscais) devem ser renomeados com identificadores UUID v4 exclusivos ao serem persistidos, prevenindo enumeração ou sobrescrita acidental.

### [RNF05] Desempenho e Tempo de Resposta
* **Descrição:** O tempo de resposta para operações comuns (consulta de saldo, listagem de triagem e gravação de despesa) deve ser inferior a 1,5 segundo em condições operacionais normais.
