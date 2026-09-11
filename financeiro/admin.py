"""
=============================================================================
FL3D Manager - Administração do Módulo Financeiro (admin.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Configura o painel administrativo do Django para o módulo financeiro,
permitindo auditoria de valores, datas, categorias e pedidos associados.
=============================================================================
"""

from django.contrib import admin
from .models import MovimentacaoFinanceira


@admin.register(MovimentacaoFinanceira)
class MovimentacaoFinanceiraAdmin(admin.ModelAdmin):
    """
    Configuração das Movimentações Financeiras no Django Admin.
    """
    list_display = ('descricao', 'tipo', 'categoria', 'valor', 'data', 'pedido', 'data_registro')
    list_filter = ('tipo', 'categoria', 'data')
    search_fields = ('descricao', 'observacoes')
    readonly_fields = ('data_registro',)
