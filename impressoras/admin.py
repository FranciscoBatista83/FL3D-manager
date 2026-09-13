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
    list_display = ('nome', 'fabricante', 'modelo', 'potencia_w', 'data_aquisicao')
    list_filter = ('fabricante',)
    search_fields = ('nome', 'fabricante', 'modelo')
