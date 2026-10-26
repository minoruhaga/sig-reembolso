from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.despesas.models import CategoriaDespesa, Despesa, FormaPagamentoOriginal, StatusDespesa, TipoDespesa
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario


class Command(BaseCommand):
    help = 'Popula usuários de demonstração e despesas de exemplo baseadas no AG VI / AG VII (Grupo Escoteiro Caramuru)'

    def handle(self, *args, **options):
        self.stdout.write("Criando usuários de demonstração...")

        # 1. Admin Geral
        admin_user, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@caramuru.org.br',
                'first_name': 'Diretoria',
                'last_name': 'Geral',
                'papel': PapelUsuario.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("✓ Admin criado: admin / admin123"))

        # 2. Tesoureiro
        tesoureiro, created = Usuario.objects.get_or_create(
            username='tesoureiro',
            defaults={
                'email': 'tesouraria@caramuru.org.br',
                'first_name': 'Carlos',
                'last_name': 'Tesoureiro',
                'papel': PapelUsuario.TESOUREIRO,
                'chave_pix': 'tesouraria@caramuru.org.br',
                'is_staff': True,
            }
        )
        if created:
            tesoureiro.set_password('tesouraria123')
            tesoureiro.save()
            self.stdout.write(self.style.SUCCESS("✓ Tesoureiro criado: tesoureiro / tesouraria123"))

        # 3. Coordenador de Cozinha
        coord_cozinha, created = Usuario.objects.get_or_create(
            username='coord_cozinha',
            defaults={
                'email': 'cozinha@caramuru.org.br',
                'first_name': 'Mariana',
                'last_name': 'Cozinha',
                'papel': PapelUsuario.COORDENADOR,
                'chave_pix': 'mariana.pix@email.com',
                'telefone': '(11) 98765-4321',
            }
        )
        if created:
            coord_cozinha.set_password('cozinha123')
            coord_cozinha.save()
            self.stdout.write(self.style.SUCCESS("✓ Coordenador Cozinha: coord_cozinha / cozinha123"))

        # 4. Coordenador de Infraestrutura
        coord_infra, created = Usuario.objects.get_or_create(
            username='coord_infra',
            defaults={
                'email': 'infra@caramuru.org.br',
                'first_name': 'Roberto',
                'last_name': 'Infra',
                'papel': PapelUsuario.COORDENADOR,
                'chave_pix': 'roberto.infra@email.com',
                'telefone': '(11) 91234-5678',
            }
        )
        if created:
            coord_infra.set_password('infra123')
            coord_infra.save()
            self.stdout.write(self.style.SUCCESS("✓ Coordenador Infra: coord_infra / infra123"))

        # Despesas de Demonstração
        self.stdout.write("Criando despesas de teste com base na realidade de campo...")
        cozinha = Coordenacao.objects.filter(sigla='ALIM').first()
        infra = Coordenacao.objects.filter(sigla='INFRA').first()

        if cozinha and not Despesa.objects.filter(titulo__contains='Verduras e Legumes').exists():
            d1 = Despesa.objects.create(
                coordenacao=cozinha,
                solicitante=coord_cozinha,
                titulo='Verduras e Legumes Frescos (Sacolão Juquitiba)',
                descricao='Compra emergencial de 20kg de tomate, alface e cenoura para o almoço do dia 2.',
                categoria=CategoriaDespesa.ALIMENTACAO,
                tipo=TipoDespesa.REEMBOLSO,
                forma_pagamento_original=FormaPagamentoOriginal.PIX,
                valor=Decimal('342.50'),
                data_despesa=timezone.now().date(),
                status=StatusDespesa.PAGO,
                analisado_por=tesoureiro,
                analisado_em=timezone.now(),
                pago_por=tesoureiro,
                pago_em=timezone.now(),
            )
            d1._registrar_transicao('RASCUNHO', 'ENVIADO', coord_cozinha, 'Submissão de compra')
            d1._registrar_transicao('ENVIADO', 'APROVADO', tesoureiro, 'Nota fiscal conferida e aprovada')
            d1._registrar_transicao('APROVADO', 'PAGO', tesoureiro, 'Transferência PIX realizada via Banco Cora')

        if infra and not Despesa.objects.filter(titulo__contains='Óleo Diesel').exists():
            d2 = Despesa.objects.create(
                coordenacao=infra,
                solicitante=coord_infra,
                titulo='Óleo Diesel S10 para Grupo Gerador 1',
                descricao='Abastecimento emergencial de 60 litros de diesel para garantir refrigeração da cozinha.',
                categoria=CategoriaDespesa.COMBUSTIVEL,
                tipo=TipoDespesa.REEMBOLSO,
                forma_pagamento_original=FormaPagamentoOriginal.CARTAO_DEBITO,
                valor=Decimal('378.00'),
                data_despesa=timezone.now().date(),
                status=StatusDespesa.ENVIADO,
            )
            d2._registrar_transicao('RASCUNHO', 'ENVIADO', coord_infra, 'Submetido em campo')

        self.stdout.write(self.style.SUCCESS("Carga de dados de demonstração concluída com sucesso!"))
