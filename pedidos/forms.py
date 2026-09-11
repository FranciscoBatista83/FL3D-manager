"""
=============================================================================
FL3D Manager - Formulários do Módulo de Pedidos (forms.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo controla os formulários da tela de pedidos.
Um pedido não é apenas um formulário comum; ele possui o cabeçalho (cliente, data,
desconto) e uma tabela de itens dinâmicos (produtos, quantidades e preços).

Para lidar com isso com máxima elegância, usamos o recurso 'inlineformset_factory'
do Django:
  1. 'PedidoForm': Cuida dos dados gerais da venda.
  2. 'ItemPedidoForm': Cuida da linha individual de cada peça adicionada.
  3. 'ItemPedidoFormSet': Permite que o operador adicione ou remova várias linhas
     de produtos na mesma tela antes de clicar em Salvar.
=============================================================================
"""

from django import forms
from django.forms.models import inlineformset_factory
from .models import Pedido, ItemPedido


class PedidoForm(forms.ModelForm):
    """
    Formulário do Cabeçalho do Pedido (Cliente, Prazos, Descontos e Pagamento).
    """
    class Meta:
        model = Pedido
        fields = [
            'cliente', 'data_entrega_prevista', 'status',
            'desconto', 'forma_pagamento', 'status_pagamento', 'observacoes'
        ]
        widgets = {
            # Calendário visual interativo para a data de entrega
            'data_entrega_prevista': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Aplica as classes do Bootstrap 5 para manter o padrão visual do sistema.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
        # Menus de seleção ganham a classe 'form-select'
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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control item-field'})
            
        # Classes especiais para que o JavaScript da tela calcule o valor total automaticamente
        self.fields['produto'].widget.attrs.update({'class': 'form-select produto-select'})
        self.fields['quantidade'].widget.attrs.update({'class': 'form-control qtd-input', 'min': '1'})
        self.fields['valor_unitario'].widget.attrs.update({'class': 'form-control preco-input'})
        self.fields['valor_total'].widget.attrs.update({'class': 'form-control total-input', 'readonly': 'readonly'})


# O FormSet junta o Pedido com múltiplos Itens de Pedido em uma única tela fluida
ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    form=ItemPedidoForm,
    extra=1,          # Exibe 1 linha em branco inicial para inclusão rápida
    can_delete=True   # Permite marcar checkbox para excluir itens existentes
)
