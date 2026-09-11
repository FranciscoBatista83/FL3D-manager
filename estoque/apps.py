"""
=============================================================================
FL3D Manager - Configuração do Aplicativo de Estoque (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Registra o módulo de Estoque no Django e define seu nome legível ("Controle de Estoque").
=============================================================================
"""

from django.apps import AppConfig


class EstoqueConfig(AppConfig):
    """
    Configuração oficial do módulo de Estoque.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'estoque'
    verbose_name = 'Controle de Estoque'

