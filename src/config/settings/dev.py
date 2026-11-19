"""
Configurações de desenvolvimento local do SIG-Reembolso.

Ativa `DEBUG` configurável por ambiente, fallback de chave para desenvolvimento
e banco SQLite local para execução rápida pela equipe e testes automatizados.
"""

import os

from .base import *

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'sig-reembolso-dev-key-change-in-prod-fatec-les-2026')  # nosec B105

DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS')
if allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
