from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """
    Formulário de autenticação visualmente alinhado ao Bootstrap 5 do SIG-Reembolso.

    - O que faz: Autentica o modelo `Usuario` com os campos nativos username/senha.
    - Como faz: Especializa `AuthenticationForm` e aplica classes CSS nos widgets, sem alterar a
      validação de credenciais do Django.
    - Qual finalidade atende: Oferece tela de entrada utilizável no celular em campo, no lugar do
      formulário padrão do Django Admin.
    """

    def __init__(self, *args, **kwargs):
        """
        Configura rótulos em português e classes Bootstrap nos campos.

        - O que faz: Ajusta `username` e `password` após a inicialização da superclasse.
        - Como faz: Define `widget.attrs` com `form-control` e placeholders.
        - Qual finalidade atende: Reduz fricção de login para voluntários sob conexão limitada.
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuário'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Seu usuário',
            'autocomplete': 'username',
            'autofocus': True,
        })
        self.fields['password'].label = 'Senha'
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Sua senha',
            'autocomplete': 'current-password',
        })
