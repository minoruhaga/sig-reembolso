from django.urls import reverse

from apps.despesas.models import Despesa
from apps.financeiro.models import Coordenacao


def usuario_pode_acessar_admin(user) -> bool:
    """
    Decide se o usuário autenticado pode permanecer em rotas `/admin/`.

    - O que faz: Encapsula a autorização administrativa com base no papel do `Usuario`.
    - Como faz: Delega à propriedade `pode_acessar_admin` (Tesoureiro, Admin Geral ou superusuário).
    - Qual finalidade atende: Centraliza o critério de bloqueio do Django Admin para coordenadores de campo.
    """
    return bool(getattr(user, 'is_authenticated', False) and user.pode_acessar_admin)


def url_pos_login(user) -> str:
    """
    Escolhe a URL inicial após autenticação bem-sucedida conforme o papel.

    - O que faz: Retorna o destino pós-login sem consultar `next` (isso cabe à view).
    - Como faz: Administrador Geral vai para `admin:index`; Tesoureiro e Coordenador vão ao dashboard.
    - Qual finalidade atende: Cumpre o redirecionamento por papel da Issue #6 e evita que o coordenador
      caia no Admin por padrão.
    """
    if user.is_admin_geral:
        return reverse('admin:index')
    return reverse('dashboard')


def coordenacoes_visiveis(user):
    """
    Recorta o queryset de coordenações ativas ao escopo do papel do usuário.

    - O que faz: Tesoureiro e Admin veem todas as pastas ativas; Coordenador vê somente a sua.
    - Como faz: Filtra `Coordenacao.objects` por `ativo=True` e, se for coordenador, por `user.coordenacao_id`.
    - Qual finalidade atende: Impede vazamento de tetos e saldos das outras 14 pastas no painel de campo (RF01).
    """
    queryset = Coordenacao.objects.filter(ativo=True).order_by('nome')
    if usuario_pode_acessar_admin(user):
        return queryset
    if getattr(user, 'is_coordenador', False) and user.coordenacao_id:
        return queryset.filter(pk=user.coordenacao_id)
    return queryset.none()


def despesas_visiveis(user):
    """
    Recorta despesas ao mesmo escopo de coordenações visíveis do usuário.

    - O que faz: Lista despesas cuja coordenação onerada pertence ao recorte RBAC.
    - Como faz: Encadeia `select_related` e filtra `coordenacao` pelo resultado de `coordenacoes_visiveis`.
    - Qual finalidade atende: Mantém o histórico recente do dashboard coerente com a pasta do voluntário.
    """
    queryset = Despesa.objects.select_related('coordenacao', 'solicitante').order_by('-criado_em')
    if usuario_pode_acessar_admin(user):
        return queryset
    return queryset.filter(coordenacao__in=coordenacoes_visiveis(user))
