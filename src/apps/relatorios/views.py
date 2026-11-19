"""
Views orquestradoras para visualização de balancetes e download de exportações contábeis (RF08).

- O que faz: Recebe requisições HTTP autenticadas de exportação CSV e balancetes sintéticos,
  delegando cálculos e filtragens para `apps.relatorios.services`.
- Como faz: Aplica proteção de sessão/RBAC e retorna respostas de download (`HttpResponse` CSV) ou
  renderiza templates de prestação de contas sem conter lógica de negócio direta.
- Qual finalidade atende: Viabiliza o cumprimento da entrega do módulo de relatórios (Issue #34)
  seguindo estritamente a separação de camadas definida em `src/AGENTS.md`.
"""
