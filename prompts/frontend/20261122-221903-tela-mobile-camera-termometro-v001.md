---
artifact: decision-analysis
schema_version: "4.0"
artifact_version: "v001"
status: accepted
created_at: "2026-11-22T22:19:03-03:00"
lineage:
  mode: initial
  root: null
  supersedes: null
  change_type: initial
  secondary_change_types: []
  decision_impact: initial
subjects:
  kind: mixed
  files:
    - path: docs/fase-2/backlog_issues_github.md
      relationship: primary
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: selected-section
      locator: "Issue #8 — Ricardo Sakugawa (Frontend & UI/UX)"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: src/templates/despesas/despesa_form.html
      relationship: primary
      representation: markup
      function: production
      format: html
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: src/apps/despesas/forms.py
      relationship: primary
      representation: source-code
      function: production
      format: python
      analysis_scope: selected-section
      locator: "DespesaForm — widgets de valor, data e comprovante"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: src/apps/despesas/views.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: selected-section
      locator: "nova_despesa_view, editar_despesa_view e mensagens ao usuário"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: src/apps/despesas/regras.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: selected-section
      locator: "calcular_soft_block_rn02"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: src/apps/financeiro/services.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: selected-section
      locator: "calcular_termometro_coordenacao, obter_resumo_orcamentario"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: src/apps/usuarios/services.py
      relationship: supporting
      representation: source-code
      function: production
      format: python
      analysis_scope: selected-section
      locator: "coordenacoes_visiveis"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: src/templates/base.html
      relationship: supporting
      representation: markup
      function: production
      format: html
      analysis_scope: whole-file
      locator: null
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: docs/requisitos/requisitos_nao_funcionais.md
      relationship: context
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: selected-section
      locator: "RNF01, RNF02, RNF05"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: docs/requisitos/requisitos_funcionais.md
      relationship: context
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: selected-section
      locator: "RF03, RF04, RF05"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: docs/requisitos/regras_de_negocio.md
      relationship: context
      representation: prose
      function: documentation
      format: markdown
      analysis_scope: selected-section
      locator: "RN01, RN02"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: src/AGENTS.md
      relationship: context
      representation: prose
      function: prompt-instruction
      format: markdown
      analysis_scope: selected-section
      locator: "RN em models/services; views e templates sem cálculo orçamentário; Decimal"
      content_state: working-tree
      revision: 4049583
      availability: available
    - path: AGENTS.md
      relationship: context
      representation: prose
      function: prompt-instruction
      format: markdown
      analysis_scope: selected-section
      locator: "docstrings, testes, ambiente isolado"
      content_state: working-tree
      revision: 4049583
      availability: available
routing:
  root: prompts
  selected_directory: prompts/frontend
  considered_directories: [prompts/frontend, prompts/backend]
  confidence: high
  rationale: "O objeto da decisão é a experiência de lançamento no celular (captura, contraste, máscara, termômetro). O serviço de prévia orçamentária é consequência da restrição de não calcular saldo no template, não o foco da issue."
classification:
  sphere: engineering
  concerns: [user-experience, accessibility, architecture]
  decision_kind: design
  scope: component
  lifecycle: delivery
  urgency: high
  uncertainty: low
  reversibility: high
  risk: low
---

# Análise de decisão — Interface mobile-first com câmera nativa e termômetro de verba (Issue #8)

## Solicitação original

Tela de submissão otimizada para smartphones (360px–430px) com botão direto de acionamento de câmera nativa do aparelho.
Design com alto contraste para operação sob luz solar intensa em campo escola.

Critérios de Aceitação:

1. Input file com captura direta da câmera do smartphone.
2. Layout mobile testado e responsivo.

Complemento do backlog (`docs/fase-2/backlog_issues_github.md`): refinamento da tela de submissão com `<input type="file" accept="image/*" capture="environment">` e termômetro visual.

## Informações complementares

