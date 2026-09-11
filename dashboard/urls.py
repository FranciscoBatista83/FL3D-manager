"""
=============================================================================
FL3D Manager - Roteamento do Módulo Dashboard (urls.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Define a rota padrão da tela inicial do sistema.
Quando o usuário entra no sistema com o endereço raiz ("http://127.0.0.1:8000/"),
este arquivo diz: "Entregue a visualização `DashboardPrincipalView`!"
=============================================================================
"""

from django.urls import path
from . import views

# Identificador exclusivo do módulo para gerar links no sistema (ex: {% url 'dashboard:index' %})
app_name = 'dashboard'

urlpatterns = [
    # Rota raiz do dashboard (tela inicial com indicadores e métricas)
    path('', views.DashboardPrincipalView.as_view(), name='index'),
]

