"""
=============================================================================
FL3D Manager - Roteamento do Módulo de Clientes (urls.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo define os links (URLs) das telas de gerenciamento de clientes:
  - /clientes/            -> Lista todos os clientes cadastrados.
  - /clientes/novo/       -> Formulário para cadastrar novo cliente.
  - /clientes/<id>/       -> Detalhes e histórico de compras do cliente com esse ID.
  - /clientes/<id>/editar/ -> Formulário para alterar os dados do cliente.
  - /clientes/<id>/excluir/ -> Tela para confirmar a inativação do cliente.
=============================================================================
"""

from django.urls import path
from . import views

# Namespace para referenciar as rotas nos templates HTML (ex: {% url 'clientes:novo' %})
app_name = 'clientes'

urlpatterns = [
    # 1. Rota para listagem com paginação e busca
    path('', views.ClienteListView.as_view(), name='lista'),
    
    # 2. Rota para cadastrar um novo cliente
    path('novo/', views.ClienteCreateView.as_view(), name='novo'),
    
    # 3. Rota para a ficha do cliente (onde <int:pk> é o número do ID do cliente no banco)
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='detalhe'),
    
    # 4. Rota para editar os dados de um cliente existente
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='editar'),
    
    # 5. Rota para inativar (soft delete) um cliente
    path('<int:pk>/excluir/', views.ClienteDeleteView.as_view(), name='excluir'),
]

