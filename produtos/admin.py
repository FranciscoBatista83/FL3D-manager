"""
=============================================================================
FL3D Manager - Administração do Módulo de Produtos (admin.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Configura o painel administrativo oficial do Django para o gerenciamento de
produtos com filtros por material, marketplace e status ativo.
=============================================================================
"""

from django.contrib import admin
from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """
    Configuração dos Produtos no painel administrativo.
    """
    list_display = ('nome', 'codigo', 'material', 'marketplace', 'preco_venda', 'custo_estimado', 'margem_lucro', 'ativo')
    list_filter = ('ativo', 'material', 'marketplace')
    search_fields = ('nome', 'codigo', 'descricao')
    list_per_page = 20
