"""
=============================================================================
FL3D Manager - Configuração do Aplicativo de Impressoras (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Registra o módulo de Impressoras no Django com o título amigável "Parque de Impressoras".
=============================================================================
"""

from django.apps import AppConfig


class ImpressorasConfig(AppConfig):
    """
    Configuração oficial do módulo de Impressoras.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'impressoras'
    verbose_name = 'Parque de Impressoras'
