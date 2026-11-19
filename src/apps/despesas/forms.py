from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from apps.despesas.models import Despesa
from apps.financeiro.models import Coordenacao


class DespesaForm(forms.ModelForm):
    """
    Formulário para lançamento e edição de despesas com suporte a dispositivos móveis.

    - O que faz: Coleta e valida sintaticamente os dados essenciais da despesa operacional (coordenação,
      título, categoria contábil, modalidade, forma de pagamento, valor em R$, data do cupom e arquivo fiscal).
    - Como faz: Utiliza `forms.ModelForm` do Django mapeando os campos da entidade `Despesa`; restringe a seleção
      de coordenações apenas às ativas no evento; configura widgets responsivos Bootstrap 5 e atributos nativos
      HTML5 para smartphones (`inputmode="decimal"`, `capture="environment"` e tipos MIME de imagem/PDF); valida
      aritmeticamente com `Decimal` que o valor lançado seja estritamente positivo.
    - Qual finalidade atende: Atende aos requisitos RF04 (Lançamento de Despesa), RNF01 (Usabilidade Mobile-First)
      e viabiliza a jornada de campo dos voluntários do AG VII no formulário da Issue #7.
    """

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
                'placeholder': 'Ex: Compra de verduras e temperos (Sacolão)',
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'forma_pagamento_original': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'inputmode': 'decimal',
                'placeholder': '0.00',
            }),
            'data_despesa': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detalhes complementares da compra ou dados do fornecedor (opcional)',
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
            raise ValidationError("O valor da despesa deve ser estritamente maior que zero (R$ 0,00).")
        return valor
