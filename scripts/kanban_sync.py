#!/usr/bin/env python3
"""
Script de sincronização automática entre Issues, Pull Requests e o GitHub Projects (Kanban).

- O que faz: Atualiza dinamicamente as colunas do quadro Kanban (Todo, In Progress, Review, Done)
  no GitHub Projects v2 quando Pull Requests ou Issues são abertos, vinculados ou encerrados,
  mesmo quando os PRs são direcionados para branches de integração contínua (como `dev`).
- Como faz: Inspeciona o evento do GitHub Actions via `GITHUB_EVENT_PATH` ou argumentos CLI; utiliza
  a API GraphQL do GitHub através da ferramenta `gh` para localizar o projeto vinculado ao repositório,
  descobrir as opções do campo 'Status' e aplicar mutações atômicas de transição de card (`addProjectV2ItemById`
  e `updateProjectV2ItemFieldValue`). Extrai referências de issues (`Closes #ID`) do corpo do PR via regex.
- Qual finalidade atende: Resolve a limitação nativa do GitHub Projects v2 que não move issues automaticamente
  para 'Review' quando PRs são abertos contra a branch `dev` (apenas contra `main`), garantindo governança
  e transparência em tempo real para a banca e para os integrantes do SIG-Reembolso.
"""

import json
import os
import re
import subprocess
import sys


def executar_graphql(query: str) -> dict:
    """
    Executa uma consulta ou mutação GraphQL via GitHub CLI (`gh api graphql`).

    - O que faz: Envia a requisição GraphQL autenticada para a API do GitHub e retorna o payload decodificado.
    - Como faz: Utiliza `subprocess.run` chamando `gh api graphql -f query=...` com captura de stdout e stderr.
    - Qual finalidade atende: Fornece o canal de comunicação direto com o GitHub Projects v2.
    """
    cmd = ['gh', 'api', 'graphql', '-f', f'query={query}']
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"Erro na API GraphQL do GitHub: {resultado.stderr.strip()}")
    return json.loads(resultado.stdout)


def obter_metadados_projeto(owner: str, repo: str) -> tuple[str, str, dict[str, str]]:
    """
    Localiza o GitHub Project v2 vinculado ao repositório e mapeia as opções do campo 'Status'.

    - O que faz: Descobre o ID do projeto, o ID do campo 'Status' e o dicionário de opções (Todo, Review, etc.).
    - Como faz: Executa query GraphQL em `repository.projectsV2` filtrando o campo do tipo `ProjectV2SingleSelectField`.
    - Qual finalidade atende: Evita IDs fixos (hardcoded), tornando o script resiliente a alterações de configuração.
    """
    query = f"""
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        projectsV2(first: 5) {{
          nodes {{
            id
            title
            fields(first: 20) {{
              nodes {{
                ... on ProjectV2SingleSelectField {{
                  id
                  name
                  options {{
                    id
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """
    data = executar_graphql(query)
    projetos = data.get('data', {}).get('repository', {}).get('projectsV2', {}).get('nodes', [])
    if not projetos:
        raise RuntimeError(f"Nenhum GitHub Project v2 vinculado ao repositório {owner}/{repo}.")

    projeto = projetos[0]
    proj_id = projeto['id']

    status_field = next(
        (f for f in projeto['fields']['nodes'] if f.get('name') == 'Status'),
        None
    )
    if not status_field:
        raise RuntimeError("Campo 'Status' não localizado no projeto.")

    status_field_id = status_field['id']
    opcoes = {opt['name']: opt['id'] for opt in status_field['options']}

    return proj_id, status_field_id, opcoes


def adicionar_e_mover_card(proj_id: str, content_id: str, status_field_id: str, option_id: str) -> str:
    """
    Adiciona um item (Issue ou PR) ao projeto e move para a coluna desejada.

    - O que faz: Garante a presença do item no quadro e atualiza seu status para o option_id informado.
    - Como faz: Executa `addProjectV2ItemById` (idempotente) e em seguida `updateProjectV2ItemFieldValue`.
    - Qual finalidade atende: Garante que o card seja movido para o status correto no Kanban.
    """
    # 1. Adiciona item ao projeto (se já existir, retorna o item existente)
    m_add = f"""
    mutation {{
      addProjectV2ItemById(input: {{ projectId: "{proj_id}", contentId: "{content_id}" }}) {{
        item {{
          id
        }}
      }}
    }}
    """
    res_add = executar_graphql(m_add)
    item_id = res_add['data']['addProjectV2ItemById']['item']['id']

    # 2. Atualiza o status
    m_update = f"""
    mutation {{
      updateProjectV2ItemFieldValue(input: {{
        projectId: "{proj_id}",
        itemId: "{item_id}",
        fieldId: "{status_field_id}",
        value: {{ singleSelectOptionId: "{option_id}" }}
      }}) {{
        projectV2Item {{
          id
        }}
      }}
    }}
    """
    executar_graphql(m_update)
    return item_id


