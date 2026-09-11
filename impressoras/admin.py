"""
=============================================================================
FL3D Manager - Administração do Módulo de Impressoras (admin.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Registra a tabela de impressoras 3D no painel administrativo do Django,
permitindo filtrar máquinas por status, fabricante e visualizar rapidamente
a situação de cada máquina.
=============================================================================
"""

from django.contrib import admin
from .models import Impressora


@admin.register(Impressora)
class ImpressoraAdmin(admin.ModelAdmin):
    """
    Configuração das Impressoras no painel administrativo.
    """
    list_display = ('nome', 'fabricante', 'modelo', 'numero_identificacao', 'status', 'data_aquisicao')
    list_filter = ('status', 'fabricante')
    search_fields = ('nome', 'fabricante', 'modelo', 'numero_identificacao')
    list_editable = ('status',)  # Permite alterar o status diretamente na lista do admin!
