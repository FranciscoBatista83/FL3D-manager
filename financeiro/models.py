"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo Financeiro (models.py)
=============================================================================
Controla o fluxo de caixa (entradas e saídas de dinheiro) da oficina 3D.
Agora com suporte Multi-Empresa.
=============================================================================
"""

from django.db import models
from core.models import Empresa
from pedidos.models import Pedido


class MovimentacaoFinanceira(models.Model):
    """
    Tabela do Livro-Caixa da empresa. Registra cada centavo que entra ou sai.
    Isolada por empresa.
    """
    class TipoChoices(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SAIDA = 'saida', 'Saída'

    class CategoriaChoices(models.TextChoices):
        VENDAS = 'vendas', 'Vendas'
        PEDIDOS = 'pedidos', 'Pedidos'
        OUTROS_RECEBIMENTOS = 'outros_recebimentos', 'Outros Recebimentos'
        FILAMENTO = 'filamento', 'Filamento'
        ENERGIA = 'energia', 'Energia'
        EMBALAGENS = 'embalagens', 'Embalagens'
        FRETE = 'frete', 'Frete'
        TAXAS = 'taxas', 'Taxas'
        MANUTENCAO = 'manutencao', 'Manutenção'
        OUTROS_CUSTOS = 'outros_custos', 'Outros Custos'

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='movimentacoes_financeiras',
        verbose_name='Empresa',
        null=True,
        blank=True
    )
    tipo = models.CharField('Tipo', max_length=10, choices=TipoChoices.choices)
    categoria = models.CharField('Categoria', max_length=30, choices=CategoriaChoices.choices)
    descricao = models.CharField('Descrição', max_length=255)
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    data = models.DateField('Data')
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='movimentacoes_financeiras'
    )
    observacoes = models.TextField('Observações', blank=True, null=True)
    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimentação Financeira'
        verbose_name_plural = 'Movimentações Financeiras'
        ordering = ['-data', '-data_registro']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} (R$ {self.valor})"
