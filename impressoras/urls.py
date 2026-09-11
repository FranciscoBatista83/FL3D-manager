"""
=============================================================================
FL3D Manager - Roteamento do Módulo de Impressoras (urls.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Define as rotas de navegação para o módulo de impressoras:
  - /impressoras/             -> Painel com todas as máquinas da oficina.
  - /impressoras/nova/        -> Formulário para cadastrar uma nova impressora.
  - /impressoras/<id>/        -> Detalhes da impressora e histórico das últimas produções.
  - /impressoras/<id>/editar/ -> Alteração de status e dados da máquina.
  - /impressoras/<id>/excluir/-> Confirmação de exclusão do equipamento.
=============================================================================
"""

from django.urls import path
from . import views

# Identificador de namespace para as rotas do módulo de impressoras
app_name = 'impressoras'

urlpatterns = [
    # Listagem de impressoras
    path('', views.ImpressoraListView.as_view(), name='lista'),
    
    # Cadastro de nova impressora
    path('nova/', views.ImpressoraCreateView.as_view(), name='nova'),
    
    # Detalhes da impressora
    path('<int:pk>/', views.ImpressoraDetailView.as_view(), name='detalhe'),
    
    # Edição de dados e status
    path('<int:pk>/editar/', views.ImpressoraUpdateView.as_view(), name='editar'),
    
    # Exclusão da impressora
    path('<int:pk>/excluir/', views.ImpressoraDeleteView.as_view(), name='excluir'),
]
