"""
=============================================================================
FL3D Manager - Configuração do Aplicativo Core (apps.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo registra o módulo 'core' perante o Django.
O módulo 'core' é o alicerce central do sistema, servindo como ponto de partida
para funções globais, filtros ou configurações genéricas que podem ser
aproveitadas por todos os outros módulos da oficina 3D.
=============================================================================
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuração do módulo Core.
    """
    # Define que as chaves primárias (IDs dos registros) usarão números inteiros de 64 bits (BigAutoField)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nome do aplicativo reconhecido internamente pelo Django
    name = 'core'
    
    # Nome legível e amigável exibido no painel de administração
    verbose_name = 'Núcleo do Sistema'

