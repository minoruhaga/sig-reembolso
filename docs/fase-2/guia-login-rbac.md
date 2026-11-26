# Login, Logout e Controle por Papel (Issue #6)

**Projeto:** SIG-Reembolso — AG VII, Grupo Escoteiro Caramuru  
**Requisito:** RF01 (RBAC)  
**Issue:** [#6](https://github.com/minoruhaga/sig-reembolso/issues/6)  
**Análise de decisão:** `prompts/backend/20261030-201542-login-logout-rbac-papel-v001.md`

Este documento descreve o que foi entregue nesta funcionalidade e como validar localmente (incluindo Windows com PowerShell sem `Activate.ps1`).

---

## 1. O que foi feito

Antes desta entrega, o painel em `/` era público, o botão Entrar apontava para o Django Admin e o modelo `Usuario` não registrava a pasta do coordenador. Não havia como cumprir “coordenador só vê a sua área”.

### Comportamento entregue

| Papel | Após o login | O que vê no dashboard | `/admin/` |
| :--- | :--- | :--- | :--- |
| Coordenador de Área | Painel operacional | Somente a coordenação vinculada (`Usuario.coordenacao`) | Bloqueado (volta ao dashboard) |
| Tesoureiro | Painel operacional | Todas as coordenações ativas | Permitido (usuário staff) |
| Administrador Geral | Django Admin (`/admin/`) | Todas as coordenações ativas (se abrir o painel) | Permitido |

- Tela de login em `/usuarios/login/` usando o modelo `Usuario` (não o formulário nativo do Admin).
- Logout por **POST** em `/usuarios/logout/` (menu do nome → Sair). O Django 5 não encerra sessão por GET.
- Visitante anônimo em `/` ou `/admin/` é enviado ao login customizado.
- Menu **Administração** e atalhos de Admin no dashboard só aparecem para Tesoureiro e Admin.

### Decisão de desenho

A regra de visibilidade vive em `apps.usuarios.services` (`coordenacoes_visiveis`, `despesas_visiveis`, `url_pos_login`). As views só orquestram, alinhado a `src/AGENTS.md`.

O vínculo “sua área” é o campo opcional `Usuario.coordenacao` (FK para `financeiro.Coordenacao`). Tesoureiro e Admin ficam sem pasta; coordenador de demo aponta para ALIM ou INFRA.

---

## 2. Arquivos principais

| Caminho | Papel |
| :--- | :--- |
| `src/apps/usuarios/models.py` | FK `coordenacao` e `pode_acessar_admin` |
| `src/apps/usuarios/services.py` | Escopo por papel e URL pós-login |
| `src/apps/usuarios/views.py` | `LoginView` / `LogoutView` |
| `src/apps/usuarios/middleware.py` | Bloqueio de `/admin/` para coordenador |
| `src/apps/core/views.py` | Dashboard com `login_required` e recorte |
| `src/templates/usuarios/login.html` | Tela Bootstrap 5 |
| `src/apps/usuarios/migrations/0002_coordenacao_atuacao.py` | Migração da FK |
| `src/apps/usuarios/tests.py` | Testes da Issue #6 |
| `src/apps/core/management/commands/popular_dados_demo.py` | Vincula `coord_cozinha`→ALIM e `coord_infra`→INFRA |

---

## 3. Como testar localmente

Execute os comandos na **raiz** do repositório (`sig-reembolso`). O Django está no ambiente virtual `.venv`, não no Python do sistema.

### 3.1 Windows (PowerShell)

Neste ambiente a política de execução pode bloquear `.venv\Scripts\Activate.ps1`. Use o interpretador do venv direto:

```powershell
.\.venv\Scripts\python.exe src\manage.py migrate
.\.venv\Scripts\python.exe src\manage.py loaddata src\fixtures\coordenacoes_iniciais.json
.\.venv\Scripts\python.exe src\manage.py popular_dados_demo
.\.venv\Scripts\python.exe src\manage.py runserver
```

Se o `.venv` ainda não existir:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r src\requirements.txt
```

Para **parar** o servidor: `Ctrl+C` (ou `Ctrl+Break`).

### 3.2 Linux / macOS / WSL (venv ou Nix)

```bash
# venv
source .venv/bin/activate
python src/manage.py migrate
python src/manage.py loaddata src/fixtures/coordenacoes_iniciais.json
python src/manage.py popular_dados_demo
python src/manage.py runserver

# ou Nix
nix develop --command python src/manage.py runserver
```

Guia completo de ambiente: [docs/configuracao-ambiente.md](../configuracao-ambiente.md).

### 3.3 Testes automatizados

```powershell
.\.venv\Scripts\python.exe src\manage.py test src/apps
```

A suíte deve terminar em `OK`. Os casos da Issue #6 estão em `src/apps/usuarios/tests.py` (login, redirect, bloqueio de Admin, recorte ALIM vs INFRA).

---

## 4. Roteiro manual no navegador

1. Abra [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Deve ir para `/usuarios/login/`.
2. Percorra as contas abaixo (use **Sair** entre uma e outra).

| Usuário | Senha | Esperado |
| :--- | :--- | :--- |
| `coord_cozinha` | `cozinha123` | Dashboard só da Alimentação (**ALIM**). Sem menu Administração. URL `/admin/` volta ao painel com aviso. |
| `coord_infra` | `infra123` | Só Infraestrutura (**INFRA**). |
| `tesoureiro` | `tesouraria123` | Termômetros das coordenações ativas; menu Administração visível. |
| `admin` | `admin123` | Após o login, cai em `/admin/`. |

3. Credenciais inválidas devem permanecer no login com mensagem de erro.
4. Sem sessão, `/admin/` também abre o login do SIG (`/usuarios/login/`), não o login nativo do Django Admin.

Se o banco já existia **antes** desta feature, rode de novo `migrate` e `popular_dados_demo` para gravar `coordenacao` nos coordenadores.

---

## 5. Critérios de aceite (checklist)

- [ ] View de login redireciona conforme o papel (Admin → `/admin/`; demais → dashboard).
- [ ] Coordenador de campo não permanece em rotas `/admin/`.
- [ ] Coordenador vê apenas a própria pasta; Tesoureiro e Admin veem todas as ativas.

---

## 6. Fora deste escopo

Submissão mobile de despesa (Issues #7/#8), ações de triagem (#11) e API de tetos (#10) não fazem parte desta entrega. Novas listagens devem reutilizar `coordenacoes_visiveis` / `despesas_visiveis` para não furar o RBAC.
