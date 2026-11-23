"""
Serviços de domínio para agregação contábil e exportação de relatórios (RF08).

- O que faz: Concentra as rotinas de consolidação financeira, balancetes por coordenação/categoria
  e geração de planilhas CSV para prestação de contas do AG VII.
- Como faz: Executa consultas ORM agregadas com precisão monetária estrita (`Decimal`) e aplica
  regras de visibilidade baseadas no papel do usuário (RBAC).
- Qual finalidade atende: Mantém as views e templates livres de lógica contábil conforme `src/AGENTS.md`
  e atende ao requisito RF08 para o fechamento financeiro do Grupo Escoteiro Caramuru.
"""

import csv
from decimal import ROUND_HALF_UP, Decimal
from io import StringIO

from django.db.models import Count, DecimalField, Sum
from django.db.models.functions import Coalesce

from apps.despesas.models import CategoriaDespesa, StatusDespesa
from apps.usuarios.services import despesas_visiveis

ZERO = Decimal('0.00')
CENTAVO = Decimal('0.01')
CAMPO_DECIMAL = DecimalField(max_digits=12, decimal_places=2)

CABECALHO_CSV = (
    'id',
    'data_despesa',
    'sigla_coordenacao',
    'coordenacao',
    'categoria',
    'categoria_descricao',
    'status',
    'status_descricao',
    'titulo',
    'tipo',
    'forma_pagamento',
    'valor',
)


def _quantizar_moeda(valor: Decimal) -> Decimal:
    """
    Normaliza um montante para centavos em Reais.

    - O que faz: Garante que totais e células monetárias tenham exatamente duas casas decimais.
    - Como faz: Aplica `Decimal.quantize` com `ROUND_HALF_UP` sobre `Decimal('0.01')`.
    - Qual finalidade atende: Impede divergência de centavos na prestação de contas do AG VII (RF08).
    """
    return (valor or ZERO).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def _texto_filtro(valor: str | None) -> str | None:
    """
    Limpa um parâmetro textual de filtro do relatório.

    - O que faz: Descarta filtros vazios para que a consulta não restrinja o recorte à toa.
    - Como faz: Converte o valor em string, remove espaços e devolve `None` quando nada sobra.
    - Qual finalidade atende: Permite exportar a pasta inteira ou afunilar por coordenação, categoria e status.
    """
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


def _rotulo_escolha(enumeracao, codigo: str) -> str:
    """
    Traduz o código persistido de uma escolha Django para o rótulo exibido à Tesouraria.

    - O que faz: Resolve a descrição de categoria ou status usada no CSV e no balancete.
    - Como faz: Instancia o `TextChoices` correspondente e lê `.label`, caindo no próprio código se for inválido.
    - Qual finalidade atende: Deixa a planilha de prestação de contas legível para o Grupo Escoteiro Caramuru.
    """
    try:
        return enumeracao(codigo).label
    except ValueError:
        return codigo


def _formatar_valor_csv(valor: Decimal) -> str:
    """
    Formata um `Decimal` para a célula monetária da planilha.

    - O que faz: Serializa o valor quantizado com vírgula decimal, no padrão de planilha pt-BR.
    - Como faz: Produz duas casas com ponto e substitui o separador decimal por vírgula.
    - Qual finalidade atende: Permite abrir o CSV no Excel em português sem deslocar os centavos (RF08).
    """
    return f'{_quantizar_moeda(valor):.2f}'.replace('.', ',')


