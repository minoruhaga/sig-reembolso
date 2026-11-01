from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView

from apps.usuarios.forms import LoginForm
from apps.usuarios.services import url_pos_login


class LoginView(DjangoLoginView):
    """
    Autentica voluntários e gestores na tela customizada do SIG-Reembolso.

    - O que faz: Processa o POST de login contra o modelo `Usuario` e redireciona conforme o papel.
    - Como faz: Reusa `django.contrib.auth.views.LoginView` com `LoginForm` e `get_success_url`
      baseado em `url_pos_login`, respeitando `next` seguro quando presente.
    - Qual finalidade atende: Substitui `/admin/login/` e cumpre o critério de redirect por papel (RF01).
    """

    template_name = 'usuarios/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        Define o destino após login bem-sucedido.

        - O que faz: Honra `next` validado pelo Django; se ausente, escolhe URL pelo papel.
        - Como faz: Chama `get_redirect_url()` e, se vazio, `url_pos_login(self.request.user)`.
        - Qual finalidade atende: Admin cai no painel Django; tesoureiro e coordenador no dashboard recortado.
        """
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        return url_pos_login(self.request.user)


class LogoutView(DjangoLogoutView):
    """
    Encerra a sessão autenticada e devolve o voluntário à tela de login.

    - O que faz: Invalida a sessão Django no POST de logout.
    - Como faz: Especializa `LogoutView` apontando `LOGOUT_REDIRECT_URL` já configurado.
    - Qual finalidade atende: Impede reuso da sessão em dispositivo compartilhado no campo.
    """

    http_method_names = ['post', 'options']
