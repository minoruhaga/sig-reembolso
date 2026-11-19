#!/nix/store/9ka5lknbqqg6nzs3zp6qyncf1k3ayz97-python3-3.12.14/bin/python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """
    Executa utilitários administrativos e comandos de gerenciamento do Django.

    - O que faz: Inicializa a variável `DJANGO_SETTINGS_MODULE` apontando para `config.settings.dev`
      por padrão e delega a execução dos subcomandos CLI ao núcleo do Django.
    - Como faz: Configura `os.environ.setdefault` antes de importar e chamar `execute_from_command_line`.
    - Qual finalidade atende: Garante execução padronizada de migrações, testes e servidor local em `src/`.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
