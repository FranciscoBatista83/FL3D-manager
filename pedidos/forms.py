"""
=============================================================================
FL3D Manager - Formulários do Módulo de Pedidos (forms.py)
=============================================================================
"""

from django import forms
from django.forms.models import inlineformset_factory
from .models import Pedido, ItemPedido
from clientes.models import Cliente
from produtos.models import Produto


class PedidoForm(forms.ModelForm):
    """
    Formulário do Cabeçalho do Pedido com filtro de clientes pela empresa.
    """
    class Meta:
        model = Pedido
        fields = [
            'cliente', 'data_entrega_prevista', 'status',
            'desconto', 'forma_pagamento', 'status_pagamento', 'observacoes'
        ]
        widgets = {
            'data_entrega_prevista': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if 'cliente' in self.fields:
            if empresa:
                self.fields['cliente'].queryset = Cliente.objects.filter(empresa=empresa, ativo=True)
            elif self.instance.pk and self.instance.empresa:
                self.fields['cliente'].queryset = Cliente.objects.filter(empresa=self.instance.empresa, ativo=True)

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['forma_pagamento'].widget.attrs.update({'class': 'form-select'})
        self.fields['status_pagamento'].widget.attrs.update({'class': 'form-select'})


class ItemPedidoForm(forms.ModelForm):
    """
    Formulário de cada linha de produto dentro do carrinho do pedido.
    """
    class Meta:
        model = ItemPedido
        fields = ['produto', 'quantidade', 'valor_unitario', 'valor_total']
        
    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if 'produto' in self.fields and empresa:
            self.fields['produto'].queryset = Produto.objects.filter(empresa=empresa, ativo=True)

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control item-field'})
            
        self.fields['produto'].widget.attrs.update({'class': 'form-select produto-select'})
        self.fields['quantidade'].widget.attrs.update({'class': 'form-control qtd-input', 'min': '1'})
        self.fields['valor_unitario'].widget.attrs.update({'class': 'form-control preco-input'})
        self.fields['valor_total'].widget.attrs.update({'class': 'form-control total-input', 'readonly': 'readonly'})


ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    form=ItemPedidoForm,
    extra=1,
    can_delete=True
)
