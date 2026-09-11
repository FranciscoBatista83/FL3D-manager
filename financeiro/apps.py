"""
=============================================================================
FL3D Manager - Configuração do Aplicativo Financeiro (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Registra o módulo Financeiro no Django sob o título oficial "Gestão Financeira".
=============================================================================
"""

from django.apps import AppConfig


class FinanceiroConfig(AppConfig):
    """
    Configuração oficial do módulo Financeiro.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financeiro'
    verbose_name = 'Gestão Financeira'
