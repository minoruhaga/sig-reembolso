from django.contrib.auth.models import AbstractUser
from django.db import models


class PapelUsuario(models.TextChoices):
    """
    Enumeração dos papéis de controle de acesso baseado em função (RBAC).

    - O que faz: Define os três níveis hierárquicos de permissão dos usuários no SIG-Reembolso.
    - Como faz: Utiliza `models.TextChoices` do Django para mapear constantes legíveis no banco de dados.
    - Qual finalidade atende: Sustenta o isolamento de visões entre voluntários de campo (Coordenadores),
      auditores financeiros (Tesoureiros) e a Diretoria do Grupo Escoteiro Caramuru (Admin).
    """

    COORDENADOR = 'COORDENADOR', 'Coordenador de Área'
    TESOUREIRO = 'TESOUREIRO', 'Tesoureiro / Gestor Financeiro'
    ADMIN = 'ADMIN', 'Administrador Geral'


class Usuario(AbstractUser):
    """
    Modelo customizado de usuário do SIG-Reembolso com suporte a RBAC e dados de liquidação PIX.

    - O que faz: Estende o usuário padrão do Django adicionando papel operacional, chave PIX e telefone.
    - Como faz: Herda de `AbstractUser` (configurado em `AUTH_USER_MODEL`) e expõe propriedades booleanas
      auxiliares para verificação rápida de permissões nas views e templates.
    - Qual finalidade atende: Permite identificar o solicitante de cada reembolso em campo, viabilizar a
      transferência bancária pelo Banco Cora PJ via chave PIX e aplicar a segregação de funções (RN03).
    """

    papel = models.CharField(
        max_length=20,
        choices=PapelUsuario.choices,
        default=PapelUsuario.COORDENADOR,
        verbose_name='Papel no Sistema'
    )
    chave_pix = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Chave PIX para Reembolso'
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone de Contato'
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        """
        Retorna a representação textual amigável do usuário.

        - O que faz: Formata o nome completo (ou username) acompanhado da descrição do seu papel.
        - Como faz: Consulta `get_full_name()` e `get_papel_display()` do modelo Django.
        - Qual finalidade atende: Facilita a identificação rápida de voluntários e tesoureiros em listagens e logs de auditoria.
        """
        nome_completo = self.get_full_name()
        return f"{nome_completo or self.username} ({self.get_papel_display()})"

    @property
    def is_coordenador(self):
        """
        Verifica se o usuário possui perfil de Coordenador de Área.

        - O que faz: Retorna `True` caso o papel atribuído seja `COORDENADOR`.
        - Como faz: Compara o atributo `self.papel` com a constante `PapelUsuario.COORDENADOR`.
        - Qual finalidade atende: Restringe a visualização e submissão de despesas apenas à área operacional do voluntário.
        """
        return self.papel == PapelUsuario.COORDENADOR

    @property
    def is_tesoureiro(self):
        """
        Verifica se o usuário possui privilégios de Tesouraria para triagem e liquidação.

        - O que faz: Retorna `True` caso o usuário seja Tesoureiro ou Superusuário.
        - Como faz: Avalia `self.papel == PapelUsuario.TESOUREIRO` ou a flag nativa `self.is_superuser`.
        - Qual finalidade atende: Protege as rotas de aprovação, rejeição e pagamento de reembolsos no painel financeiro.
        """
        return self.papel == PapelUsuario.TESOUREIRO or self.is_superuser

    @property
    def is_admin_geral(self):
        """
        Verifica se o usuário faz parte da Diretoria / Administração Geral do evento.

        - O que faz: Retorna `True` caso o usuário tenha papel `ADMIN` ou seja `is_superuser`.
        - Como faz: Compara `self.papel` com `PapelUsuario.ADMIN` combinado com `self.is_superuser`.
        - Qual finalidade atende: Garante governança administrativa sobre tetos orçamentários e cadastros mestres do AG VII.
        """
        return self.papel == PapelUsuario.ADMIN or self.is_superuser
