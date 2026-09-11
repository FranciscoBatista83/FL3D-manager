"""
=============================================================================
FL3D Manager - Configuração do Aplicativo de Produtos (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Registra o aplicativo de Produtos perante o Django e define o nome de exibição
amigável nos menus ("Catálogo de Produtos").
=============================================================================
"""

from django.apps import AppConfig


class ProdutosConfig(AppConfig):
    """
    Configuração oficial do módulo de Produtos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'produtos'
    verbose_name = 'Catálogo de Produtos'

