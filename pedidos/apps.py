"""
=============================================================================
FL3D Manager - Configuração do Aplicativo de Pedidos (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Registra o módulo de Pedidos no Django sob a nomenclatura "Vendas e Pedidos".
=============================================================================
"""

from django.apps import AppConfig


class PedidosConfig(AppConfig):
    """
    Configuração oficial do módulo de Pedidos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pedidos'
    verbose_name = 'Vendas e Pedidos'
