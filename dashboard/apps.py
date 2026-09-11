"""
=============================================================================
FL3D Manager - Configuração do Aplicativo Dashboard (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo registra o módulo 'dashboard' no Django. O Dashboard é a "torre de
controle" da FL3D Studio: ao entrar no sistema, é ele que mostra os números do mês,
as impressoras trabalhando, os pedidos recentes e o alerta de filamentos acabando.
=============================================================================
"""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """
    Configuração oficial do módulo Dashboard.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    verbose_name = 'Painel de Controle e Métricas'

