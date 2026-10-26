# Regras Gerais para Agentes e Desenvolvedores

Estas instruções aplicam-se a todo o repositório **SIG-Reembolso**. Arquivos `AGENTS.md` existentes em subpastas definem regras locais adicionais e especializadas para os seus respectivos escopos.

## Níveis de Instrução

- `[CRITICAL]` — violar esta regra torna a solução inválida ou inaceitável.
- `[REQUIRED]` — esta regra DEVE ser rigorosamente cumprida.
- `[FORBIDDEN]` — esta prática NÃO DEVE ser utilizada em nenhuma hipótese.
- `[PREFERRED]` — padrão recomendado; desvios exigem justificativa técnica documentada.
- `[CONSIDER]` — avalie a aplicação conforme a complexidade e o contexto.

---

## 1. Regras de Escopo e Hierarquia de Agentes

### CRITICAL — Instruções de Subpastas
[CRITICAL] Antes de alterar, adicionar ou avaliar código em qualquer pasta, o desenvolvedor ou agente DEVE procurar e ler o `AGENTS.md` existente no caminho entre a raiz e a pasta-alvo (especialmente `src/AGENTS.md`).

[REQUIRED] Regras de subpastas são especializações das regras da raiz. Em caso de conflito, a instrução mais específica DEVE ser seguida, exceto se atenuar uma restrição `[CRITICAL]` ou `[FORBIDDEN]`.

---

## 2. Ambientes de Execução e Reprodutibilidade

### REQUIRED — Execução em Ambiente Isolado
[REQUIRED] Todo comando de execução, migração, testes, linters ou formatação DEVE ser executado dentro do ambiente isolado do projeto:
- Via **Nix**: `nix develop` (ou `nix develop .#quality` para verificações estáticas).
- Via **Python venv**: ambiente virtual ativo com `pip install -r src/requirements.txt`.

[REQUIRED] Antes de executar comandos, consulte o passo a passo de instalação do WSL, Nix e Flakes em [docs/configuracao-ambiente.md](docs/configuracao-ambiente.md).

[FORBIDDEN] Dependências de Python NÃO DEVEM ser instaladas globalmente no sistema operacional.

---

## 3. Segurança da Informação e Segredos

### CRITICAL — Proteção de Dados Sensíveis
[CRITICAL] Nenhuma chave de API privada, credencial bancária (Banco Cora), certificado digital, senha de produção ou segredo DEVE ser comitada no repositório.

[REQUIRED] Todas as configurações sensíveis DEVEM ser carregadas via variáveis de ambiente (`.env` ou `os.getenv`).

[REQUIRED] Arquivos temporários de log pesado DEVEM ser salvos na pasta `.tmp/` (já configurada no `.gitignore`).

---

## 4. Documentação de Código e Docstrings

### REQUIRED — Padrão Obrigatório de Docstrings
[REQUIRED] Toda função, classe de modelo, view, service ou comando de gerenciamento DEVE conter docstring explicando explicitamente:
1. **O que faz:** responsabilidade e comportamento.
2. **Como faz:** fluxo, abordagem e regras de negócio utilizadas.
3. **Qual finalidade atende:** o motivo pelo qual existe e qual dor do SIG-Reembolso / AG VII ela soluciona.

---

## 5. Testes e Micro-Commits

### REQUIRED — Testes Unitários de Comportamento
[REQUIRED] Toda alteração de regra de negócio (RN01 a RN06) ou adição de funcionalidade DEVE ser acompanhada de seu respectivo caso de teste automatizado no Django (`TestCase`).

[PREFERRED] Adotar a prática de **Micro-Commits** atômicos a cada marco concluído, utilizando o padrão Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
