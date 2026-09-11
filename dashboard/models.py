"""
=============================================================================
FL3D Manager - Modelos do Módulo Dashboard (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
O módulo Dashboard não precisa de tabelas próprias no banco de dados, porque
o papel dele é apenas consultar e resumir dados que já existem em outros
módulos (como Pedidos, Produção, Estoque e Financeiro).
=============================================================================
"""

from django.db import models

# O dashboard utiliza dados consolidados dos demais aplicativos.

