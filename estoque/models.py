"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Estoque (models.py)
=============================================================================
Controle de carretéis de filamento e movimentações de estoque.
Agora com suporte Multi-Empresa.
=============================================================================
"""

from django.db import models
from django.contrib.auth.models import User
from core.models import Empresa


class Filamento(models.Model):
    """
    Representa um produto / item físico no estoque da oficina 3D.
    Isolado por empresa.
    """
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='filamentos',
        verbose_name='Empresa',
        null=True,
        blank=True
    )
    nome = models.CharField('Nome', max_length=150, blank=True, null=True)
    marca = models.CharField('Marca', max_length=100, blank=True, null=True)
    material = models.CharField('Material', max_length=100, blank=True, null=True)
    cor = models.CharField('Cor', max_length=100, blank=True, null=True)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    preco = models.DecimalField('Preço (R$)', max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    fornecedor = models.CharField(max_length=150, blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True, null=True)

    # Campos Legados
    peso_inicial = models.DecimalField('Peso Inicial (g)', max_digits=8, decimal_places=2, blank=True, null=True)
    peso_atual = models.DecimalField('Peso Atual (g)', max_digits=8, decimal_places=2, blank=True, null=True)
    custo_rolo = models.DecimalField('Custo do Rolo', max_digits=8, decimal_places=2, blank=True, null=True)
    data_entrada = models.DateField('Data de Entrada', auto_now_add=True)
    codigo_lote = models.CharField('Código/Lote', max_length=100, blank=True, null=True)
    localizacao = models.CharField('Localização', max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Item de Estoque'
        verbose_name_plural = 'Itens de Estoque'
        ordering = ['-data_entrada']

    def __str__(self):
        nome_display = self.nome or self.material or 'Item de Estoque'
        return f"{nome_display} - {self.marca or ''}"


class MovimentacaoEstoque(models.Model):
    """
    Histórico imutável de todas as alterações de estoque.
    """
    class TipoChoices(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        CONSUMO = 'consumo', 'Consumo (Produção)'
        PERDA = 'perda', 'Perda'
        AJUSTE = 'ajuste', 'Ajuste Manual'

    filamento = models.ForeignKey(Filamento, on_delete=models.PROTECT, related_name='movimentacoes')
    tipo = models.CharField('Tipo de Movimentação', max_length=20, choices=TipoChoices.choices)
    data = models.DateTimeField('Data e Hora', auto_now_add=True)
    quantidade = models.DecimalField(
        'Quantidade (g)', 
        max_digits=8, 
        decimal_places=2, 
        help_text="Valores positivos para entrada, negativos para saída"
    )
    quantidade_anterior = models.DecimalField('Quantidade Anterior (g)', max_digits=8, decimal_places=2, blank=True, null=True)
    quantidade_nova = models.DecimalField('Quantidade Nova (g)', max_digits=8, decimal_places=2, blank=True, null=True)
    motivo = models.TextField('Motivo / Observação', blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-data']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.filamento} ({self.quantidade}g)"
