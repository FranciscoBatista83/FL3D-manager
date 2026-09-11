"""
=============================================================================
FL3D Manager - Roteamento do Módulo de Pedidos (urls.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Define as rotas das telas do módulo comercial e de pedidos:
  - /pedidos/              -> Lista de vendas e orçamentos com filtros.
  - /pedidos/novo/         -> Tela de lançamento de novo pedido com itens.
  - /pedidos/<id>/         -> Ficha detalhada do pedido e itens.
  - /pedidos/<id>/editar/  -> Edição dos itens e valores do pedido.
  - /pedidos/<id>/cancelar/-> Cancelamento oficial do pedido.
=============================================================================
"""

from django.urls import path
from . import views

# Namespace para o módulo de pedidos
app_name = 'pedidos'

urlpatterns = [
    # Listagem de pedidos
    path('', views.PedidoListView.as_view(), name='lista'),
    
    # Criação de novo pedido
    path('novo/', views.PedidoCreateView.as_view(), name='novo'),
    
    # Detalhes do pedido
    path('<int:pk>/', views.PedidoDetailView.as_view(), name='detalhe'),
    
    # Edição do pedido
    path('<int:pk>/editar/', views.PedidoUpdateView.as_view(), name='editar'),
    
    # Cancelamento do pedido
    path('<int:pk>/cancelar/', views.PedidoDeleteView.as_view(), name='cancelar'),
]