def filtrar_despesas_relatorio(usuario, *, coordenacao=None, categoria=None, status=None):
    """
    Recorta as despesas visíveis ao usuário pelos filtros da prestação de contas.

    - O que faz: Parte do escopo RBAC e, se informados, restringe por sigla de coordenação, categoria e status.
    - Como faz: Reutiliza `despesas_visiveis` e encadeia `filter` somente para parâmetros não vazios.
      Coordenador continua limitado à própria pasta mesmo que peça a sigla de outra coordenação.
    - Qual finalidade atende: Sustenta a exportação analítica e o balancete sem vazar dados de outras áreas (RF01/RF08).
    """
    queryset = despesas_visiveis(usuario)
    sigla = _texto_filtro(coordenacao)
    categoria_filtro = _texto_filtro(categoria)
    status_filtro = _texto_filtro(status)
    if sigla:
        queryset = queryset.filter(coordenacao__sigla__iexact=sigla)
    if categoria_filtro:
        queryset = queryset.filter(categoria=categoria_filtro)
    if status_filtro:
        queryset = queryset.filter(status=status_filtro)
    return queryset.order_by('coordenacao__nome', 'categoria', 'data_despesa', 'id')


def gerar_csv_despesas(usuario, *, coordenacao=None, categoria=None, status=None) -> str:
    """
    Gera a planilha analítica de despesas em CSV.

    - O que faz: Exporta uma linha por despesa do recorte autorizado, com cabeçalho estável e valor em centavos.
    - Como faz: Percorre `filtrar_despesas_relatorio` e escreve com `csv.writer` usando separador `;`.
      O valor sai de `Decimal` quantizado, nunca de `float`.
    - Qual finalidade atende: Entrega a planilha estruturada da prestação de contas do AG VII (RF08 / Issue #34).
    """
    buffer = StringIO()
    escritor = csv.writer(buffer, delimiter=';', lineterminator='\r\n')
    escritor.writerow(CABECALHO_CSV)
    despesas = filtrar_despesas_relatorio(
        usuario,
        coordenacao=coordenacao,
        categoria=categoria,
        status=status,
    )
    for despesa in despesas:
        escritor.writerow([
            despesa.id,
            despesa.data_despesa.isoformat(),
            despesa.coordenacao.sigla,
            despesa.coordenacao.nome,
            despesa.categoria,
            _rotulo_escolha(CategoriaDespesa, despesa.categoria),
            despesa.status,
            _rotulo_escolha(StatusDespesa, despesa.status),
            despesa.titulo,
            despesa.tipo,
            despesa.forma_pagamento_original,
            _formatar_valor_csv(despesa.valor),
        ])
    return buffer.getvalue()


def gerar_balancete_sintetico(usuario, *, coordenacao=None, categoria=None, status=None) -> dict:
    """
    Consolida o balancete sintético por coordenação e categoria contábil.

    - O que faz: Soma quantidade e valor das despesas do recorte RBAC, agrupadas por pasta e categoria.
    - Como faz: Agrega no banco com `Sum` em `DecimalField` e `Coalesce` para zero, depois quantiza cada total.
      A ordenação padrão do model é removida antes do `GROUP BY` para não fatiar o agrupamento.
    - Qual finalidade atende: Fecha a prestação de contas consolidada do AG VII com precisão de centavos (RF08).
    """
    queryset = filtrar_despesas_relatorio(
        usuario,
        coordenacao=coordenacao,
        categoria=categoria,
        status=status,
    ).order_by()
    agregados = queryset.values(
        'coordenacao_id',
        'coordenacao__sigla',
        'coordenacao__nome',
        'categoria',
    ).annotate(
        total=Coalesce(Sum('valor'), ZERO, output_field=CAMPO_DECIMAL),
        quantidade=Count('id'),
    ).order_by('coordenacao__nome', 'categoria')

    linhas = []
    total_geral = ZERO
    quantidade_total = 0
    for item in agregados:
        total = _quantizar_moeda(item['total'])
        quantidade = int(item['quantidade'])
        total_geral += total
        quantidade_total += quantidade
        linhas.append({
            'coordenacao_id': item['coordenacao_id'],
            'sigla': item['coordenacao__sigla'],
            'coordenacao': item['coordenacao__nome'],
            'categoria': item['categoria'],
            'categoria_descricao': _rotulo_escolha(CategoriaDespesa, item['categoria']),
            'quantidade': quantidade,
            'total': total,
        })

    return {
        'linhas': linhas,
        'total_geral': _quantizar_moeda(total_geral),
        'quantidade_total': quantidade_total,
    }
