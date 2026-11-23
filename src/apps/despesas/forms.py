from decimal import Decimal, InvalidOperation

from django import forms
from django.core.exceptions import ValidationError

from apps.despesas.models import Despesa
from apps.financeiro.models import Coordenacao


def converter_valor_reais(texto) -> Decimal | None:
    """
    Converte o valor digitado na tela (formato brasileiro) em `Decimal`.

    - O que faz: Aceita "1.250,40", "1250,40", "R$ 10,00" ou o formato técnico "1250.40" e devolve
      `Decimal('1250.40')`; devolve `None` para texto vazio ou que não seja número.
    - Como faz: Remove "R$" e espaços; se houver vírgula, trata pontos como separador de milhar e a vírgula
      como separador decimal; converte com `Decimal` (nunca `float`).
    - Qual finalidade atende: A máscara de centavos da tela mobile envia o valor já formatado em reais;
      formulário e prévia do termômetro precisam ler o mesmo formato sem perder centavos.
    """
    if isinstance(texto, Decimal):
        return texto
    bruto = str(texto or '').replace('R$', '').replace('\xa0', '').replace(' ', '').strip()
    if not bruto:
        return None
    if ',' in bruto:
        bruto = bruto.replace('.', '').replace(',', '.')
    try:
        valor = Decimal(bruto)
    except InvalidOperation:
        return None
    return valor if valor.is_finite() else None


def formatar_valor_reais(valor: Decimal) -> str:
    """
    Formata um `Decimal` em reais no padrão brasileiro, sem o símbolo (ex.: `1.250,40`).

    - O que faz: Gera o texto exibido no campo de valor ao abrir uma despesa já salva.
    - Como faz: Usa a formatação de milhar do Python com duas casas e troca os separadores para o padrão pt-BR.
    - Qual finalidade atende: Faz o campo mascarado mostrar o valor salvo no mesmo formato em que é digitado.
    """
    return f"{valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


class CampoValorReais(forms.DecimalField):
    """
    Campo de valor monetário que entende o formato brasileiro digitado pela máscara de centavos.

    - O que faz: Lê "1.250,40" como `Decimal('1250.40')` e exibe valores salvos como "1.250,40".
    - Como faz: Sobrescreve `to_python` para usar `converter_valor_reais` antes da validação padrão de
      `DecimalField` (casas decimais e dígitos máximos) e `prepare_value` para formatar `Decimal` em pt-BR.
    - Qual finalidade atende: Permite que o voluntário digite só números ("1000" vira "10,00") sem quebrar
      a validação do Django nem a precisão em `Decimal` exigida pelo projeto.
    """

    def to_python(self, value):
        """
        Converte o texto digitado em `Decimal`, rejeitando o que não for número.

        - O que faz: Retorna `None` para vazio, `Decimal` para número válido e levanta erro "invalid" no resto.
        - Como faz: Delega a leitura a `converter_valor_reais` e repassa o resultado à implementação padrão.
        - Qual finalidade atende: Mantém a mensagem de erro padrão do Django para valores inválidos.
        """
        if value in self.empty_values:
            return None
        valor = converter_valor_reais(value)
        if valor is None:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return super().to_python(str(valor))

    def prepare_value(self, value):
        """
        Exibe valores `Decimal` já salvos no formato brasileiro.

        - O que faz: Converte `Decimal('185.50')` em "185,50"; textos digitados voltam sem alteração.
        - Como faz: Usa `formatar_valor_reais` apenas quando o valor é `Decimal`.
        - Qual finalidade atende: Evita que a máscara leia "185.50" como "18.550" ao abrir uma despesa salva.
        """
        if isinstance(value, Decimal):
            return formatar_valor_reais(value)
        return value


