# SIG-Reembolso

**Sistema Integrado de Gestão de Fundo de Caixa, Adiantamentos e Reembolsos**  
*Piloto Oficial:* **Acampamento Geral VII (AG VII) – Grupo Escoteiro Caramuru**  
*Disciplina:* Laboratório de Engenharia de Software (LES) – FATEC-SP (DTI) – 2º Semestre / 2026

---

## 🎯 Visão Geral do Projeto
O **SIG-Reembolso** é uma solução web focada em mobilidade (*Mobile-First*) e controle financeiro transacional para eventos temporários de grande escala. O sistema foi concebido para eliminar o extravio físico de cupons fiscais sob chuva e no campo, erradicar pedidos de PIX dispersos em grupos de WhatsApp e permitir o abatimento automático do teto orçamentário das 15 coordenações em tempo real.

* **Público Atendido:** ~100 voluntários operando no Campo Escola em Juquitiba/SP e equipe da Tesouraria.
* **Orçamento Auditado:** R$ 180.000,00 distribuídos entre 15 coordenações operacionais.
* **Conta de Liquidação Bancária:** Banco Cora PJ.

---

## 👥 Equipe e Atribuições (Fase 2)

| Integrante | Papel no Projeto | Responsabilidades Principais |
| :--- | :--- | :--- |
| **Gustavo Minoru Haga** | **Tech Lead / Core Backend & Governança** | Arquitetura Django, RBAC (`apps.usuarios`), gestão financeira de tetos (`apps.financeiro`), CI/CD e revisão de PRs. |
| **Integrante 2** | **Backend de Despesas & Regras de Negócio** | CRUD de despesas, máquina de estados finita, compressão Pillow (`RNF02`), soft-block (`RN02`) e auditoria (`RN06`). |
| **Integrante 3** | **Frontend, UX & Interfaces Mobile-First** | Telas Bootstrap 5, formulário de captura rápida por câmera, painel de triagem desktop da tesouraria e **Item 3.g (Usabilidade)**. |
| **Integrante 4** | **QA, Testes, Manuais e Homologação** | Fixtures com dados do AG VI/VII, suíte de testes (`TestCase` - **Item 3.i**), manuais de operação/treinamento (**3.j / 3.k**) e homologação (**3.l**). |

---

## 🚀 Como Executar o Projeto Localmente

O repositório suporta execução via **Nix Flakes** (Linux/WSL) ou via **Ambiente Virtual Python (venv + pip)** padrão (Windows, Linux, macOS).

### Opção A: Execução via Nix (Recomendado no Linux/WSL)

O Nix garante que Python 3.12, Django 5.2, Pillow e ferramentas de linter/segurança sejam idênticos aos da esteira de CI:

```bash
# 1. Clonar o repositório
git clone https://github.com/<usuario>/sig-reembolso.git
cd sig-reembolso

# 2. Entrar no ambiente de desenvolvimento
nix develop

# 3. Executar as migrações e popular dados de teste
python src/manage.py migrate
python src/manage.py popular_dados_demo

# 4. Iniciar o servidor
python src/manage.py runserver
```

Para rodar as verificações de linter e qualidade com Nix:
```bash
nix develop .#quality --command ruff check src
```

---

### Opção B: Execução via Python venv + pip (Windows / Mac / Linux sem Nix)

```bash
# 1. Clonar o repositório
git clone https://github.com/<usuario>/sig-reembolso.git
cd sig-reembolso

# 2. Criar e ativar o ambiente virtual
python -m venv .venv

# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No Linux / macOS:
source .venv/bin/activate

# 3. Instalar as dependências
pip install -r src/requirements.txt

# 4. Configurar variáveis locais (opcional)
cp .env.example .env

# 5. Aplicar migrações e carregar dados reais do AG VII
python src/manage.py migrate
python src/manage.py popular_dados_demo

# 6. Iniciar o servidor local
python src/manage.py runserver
```

Acesse a aplicação no navegador em: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Credenciais Padrão de Demonstração

Após rodar `python src/manage.py popular_dados_demo`, os seguintes usuários de teste ficam prontos:

| Usuário | Senha | Papel | Finalidade de Teste |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | Administrador Geral | Acesso total ao Django Admin (`/admin/`). |
| `tesoureiro` | `tesouraria123` | Tesoureiro / Gestor | Triagem de notas, aprovação, reprovação e liquidação Cora. |
| `coord_cozinha` | `cozinha123` | Coordenador de Área | Submissão de compras da Alimentação e Cozinha Central. |
| `coord_infra` | `infra123` | Coordenador de Área | Submissão de combustível e reparos de Infraestrutura. |

---

## 🧪 Executando os Testes Automatizados

O sistema conta com testes automatizados cobrindo as regras estritas de domínio contábil (RN01 a RN06):

```bash
python src/manage.py test src/apps
```

Para checagem de integridade sem iniciar o servidor:
```bash
python src/manage.py check
```

---

## 📚 Mapa da Documentação e Governança

* [Manual de Uso do Git e Branches](file:///home/minoru/projetos/sig-reembolso/docs/manual-git.md)
* [Guia de Contribuição](file:///home/minoru/projetos/sig-reembolso/CONTRIBUTING.md)
* [Regras Gerais de Agentes e IA (AGENTS.md)](file:///home/minoru/projetos/sig-reembolso/AGENTS.md)
* [Regras de Domínio e Backend Django (src/AGENTS.md)](file:///home/minoru/projetos/sig-reembolso/src/AGENTS.md)
* [Guia de Governança de IA e Uso das Skills](file:///home/minoru/projetos/sig-reembolso/docs/guia-uso-ia-e-skills.md)
* [Catálogo de Issues para o GitHub](file:///home/minoru/projetos/sig-reembolso/docs/fase-2/backlog_issues_github.md)
* [Planejamento de Entregas da 2ª Fase (Itens 3.g a 3.l)](file:///home/minoru/projetos/sig-reembolso/docs/fase-2/planejamento_fase_2.md)
* [Requisitos Funcionais (RF01 a RF08)](file:///home/minoru/projetos/sig-reembolso/docs/requisitos/requisitos_funcionais.md)
* [Regras de Negócio e Domínio (RN01 a RN06)](file:///home/minoru/projetos/sig-reembolso/docs/requisitos/regras_de_negocio.md)
* [Modelo de Dados Relacional (DER)](file:///home/minoru/projetos/sig-reembolso/docs/arquitetura/modelo_dados.md)
* [Máquina de Estados da Despesa](file:///home/minoru/projetos/sig-reembolso/docs/arquitetura/maquina_estados.md)
