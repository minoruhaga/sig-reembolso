# Planejamento de Entregas da 2ª Fase - Laboratório de Engenharia de Software

**Projeto:** SIG-Reembolso  
**Cliente / Caso Real:** Acampamento Geral VII - Grupo Escoteiro Caramuru  
**Instituição:** FATEC-SP (DTI) - 2º Semestre de 2026  
**Datas Chave (Edital da Professora):**
* **Apresentação de Trabalhos 2ª Fase:** 13/11/2026, 27/11/2026 e 04/12/2026
* **Data Limite de Entrega da Documentação no Teams:** **27/11/2026**

---

## 1. Mapeamento dos Itens Obrigatórios da 2ª Fase

Conforme o edital oficial da disciplina (*Item 3 do documento da professora*), os itens requeridos para a 2ª Fase são:

| Item Edital | Descrição Oficial | Artefato no Repositório | Status |
| :--- | :--- | :--- | :---: |
| **Sistema** | Elaborar o projeto com execução (funcionando, programas, telas) | `src/` (Aplicação Django + PostgreSQL + Bootstrap 5) | A iniciar |
| **3.g** | Definição das interfaces do sistema (com base na usabilidade e justificativa) | `docs/fase-2/3g_interfaces_usabilidade.md` | Planejado |
| **3.h** | Documentação do sistema desenvolvido (programas fontes e execução) | `docs/fase-2/3h_documentacao_sistema.md` + `README.md` | Planejado |
| **3.i** | Procedimentos descritivos de testes do sistema | `docs/fase-2/3i_procedimentos_testes.md` + `tests/` | Planejado |
| **3.j** | Manual de operação do sistema | `docs/fase-2/3j_manual_operacao.md` | Planejado |
| **3.k** | Manual de treinamento do sistema | `docs/fase-2/3k_manual_treinamento.md` | Planejado |
| **3.l** | Procedimentos de homologação (aprovação) do sistema | `docs/fase-2/3l_homologacao_sistema.md` | Planejado |

---

## 2. Roteiro de Desenvolvimento (Passo a Passo)

### Sprint 1: Setup do Projeto Django e Banco de Dados
* Inicialização do projeto Django 5 com estrutura modular em `src/apps/`.
* Configuração do SQLite para desenvolvimento ágil e suporte a PostgreSQL.
* Configuração do modelo de usuários com papéis (RBAC: Coordenador, Tesoureiro, Admin).
* Criação das migrações e fixtures das 15 coordenações operacionais do AG VII com o orçamento de R$ 180.000,00.

### Sprint 2: Core de Despesas e Regras de Negócio
* Implementação dos models `Coordenacao`, `Despesa` e `HistoricoTransicaoStatus`.
* Implementação da máquina de estados com transações atômicas (`@transaction.atomic`).
* Implementação da lógica de compressão automática de fotos de notas fiscais com Pillow (`RNF02`).
* Implementação das regras: Comprovante obrigatório (`RN01`), Soft-block de estouro com alerta (`RN02`), Segregação de funções (`RN03`), Parecer obrigatório em rejeição (`RN04`) e Imutabilidade (`RN05`).

### Sprint 3: Telas e Usabilidade Mobile-First (Item 3.g)
* Layout base com Bootstrap 5.3 responsivo e Bootstrap Icons.
* Interface Mobile-First para voluntários em campo (Nova despesa com botão de câmera, extrato de saldo da coordenação com barra de termômetro, listagem com filtros de status).
* Painel Desktop da Tesouraria (Grid de triagem de notas fiscais, visualização de cupom em modal de alta resolução, aprovação/rejeição rápida com motivo).
* Liquidação com anexo de comprovante de transferência Banco Cora PJ.

### Sprint 4: Relatórios e Testes Automatizados (Item 3.i)
* Exportação de relatórios de fechamento em CSV e PDF sintético.
* Bateria de testes unitários e de integração no Django (`TestCase`):
  * Teste de transições válidas e inválidas na máquina de estados.
  * Teste do cálculo do saldo dinâmico e soft-block de estouro.
  * Teste da regra de segregação de funções.
  * Teste de compressão de imagens.

### Sprint 5: Manuais, Homologação e Entrega Final (Itens 3.h, 3.j, 3.k, 3.l)
* Redação do Manual de Operação para coordenadores em campo.
* Redação do Manual de Treinamento para a Tesouraria.
* Elaboração do Roteiro e Termo de Homologação Formal com o cliente (Coordenação do AG VII - Grupo Escoteiro Caramuru).
* Revisão final da documentação consolidada para entrega no Microsoft Teams até 27/11/2026.
