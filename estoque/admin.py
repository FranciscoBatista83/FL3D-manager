"""
=============================================================================
FL3D Manager - Administração do Módulo de Estoque (admin.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Configura a visualização das tabelas de Filamento e de Movimentações de Estoque
dentro do painel administrativo do Django.
=============================================================================
"""

from django.contrib import admin
from .models import Filamento, MovimentacaoEstoque


@admin.register(Filamento)
class FilamentoAdmin(admin.ModelAdmin):
    """
    Exibição dos Carretéis de Filamento no Django Admin.
    """
    list_display = ('material', 'cor', 'marca', 'peso_atual', 'peso_inicial', 'custo_rolo', 'localizacao', 'data_entrada')
    list_filter = ('material', 'marca', 'data_entrada')
    search_fields = ('material', 'cor', 'marca', 'codigo_lote', 'fornecedor')
    readonly_fields = ('data_entrada',)


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    """
    Exibição do Livro-Razão de Movimentações no Django Admin.
    """
    list_display = ('filamento', 'tipo', 'quantidade', 'quantidade_anterior', 'quantidade_nova', 'data', 'usuario')
    list_filter = ('tipo', 'data')
    search_fields = ('filamento__material', 'filamento__cor', 'filamento__marca', 'motivo')
    readonly_fields = ('data',)

