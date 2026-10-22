# SIG-Reembolso

**Sistema Integrado de Gestão de Fundo de Caixa, Adiantamentos e Reembolsos**  
*Piloto Oficial:* **Acampamento Geral VII (AG VII) – Grupo Escoteiro Caramuru**  
*Disciplina:* Laboratório de Engenharia de Software (LES) – FATEC-SP (DTI) – 2º Semestre / 2026

---

## 🎯 Visão Geral
O **SIG-Reembolso** é uma solução web focada em mobilidade e controle financeiro transacional em eventos temporários de grande escala. Substitui o extravio de notas fiscais em papel, o caos de solicitações dispersas no WhatsApp e a falta de visibilidade em tempo real do orçamento das 15 coordenações operacionais do acampamento.

* **Público:** ~100 voluntários operando no Campo Escola em Juquitiba/SP e equipe da Tesouraria.
* **Orçamento Auditado:** R$ 180.000,00 distribuídos entre 15 coordenações operacionais.
* **Conta de Liquidação:** Banco Cora PJ.

---

## 📚 Documentação do Projeto

### 1. Requisitos e Regras de Negócio
* [Requisitos Funcionais (RF01 - RF08)](file:///home/minoru/projetos/sig-reembolso/docs/requisitos/requisitos_funcionais.md)
* [Requisitos Não Funcionais (RNF01 - RNF05)](file:///home/minoru/projetos/sig-reembolso/docs/requisitos/requisitos_nao_funcionais.md)
* [Regras de Negócio e Domínio (RN01 - RN06)](file:///home/minoru/projetos/sig-reembolso/docs/requisitos/regras_de_negocio.md)

### 2. Arquitetura e Engenharia de Software
* [Máquina de Estados da Despesa](file:///home/minoru/projetos/sig-reembolso/docs/arquitetura/maquina_estados.md)
* [Modelo de Dados Relacional (DER)](file:///home/minoru/projetos/sig-reembolso/docs/arquitetura/modelo_dados.md)
* [Distribuição Orçamentária das 15 Coordenações](file:///home/minoru/projetos/sig-reembolso/docs/arquitetura/distribuicao_orcamentaria_coordenacoes.md)

### 3. Fase 2 - Desenvolvimento e Critérios da Banca
* [Planejamento de Entregas da 2ª Fase (Itens 3.g a 3.l)](file:///home/minoru/projetos/sig-reembolso/docs/fase-2/planejamento_fase_2.md)
* [Documentos Originais de Referência](file:///home/minoru/projetos/sig-reembolso/docs/referencias/)

---

## 🛠️ Stack Tecnológica Definida
* **Linguagem & Backend:** Python 3.12 + Django 5.x
* **Banco de Dados:** PostgreSQL (com transações `@transaction.atomic` e suporte a SQLite em dev)
* **Frontend:** Django Templates + Bootstrap 5.3 + Bootstrap Icons (*Mobile-First*)
* **Processamento de Mídia:** Pillow (compressão automática de fotos de cupons fiscais)
* **Governança:** Alinhamento ITIL v4 e versionamento no GitHub