- O formulário funcional da Issue #7 já estava na `dev` (comentário do Tech Lead na issue): esta entrega é refinamento de interface, não criação do fluxo de submissão.
- Esta análise foi redigida ao fim da implementação, registrando as decisões tomadas durante a entrega. Por isso o `status` é `accepted`.
- Durante a revisão do responsável pela issue, foram pedidos dois ajustes que entraram no mesmo escopo: (a) mensagens de erro exibidas ao usuário sem códigos de regra (RN01, RN05...), apenas a explicação; (b) campo de valor com máscara de centavos (digitar `1000` exibe `10,00`).
- A pasta `prompts/frontend/` estava prevista no `prompts/README.md`, mas não existia; esta é a primeira análise dela.

## Mudanças desde a versão anterior

| Elemento | Versão anterior | Versão atual | Motivo | Impacto |
|---|---|---|---|---|
| N/A | Nenhum identificado | v001 inicial | Primeira análise | Decisão inaugural |

## Artefatos analisados

| Caminho | Relação | Representação | Função | Formato | Recorte | Estado/revisão |
|---|---|---|---|---|---|---|
| docs/fase-2/backlog_issues_github.md | primary | prose | documentation | markdown | Issue #8 | 4049583 |
| src/templates/despesas/despesa_form.html | primary | markup | production | html | arquivo inteiro | 4049583 |
| src/apps/despesas/forms.py | primary | source-code | production | python | widgets do DespesaForm | 4049583 |
| src/apps/despesas/views.py | supporting | source-code | production | python | views de despesa e mensagens | 4049583 |
| src/apps/despesas/regras.py | supporting | source-code | production | python | soft-block RN02 | 4049583 |
| src/apps/financeiro/services.py | supporting | source-code | production | python | termômetro | 4049583 |
| src/apps/usuarios/services.py | supporting | source-code | production | python | coordenacoes_visiveis | 4049583 |
| src/templates/base.html | supporting | markup | production | html | layout e Bootstrap | 4049583 |
| docs/requisitos/requisitos_nao_funcionais.md | context | prose | documentation | markdown | RNF01/02/05 | 4049583 |
| docs/requisitos/requisitos_funcionais.md | context | prose | documentation | markdown | RF03/04/05 | 4049583 |
| docs/requisitos/regras_de_negocio.md | context | prose | documentation | markdown | RN01/RN02 | 4049583 |
| src/AGENTS.md | context | prose | prompt-instruction | markdown | regras de camada | 4049583 |
| AGENTS.md | context | prose | prompt-instruction | markdown | docstrings/testes | 4049583 |

### Limites da evidência dos artefatos

- A captura pela câmera foi validada em navegador com emulação de dispositivo (360px, 375px e 430px) e com arquivo simulado; não houve teste em aparelho Android/iOS real até a data desta análise.
- O contraste sob luz solar foi decidido por critério (cores puras e bordas grossas), não medido em campo.

## Problema enriquecido

### Resultado desejado

O voluntário, de pé no Campo Escola, com o celular numa mão e sob sol ou chuva, registra uma compra em poucos toques: fotografa o cupom, digita o valor e envia, sabendo antes do envio se a compra cabe na verba da sua coordenação.

### Atores e interesses

- Coordenador de área: abrir a câmera rápido, ler a tela no sol, digitar o valor sem errar a vírgula, saber se ainda tem verba.
- Tesouraria: receber cupons legíveis e despesas com valor correto; ver o estouro sinalizado (RN02), sem que o campo seja bloqueado.
- Tech Lead / banca LES: manter as regras de camada do `src/AGENTS.md` e evidência de RNF01.

### Evidências e fatos observados