def obter_node_id_issue(owner: str, repo: str, numero_issue: int) -> str:
    """
    Obtém o Node ID global de uma Issue pelo seu número.
    """
    query = f"""
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        issue(number: {numero_issue}) {{
          id
        }}
      }}
    }}
    """
    data = executar_graphql(query)
    issue_data = data.get('data', {}).get('repository', {}).get('issue')
    if not issue_data:
        raise ValueError(f"Issue #{numero_issue} não encontrada no repositório.")
    return issue_data['id']


def extrair_issues_vinculadas(texto: str) -> list[int]:
    """
    Extrai números de issues referenciadas em strings (título, branch ou corpo de PR).
    Suporta sintaxes como 'Closes #7', 'Fixes #12', 'Resolves #5' e referências '#7'.
    """
    if not texto:
        return []
    # 1. Padrão com palavras-chave de fechamento
    padrao_fechamento = re.findall(
        r'(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)\s*#(\d+)',
        texto,
        re.IGNORECASE
    )
    if padrao_fechamento:
        return sorted(list({int(num) for num in padrao_fechamento}))

    # 2. Fallback para menções diretas com hashtag
    mencoes = re.findall(r'#(\d+)', texto)
    return sorted(list({int(num) for num in mencoes}))


def sincronizar_kanban():
    """
    Orquestra a leitura do evento e sincronização dos itens no Kanban.
    """
    repo_completo = os.environ.get('GITHUB_REPOSITORY', 'minoruhaga/sig-reembolso')
    owner, repo = repo_completo.split('/')

    event_path = os.environ.get('GITHUB_EVENT_PATH')
    event_name = os.environ.get('GITHUB_EVENT_NAME')

    if not event_path or not os.path.exists(event_path):
        print(f"Execução local ou sem GITHUB_EVENT_PATH. Conectando ao repositório {owner}/{repo}...")
        proj_id, status_field_id, opcoes = obter_metadados_projeto(owner, repo)
        print(f"Projeto localizado: {proj_id}")
        print(f"Opções disponíveis: {list(opcoes.keys())}")
        return

    with open(event_path, 'r', encoding='utf-8') as f:
        event = json.load(f)

    action = event.get('action')
    print(f"Processando evento '{event_name}' com ação '{action}'...")

    proj_id, status_field_id, opcoes = obter_metadados_projeto(owner, repo)

    # Caso 1: Eventos de Pull Request
    if event_name == 'pull_request':
        pr = event.get('pull_request', {})
        pr_node_id = pr.get('node_id')
        pr_number = pr.get('number')
        pr_body = pr.get('body', '') or ''
        pr_title = pr.get('title', '') or ''
        is_merged = pr.get('merged', False)

        issues_referenciadas = extrair_issues_vinculadas(f"{pr_title}\n{pr_body}")

        if action in ('opened', 'reopened', 'ready_for_review'):
            alvo = 'Review'
            if alvo in opcoes:
                option_id = opcoes[alvo]
                print(f"Movendo PR #{pr_number} para '{alvo}'...")
                adicionar_e_mover_card(proj_id, pr_node_id, status_field_id, option_id)

                for issue_num in issues_referenciadas:
                    try:
                        issue_node_id = obter_node_id_issue(owner, repo, issue_num)
                        print(f"Movendo Issue #{issue_num} vinculada ao PR para '{alvo}'...")
                        adicionar_e_mover_card(proj_id, issue_node_id, status_field_id, option_id)
                    except Exception as e:
                        print(f"Aviso ao atualizar Issue #{issue_num}: {e}")

        elif action == 'closed':
            alvo = 'Done' if is_merged else 'Todo'
            if alvo in opcoes:
                option_id = opcoes[alvo]
                print(f"PR #{pr_number} fechado (merged={is_merged}). Movendo para '{alvo}'...")
                adicionar_e_mover_card(proj_id, pr_node_id, status_field_id, option_id)

                if is_merged:
                    for issue_num in issues_referenciadas:
                        try:
                            issue_node_id = obter_node_id_issue(owner, repo, issue_num)
                            print(f"Movendo Issue #{issue_num} para '{alvo}'...")
                            adicionar_e_mover_card(proj_id, issue_node_id, status_field_id, option_id)
                        except Exception as e:
                            print(f"Aviso ao atualizar Issue #{issue_num}: {e}")

    # Caso 2: Eventos de Issues
    elif event_name == 'issues':
        issue = event.get('issue', {})
        issue_node_id = issue.get('node_id')
        issue_number = issue.get('number')

        if action in ('opened', 'reopened'):
            alvo = 'Todo'
            if alvo in opcoes:
                print(f"Movendo nova Issue #{issue_number} para '{alvo}'...")
                adicionar_e_mover_card(proj_id, issue_node_id, status_field_id, opcoes[alvo])

        elif action == 'closed':
            alvo = 'Done'
            if alvo in opcoes:
                print(f"Issue #{issue_number} fechada. Movendo para '{alvo}'...")
                adicionar_e_mover_card(proj_id, issue_node_id, status_field_id, opcoes[alvo])


if __name__ == '__main__':
    try:
        sincronizar_kanban()
        print("Sincronização do Kanban finalizada com sucesso.")
    except Exception as erro:
        print(f"Erro na execução da sincronização do Kanban: {erro}", file=sys.stderr)
        sys.exit(1)
