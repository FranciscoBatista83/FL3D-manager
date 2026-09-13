"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Produtos (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Catálogo oficial de produtos da FL3D Studio.
Armazena a ficha técnica, parâmetros de impressão 3D e métricas financeiras
alinhadas com a Calculadora de Precificação.
=============================================================================
"""

from django.db import models


class Produto(models.Model):
    """
    Ficha do Produto 3D. Guarda dados comerciais e métricas técnicas
    necessárias para a fabricação aditiva (impressão 3D).
    """
    # -------------------------------------------------------------------------
    # IDENTIFICAÇÃO BÁSICA E SKU
    # -------------------------------------------------------------------------
    nome = models.CharField('Nome do Produto', max_length=200)
    codigo = models.CharField('Código / SKU', max_length=50, unique=True, blank=True, null=True, help_text='Código SKU único interno')
    descricao = models.TextField('Descrição e Especificações', blank=True, null=True)
    foto = models.ImageField('Foto do Produto', upload_to='produtos/', blank=True, null=True)
    material = models.CharField('Material (Filamento)', max_length=100, blank=True, null=True, help_text='Ex: PLA, PETG, ABS, Resina')

    # -------------------------------------------------------------------------
    # PARÂMETROS TÉCNICOS DE IMPRESSÃO 3D E ENGENHARIA DE CUSTOS
    # -------------------------------------------------------------------------
    peso_estimado = models.DecimalField('Peso Estimado (g)', max_digits=8, decimal_places=2, default=0.00, help_text='Peso em gramas (g)')
    tempo_estimado = models.DurationField('Tempo de Impressão', blank=True, null=True, help_text='Duração (HH:MM:SS)')

    valor_kg_filamento = models.DecimalField('Preço do Filamento (R$/kg)', max_digits=10, decimal_places=2, default=0.00)
    potencia_impressora_w = models.DecimalField('Potência da Impressora (W)', max_digits=8, decimal_places=2, default=150.00)
    custo_kwh_energia = models.DecimalField('Tarifa de Energia (R$/kWh)', max_digits=8, decimal_places=2, default=0.85)

    custo_embalagem = models.DecimalField('Custo de Embalagem (R$)', max_digits=10, decimal_places=2, default=0.00)
    custo_insumos = models.DecimalField('Custo de Insumos (R$)', max_digits=10, decimal_places=2, default=0.00)
    custo_mao_de_obra = models.DecimalField('Custo de Mão de Obra (R$)', max_digits=10, decimal_places=2, default=0.00)

    # -------------------------------------------------------------------------
    # MARKETPLACE E FORMAÇÃO DE PREÇO
    # -------------------------------------------------------------------------
    marketplace = models.CharField('Marketplace Padrão', max_length=50, default='direto', help_text='Venda Direta, Shopee, TikTok Shop')
    custo_taxas_marketplace = models.DecimalField('Taxas do Marketplace (R$)', max_digits=10, decimal_places=2, default=0.00)

    custo_estimado = models.DecimalField('Custo Total de Produção (R$)', max_digits=10, decimal_places=2, default=0.00)
    preco_venda = models.DecimalField('Preço de Venda (R$)', max_digits=10, decimal_places=2, default=0.00)
    margem_lucro = models.DecimalField('Margem de Lucro (%)', max_digits=6, decimal_places=2, default=0.00)

    # Status
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return self.nome
