## Descrição da Mudança
<!-- Descreva de forma clara o que foi alterado nesta branch e qual funcionalidade foi implementada -->

Issue Relacionada: Closes #

## Tipo de Mudança
- [ ] Nova funcionalidade (`feat`)
- [ ] Correção de bug (`fix`)
- [ ] Refatoração de código (`refactor`)
- [ ] Documentação ou testes (`docs`, `test`)

## Checklist de Qualidade e Governança
- [ ] O código respeita as regras do `AGENTS.md` e `src/AGENTS.md`.
- [ ] Funções e classes possuem docstrings (O que faz, Como faz, Qual finalidade atende).
- [ ] Operações financeiras e transições de estado usam `Decimal` e `@transaction.atomic`.
- [ ] As migrações do Django foram criadas e testadas localmente (`python manage.py makemigrations`).
- [ ] Os testes unitários existentes e novos passaram com sucesso (`python manage.py test src/apps`).
- [ ] O linter não reportou erros (`ruff check src`).
- [ ] Nenhuma credencial ou segredo foi incluído no commit.
