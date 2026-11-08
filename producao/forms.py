"""
=============================================================================
FL3D Manager - Formulários do Módulo de Produção (forms.py)
=============================================================================
"""

from django import forms
from .models import Producao, RegistroImpressao, Perda
from pedidos.models import Pedido
from produtos.models import Produto
from impressoras.models import Impressora
from estoque.models import Filamento


class ProducaoForm(forms.ModelForm):
    """
    Formulário para criar ou editar uma Ordem de Produção da empresa.
    """
    class Meta:
        model = Producao
        fields = [
            'pedido', 'produto', 'quantidade',
            'impressora', 'filamento', 'cor',
            'peso_previsto', 'tempo_previsto',
            'data_inicio', 'data_conclusao',
            'status', 'observacoes'
        ]
        widgets = {
            'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'data_conclusao': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            if 'pedido' in self.fields:
                self.fields['pedido'].queryset = Pedido.objects.filter(empresa=empresa)
            if 'produto' in self.fields:
                self.fields['produto'].queryset = Produto.objects.filter(empresa=empresa, ativo=True)
            if 'impressora' in self.fields:
                self.fields['impressora'].queryset = Impressora.objects.filter(empresa=empresa)
            if 'filamento' in self.fields:
                self.fields['filamento'].queryset = Filamento.objects.filter(empresa=empresa)

        for field in self.fields:
            if hasattr(self.fields[field].widget, 'choices'):
                self.fields[field].widget.attrs['class'] = 'form-select'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-select'


class RegistroImpressaoForm(forms.ModelForm):
    """
    Formulário para apontamento de conclusão ou falha de uma impressão.
    """
    class Meta:
        model = RegistroImpressao
        fields = [
            'producao', 'pedido', 'produto',
            'impressora', 'filamento',
            'peso_utilizado', 'tempo_impressao',
            'resultado', 'observacoes'
        ]
        widgets = {
            'tempo_impressao': forms.TextInput(attrs={'placeholder': 'Ex: 02:30:00'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            if 'producao' in self.fields:
                self.fields['producao'].queryset = Producao.objects.filter(pedido__empresa=empresa)
            if 'pedido' in self.fields:
                self.fields['pedido'].queryset = Pedido.objects.filter(empresa=empresa)
            if 'produto' in self.fields:
                self.fields['produto'].queryset = Produto.objects.filter(empresa=empresa)
            if 'impressora' in self.fields:
                self.fields['impressora'].queryset = Impressora.objects.filter(empresa=empresa)
            if 'filamento' in self.fields:
                self.fields['filamento'].queryset = Filamento.objects.filter(empresa=empresa)

        for field in self.fields:
            if hasattr(self.fields[field].widget, 'choices'):
                self.fields[field].widget.attrs['class'] = 'form-select'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['resultado'].widget.attrs['class'] = 'form-select'


class PerdaForm(forms.ModelForm):
    """
    Formulário para lançamento avulso de perda de filamento.
    """
    class Meta:
        model = Perda
        fields = [
            'pedido', 'produto', 'filamento',
            'quantidade', 'motivo', 'observacao'
        ]

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            if 'pedido' in self.fields:
                self.fields['pedido'].queryset = Pedido.objects.filter(empresa=empresa)
            if 'produto' in self.fields:
                self.fields['produto'].queryset = Produto.objects.filter(empresa=empresa)
            if 'filamento' in self.fields:
                self.fields['filamento'].queryset = Filamento.objects.filter(empresa=empresa)

        for field in self.fields:
            if hasattr(self.fields[field].widget, 'choices'):
                self.fields[field].widget.attrs['class'] = 'form-select'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['motivo'].widget.attrs['class'] = 'form-select'
