"""
=============================================================================
FL3D Manager - Configuração do Aplicativo de Clientes (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Informa ao Django os dados cadastrais do aplicativo 'clientes' e define o nome
bonito em português que aparecerá nos menus do sistema ("Gestão de Clientes").
=============================================================================
"""

from django.apps import AppConfig


class ClientesConfig(AppConfig):
    """
    Configuração oficial do aplicativo de Clientes.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clientes'
    verbose_name = 'Gestão de Clientes'