- `despesa_form.html` (Issue #7) usava card Bootstrap genérico, campo de arquivo padrão e layout em colunas pensado para desktop.
- `DespesaForm.comprovante` já tinha `capture="environment"`, mas o input aparecia como campo de arquivo comum, pequeno para toque.
- `data_despesa` usava `DateInput(type="date")` sem `format`; o Django renderizava `dd/mm/aaaa`, que o `<input type="date">` não aceita, então a data inicial aparecia vazia no celular (bug).
- O valor usava `NumberInput` com `step=0.01`, exigindo ponto decimal (`45.90`), contrário ao hábito brasileiro.
- `calcular_termometro_coordenacao` e `calcular_soft_block_rn02` já existiam (Issues #10 e #12), mas nenhum projetava o efeito de uma compra ainda não enviada.
- `src/AGENTS.md` proíbe cálculo orçamentário em views e templates.
- Mensagens de erro exibiam códigos internos ("RN01: ...", "RN05 (Imutabilidade Pós-Decisão): ..."), que o voluntário não conhece.

### Hipóteses

- A maioria dos voluntários usa Android com câmera traseira; `capture="environment"` abre a câmera direto nesses aparelhos.
- A conexão Starlink tolera uma requisição JSON pequena (< 1 KB) por pausa de digitação.
- Um coordenador atua em uma coordenação (vínculo da Issue #6).

### Perguntas em aberto

Nenhuma que altere a decisão. O teste em aparelho real fica como validação pendente.

### Escopo

- Reescrita visual de `despesa_form.html` (criação e edição).
- Botão grande de captura com câmera traseira e caminho alternativo para PDF/galeria.
- Termômetro de verba com prévia do saldo após a compra.
- Máscara de centavos no valor e leitura do formato brasileiro no servidor.
- Coordenação do usuário pré-preenchida e correção da data inicial.
- Mensagens ao usuário sem códigos de regra.
- Testes automatizados da tela, da prévia e da máscara.

### Fora do escopo

- Painel da Tesouraria com modal de zoom (Issue #13).
- Documento de usabilidade do Item 3.g (Issue #16).
- Mudanças na compressão Pillow (RNF02), já entregue na Issue #7.
- Alterações de models ou migrações.

### Critérios de sucesso

1. A câmera abre com um toque a partir da tela de nova despesa (fluxo total em menos de 3 toques, RNF01).
2. Sem rolagem horizontal entre 360px e 430px.
3. Termômetro mostra o saldo antes de enviar e sinaliza estouro sem bloquear o envio.
4. Valor digitado como `1000` é gravado como `Decimal('10.00')`.
5. Nenhuma mensagem ao usuário exibe códigos RN/RF.
6. Suíte de testes existente continua passando.

## Restrições aplicáveis

- [CRITICAL] Regras de negócio em models/services; views e templates sem cálculo orçamentário (`src/AGENTS.md`).
- [CRITICAL] Valores em reais só com `Decimal`, nunca `float`.
- [REQUIRED] Docstrings o quê / como / finalidade em toda função e classe nova.
- [REQUIRED] Testes `TestCase` para funcionalidade nova.
- [REQUIRED] Execução em `.venv` ou Nix.
- Sem migração: a issue é de interface.

## Classificação comentada

Esfera `engineering`, com foco em `user-experience` e `accessibility` (leitura sob sol, alvos de toque grandes, teclado numérico) e `architecture` (onde calcular a prévia do saldo). Risco `low`: não há mudança de dados nem de regra; a reversão é trocar o template. Urgência `high` pelo prazo interno de 24/11/2026.

## Decisão de roteamento

`prompts/frontend/` — a decisão central é a experiência de lançamento no celular. O serviço de prévia orçamentária existe para cumprir a restrição de camada, não é o objeto da issue; por isso não foi para `prompts/backend/`.

## Dimensões de decisão

| Dimensão | Prioridade | Limiar ou direção | Por que importa |
|---|---|---|---|
| user-value | high | Câmera em 1 toque; valor sem pensar em vírgula | RNF01 e critério 1 da issue |
| accessibility | high | Contraste máximo, alvos ≥ 44px, foco visível | Uso sob sol, critério da issue |
| correctness | high | Prévia igual à regra usada no envio; centavos exatos | RN02 e precisão contábil |
| architecture | high | Nenhuma conta de saldo no template ou na view | `src/AGENTS.md` [CRITICAL] |
| resilience | medium | Tela utilizável sem JS ou com rede lenta | Starlink no campo |
| simplicity | medium | Sem framework JS novo; Bootstrap e JS puro | Equipe pequena, prazo curto |

## Alternativas consideradas

### A — Template próprio de alto contraste + serviço de prévia no backend + rota JSON + máscara de centavos

Template com CSS escopado (`.campo`), botão de captura como `<label>` do input de arquivo, termômetro renderizado no primeiro carregamento e atualizado via `GET despesas/previa-orcamento/`. O cálculo fica em `simular_impacto_orcamentario`, que reaproveita `calcular_termometro_coordenacao`, `calcular_soft_block_rn02` e `coordenacoes_visiveis`. Máscara em JS com leitura pt-BR no form (`CampoValorReais`).

### B — Manter o formulário Bootstrap da #7 e só ajustar classes e tamanhos

Menor esforço, mas não atende ao alto contraste nem ao botão de câmera em destaque; o termômetro continuaria fora da tela de lançamento.

### C — Termômetro calculado inteiramente no JavaScript

Enviar teto e comprometido no HTML e subtrair o valor no navegador. Resposta instantânea e sem requisição, mas viola a restrição [FORBIDDEN] de cálculo orçamentário em templates e duplica a regra de soft-block (o RN02 trata saldo ≤ 0 de forma específica), com risco de divergir do valor gravado.

## Perfil de pagamento comparativo

| Dimensão | Prioridade | Alternativa A | Alternativa B | Alternativa C | Confiança | Base |
|---|---:|---:|---:|---:|---|---|
| user-value | high | +2 | 0 | +2 | high | B não destaca a câmera |
| accessibility | high | +2 | 0 | +2 | medium | Contraste validado só em tela |
| correctness | high | +2 | +1 | -1 | high | C duplica RN02 |
| architecture | high | +2 | +2 | -2 | high | C calcula saldo no template |
| resilience | medium | +1 | +2 | +2 | medium | A depende de rede para atualizar (mas renderiza sem JS) |
| simplicity | medium | 0 | +2 | +1 | high | A adiciona rota e serviço |

## Histórico e decisão atual

### Decisão da versão anterior

Nenhum identificado.

### Decisão recomendada nesta versão

Adotar a **alternativa A**.

1. **Captura:** botão "Fotografar cupom" amarelo de sinalização (`#FFD400`), altura ≥ 7,5rem, como `<label>` do input com `capture="environment"`; link "Anexar PDF ou foto da galeria" remove `capture` só para aquele toque. Miniatura e tamanho do arquivo após a escolha.
2. **Contraste:** fundo `#FFFFFF`, texto `#000000`, bordas de 2px, verde `#0B5D3B` e vermelho `#B3261E` de estouro; fonte Atkinson Hyperlegible; campos com 56px de altura; foco visível com anel amarelo.
3. **Ordem dos campos para o celular:** cupom → coordenação → valor → termômetro → o que foi comprado → data e forma de pagamento → categoria e modalidade → observações (recolhidas). Botões de ação fixos no rodapé.
4. **Termômetro:** `apps.despesas.services.simular_impacto_orcamentario(usuario, coordenacao_id, valor)` devolve teto, comprometido, saldo atual e após a compra, estouro e larguras da barra, tudo em `Decimal` (só as larguras viram `float`, por serem CSS). Rota `despesas/previa-orcamento/` serializa os montantes como texto e responde 404 fora do recorte RBAC. O JS chama a rota 450ms após a última tecla e só exibe.
5. **Valor:** `CampoValorReais` (subclasse de `DecimalField`) lê `1.250,40`, `10,00` e `185.50`; exibe valores salvos como `1.250,40`. Máscara de centavos no JS com teclado numérico (`inputmode="numeric"`).
6. **Correções:** `DateInput(format='%Y-%m-%d')`; coordenação do usuário como valor inicial.
7. **Mensagens:** textos ao usuário sem códigos RN/RF, dizendo o que aconteceu e o que fazer; códigos permanecem nas docstrings.
8. **Testes:** `test_tela_mobile.py` com 14 casos (captura, data, prévia, soft-block, RBAC da rota, formato pt-BR, mensagem sem código).

### Impacto da revisão

Decisão inicial.

### Dimensões maximizadas ou priorizadas

| Dimensão | Estado | Ganho esperado | Evidência ou hipótese |
|---|---|---|---|
| user-value | prioritized | Câmera em 1 toque e valor sem vírgula | Botão-label e máscara |
| architecture | prioritized | Prévia usa a mesma regra do envio | Serviço reaproveita `calcular_soft_block_rn02` |
| correctness | prioritized | `1000` → `Decimal('10.00')` | Teste `test_rascunho_com_valor_mascarado_grava_decimal_exato` |

### Dimensões satisfeitas por limiar

| Dimensão | Limiar aceito | Como a decisão atende |
|---|---|---|
| resilience | Funcionar sem JS | Termômetro e formulário renderizados no servidor |
| simplicity | Sem dependência nova de build | CSS no template, JS puro, fonte via Google Fonts com fallback |

## Perdas e trade-offs

### Perdas se as prioridades não forem atendidas

| Dimensão | Perda esperada | Severidade | Afetados |
|---|---|---|---|
| user-value | Voluntário desiste de registrar no campo e acumula cupons de papel | alta | Coordenadores, Tesouraria |
| correctness | Termômetro diz que cabe e a despesa chega com estouro | média | Tesouraria |
| accessibility | Tela ilegível sob sol | alta | Coordenadores em campo |

### Custos aceitos para priorizá-las

| Dimensão favorecida | Custo ou oportunidade | Dimensão prejudicada | Aceitabilidade |
|---|---|---|---|
| architecture | Uma requisição por pausa de digitação | resilience | aceitável: payload < 1 KB, falha silenciosa mantém a última leitura |
| user-value | Visual diferente das demais telas Bootstrap | consistência visual | aceitável: tela de campo tem contexto próprio |
| user-value | Fonte externa (Google Fonts) | resilience | aceitável: `display=swap` e fallback de sistema |

## Riscos e efeitos de segunda ordem

- Alguns navegadores iOS ignoram `capture` e oferecem o seletor completo; o fluxo continua funcionando, com um toque a mais.
- Valor reenviado sem JS sem vírgula (ex.: `10`) é tratado como reais, não centavos; a máscara só se aplica com JS ativo.
- Testes de outras issues que conferiam textos de mensagem precisaram ser ajustados (um teste da #12).
- O painel da Tesouraria (#13) pode adotar o mesmo vocabulário de mensagens para manter consistência.

## Validação da decisão

| Hipótese ou resultado | Evidência necessária | Método | Sinal para revisar |
|---|---|---|---|
| Câmera em 1 toque | `capture="environment"` no HTML | TestCase + teste manual | Aparelho real abrir galeria em vez de câmera |
| Sem rolagem horizontal | `scrollWidth == innerWidth` em 360px | Navegador em modo dispositivo | Overflow em telas < 360px |
| Prévia = regra do envio | Mesmo excedente da submissão | TestCase do serviço | Mudança em `calcular_soft_block_rn02` |
| Centavos exatos | `1.250,40` → `Decimal('1250.40')` | TestCase do form | Valor gravado diferente do digitado |
| RBAC da prévia | 404 para pasta de outro coordenador | TestCase da rota | Coordenador multi-pasta |

## Handoffs e atividades posteriores

- Testar a captura em aparelhos Android e iOS reais antes da homologação (Item 3.l).
- Issue #16 (Item 3.g) pode citar esta análise como justificativa de usabilidade e contraste.
- Issue #13 pode reaproveitar a rota de prévia e o vocabulário de mensagens.

## Síntese

A issue pedia câmera direta e alto contraste; o formulário da #7 funcionava, mas foi feito para desktop. A entrega reescreve a tela para o celular, coloca a câmera a um toque, mostra o efeito da compra na verba antes do envio e aceita o valor no formato brasileiro. O termômetro é calculado no backend reaproveitando a regra de soft-block, porque calcular no navegador violaria o `src/AGENTS.md` e poderia divergir do valor gravado.
