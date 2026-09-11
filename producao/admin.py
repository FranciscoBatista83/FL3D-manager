"""
=============================================================================
FL3D Manager - Administração do Módulo de Produção (admin.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Registra as tabelas de Ordens de Produção, Registros de Impressão e Perdas
no painel administrativo do Django.
=============================================================================
"""

from django.contrib import admin
from .models import Producao, RegistroImpressao, Perda


@admin.register(Producao)
class ProducaoAdmin(admin.ModelAdmin):
    """
    Configuração das Ordens de Produção no Django Admin.
    """
    list_display = ('id', 'pedido', 'produto', 'impressora', 'filamento', 'status', 'data_inicio')
    list_filter = ('status', 'impressora', 'filamento')
    search_fields = ('pedido__numero', 'produto__nome', 'observacoes')


@admin.register(RegistroImpressao)
class RegistroImpressaoAdmin(admin.ModelAdmin):
    """
    Configuração dos Registros de Impressão no Django Admin.
    """
    list_display = ('id', 'producao', 'produto', 'impressora', 'peso_utilizado', 'tempo_impressao', 'resultado', 'data')
    list_filter = ('resultado', 'impressora', 'data')
    search_fields = ('produto__nome', 'observacoes')


@admin.register(Perda)
class PerdaAdmin(admin.ModelAdmin):
    """
    Configuração do Registro de Perdas no Django Admin.
    """
    list_display = ('id', 'data', 'produto', 'filamento', 'quantidade', 'motivo')
    list_filter = ('motivo', 'filamento', 'data')
    search_fields = ('produto__nome', 'observacao')
