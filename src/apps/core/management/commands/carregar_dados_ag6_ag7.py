import csv
import datetime
import re
import unicodedata
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.despesas.models import (
    CategoriaDespesa,
    Despesa,
    FormaPagamentoOriginal,
    StatusDespesa,
    TipoDespesa,
)
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario

MAPA_AREA_SIGLA = {
    'Geral/Programação': 'GERAL',
    'Captação': 'CAPT',
    'Financeiro': 'FIN',
    'Transporte': 'TRANS',
    'Inscrição': 'INSC',
    'Decoração': 'DECO',
    'Atividades': 'ATIV',
    'Divulgação': 'DIV',
    'Música': 'MUS',
    'Alimentação': 'ALIM',
    'Logist. Materiais': 'LOG',
    'Infra': 'INFRA',
    'Sustentabilidade': 'SUST',
    'Saúde e Bem Estar': 'SAUDE',
    'Som': 'SOM',
}


def _normalizar_slug(texto: str) -> str:
    """
    Converte um texto com acentos e espaços em identificador ASCII minúsculo.

    - O que faz: Remove acentuação Unicode e caracteres especiais para compor usernames determinísticos.
    - Como faz: Normaliza em NFKD, descarta marcas combinantes e substitui não-alfanuméricos por `_`.
    - Qual finalidade atende: Garante usernames únicos e válidos no Django para voluntários do AG VII.
    """
    sem_acentos = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^a-z0-9]+', '_', sem_acentos.lower()).strip('_')
    return slug or 'voluntario'


def _parse_valor_brl(texto: str) -> Decimal | None:
    """
    Converte valores monetários formatados em Real brasileiro (ex: 'R$ 1.557,22') para `Decimal`.

    - O que faz: Interpreta strings monetárias pt-BR retornando um `Decimal` exato ou `None` se vazio.
    - Como faz: Remove prefixo 'R$', espaços e separadores de milhar ('.'), troca vírgula decimal por ponto
      e instancia `Decimal` sem passar por `float`.
    - Qual finalidade atende: Preserva exatidão de centavos exigida por `src/AGENTS.md` ao importar CSVs do AG VI.
    """
    if not texto:
        return None
    limpo = texto.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
    if not limpo:
        return None
    try:
        valor = Decimal(limpo)
        return valor if valor > Decimal('0.00') else None
    except InvalidOperation:
        return None


def _parse_data_br(texto: str) -> datetime.date:
    """
    Converte datas no formato 'DD/MM/YY' ou 'DD/MM/YYYY' para `datetime.date`.

    - O que faz: Realiza parsing defensivo de datas presentes nas planilhas históricas do AG VI.
    - Como faz: Tenta `strptime` com `%d/%m/%y` e `%d/%m/%Y`, usando `2023-01-15` como fallback seguro.
    - Qual finalidade atende: Garante que registros históricos sem data explícita ainda atendam ao schema ORM.
    """
    if texto:
        for fmt in ('%d/%m/%y', '%d/%m/%Y'):
            try:
                return datetime.datetime.strptime(texto.strip(), fmt).date()
            except ValueError:
                continue
    return datetime.date(2023, 1, 15)


def _gerar_bytes_comprovante_padrao() -> bytes:
    """
    Gera em memória os bytes de um cupom fiscal simulado legível para lastro documental de importações.

    - O que faz: Produz um payload JPEG válido simulando cupom fiscal para representar notas da carga AG VI/VII.
    - Como faz: Delega a renderização para `gerar_imagem_cupom_simulado` uma única vez por execução do comando.
    - Qual finalidade atende: Satisfaz `RN01` e `full_clean()` sem reprocessar imagens dezenas de vezes e exibe
      imagem legível ao inspecionar notas históricas no modal de zoom da Auditoria.
    """
    from apps.core.services import gerar_imagem_cupom_simulado

    return gerar_imagem_cupom_simulado(
        titulo='Despesa Historica AG VI / AG VII',
        valor='Conforme lancamento',
        data='2026',
        tipo_doc='CUPOM FISCAL - HISTORICO',
    )


