from django.contrib.auth.models import AbstractUser
from django.db import models


class PapelUsuario(models.TextChoices):
    COORDENADOR = 'COORDENADOR', 'Coordenador de Área'
    TESOUREIRO = 'TESOUREIRO', 'Tesoureiro / Gestor Financeiro'
    ADMIN = 'ADMIN', 'Administrador Geral'


class Usuario(AbstractUser):
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
        nome_completo = self.get_full_name()
        return f"{nome_completo or self.username} ({self.get_papel_display()})"

    @property
    def is_coordenador(self):
        return self.papel == PapelUsuario.COORDENADOR

    @property
    def is_tesoureiro(self):
        return self.papel == PapelUsuario.TESOUREIRO or self.is_superuser

    @property
    def is_admin_geral(self):
        return self.papel == PapelUsuario.ADMIN or self.is_superuser
