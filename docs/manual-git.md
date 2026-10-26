# Manual de Uso do Git - SIG-Reembolso

Este manual é um guia rápido para os integrantes da equipe realizarem operações de Git com segurança, mantendo o repositório organizado e sem perdas de código.

---

## 1. Verificando o Estado Atual

Para saber em qual branch você está:
```bash
git branch
```
A branch ativa é a que possui o símbolo `*` na frente.

Para verificar se você tem arquivos modificados ou novos que precisam de commit:
```bash
git status
```

---

## 2. Iniciando uma Nova Tarefa (Branch)

Antes de começar uma nova funcionalidade, atualize sua base local com a branch de integração (`dev`):
```bash
git checkout dev
git pull origin dev
```

Crie sua nova branch a partir da Issue que você pegou no GitHub Projects:
```bash
git checkout -b feature/#04-formulario-despesa-mobile
```

---

## 3. Registrando suas Alterações (Add e Commit)

Após editar os arquivos e rodar os testes localmente:

1. Adicione os arquivos alterados para o *staging*:
   ```bash
   git add .
   ```
   *(Ou adicione apenas os arquivos específicos: `git add src/apps/despesas/models.py`)*

2. Grave o commit com uma mensagem descritiva:
   ```bash
   git commit -m "feat(despesas): adiciona validacao de comprovante obrigatorio RN01"
   ```

---

## 4. Enviando suas Alterações para o GitHub (Push)

Na primeira vez que você for enviar uma branch nova:
```bash
git push -u origin feature/#04-formulario-despesa-mobile
```

Nas vezes seguintes na mesma branch, basta executar:
```bash
git push
```

---

## 5. Mantendo sua Branch Atualizada

Se outros colegas integraram código na branch `dev` enquanto você estava trabalhando, atualize a sua branch local para evitar conflitos no futuro:

```bash
git checkout feature/#04-formulario-despesa-mobile
git fetch origin dev
git merge origin/dev
```

Se houver conflitos, abra os arquivos sinalizados, resolva as marcações (`<<<<<<<` e `>>>>>>>`), rode os testes e faça um commit de resolução.

---

## 6. O que NUNCA Fazer
* ❌ **NUNCA** use `git push --force` na branch `main` ou `dev`.
* ❌ **NUNCA** comite senhas, chaves do Banco Cora ou arquivos `.env`.
* ❌ **NUNCA** edite migrações antigas que já foram enviadas para o repositório.