def _criar_anexo_uuid(bytes_jpeg: bytes) -> ContentFile:
    """
    Encapsula os bytes JPEG em `ContentFile` com nome UUID v4 marcado como já otimizado.

    - O que faz: Cria um arquivo em memória pronto para persistência no campo `comprovante` ou `comprovante_pagamento`.
    - Como faz: Gera nome `{uuid4().hex}.jpg` e marca `_otimizado_pillow = True` para evitar recompressão no `save()`.
    - Qual finalidade atende: Cumpre `RNF04` (UUID v4) e acelera a carga em lote mantendo conformidade com `RN01`.
    """
    anexo = ContentFile(bytes_jpeg, name=f"{uuid.uuid4().hex}.jpg")
    anexo._otimizado_pillow = True
    return anexo


class Command(BaseCommand):
    """
    Comando de gerenciamento Django para carga idempotente de dados reais do AG VI e AG VII.

    - O que faz: Popula as 15 coordenações oficiais, os voluntários/coordenadores nominais do AG VII
      (`coordenadores_ag7.csv`) e as despesas históricas de Alimentação (`alimentacao_gastos_ag6.csv`) e
      Saúde/Caixa Médica (`saude_e_bem_estar_caixa_medica_ag6.csv`) do AG VI.
    - Como faz: Carrega a fixture `coordenacoes_iniciais.json` caso necessário, realiza parsing defensivo
      dos 3 CSVs sob `@transaction.atomic`, cria usuários e despesas de forma idempotente utilizando `Decimal`,
      valida cada lançamento com `full_clean()` e grava trilhas de auditoria em `HistoricoTransicaoStatus`.
    - Qual finalidade atende: Entrega a massa realista exigida pela Issue #9 para demonstração à banca,
      cálculo de indicadores e testes operacionais do SIG-Reembolso.
    """

    help = 'Carrega de forma idempotente os coordenadores do AG VII e os gastos históricos do AG VI (CSV).'

    def add_arguments(self, parser):
        """
        Registra argumentos opcionais para diretório de referências e senha inicial de voluntários.

        - O que faz: Permite sobrescrever o caminho dos CSVs ou a senha inicial em testes automatizados.
        - Como faz: Adiciona `--referencias-dir` e `--senha-padrao` ao parser de argumentos do Django.
        - Qual finalidade atende: Facilita testes isolados e flexibilidade operacional em diferentes ambientes.
        """
        parser.add_argument(
            '--referencias-dir',
            type=str,
            default=None,
            help='Caminho alternativo para a pasta de referências contendo os CSVs do AG VI e AG VII.',
        )
        parser.add_argument(
            '--senha-padrao',
            type=str,
            default='ag7caramuru2026',
            help='Senha inicial atribuída aos usuários recém-criados pela carga.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Executa a importação completa das 15 coordenações, coordenadores AG VII e despesas AG VI.

        - O que faz: Orquestra a leitura das fixtures e dos três arquivos CSV garantindo atomicidade e idempotência.
        - Como faz: Opera dentro de `@transaction.atomic`; garante coordenações via `loaddata`; importa coordenadores;
          importa despesas de Alimentação (`ALIM`) e Saúde (`SAUDE`) com `full_clean()` e auditoria `RN06`.
        - Qual finalidade atende: Cumpre os critérios de aceitação da Issue #9 sem gerar registros duplicados.
        """
        raiz_repo = Path(settings.BASE_DIR).parent
        referencias_dir = (
            Path(options['referencias_dir'])
            if options.get('referencias_dir')
            else raiz_repo / 'docs' / 'referencias'
        )
        senha_padrao = options['senha_padrao']

        if (
            Coordenacao.objects.count() < 15
            or not Coordenacao.objects.filter(sigla='FIN').exists()
            or Coordenacao.objects.filter(sigla='ALIM', nome='Alimentação e Cozinha Central').exists()
        ):
            fixture_path = Path(settings.BASE_DIR) / 'fixtures' / 'coordenacoes_iniciais.json'
            if fixture_path.exists():
                call_command('loaddata', str(fixture_path), verbosity=0)

        mapa_coords = {c.sigla: c for c in Coordenacao.objects.all()}
        bytes_jpeg = _gerar_bytes_comprovante_padrao()

        qtd_users, tesoureiro_padrao = self._carregar_coordenadores_ag7(
            referencias_dir / 'coordenadores_ag7.csv',
            mapa_coords,
            senha_padrao,
        )
        qtd_alim = self._carregar_gastos_alimentacao_ag6(
            referencias_dir / 'gastos_historicos_ag6' / 'alimentacao_gastos_ag6.csv',
            mapa_coords.get('ALIM'),
            tesoureiro_padrao,
            bytes_jpeg,
        )
        qtd_saude = self._carregar_gastos_saude_ag6(
            referencias_dir / 'gastos_historicos_ag6' / 'saude_e_bem_estar_caixa_medica_ag6.csv',
            mapa_coords.get('SAUDE'),
            tesoureiro_padrao,
            bytes_jpeg,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Carga AG VI/AG VII concluída: {qtd_users} novos coordenadores, "
                f"{qtd_alim} despesas de Alimentação e {qtd_saude} despesas de Saúde inseridas."
            )
        )

    def _carregar_coordenadores_ag7(self, csv_path: Path, mapa_coords: dict, senha_padrao: str) -> tuple[int, Usuario]:
        """
        Importa os coordenadores e membros da equipe do AG VII a partir de `coordenadores_ag7.csv`.

        - O que faz: Lê os três blocos de pilares (Administrativo, Produção e Técnico) e cria usuários RBAC.
        - Como faz: Mapeia cada coluna de área via `MAPA_AREA_SIGLA`, gera username determinístico
          `ag7_<nome>_<sigla>` e define papel `TESOUREIRO` para a pasta Financeiro (`FIN`).
        - Qual finalidade atende: Cadastra os voluntários reais do AG VII vinculados às respectivas áreas.
        """
        criados = 0
        tesoureiro_ref = Usuario.objects.filter(papel=PapelUsuario.TESOUREIRO).first()

        if csv_path.exists():
            with csv_path.open('r', encoding='utf-8-sig', newline='') as f:
                leitor = csv.reader(f)
                linhas = list(leitor)

            for linha in linhas[2:]:
                blocos = [(1, 2, 3), (5, 6, 7), (9, 10, 11)]
                for idx_nome, idx_area, idx_tel in blocos:
                    if len(linha) <= idx_tel:
                        continue
                    nome = linha[idx_nome].strip()
                    area = linha[idx_area].strip()
                    telefone = linha[idx_tel].strip()
                    if not nome or not area:
                        continue

                    sigla = MAPA_AREA_SIGLA.get(area)
                    coord = mapa_coords.get(sigla)
                    if not coord:
                        continue

                    username = f"ag7_{_normalizar_slug(nome)}_{sigla.lower()}"[:150]
                    is_financeiro = sigla == 'FIN'
                    papel = PapelUsuario.TESOUREIRO if is_financeiro else PapelUsuario.COORDENADOR

                    usuario, created = Usuario.objects.get_or_create(
                        username=username,
                        defaults={
                            'first_name': nome[:150],
                            'papel': papel,
                            'coordenacao': coord,
                            'telefone': telefone[:20],
                            'is_staff': is_financeiro,
                        },
                    )
                    if created:
                        usuario.set_password(senha_padrao)
                        usuario.save(update_fields=['password'])
                        criados += 1
                    elif usuario.coordenacao_id != coord.id or usuario.telefone != telefone[:20]:
                        usuario.coordenacao = coord
                        usuario.telefone = telefone[:20]
                        usuario.save(update_fields=['coordenacao', 'telefone'])

                    if is_financeiro and tesoureiro_ref is None:
                        tesoureiro_ref = usuario

        if tesoureiro_ref is None:
            tesoureiro_ref, created = Usuario.objects.get_or_create(
                username='ag7_tesouraria_sistema',
                defaults={
                    'first_name': 'Tesouraria',
                    'last_name': 'AG VII',
                    'papel': PapelUsuario.TESOUREIRO,
                    'coordenacao': mapa_coords.get('FIN'),
                    'is_staff': True,
                },
            )
            if created:
                tesoureiro_ref.set_password(senha_padrao)
                tesoureiro_ref.save(update_fields=['password'])

        return criados, tesoureiro_ref

    def _obter_solicitante_pasta(self, coord: Coordenacao, tesoureiro_ref: Usuario) -> Usuario:
        """
        Seleciona um coordenador vinculado à coordenação informada (distinto do tesoureiro liquidante).

        - O que faz: Busca um membro da pasta para atuar como solicitante das despesas importadas.
        - Como faz: Consulta `Usuario.objects.filter(coordenacao=coord)` excluindo `tesoureiro_ref`; se não houver,
          cria um coordenador padrão da pasta de forma idempotente.
        - Qual finalidade atende: Garante respeito estrito à segregação de funções (`RN03`) mesmo nos dados históricos.
        """
        solicitante = (
            Usuario.objects.filter(coordenacao=coord)
            .exclude(pk=tesoureiro_ref.pk)
            .order_by('id')
            .first()
        )
        if solicitante:
            return solicitante

        username = f"ag7_coord_{coord.sigla.lower()}"
        solicitante, created = Usuario.objects.get_or_create(
            username=username,
            defaults={
                'first_name': f'Coordenação {coord.sigla}',
                'papel': PapelUsuario.COORDENADOR,
                'coordenacao': coord,
            },
        )
        if created:
            solicitante.set_unusable_password()
            solicitante.save(update_fields=['password'])
        return solicitante

    def _persistir_despesa_historica(
        self,
        *,
        coordenacao: Coordenacao,
        solicitante: Usuario,
        tesoureiro: Usuario,
        titulo: str,
        descricao: str,
        categoria: str,
        tipo: str,
        valor: Decimal,
        data_despesa: datetime.date,
        status_final: str,
        bytes_jpeg: bytes,
    ) -> bool:
        """
        Persiste de maneira idempotente uma despesa histórica validada com `full_clean()` e auditoria `RN06`.

        - O que faz: Evita duplicação por `(coordenacao, titulo)` e grava despesa com comprovante válido e histórico.
        - Como faz: Verifica existência prévia; instancia `Despesa` com `_criar_anexo_uuid`; executa `full_clean()` e
          `save()`; cria entradas na trilha `HistoricoTransicaoStatus` até `status_final`.
        - Qual finalidade atende: Assegura conformidade integral com `RN01`, `RN03`, `RN05` e `RN06` na carga histórica.
        """
        titulo_limitado = titulo[:150]
        if Despesa.objects.filter(coordenacao=coordenacao, titulo=titulo_limitado).exists():
            return False

        agora = datetime.datetime.now(datetime.timezone.utc)
        kwargs_status = {}
        if status_final == StatusDespesa.PAGO:
            kwargs_status = {
                'analisado_por': tesoureiro,
                'analisado_em': agora,
                'pago_por': tesoureiro,
                'pago_em': agora,
                'comprovante_pagamento': _criar_anexo_uuid(bytes_jpeg),
            }

        despesa = Despesa(
            coordenacao=coordenacao,
            solicitante=solicitante,
            titulo=titulo_limitado,
            descricao=descricao,
            categoria=categoria,
            tipo=tipo,
            forma_pagamento_original=FormaPagamentoOriginal.PIX,
            valor=valor,
            data_despesa=data_despesa,
            comprovante=_criar_anexo_uuid(bytes_jpeg),
            status=status_final,
            **kwargs_status,
        )
        despesa.full_clean()
        despesa.save()

        despesa._registrar_transicao(StatusDespesa.RASCUNHO, StatusDespesa.ENVIADO, solicitante, 'Carga histórica AG VI')
        if status_final == StatusDespesa.PAGO:
            despesa._registrar_transicao(
                StatusDespesa.ENVIADO,
                StatusDespesa.APROVADO,
                tesoureiro,
                'Aprovado em carga histórica AG VI',
            )
            despesa._registrar_transicao(
                StatusDespesa.APROVADO,
                StatusDespesa.PAGO,
                tesoureiro,
                'Liquidado em carga histórica AG VI',
            )
        return True

    def _carregar_gastos_alimentacao_ag6(
        self,
        csv_path: Path,
        coord_alim: Coordenacao | None,
        tesoureiro: Usuario,
        bytes_jpeg: bytes,
    ) -> int:
        """
        Importa os gastos reais de Alimentação do AG VI (`alimentacao_gastos_ag6.csv`).

        - O que faz: Lê compras históricas (Assaí Atacadista, CEAGESP, Sacolão, etc.) e cria `Despesa` em `ALIM`.
        - Como faz: Converte valores com `_parse_valor_brl` e datas com `_parse_data_br`, ignora linhas sem valor
          monetário e delega a persistência idempotente a `_persistir_despesa_historica`.
        - Qual finalidade atende: Popula o histórico real da cozinha e alimentação exigido pela Issue #9.
        """
        if not coord_alim or not csv_path.exists():
            return 0

        solicitante = self._obter_solicitante_pasta(coord_alim, tesoureiro)
        inseridas = 0

        with csv_path.open('r', encoding='utf-8-sig', newline='') as f:
            linhas = list(csv.reader(f))

        for idx, linha in enumerate(linhas[7:], start=1):
            if len(linha) < 10:
                continue
            id_planilha = linha[1].strip()
            descricao_item = linha[3].strip()
            periodo = linha[4].strip()
            local = linha[5].strip()
            data_str = linha[6].strip()
            valor = _parse_valor_brl(linha[7])
            responsavel = linha[8].strip()
            reembolso = linha[9].strip()

            if valor is None or (not id_planilha and not local):
                continue

            base_desc = descricao_item or f"Suprimentos ({local or 'Fornecedor'})"
            prefixo = f"[AG6 #{id_planilha if id_planilha != '-' else f'S{idx}'}]"
            titulo = f"{prefixo} {base_desc} - {local}".strip(' -')
            descricao = (
                f"Período: {periodo or 'Geral'} | Local: {local or 'Não informado'} | "
                f"Responsável original: {responsavel or 'Não informado'}"
            )
            tipo = (
                TipoDespesa.PAGAMENTO_DIRETO
                if reembolso.lower().startswith('não') or reembolso.lower().startswith('nao')
                else TipoDespesa.REEMBOLSO
            )
            status_final = StatusDespesa.ENVIADO if reembolso.lower() == 'pendente' else StatusDespesa.PAGO

            if self._persistir_despesa_historica(
                coordenacao=coord_alim,
                solicitante=solicitante,
                tesoureiro=tesoureiro,
                titulo=titulo,
                descricao=descricao,
                categoria=CategoriaDespesa.ALIMENTACAO,
                tipo=tipo,
                valor=valor,
                data_despesa=_parse_data_br(data_str),
                status_final=status_final,
                bytes_jpeg=bytes_jpeg,
            ):
                inseridas += 1

        return inseridas

    def _carregar_gastos_saude_ag6(
        self,
        csv_path: Path,
        coord_saude: Coordenacao | None,
        tesoureiro: Usuario,
        bytes_jpeg: bytes,
    ) -> int:
        """
        Importa os itens de caixa médica e medicamentos do AG VI (`saude_e_bem_estar_caixa_medica_ag6.csv`).

        - O que faz: Processa as duas colunas paralelas (Itens de curativo e Medicamentos de farmácia) em `SAUDE`.
        - Como faz: Filtra linhas que possuam nome do item e total preenchido, ignorando linhas de subtotal/total,
          e persiste de forma idempotente via `_persistir_despesa_historica`.
        - Qual finalidade atende: Completa a massa real de Saúde e Farmácia do AG VI especificada na Issue #9.
        """
        if not coord_saude or not csv_path.exists():
            return 0

        solicitante = self._obter_solicitante_pasta(coord_saude, tesoureiro)
        inseridas = 0
        data_padrao_ag6 = datetime.date(2023, 1, 15)

        with csv_path.open('r', encoding='utf-8-sig', newline='') as f:
            linhas = list(csv.reader(f))

        for linha in linhas[2:]:
            blocos = [
                ('Caixa Médica', 1, 2, 3, 4),
                ('Farmácia / Medicamentos', 6, 7, 8, 9),
            ]
            for grupo, idx_item, idx_qtd, idx_unit, idx_total in blocos:
                if len(linha) <= idx_total:
                    continue
                item = linha[idx_item].strip()
                qtd = linha[idx_qtd].strip()
                unit = linha[idx_unit].strip()
                valor = _parse_valor_brl(linha[idx_total])

                if not item or valor is None:
                    continue

                titulo = f"[AG6-SAUDE] {item}"
                descricao = f"Grupo: {grupo} | Qtd: {qtd or '1'} | Preço unitário: {unit or '-'}"
                if self._persistir_despesa_historica(
                    coordenacao=coord_saude,
                    solicitante=solicitante,
                    tesoureiro=tesoureiro,
                    titulo=titulo,
                    descricao=descricao,
                    categoria=CategoriaDespesa.SAUDE,
                    tipo=TipoDespesa.REEMBOLSO,
                    valor=valor,
                    data_despesa=data_padrao_ag6,
                    status_final=StatusDespesa.PAGO,
                    bytes_jpeg=bytes_jpeg,
                ):
                    inseridas += 1

        return inseridas
