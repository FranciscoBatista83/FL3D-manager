"""
=============================================================================
FL3D Manager - Roteamento do Módulo de Produção (urls.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Configura os links de navegação para a gestão do chão de fábrica:
  - /producao/                     -> Lista de ordens de produção.
  - /producao/nova/                -> Criação de uma nova ordem de impressão.
  - /producao/<id>/                -> Ficha detalhada da ordem e histórico.
  - /producao/<id>/editar/         -> Atualização de status ou máquina.
  - /producao/<id>/imprimir/       -> Apontamento de término da impressão (Sucesso/Falha).
  - /producao/perdas/              -> Painel de perdas de material.
  - /producao/perdas/nova/         -> Cadastro avulso de perda de filamento.
=============================================================================
"""

from django.urls import path
from . import views

# Namespace para o módulo de produção
app_name = 'producao'

urlpatterns = [
    # Ordens de Produção
    path('', views.ProducaoListView.as_view(), name='lista'),
    path('nova/', views.ProducaoCreateView.as_view(), name='nova'),
    path('<int:pk>/', views.ProducaoDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.ProducaoUpdateView.as_view(), name='editar'),

    # Registro de Conclusão / Apontamento de Impressão
    path('<int:producao_pk>/imprimir/', views.RegistroImpressaoCreateView.as_view(), name='registrar_impressao'),

    # Gestão de Perdas e Desperdícios
    path('perdas/', views.PerdaListView.as_view(), name='perdas'),
    path('perdas/nova/', views.PerdaCreateView.as_view(), name='nova_perda'),
]
