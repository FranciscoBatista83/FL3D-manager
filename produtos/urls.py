"""
=============================================================================
FL3D Manager - Roteamento do Módulo de Produtos (urls.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Mapeia os links da barra de endereços para as telas do catálogo de produtos:
  - /produtos/             -> Lista todos os produtos cadastrados.
  - /produtos/novo/        -> Formulário para adicionar um novo produto 3D.
  - /produtos/<id>/        -> Ficha técnica e detalhes da peça.
  - /produtos/<id>/editar/ -> Tela de edição de preços e dados técnicos.
  - /produtos/<id>/excluir/-> Confirmação de inativação do item.
=============================================================================
"""

from django.urls import path
from . import views

# Namespace do módulo de produtos (ex: {% url 'produtos:lista' %})
app_name = 'produtos'

urlpatterns = [
    # Listagem de produtos
    path('', views.ProdutoListView.as_view(), name='lista'),
    
    # Cadastro de novo produto
    path('novo/', views.ProdutoCreateView.as_view(), name='novo'),
    
    # Visualização detalhada (ficha técnica)
    path('<int:pk>/', views.ProdutoDetailView.as_view(), name='detalhe'),
    
    # Edição de dados do produto
    path('<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='editar'),
    
    # Inativação do produto
    path('<int:pk>/excluir/', views.ProdutoDeleteView.as_view(), name='excluir'),
]

