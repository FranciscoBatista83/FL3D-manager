from django.urls import path
from . import views

app_name = 'calculadora'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/calcular/', views.calcular_api, name='calcular_api'),
    path('api/salvar-produto/', views.salvar_produto_api, name='salvar_produto_api'),
]
