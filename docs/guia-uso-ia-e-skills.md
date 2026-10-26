# Guia de Governança de IA e Uso das Skills - SIG-Reembolso

Este guia orienta os 4 integrantes da equipe no uso de inteligência artificial assistida durante o desenvolvimento do **SIG-Reembolso** para a disciplina de Laboratório de Engenharia de Software (LES) da FATEC-SP.

---

## 1. Princípios de Desenvolvimento Agêntico (Dossiê Master)

Para evitar a geração desordenada de código (*vibecoding*) e garantir que a banca avaliadora reconheça o rigor técnico do projeto:

1. **Arquitetura A.N.T. (Architecture, Navigation, Tools):**
   * **A (Architecture):** A arquitetura e as regras contábeis estão fixadas em `docs/requisitos/regras_de_negocio.md` e `docs/arquitetura/modelo_dados.md`. O agente nunca deve "adivinhar" regras.
   * **N (Navigation):** Ao solicitar tarefas a um agente (Antigravity, Claude, ChatGPT, etc.), aponte os caminhos exatos das SOPs e do `AGENTS.md`.
   * **T (Tools):** Use comandos atômicos do Django em `src/manage.py` e testes automatizados para validar cada mudança.

2. **Data Contract Before Code:**
   * Sempre confirme os modelos de banco de dados (`models.py`) e regras de estado antes de pedir geração de telas ou endpoints.

3. **Micro-Commits e Limpeza:**
   * Nunca envie logs pesados para o chat da IA; salve-os em `.tmp/`.
   * Realize commits pequenos e atômicos após cada funcionalidade testada.

---

## 2. Como Utilizar a Skill `$decision-analysis-v4`

Antes de implementar uma funcionalidade complexa (ex: tela de triagem com zoom, exportação de PDF, cálculo de rateio), use a skill de análise de decisão para registrar o racional técnico em `prompts/`:

```text
$decision-analysis-v4 Analise a implementação do formulário mobile-first de submissão de despesas com compressão Pillow (RNF01 e RNF02).
```

### O que essa análise produz:
* Um arquivo Markdown na subpasta correta de `prompts/`.
* Comparação de alternativas viáveis.
* Registro de restrições duras e riscos.
* Rastreabilidade total que serve como evidência de engenharia para o relatório da 2ª Fase (Item 3.c e 3.h).
