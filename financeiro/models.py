"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo Financeiro (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Controla o fluxo de caixa (entradas e saídas de dinheiro) da oficina FL3D Studio.
Para manter a saúde do negócio, precisamos saber exatamente de onde vem o dinheiro
(vendas de peças impressas) e para onde ele vai (compra de filamentos, conta de luz,
manutenção de bicos e eixos, fretes e embalagens).

Este arquivo define a tabela 'MovimentacaoFinanceira':
  - Tipo:
    * ENTRADA: Dinheiro entrando no caixa (vendas de peças, pagamentos de clientes).
    * SAÍDA: Dinheiro saindo (despesas operacionais e custos fixos/variáveis).
  - Categorias de Custos e Receitas:
    * Vendas, Pedidos, Outros Recebimentos.
    * Filamento, Energia Elétrica, Embalagens, Fretes, Taxas de Cartão/PIX, Manutenção.
  - Vínculo com Pedidos: Permite associar uma entrada diretamente a um pedido específico.
=============================================================================
"""

from django.db import models
from pedidos.models import Pedido


class MovimentacaoFinanceira(models.Model):
    """
    Tabela do Livro-Caixa da empresa. Registra cada centavo que entra ou sai.
    """
    class TipoChoices(models.TextChoices):
        """
        Direção do fluxo de dinheiro.
        """
        ENTRADA = 'entrada', 'Entrada'  # Receita
        SAIDA = 'saida', 'Saída'        # Despesa

    class CategoriaChoices(models.TextChoices):
        """
        Classificação contábil da despesa ou receita na oficina 3D.
        """
        # Receitas:
        VENDAS = 'vendas', 'Vendas'
        PEDIDOS = 'pedidos', 'Pedidos'
        OUTROS_RECEBIMENTOS = 'outros_recebimentos', 'Outros Recebimentos'
        
        # Despesas / Custos:
        FILAMENTO = 'filamento', 'Filamento'          # Compra de bobinas de matéria-prima
        ENERGIA = 'energia', 'Energia'                # Conta de luz (as impressoras consomem energia constante)
        EMBALAGENS = 'embalagens', 'Embalagens'        # Caixas, plástico bolha, fitas
        FRETE = 'frete', 'Frete'                      # Postagens em Correios ou motoboy
        TAXAS = 'taxas', 'Taxas'                      # Taxas de maquininha de cartão ou intermediadores
        MANUTENCAO = 'manutencao', 'Manutenção'        # Peças de reposição (bicos, termistores, ventoinhas)
        OUTROS_CUSTOS = 'outros_custos', 'Outros Custos'

    # Se é entrada ou saída
    tipo = models.CharField('Tipo', max_length=10, choices=TipoChoices.choices)
    
    # Categoria para relatórios detalhados de custos
    categoria = models.CharField('Categoria', max_length=30, choices=CategoriaChoices.choices)
    
    # Descrição amigável do lançamento (ex: "Venda de 3x Vasos Decorativos", "Compra de 4 rolos PLA Preto")
    descricao = models.CharField('Descrição', max_length=255)
    
    # Valor em Reais (R$)
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    
    # Data em que o pagamento ou recebimento ocorreu de fato
    data = models.DateField('Data')
    
    # Pedido associado (opcional: permite saber se esta receita veio do Pedido #123)
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='movimentacoes_financeiras'
    )
    
    # Notas adicionais (ex: "Nota fiscal nº 1054", "Comprovante enviado por WhatsApp")
    observacoes = models.TextField('Observações', blank=True, null=True)
    
    # Data e hora exatas em que o registro foi digitado no sistema
    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimentação Financeira'
        verbose_name_plural = 'Movimentações Financeiras'
        ordering = ['-data', '-data_registro']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} (R$ {self.valor})"
