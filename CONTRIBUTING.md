# Guia de Contribuição - SIG-Reembolso

Este guia orienta o fluxo de trabalho de desenvolvimento, versionamento e submissão de código dos 4 integrantes da equipe.

---

## 1. Fluxo de Branches

O repositório utiliza o fluxo baseado em branches de funcionalidade (*Feature Branches*):

```text
main (branch de produção / entregas estáveis da banca)
  ▲
  └── dev (branch de integração contínua da equipe)
        ▲
        ├── feature/#04-formulario-despesa-mobile
        ├── feature/#05-triagem-tesouraria
        └── fix/#12-validacao-extensao-pdf
```

### Regras Obrigatórias de Branches
1. **NÃO comite diretamente na `main` nem na `dev`.**
2. Toda alteração de código ou documentação deve ser feita em uma branch própria criada a partir da `dev` atualizada:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/#<numero_issue>-descricao-curta
   ```

---

## 2. Padrão de Mensagens de Commit (Conventional Commits)

Utilize mensagens claras e objetivas em português ou inglês:
* `feat:` nova funcionalidade para o usuário (ex: `feat(despesas): adiciona compressão de fotos com Pillow`).
* `fix:` correção de bug ou erro de validação (ex: `fix(financeiro): corrige cálculo do percentual de consumo de verba`).
* `docs:` alterações em documentação ou manuais (ex: `docs(fase-2): adiciona manual de operação do usuário`).
* `test:` adição ou modificação de testes automatizados (ex: `test(regras): adiciona teste unitário de segregação de funções`).
* `refactor:` refatoração sem alteração de comportamento externo.

---

## 3. Prevenção de Conflitos em Migrações do Django

Conflitos em arquivos dentro de `src/apps/*/migrations/` são comuns quando múltiplos desenvolvedores alteram models ao mesmo tempo. Para evitar:

1. **Sempre comunique a equipe** antes de alterar campos em `models.py`.
2. Antes de criar migrations, puxe as alterações mais recentes da branch `dev`:
   ```bash
   git fetch origin dev
   git merge origin/dev
   ```
3. Gere e aplique sua migração:
   ```bash
   python src/manage.py makemigrations
   python src/manage.py migrate
   ```
4. Verifique se o Django não aponta migrações conflitantes:
   ```bash
   python src/manage.py makemigrations --check --dry-run
   ```

---

## 4. Submissão de Pull Request (PR)

Ao concluir sua tarefa:
1. Envie sua branch para o GitHub:
   ```bash
   git push -u origin feature/#<numero_issue>-sua-feature
   ```
2. Abra o Pull Request apontando para a branch **`dev`** (ou `main`).
3. Preencha o template do PR informando a Issue correspondente (`Closes #...`).
4. Solicite a revisão do Tech Lead (`@minoruhaga`) ou de outro colega antes do merge.
