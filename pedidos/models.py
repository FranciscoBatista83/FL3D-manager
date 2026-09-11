"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Pedidos (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
O módulo de Pedidos é o motor comercial da FL3D Studio. É aqui que os clientes
solicitam orçamentos e compras de impressões 3D.

Este arquivo é composto por duas tabelas interligadas:
  1. 'Pedido': O cabeçalho da venda.
     - Guarda: Número sequencial automático (#1, #2...), Cliente comprador,
       Data do pedido, Prazo prometido de entrega, Status da produção,
       Totais financeiros (Soma dos itens, Desconto em R$, Valor final a pagar),
       Meio de pagamento (PIX, Cartão, Boleto, Dinheiro) e Status do pagamento
       (Pendente, Parcial, Pago).
  2. 'ItemPedido': As linhas do pedido (o carrinho de compras).
     - Um pedido pode ter vários itens (ex: 2x Suporte de Fone + 5x Chaveiros).
     - Guarda a quantidade, o valor unitário e o total de cada produto.
=============================================================================
"""

from django.db import models
from clientes.models import Cliente
from produtos.models import Produto


class Pedido(models.Model):
    """
    Tabela principal que registra a venda ou orçamento para um cliente.
    """
    class StatusChoices(models.TextChoices):
        """
        Ciclo de vida do pedido dentro da empresa:
        Orçamento -> Aprovado -> Aguardando Produção -> Em Produção -> Pronto -> Entregue
        """
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
        """
        Métodos de quitação aceitos pela oficina.
        """
        PIX = 'pix', 'PIX'
        CARTAO_CREDITO = 'credito', 'Cartão de Crédito'
        CARTAO_DEBITO = 'debito', 'Cartão de Débito'
        DINHEIRO = 'dinheiro', 'Dinheiro'
        BOLETO = 'boleto', 'Boleto'
        OUTRO = 'outro', 'Outro'
        
    class StatusPagamentoChoices(models.TextChoices):
        """
        Situação financeira do pedido.
        """
        PENDENTE = 'pendente', 'Pendente'            # Cliente ainda não pagou
        PARCIAL = 'parcial', 'Pago Parcialmente'    # Cliente deu sinal/entrada (ex: 50%)
        PAGO = 'pago', 'Pago'                        # Valor 100% quitado
        CANCELADO = 'cancelado', 'Cancelado'

    # Número identificador do pedido (chave primária gerada em ordem crescente 1, 2, 3...)
    numero = models.AutoField(primary_key=True)
    
    # Cliente que solicitou o pedido.
    # on_delete=models.PROTECT não permite apagar o cliente do banco se ele tiver pedidos cadastrados
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    
    # Data e hora exatas em que o pedido foi aberto
    data_pedido = models.DateTimeField('Data do Pedido', auto_now_add=True)
    
    # Prazo combinado com o cliente para a retirada ou postagem da encomenda
    data_entrega_prevista = models.DateField('Data Prevista de Entrega', blank=True, null=True)
    
    # Situação atual da ordem (o padrão inicial é 'novo')
    status = models.CharField('Status', max_length=30, choices=StatusChoices.choices, default=StatusChoices.NOVO)
    
    # -------------------------------------------------------------------------
    # VALORES MONETÁRIOS DO PEDIDO
    # -------------------------------------------------------------------------
    # Soma dos valores de todos os produtos do carrinho
    valor_produtos = models.DecimalField('Valor dos Produtos', max_digits=10, decimal_places=2, default=0.00)
    
    # Desconto em Reais concedido ao cliente (se houver)
    desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=0.00)
    
    # Valor líquido final a pagar (valor_produtos menos o desconto)
    valor_final = models.DecimalField('Valor Final', max_digits=10, decimal_places=2, default=0.00)
    
    # Opção de pagamento escolhida
    forma_pagamento = models.CharField('Forma de Pagamento', max_length=20, choices=FormaPagamentoChoices.choices, blank=True, null=True)
    
    # Situação do pagamento
    status_pagamento = models.CharField('Status do Pagamento', max_length=20, choices=StatusPagamentoChoices.choices, default=StatusPagamentoChoices.PENDENTE)
    
    # Requisitos especiais do cliente (ex: "Embalar para presente", "Cor azul marinho fosca")
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_pedido']  # Pedidos mais recentes aparecem primeiro

    def __str__(self):
        return f"Pedido #{self.numero} - {self.cliente.nome}"


class ItemPedido(models.Model):
    """
    Linha individual de produto dentro de um pedido específico.
    """
    # Pedido pai ao qual este item pertence.
    # on_delete=models.CASCADE faz com que, se o pedido for deletado, seus itens sumam juntos
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    
    # Produto do catálogo que foi vendido
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='itens_pedido')
    
    # Quantas unidades dessa mesma peça foram encomendadas
    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    
    # Preço cobrado por cada unidade no momento da venda
    valor_unitario = models.DecimalField('Valor Unitário', max_digits=10, decimal_places=2)
    
    # Total da linha (quantidade * valor_unitario)
    valor_total = models.DecimalField('Valor Total', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Pedido #{self.pedido.numero})"
