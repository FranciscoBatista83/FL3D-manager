"""
=============================================================================
FL3D Manager - Administração do Módulo de Produtos (admin.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Configura o painel administrativo oficial do Django para o gerenciamento de produtos
e suas categorias, com filtros por categoria, material e status ativo.
=============================================================================
"""

from django.contrib import admin
from .models import Produto, CategoriaProduto


@admin.register(CategoriaProduto)
class CategoriaProdutoAdmin(admin.ModelAdmin):
    """
    Configuração das Categorias no painel administrativo.
    """
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """
    Configuração dos Produtos no painel administrativo.
    """
    list_display = ('nome', 'codigo', 'categoria', 'material', 'preco_venda', 'custo_estimado', 'ativo')
    list_filter = ('ativo', 'categoria', 'material')
    search_fields = ('nome', 'codigo', 'descricao')
    list_per_page = 20

