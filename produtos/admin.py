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
from .models import Produto, Categoria, VariacaoProduto


class VariacaoProdutoInline(admin.TabularInline):
    model = VariacaoProduto
    extra = 1
    fields = ('nome', 'quantidade', 'custo_embalagem', 'custo_producao_total', 'margem_lucro', 'preco_venda', 'lucro_liquido')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """
    Configuração dos Produtos no painel administrativo.
    """
    list_display = ('nome', 'categoria', 'codigo', 'material', 'marketplace', 'preco_venda', 'custo_estimado', 'margem_lucro', 'ativo')
    list_filter = ('ativo', 'categoria', 'material', 'marketplace')
    search_fields = ('nome', 'codigo', 'descricao')
    list_per_page = 20
    inlines = [VariacaoProdutoInline]
