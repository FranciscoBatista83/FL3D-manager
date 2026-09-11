"""
=============================================================================
FL3D Manager - Configuração do Aplicativo Usuários (apps.py)
=============================================================================
Registra o módulo 'usuarios' no Django para que ele seja reconhecido
como parte integrante do sistema FL3D Manager.
=============================================================================
"""

from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    # Nome interno do aplicativo (deve bater com o nome da pasta)
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'
    # Nome amigável exibido no painel admin do Django
    verbose_name = 'Gestão de Usuários'
