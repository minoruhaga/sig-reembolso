# Configuração do Ambiente de Desenvolvimento - SIG-Reembolso

## Sumário

* [1. Instalando o Linux no Windows com o WSL](#1-instalando-o-linux-no-windows-com-o-wsl)
* [2. Instalando o Nix](#2-instalando-o-nix)
* [3. Instalando e Autenticando o GitHub CLI](#3-instalando-e-autenticando-o-github-cli)
* [4. Clonando o Repositório do Projeto](#4-clonando-o-repositório-do-projeto)
* [5. Utilizando os Ambientes Nix do Projeto](#5-utilizando-os-ambientes-nix-do-projeto)
* [6. Alternativa com Python venv (Windows nativo / Mac)](#6-alternativa-com-python-venv-windows-nativo--mac)
* [7. Inicializando o Banco de Dados e Carga de Demonstração](#7-inicializando-o-banco-de-dados-e-carga-de-demonstração)
* [8. Executando o Servidor Local](#8-executando-o-servidor-local)
* [9. Variáveis de Ambiente](#9-variáveis-de-ambiente)
* [10. Resolução de Problemas Comuns](#10-resolução-de-problemas-comuns)

---

## 1. Instalando o Linux no Windows com o WSL

O **Subsistema do Windows para Linux (WSL)** permite executar uma distribuição Linux (Ubuntu) nativamente dentro do Windows, garantindo que todos os integrantes da equipe trabalhem no mesmo ambiente sem problemas de incompatibilidade de caminhos, bibliotecas C (como Pillow) ou permissões.

### Passo a Passo de Instalação do WSL:

1. No Windows, abra o **PowerShell como Administrador** (clique com o botão direito no menu Iniciar > *Windows Terminal (Admin)* ou *PowerShell (Admin)*).
2. Execute o comando:
   ```powershell
   wsl --install
   ```
3. Reinicie o computador após a conclusão da instalação.
4. Ao reiniciar, o terminal do Ubuntu abrirá automaticamente. Aguarde a descompactação inicial e defina um **nome de usuário** e uma **senha** (guarde esta senha, ela é usada para comandos `sudo`).

> **Dica:** Para abrir o terminal do Linux no dia a dia, basta pesquisar por **Ubuntu** no menu Iniciar do Windows ou digitar `wsl` no terminal.

Para mais detalhes, consulte a [Documentação Oficial do WSL](https://learn.microsoft.com/pt-br/windows/wsl/).

---

## 2. Instalando o Nix

O **Nix** é o gerenciador de pacotes que garante que **todos os integrantes tenham rigorosamente a mesma versão do Python 3.12, Django 5.2, Pillow e linters**, exatamente igual à esteira de CI/CD do GitHub Actions.

A instalação do Nix deve ser realizada **dentro do terminal Linux/WSL**.

1. Abra o terminal do Ubuntu/Linux e execute:
   ```bash
   curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install | sh -s -- --no-daemon
   ```
2. Após o término da instalação, feche e abra novamente o terminal para carregar os binários no seu `PATH`.

3. Habilite os recursos de Flakes no Nix criando o arquivo de configuração:
   ```bash
   mkdir -p ~/.config/nix
   echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
   ```
4. Feche e reabra o terminal. Para testar se o Nix está funcionando:
   ```bash
   nix --version
   ```

---

## 3. Instalando e Autenticando o GitHub CLI

O **GitHub CLI (`gh`)** facilita clonar o repositório, criar branches e abrir Pull Requests diretamente pelo terminal.

1. No terminal Linux/WSL com o Nix ativo, instale o `gh`:
   ```bash
   nix profile install nixpkgs#gh
   ```
2. Faça a autenticação com a sua conta do GitHub:
   ```bash
   gh auth login
   ```
3. Siga as opções recomendadas:
   * **What account do you want to log into?** `GitHub.com`
   * **What is your preferred protocol for Git operations?** `HTTPS`
   * **Authenticate Git with your GitHub credentials?** `Yes`
   * **How would you like to authenticate GitHub CLI?** `Login with a web browser`
4. Copie o código de 8 dígitos exibido no terminal e pressione Enter para abrir a página de autorização no navegador (ou acesse [github.com/login/device](https://github.com/login/device)).

---

## 4. Clonando o Repositório do Projeto

Crie uma pasta dedicada para armazenar seus projetos no diretório de usuário do Linux:

```bash
mkdir -p ~/projetos
cd ~/projetos
```

Clone o repositório do **SIG-Reembolso**:
```bash
git clone https://github.com/<seu-usuario>/sig-reembolso.git
cd sig-reembolso
```

---

## 5. Utilizando os Ambientes Nix do Projeto

O repositório já possui um arquivo `flake.nix` configurado com dois ambientes isolados:

### A. Ambiente Principal de Desenvolvimento (`backend` ou padrão)
Disponibiliza Python 3.12, Django 5.2, Pillow e python-dotenv:

```bash
nix develop
# ou
nix develop .#backend
```

Quando o ambiente estiver ativo, você verá a mensagem:
`Ambiente Backend ativo (Python 3.12 + Django 5 + Pillow)`

Para rodar qualquer comando pontual sem entrar no shell interativo:
```bash
nix develop --command python src/manage.py test src/apps
```

### B. Ambiente de Quality Gates (`quality`)
Disponibiliza ferramentas de verificação estática, linters e scanners de segurança:
* **Ruff:** linter e formatador de imports ultrarrápido.
* **Gitleaks:** scanner que impede vazamento acidental de chaves bancárias ou segredos.
* **Bandit:** analisador estático de segurança em código Python.
* **Coverage:** medidor de cobertura de testes.

Para entrar no ambiente de qualidade:
```bash
nix develop .#quality
```

Para rodar o linter Ruff:
```bash
nix develop .#quality --command ruff check src
```

Para rodar a varredura de segredos do Gitleaks:
```bash
nix develop .#quality --command gitleaks git --redact --no-banner --exit-code 1
```

---

## 6. Alternativa com Python venv (Windows nativo / Mac)

Caso algum integrante precise rodar o sistema diretamente no Windows ou macOS sem utilizar o Nix, o projeto mantém total suporte a ambientes virtuais convencionais:

1. Certifique-se de ter o **Python 3.12** instalado na máquina.
2. Na raiz do projeto, crie o ambiente virtual:
   ```bash
   python -m venv .venv
   ```
3. Ative o ambiente virtual:
   * **No Windows (PowerShell):**
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   * **No Linux / macOS / Git Bash:**
     ```bash
     source .venv/bin/activate
     ```
4. Instale as dependências:
   ```bash
   pip install -r src/requirements.txt
   ```

---

## 7. Inicializando o Banco de Dados e Carga de Demonstração

Com o ambiente ativo (seja via `nix develop` ou `.venv`), execute:

```bash
# 1. Aplicar as migrações no banco SQLite local
python src/manage.py migrate

# 2. Carregar as 15 coordenações e dados reais do AG VII (Grupo Escoteiro Caramuru)
python src/manage.py popular_dados_demo
```

Esse comando cria os usuários de demonstração (`admin`, `tesoureiro`, `coord_cozinha`, `coord_infra`) e lança compras de teste baseadas na rotina de campo do acampamento.

---

## 8. Executando o Servidor Local

Inicie o servidor de desenvolvimento do Django:

```bash
python src/manage.py runserver
```

Abra o seu navegador e acesse:
* **Painel do Evento / Termômetro de Verba:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Painel Administrativo do Django:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Para encerrar o servidor, pressione `Ctrl + C` no terminal.

---

## 9. Variáveis de Ambiente

O projeto lê variáveis a partir de um arquivo `.env`. Na raiz do projeto, copie o modelo de exemplo:

```bash
cp .env.example .env
```

| Variável | Padrão Local | Descrição |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | Chave de teste | Chave criptográfica do Django. Nunca use chaves de produção no repositório. |
| `DJANGO_DEBUG` | `True` | Ativa o modo de depuração para desenvolvimento local. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts permitidos para conexão HTTP. |

---

## 10. Resolução de Problemas Comuns

### 1. `wsl: command not found` no PowerShell
* Verifique se a virtualização está habilitada na BIOS da sua placa-mãe (Intel VT-x ou AMD-V).
* Certifique-se de estar utilizando o Windows 10 (versão 2004 ou superior) ou Windows 11.

### 2. `error: experimental Nix feature 'nix-command' is not enabled`
* Execute o comando:
  ```bash
  mkdir -p ~/.config/nix
  echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
  ```
  Feche e reabra o terminal.

### 3. Erro ao salvar imagens com Pillow no Windows
* Se estiver usando Windows nativo sem WSL, instale os compiladores C++ ou prefira rodar via WSL/Linux onde o Pillow já possui todas as bibliotecas binárias de manipulação gráfica compiladas no Nix.
