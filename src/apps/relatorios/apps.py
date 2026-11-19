from django.apps import AppConfig


class RelatoriosConfig(AppConfig):
    """
    Configuração do aplicativo Django responsável pelos relatórios contábeis e exportações (RF08).

    - O que faz: Registra o app `apps.relatorios` no ecossistema Django e define metadados de exibição no Admin.
    - Como faz: Especializa `django.apps.AppConfig` configurando `name = 'apps.relatorios'` e `default_auto_field`.
    - Qual finalidade atende: Organiza e isola o módulo de prestação de contas (CSV e balancetes) do AG VII,
      permitindo desenvolvimento paralelo sem conflitos de merge.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.relatorios'
    verbose_name = 'Relatórios e Prestação de Contas'
