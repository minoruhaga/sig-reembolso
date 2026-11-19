"""
Ponto de entrada retrocompatível para o pacote de configurações do SIG-Reembolso.

Seleciona `config.settings.prod` quando `DJANGO_ENV=prod` e `config.settings.dev` por padrão,
garantindo compatibilidade com `DJANGO_SETTINGS_MODULE=config.settings`.
"""

import os

if os.getenv('DJANGO_ENV') == 'prod':
    from .prod import *
else:
    from .dev import *
