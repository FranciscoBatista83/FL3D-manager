"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Relatórios (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
O módulo de Relatórios consulta diretamente as tabelas de Pedidos, Produção,
Estoque e Financeiro para gerar estatísticas. Portanto, não requer tabelas
próprias no banco de dados para os indicadores padrão do sistema.
=============================================================================
"""

from django.db import models

# Modelos para guardar relatórios salvos ou agendados podem ser definidos aqui futuramente.
