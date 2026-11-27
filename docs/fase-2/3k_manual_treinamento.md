# Item 3.k — Manual de Treinamento e Operação Financeira da Tesouraria

**Projeto:** SIG-Reembolso  
**Cliente / evento:** Acampamento Geral VII (AG VII) — Grupo Escoteiro Caramuru  
**Disciplina:** Laboratório de Engenharia de Software (LES) — FATEC-SP (DTI) — 2º semestre de 2026  
**Item do edital:** 3.k — Manual de treinamento do sistema  
**Artefato:** `docs/fase-2/3k_manual_treinamento.md`  
**Público:** equipe de Tesouraria e Coordenação Geral financeira do AG VII  
**Responsável:** Marina (`@Mah-Rod`) — [Issue #48](https://github.com/minoruhaga/sig-reembolso/issues/48)  
**Versão:** 1.0 — 27/11/2026

---

## Aderência ao Item 3.k

O edital pede um roteiro de capacitação da Tesouraria e dos coordenadores gerais para **triar despesas**, **autorizar estouro de teto** e **conciliar o fechamento bancário**. Este manual é esse roteiro, escrito para quem opera o caixa do evento no computador da Secretaria, não para quem lança compra no celular.

| O que a entrega pede | Onde está neste manual |
| :--- | :--- |
| Login com perfil de Tesoureiro e de Administrador | [Seção 2](#2-entrar-no-sistema) |
| Triagem no painel desktop e conferência do cupom no modal de zoom | [Seções 3 e 4](#3-fila-de-auditoria-de-notas) |
| Aprovação, reprovação com parecer obrigatório (RN04) e liquidação PIX no Banco Cora PJ com comprovante (RF07) | [Seções 5, 6 e 7](#5-aprovar-uma-despesa) |
| Autorização consciente de estouro de teto | [Seção 5.2](#52-quando-a-nota-estoura-o-teto) |
| Balancete sintético e planilha CSV (RF08) | [Seção 8](#8-prestação-de-contas-balancete-e-csv) |
| Roteiro de treino para repetir com a equipe | [Seção 9](#9-roteiro-de-capacitação) |

O lançamento da despesa pelo voluntário está no [Manual de Operação (Item 3.j)](3j_manual_operacao.md). A instalação do sistema está no [Item 3.h](3h_documentacao_sistema.md).

---

## Sumário

1. [Para quem é este treinamento](#1-para-quem-é-este-treinamento)
2. [Entrar no sistema](#2-entrar-no-sistema)
3. [Fila de Auditoria de Notas](#3-fila-de-auditoria-de-notas)
4. [Conferir o cupom no modal de zoom](#4-conferir-o-cupom-no-modal-de-zoom)
5. [Aprovar uma despesa](#5-aprovar-uma-despesa)
6. [Reprovar com parecer obrigatório (RN04)](#6-reprovar-com-parecer-obrigatório-rn04)
7. [Liquidar o PIX no Banco Cora PJ (RF07)](#7-liquidar-o-pix-no-banco-cora-pj-rf07)
8. [Prestação de contas: balancete e CSV (RF08)](#8-prestação-de-contas-balancete-e-csv)
9. [Roteiro de capacitação](#9-roteiro-de-capacitação)
10. [Dúvidas frequentes](#10-dúvidas-frequentes)
11. [Referências](#11-referências)

---

## 1. Para quem é este treinamento

Use este guia na capacitação de quem fecha o caixa do AG VII:

- **Tesoureiro**, que confere nota, aprova ou devolve, paga o PIX e tira o balancete.
- **Administrador Geral** (Diretoria), que entra na administração de cadastros e, na conta de demonstração, também alcança a auditoria de notas.

O trabalho da Tesouraria é feito no **navegador do computador** (Chrome ou Edge), em tela larga. O painel se chama **Auditoria de Notas**. Cada despesa chega como um cartão. A leitura da nota acontece num modal em tela cheia, com zoom.

O sistema **não envia PIX**. O tesoureiro paga no internet banking do **Banco Cora PJ** e só então anexa o comprovante. Sem esse anexo, a despesa não passa para **Pago**.

Contas de demonstração, depois de `python src/manage.py popular_dados_demo`:

| Usuário | Senha | Papel | Para onde o login leva |
| :--- | :--- | :--- | :--- |
| `tesoureiro` | `tesouraria123` | Tesoureiro | Painel geral. O menu **Auditoria de Notas** fica disponível. |
| `admin` | `admin123` | Administrador Geral (e superusuário de demonstração) | Administração (`/admin/`). O menu **Auditoria de Notas** também aparece, porque essa conta de aula acumula os dois acessos. |

No evento real, a senha é a entregue pela Diretoria. As senhas acima servem só para treino e para a banca.

---

## 2. Entrar no sistema

### 2.1 Tesoureiro

1. Abra o navegador no computador da Tesouraria.
2. Acesse o endereço informado pela Coordenação. Na demonstração local: [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Quem não tem sessão cai em **Entrar no SIG-Reembolso**.
3. Preencha **Usuário** com `tesoureiro` e **Senha** com `tesouraria123`.
4. Clique em **Entrar**.
5. A tela seguinte é o **Painel** geral, com os termômetros das coordenações ativas. No menu verde superior, confira o seu nome. O cabeçalho do menu mostra **Tesoureiro / Gestor Financeiro**.
6. Clique em **Auditoria de Notas**. O endereço fica `/despesas/triagem/` e o título da página é **Auditoria de Notas da Tesouraria**.

Usuário ou senha errados permanecem na tela de login, com aviso em vermelho. Não existe atalho de “esqueci a senha” nesta versão: a Diretoria redefine a senha na Administração.

Para sair de um computador compartilhado, abra o seu nome no canto superior direito e clique em **Sair**. O encerramento só vale pelo botão. Recarregar a página não desloga.

### 2.2 Administrador

1. Na mesma tela de login, use **Usuário** `admin` e **Senha** `admin123`.
2. Clique em **Entrar**.
3. O sistema abre a **Administração** (`/admin/`), com o título **SIG-Reembolso | AG VII Caramuru**. Ali a Diretoria consulta usuários, coordenações e o histórico das despesas. Não é nessa tela que se aprova nota.
4. Para auditar cupom, volte ao sistema operacional pelo menu do navegador ou abra [http://127.0.0.1:8000/despesas/triagem/](http://127.0.0.1:8000/despesas/triagem/). A conta `admin` de demonstração é superusuária, então o menu **Auditoria de Notas** aparece e as ações de aprovar, reprovar e liquidar funcionam.
5. Um administrador que **não** seja tesoureiro nem superusuário entra na Administração e **não** vê **Auditoria de Notas**. Se tentar o endereço da fila, o sistema recusa o acesso. A decisão da nota fica com a Tesouraria.

Coordenador de campo não usa este manual. O login dele não mostra **Auditoria de Notas** nem **Administração**.

---

## 3. Fila de Auditoria de Notas

A fila é a mesa de trabalho. Três cartões no topo resumem o movimento, já filtrado pela coordenação escolhida:

| Cartão | Significado |
| :--- | :--- |
| **Aguardando decisão** | Notas enviadas pelo campo, ainda sem parecer. |
| **Aprovadas, aguardando PIX** | Notas liberadas, ainda sem comprovante do Cora. |
| **Acima do teto** | Notas que passaram do saldo da pasta. O envio do campo não foi bloqueado; a decisão é da Tesouraria. |

Abaixo, os filtros:

1. Em **Situação**, o padrão é **Pendentes (aguardando decisão ou PIX)**. As outras opções são **Aguardando decisão**, **Aprovadas (pagar PIX)**, **Pagas**, **Rejeitadas** e **Todas**.
2. Em **Coordenação**, deixe **Todas as coordenações** ou escolha uma pasta (sigla e nome).
3. Clique em **Filtrar**. **Limpar** volta ao padrão.

Cada despesa aparece como cartão, com número, sigla, situação, solicitante, data, chave PIX quando existir, valor e a miniatura da nota. Borda vermelha e a faixa **ESTOURO DE TETO** marcam gasto acima do saldo. A faixa **Solicitação própria** avisa que a despesa é sua: outro tesoureiro precisa decidir (segregação de funções, RN03).

Ordem sugerida no dia do evento:

1. Filtre **Aguardando decisão** e zere a fila de parecer.
2. Troque para **Aprovadas (pagar PIX)** e liquide o que já foi conferido.
3. No fechamento do dia, abra **Pagas** e confronte com o extrato do Cora. O balancete da [seção 8](#8-prestação-de-contas-balancete-e-csv) fecha o número.

---

## 4. Conferir o cupom no modal de zoom

Não aprove pelo valor do cartão. Abra o documento.

1. Clique na miniatura (**Conferir**) ou no botão **Conferir nota**.
2. Abre o modal **em tela cheia**. À esquerda, o visor escuro da nota. À direita, os dados: valor, coordenação, solicitante, **Chave PIX**, data, categoria, tipo, forma de pagamento na ponta e observações.
3. Leia, no mínimo, estabelecimento ou CNPJ, data, valor total e se o item condiz com a categoria da pasta (alimentação na ALIM, combustível na infraestrutura, e assim por diante).
4. Use o zoom para ler número pequeno de cupom térmico:
   - **+** e **−** na barra, ou as teclas `+` e `-`, ou a roda do mouse sobre a imagem.
   - Duplo clique amplia no ponto clicado.
   - Arraste a imagem com o mouse para chegar no rodapé, onde costuma estar o total.
   - **Ajustar** (tecla `0`) encaixa a nota na tela.
   - **1:1** (tecla `1`) mostra o tamanho real, útil para conferir nitidez.
   - **Girar** (tecla `G`) corrige foto deitada.
5. Se a nota for PDF, o visor mostra o documento e os botões de zoom ficam ocultos. Use o zoom do próprio leitor de PDF.
6. **Abrir original** abre o arquivo numa aba nova, se a tela cheia ainda ficar pequena.
7. As setas **anterior** e **próxima** (teclas `←` e `→`) passam para o cartão vizinho sem fechar o modal. O contador mostra a posição, por exemplo “2 de 8”.
8. `Esc` ou o X fecham a conferência e voltam à fila.

A aba **Comprovante de pagamento** só fica ativa depois da liquidação. Na triagem inicial, a aba correta é **NF ou recibo**.

Devolva a nota se a foto estiver cortada, tremida, com flash estourado ou sem o total. O campo já recebeu o checklist de foto no manual de operação. O parecer da [seção 6](#6-reprovar-com-parecer-obrigatório-rn04) diz o que refazer.

---

## 5. Aprovar uma despesa

A aprovação só aparece no modal quando a situação é **Aguardando decisão** e a despesa **não** é sua.

1. Confira a nota como na [seção 4](#4-conferir-o-cupom-no-modal-de-zoom).
2. Confira a **Chave PIX** do solicitante no painel direito. É para essa chave que o Cora vai pagar depois.
3. Clique em **Aprovar** (tecla `A` com o modal aberto e o cursor fora da caixa de texto).
4. Confirme a pergunta “Aprovar a despesa #… de R$ …?”. Cancelar não grava nada.
5. A fila recarrega com a mensagem verde de despesa aprovada e liberada para liquidação. O cartão passa a **Aprovado** e entra no grupo **Aprovadas, aguardando PIX**.

Aprovar não paga. O dinheiro só sai na [seção 7](#7-liquidar-o-pix-no-banco-cora-pj-rf07). Depois de aprovado, valor, pasta, data e anexo fiscal não podem mais ser alterados.

### 5.2 Quando a nota estoura o teto

O campo pode enviar a compra mesmo sem saldo. O sistema marca **ESTOURO DE TETO** e mostra o quanto passou (por exemplo, `+R$ 40,00`). Isso é alerta, não trava.

Autorizar o estouro é **aprovar mesmo assim**, de propósito:

1. Leia o valor excedente no cartão vermelho e no modal.
2. Decida se o gasto é essencial para o acampamento (medicamento, gás da cozinha, combustível de resgate).
3. Se for, aprove e confirme. Essa confirmação é a autorização especial da Tesouraria.
4. Se não for, reprove com parecer que explique o teto, para o coordenador saber por que a nota voltou.

Não existe um segundo botão de “autorizar estouro”. A faixa vermelha mais a confirmação de **Aprovar** registram a decisão.

---

## 6. Reprovar com parecer obrigatório (RN04)

Reprovar sem texto é recusado. O coordenador precisa saber o que corrigir.

1. No modal de uma despesa **Aguardando decisão**, vá ao campo **Motivo da rejeição**. O exemplo na caixa é “Cupom fiscal ilegível, CNPJ divergente ou item não autorizado”.
2. Escreva o parecer em uma frase concreta. Sirva-se destes modelos, ajustando o caso:
   - “Cupom cortado: não aparece o valor total. Reenvie a foto inteira.”
   - “CNPJ do cupom não é o do estabelecimento descrito.”
   - “Item não autorizado para esta pasta.”
   - “Valor do cupom (R$ 86,40) diferente do valor lançado (R$ 68,40).”
3. Clique em **Rejeitar** (tecla `R`). Com o cursor dentro da caixa, `Ctrl+Enter` também envia.
4. Confirme a pergunta, que repete o motivo. Se a caixa estiver vazia, o campo fica inválido e o foco volta para ele. Espaços em branco não contam como parecer.
5. A despesa sai da fila de pendentes e fica **Rejeitado**, com o parecer visível no cartão. O solicitante lê o mesmo texto em **Minhas Despesas** e pode corrigir e reenviar.

Não use “não” ou “errado” sozinhos. O parecer é o recado que chega no campo, muitas vezes à noite e com pressa.

---

## 7. Liquidar o PIX no Banco Cora PJ (RF07)

A liquidação junta o internet banking e o SIG-Reembolso. A ordem importa: primeiro o PIX, depois o anexo.

1. No Cora PJ, na conta do Grupo Escoteiro Caramuru, faça o PIX para a **Chave PIX** exibida no cartão ou no modal. O valor é o da despesa aprovada. Guarde o comprovante em PDF ou foto (JPEG, PNG ou WEBP).
2. No SIG-Reembolso, filtre **Aprovadas (pagar PIX)**.
3. Abra **Conferir nota** e confira de novo valor e chave antes de anexar.
4. No painel direito, em **Comprovante bancário Cora PJ**, escolha o arquivo.
5. Clique em **Registrar pagamento**.
6. A mensagem verde informa que a despesa foi liquidada como **Pago**. O cartão muda para **Pago**. No modal, a aba **Comprovante de pagamento** passa a abrir o arquivo do Cora, ao lado da NF.

Sem arquivo, o botão não conclui a liquidação. Despesa ainda **Aguardando decisão** não mostra esse formulário: aprove antes.

Se a despesa for sua, o aviso **Esta despesa é sua. Outro tesoureiro precisa decidir.** substitui os botões. Peça ao outro membro da Tesouraria para liquidar. Isso vale também para aprovar e reprovar (RN03).

O comprovante do Cora é a conciliação de cada lançamento. O fechamento do conjunto está na seção seguinte.

---

## 8. Prestação de contas: balancete e CSV (RF08)

No menu, clique em **Balancete**. A página se chama **Prestação de Contas** (`/relatorios/balancete/`).

### 8.1 Ler o balancete sintético

O balancete soma as despesas por pasta e por categoria. Dois cartões no topo mostram o **total em reais** e a **quantidade**. A tabela **Gastos por pasta e categoria** traz sigla, nome, categoria, quantidade e total.

O filtro **Status** começa em **Comprometidos (padrão)**. Comprometido aqui é o que já sensibiliza o teto:

- **Enviado para triagem** (ainda sem parecer);
- **Aprovado** (parecer dado, PIX pendente);
- **Pago**.

Rascunho, rejeitada e cancelada ficam de fora, para o número bater com o saldo da coordenação. Se precisar de um único estado, escolha-o na lista e clique em **Filtrar**. Coordenação e categoria funcionam do mesmo modo. **Todas** em coordenação mostra as 15 pastas ativas para Tesoureiro e Administrador.

### 8.2 Baixar a planilha CSV

1. Ajuste os filtros na tela. A exportação usa exatamente esses filtros.
2. Clique em **Exportar CSV**, no canto superior direito.
3. O navegador baixa `prestacao_contas_ag7.csv`.

Como abrir no Excel em português:

- O arquivo vem em **UTF-8 com BOM**, para acento não virar símbolo estranho.
- As colunas são separadas por **ponto e vírgula**.
- O valor usa **vírgula decimal** (`186,40`), sem ponto de milhar.
- Cada linha é uma despesa. As colunas são: número, data, sigla, coordenação, código e nome da categoria, código e nome do status, título, solicitante, tipo de acerto, forma de pagamento na ponta e valor.

No fechamento, compare a soma da coluna de valor (status **Pago**) com o extrato de PIX do Cora no mesmo período. Divergência de um lançamento se resolve abrindo a despesa em **Auditoria de Notas**, filtro **Pagas**, e conferindo a aba **Comprovante de pagamento**.

---

## 9. Roteiro de capacitação

Duração sugerida: 45 minutos, em dupla, no computador da Secretaria. Uma pessoa opera, a outra confere o extrato. Troquem na segunda passagem.

Pré-requisito: sistema no ar, com as contas da [seção 1](#1-para-quem-é-este-treinamento). Peça a um colega, logado como `coord_cozinha`, que envie duas despesas da pasta ALIM com foto legível: uma dentro do saldo e outra de propósito acima do teto, se a pasta de treino ainda tiver folga pequena. Se não houver envio novo, use as despesas de demonstração já carregadas.

| Passo | Quem opera | O que fazer | Pronto quando |
| :--- | :--- | :--- | :--- |
| 1 | Tesoureiro | Entrar com `tesoureiro` e abrir **Auditoria de Notas**. | O menu mostra o papel Tesoureiro e a fila abre. |
| 2 | Tesoureiro | Filtrar **Aguardando decisão**. Abrir **Conferir nota**, ampliar o total com zoom e girar se a foto estiver deitada. | O valor do cupom foi lido em voz alta e confere com o valor do painel. |
| 3 | Tesoureiro | Aprovar a nota regular e confirmar. | Mensagem verde e cartão **Aprovado**. |
| 4 | Tesoureiro | Na nota com **ESTOURO DE TETO**, decidir em voz alta se autoriza. Aprovar só se a dupla concordar; senão, reprovar. | A faixa vermelha foi discutida antes do clique. |
| 5 | Tesoureiro | Reprovar outra nota com a caixa vazia. | O sistema não aceita. |
| 6 | Tesoureiro | Reprovar de novo com o parecer “Cupom sem o valor total. Reenvie a foto inteira.” | Cartão **Rejeitado** mostra o parecer. |
| 7 | Tesoureiro | Simular o PIX no Cora (ou usar um PDF de comprovante de treino) e **Registrar pagamento** na despesa aprovada. | Cartão **Pago** e aba **Comprovante de pagamento** abre o arquivo. |
| 8 | Tesoureiro | Abrir **Balancete**, deixar **Comprometidos**, clicar em **Exportar CSV** e abrir a planilha. | Colunas separadas, acentos corretos e o valor pago aparece na linha da despesa. |
| 9 | Administrador | **Sair**, entrar com `admin` e observar a abertura em `/admin/`. Em seguida abrir **Auditoria de Notas**. | A Diretoria vê a diferença entre cadastro e auditoria. |
| 10 | Dupla | **Sair** ao terminar. | A tela volta para **Entrar**. |

Quem for treinar a própria despesa deve ver o aviso **Solicitação própria** e passar o mouse para o colega concluir o passo. Esse é o exercício da segregação de funções.

---

## 10. Dúvidas frequentes

**Aprovei sem querer.** Valor, pasta e nota fiscal já ficaram travados. Não apague o lançamento. Se o PIX ainda não saiu, alinhe com a Diretoria antes de liquidar. O histórico da transição fica gravado com o seu usuário.

**O botão Aprovar não aparece.** A despesa não está **Aguardando decisão**, ou é uma solicitação sua. Filtro **Aguardando decisão** e o aviso **Solicitação própria** esclarecem qual dos dois casos é.

**Rejeitar não envia.** O motivo está vazio ou só tem espaços. Escreva o parecer e confirme a pergunta do navegador. Cancelar a pergunta também interrompe.

**O CSV abre tudo numa coluna só.** O Excel não usou o ponto e vírgula. Abra pelo menu **Dados → De Texto/CSV** e escolha o separador **ponto e vírgula** e a origem **65001: Unicode (UTF-8)**.

**O balancete não bate com o extrato do banco.** O padrão inclui também o que está **enviado** e **aprovado**, ainda sem PIX. Para cruzar com o Cora, filtre o status **Pago / Liquidado** antes de exportar.

**O coordenador pergunta por que a nota voltou.** O texto está no parecer. Se ficou genérico, oriente a equipe a reenviar com o motivo que este manual pede na [seção 6](#6-reprovar-com-parecer-obrigatório-rn04).

---

## 11. Referências

- [Item 3.j — Manual de operação do voluntário de campo](3j_manual_operacao.md)
- [Item 3.h — Documentação técnica e execução do sistema](3h_documentacao_sistema.md)
- [Regras de negócio RN01 a RN06](../requisitos/regras_de_negocio.md)
- [Guia de login e papéis](guia-login-rbac.md)
- Tela de auditoria: `src/templates/despesas/painel_triagem.html`
- Balancete e CSV: `src/apps/relatorios/`
