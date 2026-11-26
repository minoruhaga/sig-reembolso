# Item 3.h — Documentação do Sistema Desenvolvido

**Projeto:** SIG-Reembolso  
**Cliente / caso real:** Acampamento Geral VII — Grupo Escoteiro Caramuru  
**Disciplina:** Laboratório de Engenharia de Software (LES) — FATEC-SP (DTI) — 2º semestre de 2026  
**Artefato:** `docs/fase-2/3h_documentacao_sistema.md`  
**Repositório:** [github.com/minoruhaga/sig-reembolso](https://github.com/minoruhaga/sig-reembolso)  
**Responsável pelo documento:** Gustavo Minoru Haga (`@minoruhaga`)  
**Seção de segurança, autenticação e RBAC:** Marina (`@Mah-Rod`) — módulo `apps.usuarios` e apoio neste item  
**Data de referência:** 25/11/2026

---

## 1. Aderência ao roteiro do edital

O Item 3 do edital da disciplina pede, no **Item 3.h**, a documentação do sistema desenvolvido, cobrindo **programas-fonte** e **instruções de execução**. Este documento é o artefato formal dessa exigência. Cada seção abaixo responde a um ponto do roteiro:

| Exigência do Item 3.h | Onde está neste documento |
| :--- | :--- |
| Programas-fonte | [Seção 3](#3-programas-fonte) |
| Dependências | [Seção 4](#4-dependências-de-software) |
| Arquitetura técnica em Django 5 | [Seção 5](#5-arquitetura-técnica) |
| Módulos em `src/apps/` | [Seção 6](#6-módulos-de-domínio-srcapps) |
| Models relacionais | [Seção 7](#7-modelos-relacionais) |
| Segurança, autenticação e controle de acesso por papel (RBAC), com apoio de `@Mah-Rod` | [Seção 8](#8-segurança-autenticação-e-controle-de-acesso-rbac) |
| Onboarding e ambiente reproduzível (Nix/Flakes e Python virtualenv) | [Seção 9](#9-ambiente-reproduzível) |
| Instruções completas de execução | [Seção 10](#10-instruções-completas-de-execução) |

O manual de operação de campo (Item 3.j) e o manual de treinamento da Tesouraria (Item 3.k) descrevem o uso pedagógico das telas. Este Item 3.h descreve **o que o software é**, **de quais programas é feito** e **como colocá-lo para executar**.

---

## 2. Identificação do sistema

O SIG-Reembolso é uma aplicação web que registra compras operacionais das 15 coordenações do AG VII, comprime o comprovante fiscal no envio, aplica teto orçamentário com alerta de estouro (soft-block), tria a nota na Tesouraria e exporta a prestação de contas.

| Atributo | Valor |
| :--- | :--- |
| Linguagem | Python 3.12 |
| Framework | Django 5 (`Django>=5.0,<5.3`) |
| Banco de desenvolvimento e testes | SQLite (`src/db.sqlite3`) |
| Banco previsto para produção | PostgreSQL, via variáveis `POSTGRES_*` em `config.settings.prod` |
| Interface | Templates Django + Bootstrap 5.3.3 e Bootstrap Icons 1.11.3 (CDN) |
| Precisão monetária | `decimal.Decimal` e `DecimalField` (proibido `float` em valores em reais) |
| Orçamento modelado | R$ 193.320,00 nas 15 coordenações (`src/fixtures/coordenacoes_iniciais.json`) |
| Conta de liquidação | Banco Cora PJ (comprovante anexado na transição para `PAGO`) |

A pasta `src/` é a raiz do projeto Django. O arquivo `src/manage.py` define `DJANGO_SETTINGS_MODULE=config.settings.dev`. O pacote `config.settings` escolhe produção somente quando a variável `DJANGO_ENV` vale `prod`.

---

## 3. Programas-fonte

A árvore abaixo lista os programas que constituem o sistema executável. Arquivos `__init__.py` apenas marcam pacotes Python e foram omitidos.

### 3.1 Núcleo de configuração

| Programa | Responsabilidade |
| :--- | :--- |
| `src/manage.py` | Ponto de entrada da CLI: migrações, testes, carga de dados e `runserver`. |
| `src/config/urls.py` | Roteador central. Delega para `usuarios`, `financeiro`, `despesas` e `relatorios` e publica o dashboard em `/`. |
| `src/config/wsgi.py` | Aplicação WSGI para servidor de produção (`config.settings`). |
| `src/config/asgi.py` | Aplicação ASGI equivalente. |
| `src/config/settings/base.py` | Apps instalados, middleware, templates, estáticos, mídia, idioma `pt-br`, fuso `America/Sao_Paulo`, modelo de usuário e validadores de senha. |
| `src/config/settings/dev.py` | `DEBUG` configurável, `SECRET_KEY` com fallback de desenvolvimento e SQLite. |
| `src/config/settings/prod.py` | Exige `DJANGO_SECRET_KEY`, desliga `DEBUG`, aceita PostgreSQL e liga cookies seguros. |
| `src/config/settings/__init__.py` | Importa `prod` se `DJANGO_ENV=prod`; caso contrário, importa `dev`. |
| `src/requirements.txt` | Dependências Python do ambiente virtual. |
| `flake.nix` | Ambientes Nix `default`/`backend` e `quality`, pinados em Python 3.12. |
| `src/fixtures/coordenacoes_iniciais.json` | Carga das 15 coordenações e tetos do AG VII. |

### 3.2 `apps.core` — infraestrutura transversal

| Programa | Responsabilidade |
| :--- | :--- |
| `src/apps/core/views.py` | Dashboard autenticado, com recorte de coordenações e despesas conforme o papel. |
| `src/apps/core/services.py` | `otimizar_comprovante_fiscal`: valida extensão, rejeita arquivo corrompido, comprime imagem para menos de 350 KB (RNF02) e renomeia com UUID v4 (RNF04). PDF só é renomeado. |
| `src/apps/core/exceptions.py` | Exceções de domínio (comprovante obrigatório, transição inválida, imutabilidade, justificativa, permissão). |
| `src/apps/core/management/commands/popular_dados_demo.py` | Contas de demonstração e despesas de exemplo, de forma idempotente. |
| `src/apps/core/management/commands/carregar_dados_ag6_ag7.py` | Carga histórica AG VI / operacional AG VII (Issue #9). |
| `src/apps/core/tests.py` e `src/apps/core/test_carga_ag6_ag7.py` | Testes da compressão e da carga. |

### 3.3 `apps.usuarios` — identidade e RBAC (`@Mah-Rod`)

| Programa | Responsabilidade |
| :--- | :--- |
| `src/apps/usuarios/models.py` | `Usuario` (`AbstractUser`), papéis `COORDENADOR`, `TESOUREIRO`, `ADMIN` e `pode_acessar_painel_auditoria`. |
| `src/apps/usuarios/services.py` | `url_pos_login`, `coordenacoes_visiveis`, `despesas_visiveis`, `usuario_pode_acessar_admin` e `usuario_pode_acessar_painel_auditoria`. |
| `src/apps/usuarios/views.py` | Login e logout próprios (logout somente por POST, exigência do Django 5). |
| `src/apps/usuarios/forms.py` | Formulário de autenticação sobre o modelo `Usuario`. |
| `src/apps/usuarios/middleware.py` | `BloqueioAdminCoordenadorMiddleware`: anônimo vai ao login do SIG; coordenador não permanece em `/admin/`. |
| `src/apps/usuarios/urls.py` | `/usuarios/login/` e `/usuarios/logout/`. |
| `src/apps/usuarios/admin.py` | Cadastro do usuário no Django Admin. |
| `src/apps/usuarios/tests.py` | Login, redirecionamento por papel, bloqueio do Admin e recorte ALIM × INFRA. |
| `src/apps/usuarios/migrations/` | Schema do usuário customizado e da FK `coordenacao`. |

### 3.4 `apps.financeiro` — tetos e saldo

| Programa | Responsabilidade |
| :--- | :--- |
| `src/apps/financeiro/models.py` | `Coordenacao`: teto, total comprometido, saldo disponível e percentual consumido, sempre em `Decimal`. |
| `src/apps/financeiro/services.py` | Atualização de teto e agregações usadas pelo painel. |
| `src/apps/financeiro/views.py` | Painel de saldos, API JSON de saldos e atualização de teto. |
| `src/apps/financeiro/urls.py` | `/financeiro/saldos/`, `/financeiro/api/saldos/`, `/financeiro/coordenacoes/<id>/teto/`. |
| `src/apps/financeiro/tests.py` | Cálculo de saldo e teto. |

### 3.5 `apps.despesas` — ciclo de vida da despesa

| Programa | Responsabilidade |
| :--- | :--- |
| `src/apps/despesas/models.py` | `Despesa`, `HistoricoTransicaoStatus` e transições atômicas (`submeter`, `aprovar`, `rejeitar`, `liquidar`). |
| `src/apps/despesas/regras.py` | RN02 (soft-block) e RN03 (segregação de funções). |
| `src/apps/despesas/services.py` | Orquestração da triagem: listagem, aprovação, reprovação e liquidação. |
| `src/apps/despesas/forms.py` | Formulários de submissão, rejeição (motivo obrigatório) e liquidação (comprovante Cora). |
| `src/apps/despesas/views.py` | Telas de campo e painel de triagem. A view só autentica, autoriza e chama o serviço. |
| `src/apps/despesas/urls.py` | Rotas de submissão, prévia de orçamento, edição, auditoria/triagem, comprovante protegido, aprovar, rejeitar e liquidar. |
| `src/apps/despesas/tests.py`, `test_regras_rn02_rn03.py`, `test_triagem_workflow.py`, `test_tela_mobile.py`, `test_painel_auditoria.py`, `test_correcoes_pos_pr46.py` | Regras RN01–RN06, tela mobile, painel de auditoria com rota de comprovantes e regressões pós-E2E. |

### 3.6 `apps.relatorios` — prestação de contas (`@Mah-Rod`)

| Programa | Responsabilidade |
| :--- | :--- |
| `src/apps/relatorios/services.py` | `gerar_balancete_sintetico` e `gerar_csv_despesas`, com `Decimal` e o mesmo recorte RBAC de `despesas_visiveis`. |
| `src/apps/relatorios/views.py` | Página do balancete e download CSV (`prestacao_contas_ag7.csv`, BOM UTF-8). |
| `src/apps/relatorios/urls.py` | `/relatorios/balancete/` e `/relatorios/exportar.csv`. |
| `src/apps/relatorios/templatetags/moeda.py` | Formatação de reais nos templates. |
| `src/apps/relatorios/tests.py` | Exportação e totais do balancete. |

### 3.7 Apresentação

| Programa | Responsabilidade |
| :--- | :--- |
| `src/templates/base.html` | Layout, Bootstrap 5.3 e menu condicionado ao papel. |
| `src/templates/usuarios/login.html` | Tela de login. |
| `src/templates/dashboard.html` | Termômetros de verba e atalhos. |
| `src/templates/despesas/despesa_form.html` | Submissão mobile, inclusive captura pela câmera. |
| `src/templates/despesas/minhas_despesas.html` | Histórico do solicitante. |
| `src/templates/despesas/painel_triagem.html` | Fila da Tesouraria, modal da nota, modal de reprovação e modal de liquidação Cora. |
| `src/templates/financeiro/painel_saldos.html` | Saldos das pastas. |
| `src/templates/relatorios/balancete.html` | Balancete sintético e filtros da exportação. |

### 3.8 Regra de localização da lógica

As regras contábeis RN01 a RN06 residem em `models.py`, `regras.py` ou `services.py`. Templates e views não calculam saldo, não decidem transição de estado e não aplicam soft-block. Toda alteração de saldo, estado ou upload protegido pelo domínio corre dentro de `@transaction.atomic`. O schema evolui só por migrações Django (`makemigrations` / `migrate`).

---

## 4. Dependências de software

### 4.1 Python (`src/requirements.txt`)

| Pacote | Faixa | Uso no sistema |
| :--- | :--- | :--- |
| Django | `>=5.0,<5.3` | ORM, autenticação, admin, templates, testes e servidor de desenvolvimento. |
| Pillow | `>=10.0.0` | Compressão e saneamento de fotos de cupom (RNF02). |
| python-dotenv | `>=1.0.0` | Leitura de `.env` em `config.settings.base`. |
| psycopg | `>=3.1.0` (comentado) | Driver PostgreSQL. Necessário apenas quando `POSTGRES_DB` estiver definido em produção. |

O ambiente Nix (`flake.nix`) instala, no shell `backend`, Python 3.12 com Django, Pillow, python-dotenv e pip. O shell `quality` acrescenta Ruff, Bandit, Coverage e Gitleaks, os mesmos usados no workflow `.github/workflows/ci.yml`.

### 4.2 Front-end e runtime

| Dependência | Como entra no sistema |
| :--- | :--- |
| Bootstrap 5.3.3 e Bootstrap Icons 1.11.3 | Folhas de estilo carregadas por CDN em `base.html`. A execução visual das telas pede acesso à internet na primeira abertura, ou cache do navegador. |
| Navegador atual | Cliente único. Não há aplicativo móvel separado: o formulário de campo é a mesma aplicação, em layout mobile-first. |
| Git | Clonagem do repositório. |
| Nix com Flakes **ou** Python 3.12 + `venv` | Um dos dois caminhos da [Seção 9](#9-ambiente-reproduzível). |

Não há chave de API bancária no código. A liquidação “via Cora PJ” registra o comprovante da transferência feita pelo tesoureiro no internet banking; o sistema não dispara PIX.

---

## 5. Arquitetura técnica

O sistema segue o projeto Django em camadas, com um app por contexto de negócio.

```text
Navegador (Bootstrap 5.3)
        │  HTTP + sessão + CSRF
        ▼
config.urls  ──►  views (orquestração, login_required, checagem de papel)
        │
        ▼
services.py / regras.py / models.py   ← RN01–RN06, Decimal, @transaction.atomic
        │
        ▼
SQLite (dev/testes)  ou  PostgreSQL (produção, se POSTGRES_DB estiver definido)
        │
        └── media/   comprovantes fiscais e comprovantes Cora, nome UUID
```

Configurações compartilhadas ficam em `base.py`. Desenvolvimento e produção divergem só em segredo, debug, hosts, banco e cookies. O default local é desenvolvimento, para que `python src/manage.py runserver` funcione logo após o clone.

Fluxo de uma despesa, da submissão à prestação de contas:

1. O coordenador autentica em `/usuarios/login/`. O serviço `url_pos_login` envia Admin ao `/admin/` e os demais ao dashboard.
2. O dashboard chama `coordenacoes_visiveis`: o coordenador vê a pasta ligada em `Usuario.coordenacao`; Tesoureiro e Admin veem as pastas ativas.
3. `POST /despesas/nova/` grava rascunho. A submissão exige comprovante (RN01), passa o arquivo por `otimizar_comprovante_fiscal` e marca `excede_teto` se o valor ultrapassa o saldo (RN02), sem impedir o envio.
4. A Tesouraria abre `/despesas/triagem/`. No modal, confere a nota. Aprovar, reprovar (com texto, RN04) ou liquidar (com comprovante Cora) só é aceito de usuário `is_tesoureiro`, e nunca sobre despesa do próprio solicitante (RN03).
5. Cada transição grava `HistoricoTransicaoStatus` (RN06). Depois de `APROVADO` ou `PAGO`, valor, coordenação, data e comprovante fiscal ficam imutáveis (RN05).
6. `/relatorios/balancete/` e `/relatorios/exportar.csv` consolidam apenas as despesas visíveis ao papel da sessão.

O saldo da coordenação não é coluna armazenada. `Coordenacao.total_comprometido` soma, na consulta, despesas em `ENVIADO`, `APROVADO` e `PAGO`. Rascunho, rejeitada e cancelada não comprometem teto.

---

## 6. Módulos de domínio (`src/apps/`)

`INSTALLED_APPS` em `config/settings/base.py` registra, nesta ordem de domínio: `apps.core`, `apps.usuarios`, `apps.financeiro`, `apps.despesas`, `apps.relatorios`.

| Módulo | Prefixo HTTP | Dono na equipe | O que resolve no AG VII |
| :--- | :--- | :--- | :--- |
| `apps.core` | `/` | Infraestrutura compartilhada | Dashboard e compressão de comprovante. |
| `apps.usuarios` | `/usuarios/` | `@Mah-Rod` | Quem entra e o que cada papel pode ver. |
| `apps.financeiro` | `/financeiro/` | `@minoruhaga` | Teto das 15 pastas e saldo em tempo real. |
| `apps.despesas` | `/despesas/` | `@minoruhaga` | Lançamento, triagem, reprovação e liquidação. |
| `apps.relatorios` | `/relatorios/` | `@Mah-Rod` | Balancete e CSV da prestação de contas. |

Mapa de rotas da aplicação:

| Rota | Nome Django | Quem acessa |
| :--- | :--- | :--- |
| `/usuarios/login/` | `usuarios:login` | Anônimo |
| `/usuarios/logout/` | `usuarios:logout` | Autenticado (POST) |
| `/` | `dashboard` | Autenticado; dados recortados pelo papel |
| `/despesas/nova/` | `despesas:nova` | Autenticado |
| `/despesas/previa-orcamento/` | `despesas:previa_orcamento` | Autenticado (GET JSON para o termômetro da verba) |
| `/despesas/minhas/` | `despesas:minhas` | Autenticado; lista as suas |
| `/despesas/<id>/editar/` | `despesas:editar` | Solicitante, enquanto o estado permitir |
| `/despesas/<id>/submeter/` | `despesas:submeter` | Solicitante |
| `/despesas/triagem/` | `despesas:triagem` | Somente Tesoureiro ou superusuário (`pode_acessar_painel_auditoria`); Administrador Geral e Coordenador recebem 403 |
| `/despesas/<id>/comprovante/<nota\|pagamento>/` | `despesas:comprovante` | Somente Tesoureiro ou superusuário (entrega inline com `X-Frame-Options: SAMEORIGIN`) |
| `/despesas/<id>/aprovar/` | `despesas:aprovar` | Tesoureiro (POST) |
| `/despesas/<id>/rejeitar/` | `despesas:rejeitar` | Tesoureiro (POST) + justificativa |
| `/despesas/<id>/liquidar/` | `despesas:liquidar` | Tesoureiro (POST) + comprovante Cora |
| `/financeiro/saldos/` | `financeiro:saldos` | Autenticado, no recorte do papel |
| `/financeiro/api/saldos/` | `financeiro:api_saldos` | Autenticado, no recorte do papel |
| `/financeiro/coordenacoes/<id>/teto/` | `financeiro:atualizar_teto` | Tesoureiro ou Administrador Geral (POST) |
| `/relatorios/balancete/` | `relatorios:balancete` | Autenticado, no recorte do papel |
| `/relatorios/exportar.csv` | `relatorios:exportar_csv` | Autenticado, no recorte do papel |
| `/admin/` | `admin:index` | Tesoureiro, Admin ou superusuário. Coordenador é devolvido ao dashboard |

---

## 7. Modelos relacionais

O diagrama completo e as fórmulas de saldo estão em [docs/arquitetura/modelo_dados.md](../arquitetura/modelo_dados.md). A máquina de estados está em [docs/arquitetura/maquina_estados.md](../arquitetura/maquina_estados.md). O resumo abaixo é o contrato implementado no ORM.

```text
Usuario 1───N Despesa            (solicitante, analisado_por, pago_por)
Usuario N───1 Coordenacao        (coordenacao de atuação; nula para Tesoureiro e Admin)
Coordenacao 1───N Despesa        (pasta onerada; on_delete=PROTECT)
Despesa 1───N HistoricoTransicaoStatus
Usuario 1───N HistoricoTransicaoStatus   (autor da transição)
```

| Modelo | Tabela lógica | Campos que sustentam a regra |
| :--- | :--- | :--- |
| `Usuario` | usuário customizado (`AUTH_USER_MODEL`) | `papel`, `coordenacao`, `chave_pix`, `telefone`, mais os campos de `AbstractUser` |
| `Coordenacao` | pasta orçamentária | `nome`, `sigla`, `teto_orcamentario` (`Decimal`), `ativo` |
| `Despesa` | lançamento | `valor` (`Decimal`), `status`, `comprovante`, `excede_teto`, `valor_excedente`, `motivo_rejeicao`, `comprovante_pagamento`, FKs de solicitante, analista e liquidador |
| `HistoricoTransicaoStatus` | trilha RN06 | `status_anterior`, `novo_status`, `alterado_por`, `data_hora`, `observacao` |

Estados de `Despesa`: `RASCUNHO` → `ENVIADO` → `APROVADO` → `PAGO`. De `ENVIADO` também se vai a `REJEITADO`. `RASCUNHO` e `ENVIADO` podem ir a `CANCELADO`. Transição fora desse grafo levanta `TransicaoStatusInvalidaError`.

Integridade referencial: apagar coordenação ou usuário que já participa de despesa é recusado (`PROTECT`). O histórico acompanha a despesa (`CASCADE`) porque não existe fora dela. Comprovantes aceitos: `jpg`, `jpeg`, `png`, `webp` e `pdf`, gravados em `media/comprovantes/%Y/%m/` com nome UUID.

---

## 8. Segurança, autenticação e controle de acesso (RBAC)

Esta seção foi elaborada com apoio de **Marina (`@Mah-Rod`)**, responsável pelo módulo `apps.usuarios`, pela proteção das rotas e pela exportação em `apps.relatorios`. O detalhe operacional da Issue #6 está em [docs/fase-2/guia-login-rbac.md](guia-login-rbac.md).

### 8.1 Autenticação

- O modelo de usuário é `usuarios.Usuario`, declarado em `AUTH_USER_MODEL`. O Django Admin, a sessão e as views usam esse modelo, não o `User` padrão.
- A tela de entrada é `/usuarios/login/`. `LOGIN_URL` aponta para ela. Visitante sem sessão que abre `/` ou `/admin/` cai nessa tela, com `next` preservado quando a rota era administrativa.
- O logout é `POST` em `/usuarios/logout/`. O Django 5 não encerra sessão por GET, o que evita logout acidental por link ou prefetch.
- Senhas passam pelos quatro validadores padrão do Django (semelhança com atributos do usuário, tamanho mínimo, senha comum e senha numérica) e são armazenadas com o hasher do framework.
- A sessão usa o middleware de sessão do Django. O middleware CSRF protege os POST de aprovação, reprovação, liquidação e logout.

### 8.2 Papéis

| Papel (`PapelUsuario`) | Depois do login | Escopo de dados | `/admin/` | Aprovar, reprovar, liquidar |
| :--- | :--- | :--- | :--- | :--- |
| `COORDENADOR` | Dashboard | Só `Usuario.coordenacao` | Bloqueado pelo middleware, com aviso | Não |
| `TESOUREIRO` | Dashboard | Todas as coordenações ativas | Permitido (`staff`) | Sim, exceto despesa em que ele mesmo é o solicitante (RN03) |
| `ADMIN` | `/admin/` | Todas as coordenações ativas | Permitido | Não (recebe 403 em `/despesas/triagem/`; auditoria é exclusiva de Tesoureiro e superusuário) |

As propriedades `is_coordenador`, `is_tesoureiro`, `is_admin_geral`, `pode_acessar_admin` e `pode_acessar_painel_auditoria` concentram essa leitura. `is_tesoureiro` e `is_admin_geral` também valem para `is_superuser`, para a conta `admin` de demonstração operar a governança.

O recorte de linhas não fica espalhado nas views. `coordenacoes_visiveis` e `despesas_visiveis` (`apps.usuarios.services`) são a fonte usada pelo dashboard e pelos relatórios. Coordenador sem pasta vinculada recebe queryset vazio, em vez da lista global.

### 8.3 O que cada barreira impede

| Ameaça no contexto do AG VII | Controle implementado |
| :--- | :--- |
| Voluntário abre o cadastro mestre pelo Admin | `BloqueioAdminCoordenadorMiddleware` devolve o coordenador ao dashboard. |
| Coordenador lê teto e notas das outras 14 pastas | Querysets filtrados pelo papel antes da renderização e antes do CSV. |
| Tesoureiro aprova o próprio reembolso | RN03 em `validar_segregacao_funcoes_rn03`, chamada nas transições do modelo. |
| Reprovação sem rastro para o campo | RN04: `RejeicaoDespesaForm` recusa motivo vazio; o texto vai para `motivo_rejeicao` e para o histórico. |
| Alterar valor depois da decisão da Tesouraria | RN05: `clean`/`save` bloqueiam os campos de `CAMPOS_IMUTAVEIS_POS_DECISAO` em `APROVADO` e `PAGO`. |
| Apagar o rastro da decisão | RN06: toda transição insere `HistoricoTransicaoStatus` na mesma transação. |
| Upload de executável com extensão de imagem, ou foto de dezenas de MB na Starlink | `otimizar_comprovante_fiscal` valida extensão, rejeita imagem que o Pillow não abre, limita o bruto a 10 MB e comprime JPEG abaixo de 350 KB. |
| Adivinhar URL de comprovante pelo nome original da nota | Nome físico substituído por UUID v4. |
| Segredo de produção no repositório | `config.settings.prod` recusa subir sem `DJANGO_SECRET_KEY`. `.env` permanece fora do Git. A CI roda Gitleaks no histórico. |
| Sessão e conteúdo em produção | `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` e `SECURE_CONTENT_TYPE_NOSNIFF` em `prod.py`. |

A conta de demonstração usa senhas públicas de propósito (`admin123`, `tesouraria123`, `cozinha123`, `infra123`). Elas existem só depois de `popular_dados_demo` e não são credenciais de produção.

---

## 9. Ambiente reproduzível

Há dois caminhos equivalentes. O Nix é o que a CI executa em `ubuntu-latest`. O virtualenv é o caminho do Windows nativo, do macOS e de quem não usa Nix. Os dois instalam o mesmo trio Django, Pillow e python-dotenv.

O passo a passo de WSL, instalação do Nix, Flakes e GitHub CLI está em [docs/configuracao-ambiente.md](../configuracao-ambiente.md). Os comandos desta seção pressupõem o repositório já clonado e o terminal na **raiz** (`sig-reembolso/`, onde estão `flake.nix` e `src/`).

### 9.1 Nix Flakes (Linux e WSL)

Requisitos: Nix instalado e `experimental-features = nix-command flakes` em `~/.config/nix/nix.conf`. O flake fixa `x86_64-linux` e Python 3.12.

```bash
nix develop
python src/manage.py migrate
python src/manage.py loaddata src/fixtures/coordenacoes_iniciais.json
python src/manage.py popular_dados_demo
python src/manage.py runserver
```

O shell `backend` exporta `PYTHONPATH` com `$PWD/src`. Verificações estáticas, iguais às da CI:

```bash
nix develop .#quality --command ruff check src
nix develop --command python src/manage.py check
nix develop --command python src/manage.py makemigrations --check --dry-run
nix develop --command python src/manage.py test src/apps
```

### 9.2 Python virtualenv (Windows, macOS e Linux)

Requisito: Python 3.12 disponível como `python` ou `py -3.12`. Dependências ficam no `.venv` do repositório. Não instalar Django nem Pillow no Python global do sistema.

```bash
python -m venv .venv
```

Ativação no Linux e no macOS:

```bash
source .venv/bin/activate
pip install -r src/requirements.txt
```

Ativação no Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r src\requirements.txt
```

Se a política de execução bloquear `Activate.ps1`, chame o interpretador do venv direto, sem ativar:

```powershell
.\.venv\Scripts\python.exe -m pip install -r src\requirements.txt
.\.venv\Scripts\python.exe src\manage.py migrate
.\.venv\Scripts\python.exe src\manage.py loaddata src\fixtures\coordenacoes_iniciais.json
.\.venv\Scripts\python.exe src\manage.py popular_dados_demo
.\.venv\Scripts\python.exe src\manage.py runserver
```

Nos demais sistemas, depois do `pip install`:

```bash
cp .env.example .env
python src/manage.py migrate
python src/manage.py loaddata src/fixtures/coordenacoes_iniciais.json
python src/manage.py popular_dados_demo
python src/manage.py runserver
```

O arquivo `.env` é opcional em desenvolvimento: `dev.py` já tem chave e `DEBUG` de fallback. Para copiá-lo no PowerShell, use `Copy-Item .env.example .env`.

### 9.3 Variáveis de ambiente

| Variável | Desenvolvimento | Produção (`DJANGO_ENV=prod`) |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | Opcional; há fallback inseguro só para aula | Obrigatória. Sem ela o processo não sobe |
| `DJANGO_DEBUG` | `True` por omissão | Ignorada: `DEBUG` é `False` |
| `DJANGO_ALLOWED_HOSTS` | `*` se omitida | Lista separada por vírgula, sem curinga implícito |
| `DJANGO_ENV` | omitir ou qualquer valor diferente de `prod` | `prod` seleciona `config.settings.prod` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | Não usadas (SQLite) | Se `POSTGRES_DB` existir, o engine passa a `django.db.backends.postgresql` |

Credenciais bancárias, certificado digital e senha de produção não entram no repositório. Logs volumosos, se gerados, ficam em `.tmp/`, já ignorada pelo Git.

### 9.4 Produção

```bash
export DJANGO_ENV=prod
export DJANGO_SECRET_KEY="chave-longa-exclusiva-do-ambiente"
export DJANGO_ALLOWED_HOSTS="sig.exemplo.br"
export POSTGRES_DB=sig_reembolso
export POSTGRES_USER=sig
export POSTGRES_PASSWORD="senha-do-banco"
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
pip install "psycopg[binary]>=3.1.0"
python src/manage.py migrate
python src/manage.py collectstatic --noinput
```

O processo HTTP de produção usa o callable `application` de `src/config/wsgi.py` (gunicorn, waitress ou equivalente no host). O `runserver` permanece restrito a desenvolvimento e demonstração de banca.

---

## 10. Instruções completas de execução

### 10.1 Subir o sistema

1. Clonar `https://github.com/minoruhaga/sig-reembolso.git` e entrar na pasta.
2. Entrar no Nix (`nix develop`) **ou** criar o `.venv` e instalar `src/requirements.txt`, conforme a [Seção 9](#9-ambiente-reproduzível).
3. Aplicar migrações: `python src/manage.py migrate`.
4. Carregar as 15 coordenações: `python src/manage.py loaddata src/fixtures/coordenacoes_iniciais.json`.
5. Criar usuários e despesas de demonstração: `python src/manage.py popular_dados_demo`. O comando é idempotente: rodar de novo não duplica as contas padrão.
6. Subir o servidor: `python src/manage.py runserver`.
7. Abrir [http://127.0.0.1:8000/](http://127.0.0.1:8000/). A raiz redireciona para `/usuarios/login/`.

Conferir a instalação sem subir o servidor:

```bash
python src/manage.py check
python src/manage.py test src/apps
```

A suíte deve terminar em `OK`. Ela cobre transições de estado, soft-block, segregação de funções, compressão de imagem, RBAC e exportação CSV.

### 10.2 Contas para a banca

| Usuário | Senha | Papel | O que exercitar |
| :--- | :--- | :--- | :--- |
| `coord_cozinha` | `cozinha123` | Coordenador (ALIM) | Dashboard só da Alimentação. `/admin/` volta ao painel. |
| `coord_infra` | `infra123` | Coordenador (INFRA) | Dashboard só da Infraestrutura. |
| `tesoureiro` | `tesouraria123` | Tesoureiro | Triagem, reprovação, liquidação, balancete e CSV de todas as pastas. |
| `admin` | `admin123` | Administrador Geral | Cai em `/admin/` após o login. |

Use **Sair** entre uma conta e outra. Credencial inválida permanece na tela de login com mensagem de erro.

### 10.3 Roteiro mínimo para comprovar que o sistema executa

Este roteiro verifica a execução ponta a ponta. O treinamento da Tesouraria (Item 3.k) aprofunda o mesmo fluxo para os operadores.

1. Entre como `coord_cozinha`. Confirme o termômetro da sigla **ALIM** e a ausência da pasta INFRA.
2. Em **Nova despesa**, lance um item com foto ou PDF. Envie para triagem. Sem anexo, a submissão é recusada (RN01).
3. Saia e entre como `tesoureiro`. Abra **Auditoria de Notas** (`/despesas/triagem/`).
4. Em **Conferir nota**, o modal em tela cheia mostra o comprovante com zoom. Aprove uma despesa `ENVIADO` que não seja sua.
5. Em outra despesa `ENVIADO`, abra o modal, deixe o campo **Motivo da rejeição** vazio e clique em **Rejeitar**: o sistema recusa (RN04). Repita com um parecer (por exemplo, “CNPJ divergente do cupom”) e observe a despesa sair da fila.
6. Numa despesa `APROVADO`, abra o modal, anexe o comprovante da transferência Cora PJ e clique em **Registrar pagamento**. O estado passa a `PAGO`.
7. Abra `/relatorios/balancete/`, filtre se quiser por coordenação, categoria ou status, e use a exportação CSV. O arquivo `prestacao_contas_ag7.csv` abre em planilha com cabeçalho em português de códigos e descrições.
8. Entre de novo como `coord_cozinha` e abra o mesmo balancete: a planilha e a tela ficam restritas à pasta ALIM.

### 10.4 Parar e repetir

- Interrompa o servidor com `Ctrl+C`.
- O banco de desenvolvimento é o arquivo `src/db.sqlite3`. Apagá-lo e repetir os passos 3 a 5 da [Seção 10.1](#101-subir-o-sistema) recria o ambiente do zero.
- Comprovantes enviados ficam em `src/media/`. Essa pasta é dado local de execução, não programa-fonte.

---

## 11. Rastreabilidade com os requisitos já especificados

| Regra / requisito | Onde o código cumpre | Onde a especificação está |
| :--- | :--- | :--- |
| RF01 — acesso por papel | `apps.usuarios` | [guia-login-rbac.md](guia-login-rbac.md) |
| RF02 / RF03 — teto e saldo | `apps.financeiro.models.Coordenacao` | [modelo_dados.md](../arquitetura/modelo_dados.md) |
| RF06 / RF07 — triagem e liquidação | `apps.despesas` | [regras_de_negocio.md](../requisitos/regras_de_negocio.md) |
| RF08 — prestação de contas | `apps.relatorios` | esta seção 3.6 e a seção 10.3 |
| RN01 a RN06 | `apps.despesas.models`, `regras.py`, `services.py` | [regras_de_negocio.md](../requisitos/regras_de_negocio.md) |
| RNF02 / RNF04 — compressão e anonimização | `apps.core.services.otimizar_comprovante_fiscal` | [src/AGENTS.md](../../src/AGENTS.md) |

---

## 12. Documentos relacionados

- [README.md](../../README.md) — entrada rápida de execução na raiz do repositório.
- [docs/configuracao-ambiente.md](../configuracao-ambiente.md) — WSL, Nix, Flakes e GitHub CLI.
- [docs/fase-2/planejamento_fase_2.md](planejamento_fase_2.md) — mapeamento dos itens 3.g a 3.l.
- [docs/fase-2/guia-login-rbac.md](guia-login-rbac.md) — evidência da autenticação por papel.
- [docs/arquitetura/modelo_dados.md](../arquitetura/modelo_dados.md) — DER.
- [docs/arquitetura/maquina_estados.md](../arquitetura/maquina_estados.md) — transições da despesa.
