"""
=============================================================================
FL3D Manager - Rotas do Módulo Core (urls.py)
=============================================================================
Rotas administrativas para gestão de Empresas clientes (Painel Master).
=============================================================================
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('empresas/', views.EmpresaListView.as_view(), name='empresas_lista'),
    path('empresas/nova/', views.EmpresaCreateView.as_view(), name='empresa_criar'),
    path('empresas/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_editar'),
    path('empresas/<int:pk>/toggle-ativo/', views.EmpresaToggleAtivoView.as_view(), name='empresa_toggle_ativo'),
]

