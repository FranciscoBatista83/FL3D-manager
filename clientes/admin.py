"""
=============================================================================
FL3D Manager - Administração do Módulo de Clientes (admin.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Aqui conectamos a tabela de Clientes ao painel administrativo oficial do Django
('/admin/'). Configuramos colunas visíveis, filtros laterais e barra de busca
para facilitar a vida do administrador do sistema.
=============================================================================
"""

from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuração da exibição dos Clientes no Django Admin.
    """
    # Colunas que aparecerão na tabela de listagem do painel admin
    list_display = ('nome', 'telefone', 'whatsapp', 'cidade', 'estado', 'ativo', 'data_cadastro')
    
    # Filtros laterais para encontrar clientes rapidamente
    list_filter = ('ativo', 'estado', 'data_cadastro')
    
    # Campos que serão pesquisados quando você digitar algo na barra de busca do admin
    search_fields = ('nome', 'cpf_cnpj', 'email', 'telefone', 'whatsapp', 'cidade')
    
    # Paginação no painel admin
    list_per_page = 20

