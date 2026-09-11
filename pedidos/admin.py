"""
=============================================================================
FL3D Manager - Administração do Módulo de Pedidos (admin.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Configura o gerenciamento avançado de pedidos dentro do Django Admin,
incluindo os itens do carrinho integrados na mesma página (TabularInline).
=============================================================================
"""

from django.contrib import admin
from .models import Pedido, ItemPedido


class ItemPedidoInline(admin.TabularInline):
    """
    Exibe os itens do pedido em formato de tabela dentro da própria página do Pedido.
    """
    model = ItemPedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """
    Configuração dos Pedidos no painel administrativo.
    """
    list_display = ('numero', 'cliente', 'status', 'valor_final', 'forma_pagamento', 'status_pagamento', 'data_pedido')
    list_filter = ('status', 'status_pagamento', 'forma_pagamento', 'data_pedido')
    search_fields = ('numero', 'cliente__nome', 'observacoes')
    inlines = [ItemPedidoInline]
    readonly_fields = ('data_pedido',)
