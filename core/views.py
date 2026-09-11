"""
=============================================================================
FL3D Manager - Visualizações do Módulo Core (views.py)
=============================================================================
VISÃO GERAL E CONCEITO:
No Django, uma "View" é o garçom do sistema:
  1. O cliente (navegador) faz um pedido (requisição HTTP).
  2. A View recebe esse pedido, busca os ingredientes necessários no banco de dados (Models).
  3. Prepara as informações e entrega o prato pronto (página HTML renderizada) para o navegador.

As views deste módulo servem para páginas institucionais ou tratamentos globais.
=============================================================================
"""

from django.shortcuts import render

# Views globais do sistema podem ser definidas aqui

