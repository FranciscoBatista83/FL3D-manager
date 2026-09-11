"""
=============================================================================
FL3D Manager - Roteamento do Módulo Financeiro (urls.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Mapeia as páginas do departamento financeiro e fluxo de caixa:
  - /financeiro/                    -> Painel geral financeiro (gráficos e resumos).
  - /financeiro/lancamentos/        -> Extrato de entradas e saídas.
  - /financeiro/lancamentos/novo/   -> Formulário para lançar receita ou despesa.
  - /financeiro/lancamentos/<id>/editar/  -> Edição de lançamento.
  - /financeiro/lancamentos/<id>/excluir/ -> Exclusão de lançamento.
  - /financeiro/relatorio/          -> Relatório de resultados e custos por categoria.
=============================================================================
"""

from django.urls import path
from . import views

# Namespace para o módulo financeiro
app_name = 'financeiro'

urlpatterns = [
    # Painel com gráficos e métricas
    path('', views.DashboardFinanceiroView.as_view(), name='dashboard'),
    
    # Livro-caixa / extrato
    path('lancamentos/', views.MovimentacaoFinanceiraListView.as_view(), name='lista'),
    
    # Novo lançamento
    path('lancamentos/novo/', views.MovimentacaoFinanceiraCreateView.as_view(), name='novo'),
    
    # Edição de lançamento
    path('lancamentos/<int:pk>/editar/', views.MovimentacaoFinanceiraUpdateView.as_view(), name='editar'),
    
    # Exclusão de lançamento
    path('lancamentos/<int:pk>/excluir/', views.MovimentacaoFinanceiraDeleteView.as_view(), name='excluir'),
    
    # Relatório analítico por período e categorias
    path('relatorio/', views.RelatorioView.as_view(), name='relatorio'),
]
