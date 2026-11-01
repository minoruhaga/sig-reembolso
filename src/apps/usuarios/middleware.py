from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from apps.usuarios.services import usuario_pode_acessar_admin


class BloqueioAdminCoordenadorMiddleware:
    """
    Intercepta requisições ao Django Admin e aplica o RBAC do SIG-Reembolso.

    - O que faz: Redireciona anônimos ao login customizado e impede coordenadores autenticados de usar `/admin/`.
    - Como faz: Roda depois de `AuthenticationMiddleware`, testa o prefixo `/admin/` e consulta
      `usuario_pode_acessar_admin`.
    - Qual finalidade atende: Substitui o login nativo do Admin e bloqueia rotas administrativas para
      voluntários de campo (critério 2 da Issue #6).
    """

    def __init__(self, get_response):
        """
        Armazena o próximo handler da cadeia de middleware.

        - O que faz: Recebe o callable `get_response` padrão do Django.
        - Como faz: Guarda a referência para invocação em `__call__`.
        - Qual finalidade atende: Integra o bloqueio ao pipeline HTTP sem view dedicada.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Avalia cada request antes de chegar às views do Admin.

        - O que faz: Se o caminho começa com `/admin/`, exige usuário gestor; caso contrário, segue o fluxo.
        - Como faz: Anônimo vai para `usuarios:login` com `next`; coordenador autenticado vai ao dashboard
          com mensagem de aviso.
        - Qual finalidade atende: Garante um único ponto de autenticação e isola o Admin da operação de campo.
        """
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                login_url = reverse('usuarios:login')
                return redirect(f'{login_url}?next={request.get_full_path()}')
            if not usuario_pode_acessar_admin(request.user):
                messages.warning(
                    request,
                    'O painel administrativo é restrito à Tesouraria e à Diretoria. '
                    'Coordenadores de campo acompanham apenas a própria pasta.'
                )
                return redirect('dashboard')
        return self.get_response(request)
