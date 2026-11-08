"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Pedidos (models.py)
=============================================================================
Gestão comercial, orçamentos e pedidos de impressão 3D.
Agora com suporte Multi-Empresa.
=============================================================================
"""

from django.db import models
from core.models import Empresa
from clientes.models import Cliente
from produtos.models import Produto


class Pedido(models.Model):
    """
    Tabela principal que registra a venda ou orçamento para um cliente.
    Isolada por empresa.
    """
    class StatusChoices(models.TextChoices):
        NOVO = 'novo', 'Novo'
        ORCAMENTO = 'orcamento', 'Orçamento'
        AGUARDANDO_APROVACAO = 'aguardando_aprovacao', 'Aguardando Aprovação'
        APROVADO = 'aprovado', 'Aprovado'
        AGUARDANDO_PRODUCAO = 'aguardando_producao', 'Aguardando Produção'
        EM_PRODUCAO = 'em_producao', 'Em Produção'
        PRONTO = 'pronto', 'Pronto'
        ENTREGUE = 'entregue', 'Entregue'
        CANCELADO = 'cancelado', 'Cancelado'

    class FormaPagamentoChoices(models.TextChoices):
        PIX = 'pix', 'PIX'
        CARTAO_CREDITO = 'credito', 'Cartão de Crédito'
        CARTAO_DEBITO = 'debito', 'Cartão de Débito'
        DINHEIRO = 'dinheiro', 'Dinheiro'
        BOLETO = 'boleto', 'Boleto'
        OUTRO = 'outro', 'Outro'
        
    class StatusPagamentoChoices(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        PARCIAL = 'parcial', 'Pago Parcialmente'
        PAGO = 'pago', 'Pago'
        CANCELADO = 'cancelado', 'Cancelado'

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name='Empresa',
        null=True,
        blank=True
    )
    numero = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    data_pedido = models.DateTimeField('Data do Pedido', auto_now_add=True)
    data_entrega_prevista = models.DateField('Data Prevista de Entrega', blank=True, null=True)
    status = models.CharField('Status', max_length=30, choices=StatusChoices.choices, default=StatusChoices.NOVO)
    
    valor_produtos = models.DecimalField('Valor dos Produtos', max_digits=10, decimal_places=2, default=0.00)
    desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=0.00)
    valor_final = models.DecimalField('Valor Final', max_digits=10, decimal_places=2, default=0.00)
    
    forma_pagamento = models.CharField('Forma de Pagamento', max_length=20, choices=FormaPagamentoChoices.choices, blank=True, null=True)
    status_pagamento = models.CharField('Status do Pagamento', max_length=20, choices=StatusPagamentoChoices.choices, default=StatusPagamentoChoices.PENDENTE)
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_pedido']

    def __str__(self):
        return f"Pedido #{self.numero} - {self.cliente.nome}"


class ItemPedido(models.Model):
    """
    Linha individual de produto dentro de um pedido específico.
    """
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='itens_pedido')
    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    valor_unitario = models.DecimalField('Valor Unitário', max_digits=10, decimal_places=2)
    valor_total = models.DecimalField('Valor Total', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Pedido #{self.pedido.numero})"