class DespesaForm(forms.ModelForm):
    """
    Formulário para lançamento e edição de despesas com suporte a dispositivos móveis.

    - O que faz: Coleta e valida sintaticamente os dados essenciais da despesa operacional (coordenação,
      título, categoria contábil, modalidade, forma de pagamento, valor em R$, data do cupom e arquivo fiscal).
    - Como faz: Utiliza `forms.ModelForm` do Django mapeando os campos da entidade `Despesa`; restringe a seleção
      de coordenações apenas às ativas no evento; configura widgets responsivos Bootstrap 5 e atributos nativos
      HTML5 para smartphones (teclado numérico no valor com máscara de centavos via `CampoValorReais`,
      `capture="environment"` e tipos MIME de imagem/PDF); valida
      aritmeticamente com `Decimal` que o valor lançado seja estritamente positivo.
    - Qual finalidade atende: Atende aos requisitos RF04 (Lançamento de Despesa), RNF01 (Usabilidade Mobile-First)
      e viabiliza a jornada de campo dos voluntários do AG VII no formulário da Issue #7.
    """

    valor = CampoValorReais(
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'inputmode': 'numeric',
            'autocomplete': 'off',
            'maxlength': '13',
            'placeholder': '0,00',
        }),
    )

    class Meta:
        model = Despesa
        fields = [
            'coordenacao',
            'titulo',
            'categoria',
            'tipo',
            'forma_pagamento_original',
            'valor',
            'data_despesa',
            'descricao',
            'comprovante',
        ]
        widgets = {
            'coordenacao': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Verduras e temperos (Sacolão)',
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'forma_pagamento_original': forms.Select(attrs={'class': 'form-select'}),
            'data_despesa': forms.DateInput(
                format='%Y-%m-%d',  # <input type="date"> só aceita ISO; sem isso a data inicial some no celular
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                },
            ),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ex: nome da loja ou detalhes da compra',
            }),
            'comprovante': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp,application/pdf',
                'capture': 'environment',
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário personalizando querysets e obrigatoriedade de campos.

        - O que faz: Filtra as coordenações operacionais ativas e flexibiliza o comprovante como opcional
          no nível de formulário para permitir salvamento preliminar como rascunho (RF05 / RN01).
        - Como faz: Sobrescreve `__init__`, atribui `Coordenacao.objects.filter(ativo=True)` e define
          `self.fields['comprovante'].required = False`.
        - Qual finalidade atende: Dá suporte à criação de rascunhos sem foto prévia e evita exibição de
          coordenações inativas ou descontinuadas.
        """
        super().__init__(*args, **kwargs)
        self.fields['coordenacao'].queryset = Coordenacao.objects.filter(ativo=True).order_by('nome')
        self.fields['comprovante'].required = False

    def clean_valor(self):
        """
        Garante que o valor monetário da despesa seja estritamente maior que zero.

        - O que faz: Valida se o montante financeiro informado é positivo.
        - Como faz: Compara o atributo `valor` com `Decimal('0.00')`, lançando `ValidationError` caso seja <= 0.
        - Qual finalidade atende: Protege a integridade contábil do orçamento contra lançamentos nulos ou negativos.
        """
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor <= Decimal('0.00'):
            raise ValidationError("Informe um valor maior que R$ 0,00.")
        return valor


class RejeicaoDespesaForm(forms.Form):
    """
    Formulário para registro obrigatório de parecer na reprovação de despesas (RN04).

    - O que faz: Valida o motivo textual exigido pela Tesouraria antes de retornar uma despesa como `REJEITADO`.
    - Como faz: Define `motivo_rejeicao` como `CharField` obrigatório com widget textarea Bootstrap 5 e
      remove espaços vazios em `clean_motivo_rejeicao`.
    - Qual finalidade atende: Cumpre estritamente a RN04, fornecendo orientação clara ao solicitante em campo.
    """

    motivo_rejeicao = forms.CharField(
        label='Justificativa da Reprovação',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ex: Cupom fiscal ilegível, CNPJ divergente ou item não autorizado.',
        }),
    )

    def clean_motivo_rejeicao(self):
        """
        Impede o envio de justificativa composta apenas por espaços em branco.

        - O que faz: Verifica que o motivo possui texto útil após remoção de espaços nas extremidades.
        - Como faz: Executa `.strip()` e levanta `ValidationError` caso o texto resultante esteja vazio.
        - Qual finalidade atende: Bloqueia reprovações sem parecer real na camada de entrada (RN04).
        """
        motivo = (self.cleaned_data.get('motivo_rejeicao') or '').strip()
        if not motivo:
            raise ValidationError("Informe a justificativa da reprovação.")
        return motivo


class LiquidacaoDespesaForm(forms.Form):
    """
    Formulário para registro do comprovante de transferência bancária na liquidação (RF07).

    - O que faz: Coleta o comprovante PIX/transferência emitido pelo internet banking do Banco Cora PJ.
    - Como faz: Expõe `comprovante_pagamento` como `FileField` obrigatório com filtro MIME para imagens e PDF.
    - Qual finalidade atende: Garante lastro documental bancário na transição `APROVADO -> PAGO` (Issue #11).
    """

    comprovante_pagamento = forms.FileField(
        label='Comprovante de Transferência Banco Cora PJ',
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png,image/webp,application/pdf',
        }),
    )
