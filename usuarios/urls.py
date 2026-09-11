"""
=============================================================================
FL3D Manager - Rotas do Módulo de Usuários (urls.py)
=============================================================================
Define os endereços (URLs) de acesso às telas de gestão de usuários:
  /usuarios/              -> Lista de todos os usuários
  /usuarios/novo/         -> Formulário de cadastro de novo usuário
  /usuarios/<id>/editar/  -> Formulário de edição de usuário existente
  /usuarios/<id>/toggle/  -> Ativa ou desativa o usuário (via POST)
=============================================================================
"""

from django.urls import path
from . import views

# Namespace do módulo: permite usar 'usuarios:lista', 'usuarios:novo', etc.
# nos templates HTML e nas views com reverse_lazy()
app_name = 'usuarios'

urlpatterns = [
    # Lista todos os usuários do sistema
    path('', views.UsuarioListView.as_view(), name='lista'),

    # Formulário de criação de novo usuário
    path('novo/', views.UsuarioCriarView.as_view(), name='novo'),

    # Formulário de edição de um usuário específico (identificado pelo <pk>)
    path('<int:pk>/editar/', views.UsuarioEditarView.as_view(), name='editar'),

    # Botão de ativar/desativar — recebe POST com o ID do usuário
    path('<int:pk>/toggle/', views.UsuarioToggleAtivoView.as_view(), name='toggle'),

    # Exclusão definitiva do usuário
    path('<int:pk>/excluir/', views.UsuarioExcluirView.as_view(), name='excluir'),
]
