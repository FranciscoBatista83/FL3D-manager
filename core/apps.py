"""
=============================================================================
FL3D Manager - Configuração do Aplicativo Core (apps.py)
=============================================================================
Este arquivo registra o módulo 'core' perante o Django.
=============================================================================
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Núcleo do Sistema'

    def ready(self):
        import core.signals  # Conecta os sinais de criação automática de perfil
