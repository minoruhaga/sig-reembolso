from django.apps import apps
from django.test import TestCase


class RelatoriosAppConfigTestCase(TestCase):
    """
    Testes de registro e integridade estrutural do aplicativo `apps.relatorios`.

    - O que faz: Valida que o app de relatórios está corretamente registrado em `INSTALLED_APPS`
      e acessível pelo registro central de aplicações do Django.
    - Como faz: Consulta `django.apps.apps.is_installed` e `apps.get_app_config('relatorios')`.
    - Qual finalidade atende: Garante que o esqueleto criado para a frente de relatórios (Issue #34)
      esteja íntegro e pronto para receber os serviços e rotas de exportação RF08.
    """

    def test_app_relatorios_esta_instalado_e_configurado(self):
        """
        Verifica se `apps.relatorios` está instalado e com `name` esperado no registry do Django.

        - O que faz: Confirma a presença de `apps.relatorios` e valida `AppConfig.name`.
        - Como faz: Executa `assertTrue(apps.is_installed('apps.relatorios'))` e compara `config.name`.
        - Qual finalidade atende: Previne falhas silenciosas de importação ou configuração antes da entrega RF08.
        """
        self.assertTrue(apps.is_installed('apps.relatorios'))
        app_config = apps.get_app_config('relatorios')
        self.assertEqual(app_config.name, 'apps.relatorios')
