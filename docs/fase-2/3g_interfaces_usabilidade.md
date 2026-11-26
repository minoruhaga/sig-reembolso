# Item 3.g — Definição das interfaces do sistema com base na usabilidade

**Projeto:** SIG-Reembolso (Acampamento Geral VII — Grupo Escoteiro Caramuru)
**Disciplina:** Laboratório de Engenharia de Software (LES) — FATEC-SP
**Item do edital:** 3.g — Definição das interfaces do sistema (com base na usabilidade e com justificativa)
**Responsável:** Ricardo Sakugawa (`@ricardosakugawa`) — [Issue #16](https://github.com/minoruhaga/sig-reembolso/issues/16)
**Versão:** 1.0 — 25/11/2026

---

## Sumário

1. [Objetivo e escopo](#1-objetivo-e-escopo)
2. [Contexto de uso](#2-contexto-de-uso)
3. [Critérios de usabilidade adotados](#3-critérios-de-usabilidade-adotados)
4. [Mapa das interfaces](#4-mapa-das-interfaces)
5. [Interface mobile do voluntário: lançamento de despesa](#5-interface-mobile-do-voluntário-lançamento-de-despesa)
6. [Painel desktop da Tesouraria: auditoria de notas](#6-painel-desktop-da-tesouraria-auditoria-de-notas)
7. [Demais interfaces](#7-demais-interfaces)
8. [Desempenho em conexão móvel e Starlink](#8-desempenho-em-conexão-móvel-e-starlink)
9. [Mapeamento das heurísticas de Nielsen](#9-mapeamento-das-heurísticas-de-nielsen)
10. [Limitações e validações pendentes](#10-limitações-e-validações-pendentes)
11. [Referências](#11-referências)

---

## 1. Objetivo e escopo

Este documento define as interfaces do SIG-Reembolso e justifica cada decisão de projeto com base em critérios de usabilidade, ergonomia e acessibilidade. As decisões descritas aqui estão implementadas no código da branch `dev` e foram entregues nas Issues [#8](https://github.com/minoruhaga/sig-reembolso/issues/8) (tela mobile com câmera nativa) e [#13](https://github.com/minoruhaga/sig-reembolso/issues/13) (painel de auditoria da Tesouraria).

O documento cobre:

- o contexto físico e técnico em que o sistema é usado no Campo Escola de Juquitiba/SP;
- as duas interfaces centrais do sistema, a tela mobile de lançamento e o painel desktop da Tesouraria, com as justificativas de cada decisão;
- as telas de apoio (login, painel operacional, saldos, minhas despesas e prestação de contas);
- o mapeamento das dez heurísticas de Nielsen nas telas do sistema.

Os requisitos citados (RF, RNF e RN) estão em [`docs/requisitos/`](../requisitos/).

---

## 2. Contexto de uso

### 2.1 Ambiente físico

O AG VII dura 7 dias no Campo Escola de Juquitiba/SP, em área de serra e Mata Atlântica. Cerca de 100 voluntários adultos fazem compras de emergência nas cidades vizinhas: alimentos perecíveis para a cozinha, remédios na farmácia de plantão, conexões hidráulicas e combustível para os geradores ([documento descritivo, seção 1](../referencias/documento_descritivo_sig_reembolso.md)).

Esse ambiente impõe condições que guiaram o projeto das telas:

| Condição | Efeito sobre o uso | Resposta na interface |
|---|---|---|
| Luz solar direta sobre a tela do celular | Cores claras e cinzas de baixo contraste desaparecem | Paleta preto sobre branco, contraste mínimo de 5,7:1 na tela de campo (seção 5.3) |
| Chuva, mãos molhadas, luvas e cansaço físico | Toques imprecisos | Alvos de toque de 56 px de altura e botão de câmera de 120 px (seção 5.4) |
| Cupom de papel térmico que amassa, molha ou se perde no bolso | Perda do comprovante, problema central do fluxo antigo | Foto da NF ou recibo no momento da compra, em 2 toques (seção 5.2) |
| Sem cobertura 4G no campo; internet só pela antena Starlink, com Wi-Fi restrito à Secretaria e à Tesouraria | Envio pode acontecer depois, em rede ruim ou compartilhada | Fotos reduzidas para até 350 KB, prévia de saldo com resposta de menos de 1 KB e rascunho para enviar depois (seção 8) |
| Aparelhos pessoais (BYOD): Android 10+ e iOS 15+, telas de 360 px a 430 px | Grande variação de tamanho e navegador | Layout desenhado primeiro para 360 px; tela de campo verificada em 360, 390 e 430 px e painel de auditoria em 460, 800 e 1280 px (seção 10.1) |

### 2.2 Perfis de usuário (personas)

As personas abaixo são fictícias. Os nomes coincidem com os usuários de demonstração do sistema (`popular_dados_demo`) e os perfis vêm das entrevistas e do quadro de voluntários do documento descritivo (seções 1.f e 3.c).

**Mariana, coordenadora da Alimentação (papel Coordenador).** Coordena a brigada de 22 voluntários da cozinha. Sai do campo para comprar verduras e temperos, paga do próprio bolso via PIX e precisa ser reembolsada. Usa o próprio celular Android, quase sempre com pressa e com as mãos ocupadas. Não conhece os códigos das regras de negócio (RN01 a RN06) e não quer saber de "triagem" ou "soft-block": quer saber se a compra cabe na verba da cozinha e o que falta para mandar o pedido.

**Carlos, tesoureiro (papel Tesoureiro).** Um dos 4 voluntários da Tesouraria, que opera o sistema no notebook dentro da Secretaria, onde há Wi-Fi da Starlink. Confere dezenas de notas por dia, lê CNPJ, valor e data em cupons fotografados de qualquer jeito (tortos, de lado, com pouca luz) e precisa aprovar, rejeitar com motivo ou registrar o PIX de reembolso sem trocar de tela a cada despesa.

**Diretoria do AG VII (papel Administrador Geral).** Ajusta tetos orçamentários e cadastros no Django Admin e acompanha saldos e a prestação de contas. Não audita notas fiscais: por decisão do cliente, a conferência de comprovantes é exclusiva da Tesouraria (seção 6.1).

---

## 3. Critérios de usabilidade adotados

| Critério | Fonte | Como foi aplicado |
|---|---|---|
| Eficácia, eficiência e satisfação em um contexto de uso definido | ISO 9241-11:2018 | Cada tela foi desenhada para uma persona e um ambiente da seção 2, e não para um usuário genérico |
| Dez heurísticas de usabilidade | Nielsen (1994) | Mapeadas tela a tela na seção 9 |
| Contraste mínimo de 4,5:1 para texto (nível AA) e 7:1 (nível AAA) | WCAG 2.1, critérios 1.4.3 e 1.4.6 | Paleta da tela de campo calculada com a fórmula de luminância relativa da WCAG (seção 5.3) |
| Alvo de toque de pelo menos 44 × 44 px | WCAG 2.1, critério 2.5.5 | Todos os controles da tela de campo têm 44 px ou mais e os campos têm 56 px (seção 5.4); nas telas de apoio, botões e campos passam a 44 px em telas abaixo de 768 px (seção 10.1) |
| Foco visível ao navegar pelo teclado | WCAG 2.1, critério 2.4.7 | Anel de foco amarelo de 3 px com contorno preto |
| Respeito a quem pede menos movimento | WCAG 2.1, critério 2.3.3 | Animações do botão de câmera e dos botões de ação desligadas com `prefers-reduced-motion` |
| Mobile-first | RNF01 | A tela de campo foi desenhada para 360 px e só depois ampliada para tablet e desktop |
| Captura em menos de 3 toques | RNF01 | Câmera aberta em 2 toques depois do login (seção 5.2) |
| Respostas abaixo de 1,5 s | RNF05 | Telas renderizadas no servidor, sem etapa de build e com poucas requisições (seção 8) |

---

## 4. Mapa das interfaces

| Tela | Rota | Quem acessa | Dispositivo principal |
|---|---|---|---|
| Login | `/usuarios/login/` | Todos | Celular e desktop |
| Painel operacional | `/` | Todos (cada papel vê seu recorte) | Celular e desktop |
| **Nova despesa / editar despesa** | `/despesas/nova/`, `/despesas/<id>/editar/` | Coordenador, Tesoureiro | **Celular** |
| Minhas despesas | `/despesas/minhas/` | Todos | Celular |
| **Auditoria de notas** | `/despesas/triagem/` | **Somente Tesouraria** | **Desktop** |
| Saldos e tetos | `/financeiro/saldos/` | Todos (ajuste de teto só Tesouraria e Admin) | Desktop |
| Prestação de contas | `/relatorios/balancete/` | Todos (recorte por papel) | Desktop |

O menu superior mostra só o que o papel pode abrir. O item "Auditoria de Notas" aparece apenas para a Tesouraria e o item "Administração", para Tesouraria e Administrador Geral. Assim nenhum usuário vê um link que o levaria a uma página de acesso negado.

---

## 5. Interface mobile do voluntário: lançamento de despesa

Arquivo: `src/templates/despesas/despesa_form.html`. Requisitos: RF04, RF05, RF03, RNF01, RNF02.

### 5.1 Estrutura da tela

A tela foi reescrita na Issue #8 porque o formulário anterior (Issue #7) usava o layout padrão do Bootstrap, pensado para desktop. A ordem dos campos segue a sequência real de uma compra no balcão:

1. **Foto da NF ou recibo**, logo no topo, enquanto o cupom ainda está na mão;
2. **Coordenação**, já preenchida com a pasta do usuário;
3. **Valor do gasto**, em fonte grande;
4. **Termômetro da verba**, que mostra o efeito da compra no saldo;
5. **O que foi comprado**;
6. **Data do gasto** e **Pago com**, lado a lado, com a data de hoje já preenchida;
7. **Categoria** e **Tipo de acerto**, um em cada linha no celular;
8. **Observações**, recolhidas por padrão porque são opcionais.

Os botões "Salvar rascunho" e "Enviar para a tesouraria" ficam fixos no rodapé da tela, sempre ao alcance do polegar, e respeitam a área segura de aparelhos com barra de gestos (`env(safe-area-inset-bottom)`).

### 5.2 Captura da NF ou recibo com a câmera nativa

| Decisão | Justificativa |
|---|---|
| O botão amarelo "Tirar foto da NF ou recibo" é o `<label>` de um `<input type="file" capture="environment">` | Um toque abre direto a câmera traseira do aparelho, sem passar pela galeria. Não há aplicativo para instalar: funciona no navegador de qualquer Android 10+ ou iOS 15+. |
| Caminho até a câmera: login → botão "Nova Despesa (Campo)" do painel → botão amarelo | São 2 toques depois do login, abaixo do limite de 3 toques do RNF01. |
| Link "Anexar PDF ou foto da galeria" logo abaixo | Cobre a NF eletrônica recebida em PDF e a foto tirada antes. Esse link remove o `capture` só naquele toque, então a câmera continua sendo o caminho padrão. |
| Miniatura e tamanho do arquivo aparecem depois da escolha | O voluntário confere na hora se a foto saiu legível e se pegou o cupom certo (visibilidade do estado do sistema). |
| Texto do botão em linguagem do dia a dia: "NF ou recibo" e "gasto" | Na revisão do PR #41 a equipe trocou "cupom" e "Fotografar" por termos mais diretos, porque nem toda compra gera cupom fiscal: frete e serviços avulsos geram recibo. |
| Aviso "A foto é reduzida antes do envio para gastar pouca internet" | Explica por que a foto pode demorar um pouco a subir e tranquiliza quem está numa rede fraca. |

### 5.3 Alto contraste para uso sob sol

A tela de campo não usa o tema claro do Bootstrap. A paleta foi definida no próprio template, e as razões de contraste abaixo foram calculadas com a fórmula de luminância relativa da WCAG 2.1:

| Combinação | Onde aparece | Contraste | Nível WCAG |
|---|---|---|---|
| Preto `#000000` sobre branco `#FFFFFF` | Texto, rótulos e bordas | 21,0:1 | AAA |
| Cinza `#3A3A3A` sobre branco | Textos de apoio e ajuda | 11,4:1 | AAA |
| Preto sobre amarelo de sinalização `#FFD400` | Botão de câmera | 14,7:1 | AAA |
| Branco sobre verde `#0B5D3B` | Botão "Enviar para a tesouraria" e barra do termômetro | 7,9:1 | AAA |
| Vermelho `#B3261E` sobre branco | Mensagens de erro | 6,5:1 | AA |
| Vermelho `#B3261E` sobre rosa `#FDECEA` | Termômetro em estouro e avisos de erro | 5,7:1 | AA |

Para comparação, o cinza `text-muted` padrão do Bootstrap (`#6C757D`) dá 4,7:1 sobre branco, o que passa no nível AA mas fica difícil de ler com o sol batendo na tela. Por isso a tela de campo não usa esse cinza.

Outras decisões ligadas à leitura sob luz forte:

- **Bordas de 2 px pretas** em todos os campos, para que o contorno de cada campo continue visível mesmo quando o reflexo apaga o fundo;
- **Fonte Atkinson Hyperlegible**, desenhada pelo Braille Institute para leitores com baixa visão: ela diferencia caracteres que costumam se confundir (como `I`, `l` e `1`, ou `0` e `O`), o que importa ao conferir valores e CNPJ. Se a fonte não carregar, entra a fonte do sistema;
- **Texto base de 18 px** (1,125 rem) e valor do gasto em 36 px (2,25 rem) com algarismos de largura fixa (`tabular-nums`), para os dígitos não "dançarem" enquanto o valor é digitado;
- **O estado do termômetro não depende só da cor**: quando a compra passa do teto, além do vermelho aparece o texto "Passa do teto em R$ X" e a nota "Você ainda pode enviar. A tesouraria decide se libera a verba extra." Se a coordenação já estava acima do teto antes da compra, o termômetro abre em vermelho com "A verba já passou do teto em R$ X." e a mesma nota. Quem não distingue vermelho e verde recebe a mesma informação.

### 5.4 Ergonomia de toque

| Elemento | Tamanho | Referência |
|---|---|---|
| Botão de câmera | 120 px de altura, largura total da tela | Maior alvo da tela, porque é a ação principal |
| Campos de texto e seleção | 56 px de altura | Acima dos 44 px do critério 2.5.5 da WCAG 2.1 |
| Botões do rodapé | 56 px de altura | Idem |
| Links secundários ("Minhas despesas", "Anexar PDF...") | 44 px de altura | Mínimo do critério 2.5.5 |
| Campo de valor | 68 px de altura | Facilita tocar no campo e ler o número |

O campo de valor abre o **teclado numérico** do celular (`inputmode="numeric"`) e usa máscara de centavos: o voluntário digita só números e o campo formata sozinho (`1000` vira `10,00`; `125040` vira `1.250,40`). Não é preciso procurar a vírgula num teclado pequeno, e o valor chega ao servidor em `Decimal`, sem erro de arredondamento.

### 5.5 Termômetro da verba e retorno imediato

O termômetro mostra, abaixo do campo de valor, quanto da verba da coordenação já foi usado e quanto esta compra vai ocupar:

- barra verde com a parte já comprometida e barra amarela listrada com a compra atual;
- frase de resultado: "Saldo livre: R$ X", "Depois desta compra sobram R$ Y" ou "Passa do teto em R$ Z".

A conta é feita no servidor pelo serviço `simular_impacto_orcamentario`, com a mesma regra de soft-block da submissão (RN02). Assim, o número que a voluntária vê antes de enviar é o mesmo que a Tesouraria vai receber. O navegador só pede a prévia 450 ms depois da última tecla, para não disparar uma requisição a cada dígito. Sem JavaScript, o termômetro aparece calculado no carregamento da página.

O estouro de teto não bloqueia o envio. Essa é a regra RN02 (soft-block): numa emergência a compra precisa acontecer, e a decisão de liberar verba extra é da Tesouraria. A tela informa isso em vez de impedir.

### 5.6 Prevenção de erros e mensagens

| Situação | Comportamento | Justificativa |
|---|---|---|
| Envio sem foto ou PDF | Mensagem "Anexe a foto ou o PDF da NF ou recibo para enviar a despesa à tesouraria." junto ao botão de câmera, que fica com borda vermelha | Diz o que falta e onde resolver (RN01) |
| Valor zero | "Informe um valor maior que R$ 0,00." | Linguagem direta, sem jargão |
| Sem foto no momento da compra | Botão "Salvar rascunho" grava a despesa sem anexo; a mensagem diz "Rascunho #N salvo. Você pode voltar depois para anexar a foto da NF ou recibo e enviar." | Permite registrar o gasto na hora e completar depois (RF05) |
| Despesa devolvida pela Tesouraria | Aviso "A tesouraria devolveu esta despesa" no topo da tela de edição, com o motivo escrito pelo tesoureiro | O voluntário sabe exatamente o que corrigir (RN04) |
| Despesa já aprovada ou paga | Edição bloqueada com a mensagem "Despesas no estado 'X' não podem mais ser alteradas." | Evita alteração depois da decisão (RN05) |

As mensagens exibidas ao usuário não mostram códigos de regra. Na Issue #8, textos como "RN01: O comprovante fiscal é estritamente obrigatório..." foram trocados por frases que dizem o que aconteceu e o que fazer. Os códigos continuam nas docstrings do código, onde servem à equipe de desenvolvimento.

---

## 6. Painel desktop da Tesouraria: auditoria de notas

Arquivo: `src/templates/despesas/painel_triagem.html`. Requisitos: RF06, RF07, RN02, RN03, RN04.

### 6.1 Acesso restrito à auditoria

O painel é exclusivo da Tesouraria. O Administrador Geral, que tinha acesso na versão da Issue #11, passou a receber "acesso negado", e o item de menu deixou de aparecer para ele. A conferência de notas fiscais é a função de auditoria das contas do AG VII, e separar quem audita de quem administra cadastros reduz o número de pessoas que veem documentos fiscais e dados de PIX de todos os voluntários.

### 6.2 Cards com badges

A tabela da versão anterior foi trocada por uma grade de cards (3 colunas em telas largas, 2 em médias e 1 em pequenas). Cada card traz:

- miniatura da NF ou recibo (ou ícone de PDF), que já abre a conferência ao ser clicada;
- badges de situação: "Aguardando decisão" (amarelo), "Aprovado" (azul), "Pago" (verde), "Rejeitado" (vermelho);
- badge vermelho "ESTOURO DE TETO (+R$ X)" e borda vermelha no card quando a compra passou do teto (RN02);
- badge "Solicitação própria" quando a despesa é do tesoureiro logado (RN03);
- título, solicitante, data, chave PIX e valor em destaque.

A miniatura deixa o tesoureiro ver de relance se a foto está legível antes de abrir a conferência. A fila vem ordenada com os estouros de teto primeiro, porque são os casos que pedem decisão sobre verba extra.

No topo, três contadores resumem a fila ("Aguardando decisão", "Aprovadas, aguardando PIX" e "Acima do teto"), e os filtros por situação e coordenação permitem trabalhar uma pasta de cada vez.

### 6.3 Modal de conferência em tela cheia com zoom

| Recurso | Justificativa |
|---|---|
| Modal em tela cheia, com a nota à esquerda e os dados e ações numa coluna lateral de 352 px | A nota ocupa quase toda a tela do notebook e os dados que precisam ser comparados com ela (valor, data, solicitante, PIX) ficam ao lado, sem rolagem |
| Zoom por botões (+, −, "Ajustar", "1:1"), pela roda do mouse e por duplo clique | A chave de acesso e o CNPJ de um cupom térmico são impressos em fonte pequena. O zoom da roda e do duplo clique é centrado no ponto do cursor, então o tesoureiro aproxima exatamente a linha que quer ler. Nos testes, um texto ilegível em 25% ficou legível em 227% |
| Arrastar a imagem com o mouse | Percorre um cupom comprido sem sair do zoom |
| Girar 90° | Voluntários fotografam o cupom de lado com frequência |
| Abas "NF ou recibo" e "Comprovante de pagamento" | Depois do PIX, o tesoureiro confere no mesmo lugar a nota e o comprovante bancário Cora PJ (RF07) |
| PDF aberto no leitor embutido do navegador | DANFEs e notas eletrônicas chegam em PDF e mantêm o zoom nativo do leitor |
| Botão "Abrir original" | Abre o arquivo numa aba nova, para quem prefere imprimir ou usar dois monitores |
| Botões ‹ › e contador "3 de 8" no cabeçalho | Passa à próxima despesa da fila sem fechar o modal |

Os arquivos chegam ao modal por uma rota protegida (`/despesas/<id>/comprovante/<nota|pagamento>/`), que só entrega o documento para a Tesouraria. Essa rota também permite que o PDF seja exibido dentro do próprio sistema, o que o bloqueio padrão contra clickjacking (`X-Frame-Options: DENY`) impedia. O restante do site continua com o bloqueio.

Em telas abaixo de 992 px, a nota fica no topo (70% da altura da tela) e os dados e ações descem para baixo dela, sem sobreposição. Esse ajuste foi feito depois de um teste manual em que a nota invadia a coluna de ações em telas estreitas.

### 6.4 Ações rápidas e atalhos de teclado

As ações ficam na coluna lateral do modal, ao lado da nota:

- **Aprovar**, com confirmação "Aprovar a despesa #N de R$ X?";
- **Rejeitar**, com campo de motivo obrigatório (RN04) e confirmação que repete o motivo;
- **Registrar pagamento**, com anexo do comprovante Cora PJ, para despesas aprovadas.

| Tecla | Ação |
|---|---|
| `A` | Aprova (pede confirmação) |
| `R` | Rejeita se o motivo já foi escrito (pede confirmação); com o campo vazio, leva o cursor até ele |
| `Ctrl` + `Enter` | Rejeita com o cursor ainda dentro do campo de motivo |
| `←` / `→` | Despesa anterior / próxima |
| `+` / `−` | Aumenta / diminui o zoom |
| `0` / `1` | Ajusta a nota à tela / mostra em tamanho real |
| `G` | Gira 90° |
| `Esc` | Fecha o modal |

Os atalhos atendem ao uso repetitivo: um tesoureiro que confere dezenas de notas por sessão trabalha com uma mão no mouse para o zoom e a outra no teclado para decidir e avançar. Os atalhos ficam listados no rodapé da coluna lateral e as letras aparecem nos próprios botões ("Aprovar `A`", "Rejeitar `R`"), então quem não sabe que eles existem descobre na primeira vez que abre o modal.

Os atalhos não funcionam enquanto o cursor está num campo de texto, para que a letra "r" digitada no motivo não dispare a rejeição. Toda decisão pede confirmação, porque aprovar ou rejeitar muda o saldo da coordenação e grava uma linha na trilha de auditoria (RN06).

### 6.5 Segregação de funções na interface

Quando a despesa é do próprio tesoureiro, o card mostra "Solicitação própria", os botões de decisão somem do modal e aparece a frase "Esta despesa é sua. Outro tesoureiro precisa decidir." O impedimento é calculado no servidor pela regra RN03 (`verificar_impedimento_rn03`). A interface apenas esconde os botões e explica o motivo, e as rotas de aprovação e rejeição recusam a operação mesmo que alguém tente chamá-las diretamente.

---

## 7. Demais interfaces

| Tela | Decisões de usabilidade |
|---|---|
| **Login** (`/usuarios/login/`) | Cartão centralizado com dois campos e um botão. Credenciais inválidas mantêm o usuário na mesma tela com a mensagem de erro. Depois do login, cada papel cai na tela que mais usa: Administrador Geral no Django Admin, os demais no painel operacional. |
| **Painel operacional** (`/`) | Três totais no topo (orçado, comprometido e saldo livre), termômetro por coordenação com barras de progresso que mudam de cor (verde até 60%, amarelo até 90% e vermelho acima) e a lista das últimas despesas. O coordenador vê só a própria pasta; Tesouraria e Diretoria veem as 15. O botão verde "Nova Despesa (Campo)", com ícone de câmera, é o primeiro toque do caminho de 2 toques até a câmera. |
| **Minhas despesas** (`/despesas/minhas/`) | Lista do próprio voluntário com badges de situação, aviso de estouro e ações por linha (editar, enviar rascunho). Quando a lista está vazia, mostra uma mensagem e o botão para lançar a primeira despesa. |
| **Saldos e tetos** (`/financeiro/saldos/`) | Tabela por coordenação com teto, valores em triagem, aprovados, pagos, saldo livre e barra de consumo. O campo "Ajustar Teto" só aparece para quem pode alterar (Tesouraria e Administrador Geral). |
| **Prestação de contas** (`/relatorios/balancete/`) | Filtros por situação, coordenação e categoria, totais no topo e exportação em CSV para o fechamento contábil (RF08). |

Todas essas telas usam o mesmo cabeçalho verde, os mesmos ícones (Bootstrap Icons) e a mesma formatação de moeda (`R$ 1.250,40`), o que mantém a consistência entre elas.

---

## 8. Desempenho em conexão móvel e Starlink

O campo não tem 4G. A internet vem de uma única antena Starlink, compartilhada pela base administrativa. As decisões abaixo reduzem o volume de dados e o número de requisições:

| Decisão | Efeito |
|---|---|
| Fotos reduzidas no servidor pelo serviço `otimizar_comprovante_fiscal` (Pillow): largura máxima de 1920 px e qualidade JPEG ajustada até o arquivo caber em 350 KB | Uma foto de celular de 3 a 5 MB vira um arquivo de até 350 KB, ainda legível para valor e CNPJ (RNF02). Arquivos acima de 10 MB são recusados com mensagem |
| Prévia do termômetro com resposta JSON de menos de 1 KB e pedida só depois de 450 ms sem digitação | Uma requisição pequena por pausa, em vez de uma por tecla |
| Telas renderizadas no servidor (Django templates), sem framework JavaScript nem etapa de build | A página chega pronta e funciona com JavaScript desligado ou carregado pela metade |
| CSS e JavaScript da tela de campo escritos no próprio template | Uma requisição a menos por recurso; não há pacote JavaScript extra para baixar |
| Fonte carregada com `display=swap` | O texto aparece imediatamente com a fonte do sistema e troca quando a Atkinson Hyperlegible chega; se a rede cair, a tela continua legível |
| "Salvar rascunho" sem anexo | O voluntário registra o gasto no balcão e envia a foto quando estiver na área do Wi-Fi |
| Miniaturas da Tesouraria com `loading="lazy"` | O navegador só baixa as imagens dos cards que aparecem na tela |

---

## 9. Mapeamento das heurísticas de Nielsen

| # | Heurística | Onde é aplicada | Evidência no sistema |
|---|---|---|---|
| 1 | Visibilidade do estado do sistema | Tela de campo, painel de auditoria, minhas despesas | Termômetro atualizado enquanto o valor é digitado; miniatura e tamanho do arquivo depois da foto; badges de situação nos cards e na lista; contador "3 de 8" e nível de zoom ("227%") no modal |
| 2 | Correspondência entre o sistema e o mundo real | Tela de campo | Rótulos na linguagem do voluntário: "NF ou recibo", "Valor do gasto", "O que foi comprado", "Pago com", "Tipo de acerto"; ordem dos campos igual à sequência da compra; valores no formato `R$ 1.250,40` |
| 3 | Controle e liberdade do usuário | Tela de campo, painel de auditoria | "Salvar rascunho" para terminar depois; edição de rascunhos e de despesas devolvidas; link "Anexar PDF ou foto da galeria" como alternativa à câmera; confirmação com opção de cancelar antes de aprovar ou rejeitar; `Esc` fecha o modal |
| 4 | Consistência e padrões | Todas as telas | Mesmas cores para cada situação em todas as telas (amarelo aguardando decisão, azul aprovado, verde pago, vermelho rejeitado ou estouro; o texto do badge "Enviado" ainda varia, ver seção 10); mesmo formato de moeda; mesmo cabeçalho e ícones; componentes do Bootstrap 5.3 que seguem convenções conhecidas de formulários e modais |
| 5 | Prevenção de erros | Tela de campo, painel de auditoria | Máscara de centavos que impede valores mal formatados; data e coordenação já preenchidas; envio bloqueado sem anexo (RN01); motivo obrigatório na rejeição (RN04); confirmação antes de decidir; atalhos desligados dentro de campos de texto; botões de decisão escondidos na própria solicitação (RN03) |
| 6 | Reconhecimento em vez de memorização | Painel de auditoria, tela de campo | Letras dos atalhos impressas nos botões e lista de atalhos no modal; dados da despesa ao lado da nota, sem precisar lembrar do card; coordenação do usuário já selecionada |
| 7 | Flexibilidade e eficiência de uso | Painel de auditoria | Atalhos de teclado para quem confere muitas notas; zoom por roda, duplo clique ou botões; navegação ‹ › entre despesas sem fechar o modal; filtros por situação e coordenação |
| 8 | Estética e design minimalista | Tela de campo | Uma ação principal por tela (botão amarelo da câmera); observações recolhidas por serem opcionais; sem elementos decorativos; o termômetro mostra uma frase de resultado em vez de uma tabela de valores |
| 9 | Ajudar o usuário a reconhecer, diagnosticar e recuperar-se de erros | Tela de campo, minhas despesas | Mensagens sem códigos internos que dizem o que fazer ("Anexe a foto ou o PDF da NF ou recibo..."); erro exibido junto ao campo; motivo da devolução no topo da despesa rejeitada |
| 10 | Ajuda e documentação | Tela de campo, painel de auditoria | Textos de ajuda junto aos controles ("A foto é reduzida antes do envio para gastar pouca internet"; dica de `Ctrl` + `Enter` no campo de motivo); manuais de operação (Item 3.j) e de treinamento (Item 3.k) |

---

## 10. Limitações e validações pendentes

### 10.1 Verificação nas larguras de celular (25/11/2026)

As telas foram abertas no navegador em modo dispositivo, com o usuário de demonstração `coord_cozinha`, nas duas larguras extremas do RNF01. Em cada tela foram medidos: rolagem horizontal da página, elementos que passam da borda, alvos de toque abaixo de 44 px, opções de seleção cortadas e placeholders cortados.

A primeira rodada encontrou três problemas:

| Tela | 360 px | 430 px |
|---|---|---|
| Nova despesa | Sem rolagem horizontal; todos os controles com 44 px ou mais; o nome da coordenação no seletor aparecia cortado ("ALIM - Alimentação e Cozinha Cent…"); com a pasta acima do teto, o termômetro mostrava "Saldo livre: R$ -3.166,97" em preto | Nada cortado; mesmo problema do saldo negativo |
| Painel operacional | Sem rolagem horizontal da página; as duas tabelas rolam para o lado dentro do próprio quadro (conteúdo de 784 px numa área de 288 px); botão "Nova Despesa (Campo)" com 38 px de altura; saldo negativo em verde no cartão "Saldo financeiro livre" | Mesmo comportamento, com área de 358 px |
| Minhas despesas | Sem rolagem horizontal da página; tabela rola dentro do quadro (755 px em 288 px); botão "Nova Despesa (Campo)" com 38 px | Mesmo comportamento |
| Saldos e tetos | Sem rolagem horizontal da página; tabela rola dentro do quadro (778 px em 288 px); botões "API JSON" e "Painel Geral" com 31 px | Mesmo comportamento |
| Prestação de contas | Sem rolagem horizontal da página; tabela rola dentro do quadro (461 px em 288 px); filtros e botão "Filtrar" com 38 px; "Exportar CSV" com 31 px | Mesmo comportamento |

Correções feitas em seguida, e conferidas de novo nas duas larguras:

- **Seletor de coordenação.** A opção mostra só o nome da pasta (sem o prefixo `"SIGLA - "`). Mesmo em pastas com nomes longos (como o caso de teste `"Alimentação e Cozinha Central"`, posteriormente simplificado para `"Alimentação"` na fixture oficial `coordenacoes_iniciais.json`), em 360 px o texto cabe nos 280 px úteis do campo. A sigla continua no cabeçalho do termômetro ("Verba da ALIM").
- **Saldo negativo.** O serviço `simular_impacto_orcamentario` passou a informar se a verba já estava acima do teto e em quanto. O termômetro abre em vermelho com "A verba já passou do teto em R$ 3.166,97." e a nota da tesouraria. No painel operacional, o cartão "Saldo financeiro livre" fica vermelho, com ícone de alerta e a legenda "Gastos acima do teto da sua coordenação", como já acontecia na tela de saldos.
- **Alvos de toque nas telas de apoio.** Abaixo de 768 px, botões (inclusive os pequenos), campos, seletores e o botão do menu passam a ter pelo menos 44 px de altura. Depois da correção, nenhum controle visível das cinco telas ficou abaixo de 44 px, em 360 ou em 430 px, e nenhuma ganhou rolagem horizontal.

As tabelas das telas de apoio continuam rolando para o lado dentro do próprio quadro, sem rolagem horizontal da página.

### 10.2 Pendências

- **Aparelhos reais.** As medições da seção 10.1 foram feitas no navegador em modo dispositivo, e os testes automatizados conferem a presença do `capture="environment"`. Falta testar a captura em celulares Android e iOS reais antes da homologação (Item 3.l). Alguns navegadores do iOS ignoram o `capture` e abrem o seletor completo; o fluxo continua funcionando, com um toque a mais.
- **Navegadores.** O painel de auditoria foi testado no Chromium. Safari e Firefox ainda não foram testados.
- **Teste com usuários.** As decisões partem das entrevistas e protótipos da fase de elicitação (documento descritivo, seção 3.c). Ainda não houve teste de usabilidade com tarefas cronometradas usando o sistema pronto; a homologação com a Coordenação do AG VII (Item 3.l) é a primeira oportunidade.
- **Telas de apoio.** Painel operacional, saldos e prestação de contas usam o tema padrão do Bootstrap, com o cinza `text-muted` de 4,7:1 (nível AA). Como essas telas são usadas sobretudo dentro da Secretaria, não receberam o tratamento de alto contraste da tela de campo.
- **Nome da situação "Enviado".** As cores são as mesmas em todas as telas, mas o texto do badge varia: "Em Triagem" no painel operacional e em "Minhas despesas", "Aguardando decisão" no painel de auditoria. Convém escolher um só nome.
- **Arquivos em `/media/`.** O painel de auditoria usa a rota protegida, mas "Minhas despesas" e o Django Admin ainda abrem os comprovantes pelo endereço público `/media/`.

---

## 11. Referências

- INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. **ISO 9241-11:2018**: Ergonomics of human-system interaction — Part 11: Usability: Definitions and concepts. Genebra: ISO, 2018.
- NIELSEN, Jakob. **10 Usability Heuristics for User Interface Design**. Nielsen Norman Group, 24 abr. 1994 (texto atualizado em 2020). Disponível em: <https://www.nngroup.com/articles/ten-usability-heuristics/>.
- WORLD WIDE WEB CONSORTIUM (W3C). **Web Content Accessibility Guidelines (WCAG) 2.1**. W3C Recommendation, 2018 (edição vigente de 6 maio 2025). Disponível em: <https://www.w3.org/TR/WCAG21/>.
- BRAILLE INSTITUTE OF AMERICA. **Atkinson Hyperlegible Font**. 2019. Disponível em: <https://www.brailleinstitute.org/freefont/>.
- Documentos do projeto: [documento descritivo](../referencias/documento_descritivo_sig_reembolso.md), [requisitos funcionais](../requisitos/requisitos_funcionais.md), [requisitos não funcionais](../requisitos/requisitos_nao_funcionais.md), [regras de negócio](../requisitos/regras_de_negocio.md) e [análise de decisão da tela mobile (Issue #8)](../../prompts/frontend/20261122-221903-tela-mobile-camera-termometro-v001.md).
