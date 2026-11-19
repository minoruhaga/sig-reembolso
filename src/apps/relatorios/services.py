"""
Serviços de domínio para agregação contábil e exportação de relatórios (RF08).

- O que faz: Concentra as rotinas de consolidação financeira, balancetes por coordenação/categoria
  e geração de planilhas CSV para prestação de contas do AG VII.
- Como faz: Executa consultas ORM agregadas com precisão monetária estrita (`Decimal`) e aplica
  regras de visibilidade baseadas no papel do usuário (RBAC).
- Qual finalidade atende: Mantém as views e templates livres de lógica contábil conforme `src/AGENTS.md`
  e atende ao requisito RF08 para o fechamento financeiro do Grupo Escoteiro Caramuru.
"""
