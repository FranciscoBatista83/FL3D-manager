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


class Categoria(models.Model):
    """
    Categoria de produtos 3D (ex: Vasos, Decoração, Utilitários, Brindes, Action Figures).
    """
    nome = models.CharField('Nome da Categoria', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True, null=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """
    Ficha do Produto 3D. Guarda dados comerciais e métricas técnicas
    necessárias para a fabricação aditiva (impressão 3D).
    """
    # -------------------------------------------------------------------------
    # IDENTIFICAÇÃO BÁSICA E SKU
    # -------------------------------------------------------------------------
    nome = models.CharField('Nome do Produto', max_length=200)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos',
        verbose_name='Categoria'
    )
    codigo = models.CharField('Código / SKU', max_length=50, unique=True, blank=True, null=True, help_text='Código SKU único interno')
    descricao = models.TextField('Descrição e Especificações', blank=True, null=True)
    foto = models.ImageField('Foto do Produto', upload_to='produtos/', blank=True, null=True)
    arquivo_impressao = models.FileField('Arquivo de Impressão', upload_to='arquivos_impressao/', blank=True, null=True, help_text='Ex: .gcode, .stl, .3mf')
    material = models.CharField('Material (Filamento)', max_length=100, blank=True, null=True, help_text='Ex: PLA, PETG, ABS, Resina')

    # -------------------------------------------------------------------------
    # PARÂMETROS TÉCNICOS DE IMPRESSÃO 3D E ENGENHARIA DE CUSTOS
    # -------------------------------------------------------------------------
    peso_estimado = models.DecimalField('Peso Estimado (g)', max_digits=8, decimal_places=2, default=0.00, help_text='Peso em gramas (g)')
    tempo_estimado = models.DurationField('Tempo de Impressão', blank=True, null=True, help_text='Duração (HH:MM:SS)')

    valor_kg_filamento = models.DecimalField('Preço do Filamento (R$/kg)', max_digits=10, decimal_places=2, default=0.00)
    detalhes_filamentos = models.JSONField('Detalhes dos Filamentos', default=list, blank=True)
    potencia_impressora_w = models.DecimalField('Potência da Impressora (W)', max_digits=8, decimal_places=2, default=150.00)
    custo_kwh_energia = models.DecimalField('Tarifa de Energia (R$/kWh)', max_digits=8, decimal_places=2, default=0.85)

    custo_embalagem = models.DecimalField('Custo de Embalagem (R$)', max_digits=10, decimal_places=2, default=0.00)
    custo_insumos = models.DecimalField('Custo de Insumos (R$)', max_digits=10, decimal_places=2, default=0.00)
    custo_mao_de_obra = models.DecimalField('Custo de Mão de Obra (R$)', max_digits=10, decimal_places=2, default=0.00)

    # -------------------------------------------------------------------------
    # MARKETPLACE E FORMAÇÃO DE PREÇO
    # -------------------------------------------------------------------------
    marketplace = models.CharField('Marketplace Padrão', max_length=50, default='direto', help_text='Venda Direta, Shopee, TikTok Shop')
    comissao_afiliado_percentual = models.DecimalField('Comissão de Afiliados (%)', max_digits=5, decimal_places=2, default=0.00, help_text='Percentual de comissão de afiliado (Shopee/TikTok)')
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

    @property
    def lucro_liquido_unitario(self):
        """Lucro líquido da unidade base (preco_venda - custo_estimado - custo_taxas_marketplace)."""
        return round(self.preco_venda - self.custo_estimado - self.custo_taxas_marketplace, 2)


class VariacaoProduto(models.Model):
    """
    Pacotes e variações por quantidade de um mesmo produto (ex: 5 un, 10 un, 20 un).
    Permite precificação em lote com margens, embalagens e taxas de marketplace próprias.
    """
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='variacoes',
        verbose_name='Produto Principal'
    )
    nome = models.CharField('Nome da Variação / Pacote', max_length=100, help_text='Ex: Pacote com 5 un, Kit Atacado 20 un')
    quantidade = models.PositiveIntegerField('Quantidade de Peças', default=1)
    sku_sufixo = models.CharField('Sufixo SKU', max_length=30, blank=True, null=True, help_text='Ex: -KIT5, -KIT10')

    custo_embalagem = models.DecimalField('Custo de Embalagem (R$)', max_digits=10, decimal_places=2, default=0.00)
    custo_producao_total = models.DecimalField('Custo de Produção Total (R$)', max_digits=10, decimal_places=2, default=0.00)

    margem_lucro = models.DecimalField('Margem de Lucro Alvo (%)', max_digits=6, decimal_places=2, default=0.00)
    preco_venda = models.DecimalField('Preço de Venda do Pacote (R$)', max_digits=10, decimal_places=2, default=0.00)
    custo_taxas_marketplace = models.DecimalField('Taxas do Marketplace (R$)', max_digits=10, decimal_places=2, default=0.00)
    lucro_liquido = models.DecimalField('Lucro Líquido (R$)', max_digits=10, decimal_places=2, default=0.00)

    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Variação / Pacote'
        verbose_name_plural = 'Variações / Pacotes'
        ordering = ['quantidade', 'preco_venda']

    def __str__(self):
        return f"{self.produto.nome} - {self.nome} ({self.quantidade} un)"

    @property
    def preco_unitario(self):
        """Preço por unidade dentro do pacote."""
        if self.quantidade and self.quantidade > 0:
            return round(self.preco_venda / self.quantidade, 2)
        return self.preco_venda
