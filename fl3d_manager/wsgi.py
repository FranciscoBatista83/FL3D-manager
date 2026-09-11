"""
=============================================================================
FL3D Manager - Conector de Servidor Web Tradicional (wsgi.py)
=============================================================================
WSGI significa "Web Server Gateway Interface" (Interface de Comunicação com Servidor Web).

VISÃO GERAL E CONCEITO:
Quando você coloca este sistema na internet através de servidores web profissionais
como Nginx, Apache ou Gunicorn, esses servidores não conversam diretamente em Python.
Eles precisam de um "tradutor" oficial que recebe o pedido da internet e o entrega
ao Django de forma padronizada. Esse tradutor é a variável `application` criada abaixo.
=============================================================================
"""

import os
from django.core.wsgi import get_wsgi_application

# 1. Avisa ao servidor qual arquivo contém as configurações da FL3D Studio
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fl3d_manager.settings')

# 2. Cria a aplicação executável que receberá as conexões web
application = get_wsgi_application()

