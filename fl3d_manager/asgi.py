"""
=============================================================================
FL3D Manager - Conector de Servidor Web Assíncrono (asgi.py)
=============================================================================
ASGI significa "Asynchronous Server Gateway Interface" (Interface de Comunicação
com Servidor Web Assíncrono).

VISÃO GERAL E CONCEITO:
Diferente do WSGI tradicional que atende uma requisição por vez de forma síncrona,
o padrão ASGI permite que o sistema lide com eventos modernos em tempo real,
como WebSockets, chats ao vivo ou notificações instantâneas sem travar o servidor.
Ele é a porta de entrada assíncrona do FL3D Manager.
=============================================================================
"""

import os
from django.core.asgi import get_asgi_application

# 1. Aponta para as configurações do FL3D Manager
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fl3d_manager.settings')

# 2. Cria a aplicação executável compatível com servidores assíncronos (ex: Daphne, Uvicorn)
application = get_asgi_application()

