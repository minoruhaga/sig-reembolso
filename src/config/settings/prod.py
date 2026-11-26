"""
Configurações de produção do SIG-Reembolso.

Exige chave secreta explícita via ambiente, desabilita modo debug, suporta
PostgreSQL via variáveis `POSTGRES_*` e ativa cabeçalhos/cookies seguros.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("A variável de ambiente DJANGO_SECRET_KEY é obrigatória em produção.")

DEBUG = False

allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]

if os.getenv('POSTGRES_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Endurecimento HTTP/Cookies em produção
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
