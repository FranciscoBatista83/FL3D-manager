"""
=============================================================================
FL3D Manager - Roteamento do Módulo de Estoque (urls.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Define os links de navegação para o estoque de filamentos:
  - /estoque/             -> Visão geral de todos os carretéis de filamento.
  - /estoque/novo/        -> Cadastro de uma nova bobina que chegou.
  - /estoque/<id>/        -> Ficha detalhada, barra de progresso e histórico de uso.
  - /estoque/<id>/editar/ -> Edição de dados cadastrais (marca, cor, fornecedor).
  - /estoque/<id>/ajuste/ -> Tela de aferição na balança física.
=============================================================================
"""

from django.urls import path
from . import views

# Namespace do módulo de estoque (ex: {% url 'estoque:lista' %})
app_name = 'estoque'

urlpatterns = [
    # Lista de filamentos
    path('', views.FilamentoListView.as_view(), name='lista'),
    
    # Cadastro de novo filamento
    path('novo/', views.FilamentoCreateView.as_view(), name='novo'),
    
    # Ficha de detalhes do filamento
    path('<int:pk>/', views.FilamentoDetailView.as_view(), name='detalhe'),
    
    # Edição do filamento
    path('<int:pk>/editar/', views.FilamentoUpdateView.as_view(), name='editar'),
    
    # Ajuste manual por pesagem na balança
    path('<int:pk>/ajuste/', views.ajuste_estoque_view, name='ajuste'),
]

