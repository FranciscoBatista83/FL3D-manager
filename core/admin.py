"""
=============================================================================
FL3D Manager - Administração do Módulo Core (admin.py)
=============================================================================
Registro dos modelos Empresa e PerfilUsuario no Django Admin.
=============================================================================
"""

from django.contrib import admin
from .models import Empresa, PerfilUsuario


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nome_fantasia', 'documento', 'telefone', 'ativo', 'criado_em')
    list_filter = ('ativo', 'criado_em')
    search_fields = ('nome', 'nome_fantasia', 'documento', 'email')
    ordering = ('nome',)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'nivel', 'telefone')
    list_filter = ('nivel', 'empresa')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__email', 'empresa__nome')
