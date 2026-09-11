"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Estoque (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Na impressão 3D (FDM), o filamento plástico é o sangue da oficina!
Compramos carretéis (bobinas) que normalmente vêm com 1.000 gramas (1 kg).
Conforme as impressoras imprimem as peças dos clientes, esse plástico vai sendo
derretido e gasto grama por grama.

Este arquivo cria duas tabelas essenciais:
  1. 'Filamento': É o carretel individual que você tem na prateleira.
     - Guarda: Marca, Tipo do Plástico (PLA, PETG, ABS), Cor exata,
       Peso Inicial (ex: 1000g), Peso Atual Restante (ex: 430g), Custo do Rolo (R$),
       Fornecedor e Localização física (ex: "Gaveta 2", "Estufa de Secagem").
  2. 'MovimentacaoEstoque': É o extrato bancário de cada grama de filamento.
     - Toda vez que entra um rolo novo, que uma peça é impressa (consumo),
       que uma impressão falha (perda) ou que você pesa o rolo na balança
       (ajuste manual), uma linha é gerada aqui registrando quem fez, quando,
       quanto pesava antes, quanto pesou depois e a diferença!
=============================================================================
"""

from django.db import models
from django.contrib.auth.models import User


class Filamento(models.Model):
    """
    Representa um carretel/bobina de filamento físico no estoque da oficina 3D.
    """
    # Marca do fabricante (ex: Voolt3D, Creality, Polymaker, eSun)
    marca = models.CharField('Marca', max_length=100)
    
    # Tipo de polímero/plástico (ex: PLA, PLA Silk, PETG, ABS, TPU Flexível)
    material = models.CharField('Material', max_length=100)
    
    # Cor visual do filamento (ex: Preto Fosco, Vermelho Rubi, Azul Céu, Branco Neve)
    cor = models.CharField('Cor', max_length=100)
    
    # Peso total do filamento quando o rolo foi comprado/aberto (geralmente 1000g ou 250g)
    peso_inicial = models.DecimalField('Peso Inicial (g)', max_digits=8, decimal_places=2)
    
    # Quantidade de plástico que ainda sobra no rolo neste momento.
    # Conforme as impressões vão sendo concluídas, este número diminui automaticamente!
    peso_atual = models.DecimalField('Peso Atual (g)', max_digits=8, decimal_places=2)
    
    # Quanto foi pago pelo rolo na compra (ex: R$ 95,00). Usado para calcular o custo do grama!
    custo_rolo = models.DecimalField('Custo do Rolo', max_digits=8, decimal_places=2)
    
    # Data em que o carretel chegou e foi cadastrado na oficina
    data_entrada = models.DateField('Data de Entrada', auto_now_add=True)
    
    # De quem o filamento foi comprado (ex: Loja 3D, Mercado Livre, Fabricante Direto)
    fornecedor = models.CharField('Fornecedor', max_length=150, blank=True, null=True)
    
    # Lote de fabricação do carretel (útil caso venha com variação de cor ou diâmetro)
    codigo_lote = models.CharField('Código/Lote', max_length=100, blank=True, null=True)
    
    # Onde a bobina está guardada na oficina (ex: "Prateleira A", "Caixa Hermética 1")
    localizacao = models.CharField('Localização', max_length=100, blank=True, null=True)
    
    # Notas adicionais (ex: "Secar a 50°C antes de usar", "Temperatura de bico ideal 215°C")
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Filamento'
        verbose_name_plural = 'Filamentos'
        ordering = ['-data_entrada']  # Exibe os mais novos no topo

    def __str__(self):
        # Texto exibido ao selecionar o filamento na fila de produção ou pedidos
        return f"{self.material} {self.cor} - {self.marca} ({self.peso_atual}g restantes)"


class MovimentacaoEstoque(models.Model):
    """
    Histórico imutável (livro-razão) de todas as alterações de peso dos filamentos.
    Garante rastreabilidade total de para onde foi cada grama de matéria-prima.
    """
    class TipoChoices(models.TextChoices):
        """
        Tipos possíveis de movimentação de material.
        """
        ENTRADA = 'entrada', 'Entrada'               # Chegada de novo rolo na oficina
        CONSUMO = 'consumo', 'Consumo (Produção)'     # Gasto na impressão de uma peça com sucesso
        PERDA = 'perda', 'Perda'                     # Peça descolou, bico entupiu ou faltou luz
        AJUSTE = 'ajuste', 'Ajuste Manual'           # Operador pesou o carretel e corrigiu a diferença

    # Carretel que sofreu a movimentação.
    # on_delete=models.PROTECT impede que alguém apague um filamento que já tenha movimentações
    filamento = models.ForeignKey(Filamento, on_delete=models.PROTECT, related_name='movimentacoes')
    
    # Tipo de operação realizada (escolhido entre as opções acima)
    tipo = models.CharField('Tipo de Movimentação', max_length=20, choices=TipoChoices.choices)
    
    # Momento exato em que a movimentação ocorreu
    data = models.DateTimeField('Data e Hora', auto_now_add=True)
    
    # Quantidade em gramas alterada (positivo para entrada, negativo para consumo/perda)
    quantidade = models.DecimalField(
        'Quantidade (g)', 
        max_digits=8, 
        decimal_places=2, 
        help_text="Valores positivos para entrada, negativos para saída"
    )
    
    # Peso que estava gravado no sistema antes desta operação
    quantidade_anterior = models.DecimalField('Quantidade Anterior (g)', max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Peso que ficou gravado após a operação
    quantidade_nova = models.DecimalField('Quantidade Nova (g)', max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Justificativa da alteração (ex: "Impressão da Ordem #42 finalizada", "Aferição periódica na balança")
    motivo = models.TextField('Motivo / Observação', blank=True, null=True)
    
    # Usuário (operador da oficina) que realizou a pesagem ou ação
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-data']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.filamento} ({self.quantidade}g)"

