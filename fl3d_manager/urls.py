"""
=============================================================================
FL3D Manager - Roteador Principal de Endereços Web (urls.py)
=============================================================================
Este arquivo é o "guia de tráfego" ou a "recepção" de todo o sistema web.

VISÃO GERAL E CONCEITO:
Toda vez que você digita um endereço no navegador (por exemplo, `/clientes/` ou
`/produtos/`), o Django consulta esta lista chamada `urlpatterns` para saber
qual departamento (aplicativo) deve atender aquele pedido.

Pense neste arquivo como o índice de um livro ou a lista de ramais de uma empresa:
  - Ramal 'admin/'       -> Painel de Controle Oficial do Django
  - Ramal 'accounts/'    -> Telas de Login e Logout
  - Ramal 'clientes/'    -> Lista e Cadastro de Clientes
  - Ramal 'produtos/'    -> Catálogo de Peças e Itens 3D
  - Ramal 'pedidos/'     -> Vendas e Pedidos de Impressão
  - Ramal 'producao/'    -> Chão de Fábrica e Fila de Máquinas
  - Ramal 'estoque/'     -> Carretéis de Filamento e Insumos
  - Ramal 'impressoras/' -> Monitoramento das Impressoras 3D
  - Ramal 'financeiro/'  -> Entradas, Saídas e Fluxo de Caixa
  - Ramal vazio ''       -> Tela Inicial (Painel do Dashboard)
=============================================================================
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Lista de rotas mestras do sistema
urlpatterns = [
    # 1. Painel Administrativo interno do Django (gerenciamento avançado)
    path('admin/', admin.site.urls),
    
    # 2. Rotas padrão de autenticação do Django (login, logout, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 3. Módulo de Clientes: cadastro, visualização, edição e histórico
    path('clientes/', include('clientes.urls')),
    
    # 4. Módulo de Produtos: catálogo de peças 3D, valores e tempos estimados
    path('produtos/', include('produtos.urls')),
    
    # 5. Módulo de Pedidos: orçamentos, vendas aprovadas e controle de status
    path('pedidos/', include('pedidos.urls')),
    
    # 6. Módulo de Produção: ordens de serviço, impressões em andamento e perdas
    path('producao/', include('producao.urls')),
    
    # 7. Módulo de Estoque: filamentos (PLA, PETG, ABS), cores, marcas e pesos
    path('estoque/', include('estoque.urls')),
    
    # 8. Módulo de Impressoras: máquinas da oficina, modelos, status e custos de hora
    path('impressoras/', include('impressoras.urls')),
    
    # 9. Módulo Financeiro: lançamentos, receitas, despesas e relatórios de caixa
    path('financeiro/', include('financeiro.urls')),

    # 10. Módulo de Usuários: cadastro, edição e controle de acesso dos operadores
    path('usuarios/', include('usuarios.urls')),

    # 11. Módulo Calculadora: ferramentas de cálculo e custos de impressão 3D
    path('calculadora/', include('calculadora.urls')),

    # 12. Raiz do Sistema ('/'): carrega diretamente o Painel Principal (Dashboard)
    path('', include('dashboard.urls')),
]

# Configuração para Ambiente de Desenvolvimento (DEBUG = True):
# Permite que o navegador exiba e baixe fotos e arquivos carregados no sistema (pasta media/)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

