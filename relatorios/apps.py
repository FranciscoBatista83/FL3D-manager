"""
=============================================================================
FL3D Manager - Configuração do Aplicativo de Relatórios (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Registra o módulo de Relatórios no Django. Este módulo é reservado para a geração
de relatórios avançados consolidados, exportações para PDF/Excel e inteligência
de negócios da FL3D Studio.
=============================================================================
"""

from django.apps import AppConfig


class RelatoriosConfig(AppConfig):
    """
    Configuração oficial do módulo de Relatórios.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'relatorios'
    verbose_name = 'Relatórios e Análises'
