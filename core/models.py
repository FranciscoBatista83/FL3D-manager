"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo Core (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
No Django, um "Model" é a representação de uma tabela do banco de dados em forma
de código Python. Cada classe aqui se transforma em uma tabela onde os dados
são organizados em colunas e linhas.

Este aplicativo 'core' foi projetado para guardar modelos compartilhados
(como classes abstratas de data de criação/atualização ou configurações globais).
Atualmente, cada módulo específico (Clientes, Produtos, etc.) possui seus
próprios modelos dedicados.
=============================================================================
"""

from django.db import models

# Modelos compartilhados globais podem ser adicionados aqui conforme o sistema evoluir.

