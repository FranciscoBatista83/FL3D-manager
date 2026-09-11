"""
=============================================================================
FL3D Manager - Configuração do Aplicativo de Produção (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Registra o módulo de Produção no Django sob o título "Controle de Produção".
=============================================================================
"""

from django.apps import AppConfig


class ProducaoConfig(AppConfig):
    """
    Configuração oficial do módulo de Produção.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'producao'
    verbose_name = 'Controle de Produção'
