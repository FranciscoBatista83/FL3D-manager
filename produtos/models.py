"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Produtos (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Aqui criamos o catálogo oficial de produtos da FL3D Studio.
Na impressão 3D, um "produto" pode ser uma peça decorativa (vaso, estatueta),
uma peça técnica de reposição, um chaveiro personalizado ou um suporte.

Este arquivo organiza duas tabelas:
  1. 'CategoriaProduto': Agrupa as peças (ex: Decoração, Peças Automotivas,
     Colecionáveis, Utilitários).
  2. 'Produto': A ficha técnica e comercial de cada item, contendo:
     - Dados de Venda: Nome, Código SKU único, Preço de Venda, Foto e Margem de Lucro.
     - Parâmetros Técnicos de Impressão 3D:
       * Material recomendado (ex: PLA, PETG, ABS, Resina).
       * Cor recomendada (ex: Preto Fosco, Vermelho Seda, Mármore).
       * Peso Estimado em gramas (g): fundamental para saber quanto filamento será gasto!
       * Tempo Estimado de Impressão (HH:MM:SS): essencial para planejar a fila das impressoras.
       * Custo Estimado: soma do valor do filamento gasto + energia elétrica + desgaste da máquina.
=============================================================================
"""

from django.db import models


class CategoriaProduto(models.Model):
    """
    Classificação ou família a qual o produto pertence (ex: Acessórios, Decoração, Engenharia).
    """
    # Nome da categoria (obrigatório, até 100 caracteres)
    nome = models.CharField('Nome da Categoria', max_length=100)
    
    # Explicação detalhada sobre o tipo de produtos dessa categoria (opcional)
    descricao = models.TextField('Descrição', blank=True, null=True)

    class Meta:
        verbose_name = 'Categoria de Produto'
        verbose_name_plural = 'Categorias de Produtos'
        ordering = ['nome']  # Lista sempre em ordem alfabética

    def __str__(self):
        # Exibe o nome da categoria nos menus de seleção
        return self.nome


class Produto(models.Model):
    """
    Ficha do Produto 3D. Guarda tanto os dados comerciais quanto as métricas
    técnicas necessárias para a fabricação aditiva (impressão 3D).
    """
    # -------------------------------------------------------------------------
    # IDENTIFICAÇÃO BÁSICA
    # -------------------------------------------------------------------------
    # Nome do produto (ex: "Suporte de Fone de Ouvido Skull")
    nome = models.CharField('Nome', max_length=200)
    
    # Código interno ou SKU para facilitar a busca rápida e etiquetas (deve ser único)
    codigo = models.CharField('Código', max_length=50, unique=True, blank=True, null=True)
    
    # Categoria vinculada. Se a categoria for apagada, o produto continua existindo (SET_NULL)
    categoria = models.ForeignKey(
        CategoriaProduto, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='produtos'
    )
    
    # Detalhes, modo de montagem ou especificações do item
    descricao = models.TextField('Descrição', blank=True, null=True)
    
    # Foto real do produto impresso ou render 3D (salva na pasta 'media/produtos/')
    foto = models.ImageField('Foto', upload_to='produtos/', blank=True, null=True)
    
    # -------------------------------------------------------------------------
    # PARÂMETROS TÉCNICOS DE IMPRESSÃO 3D
    # -------------------------------------------------------------------------
    # Tipo de filamento mais adequado (ex: PLA para decoração, PETG para peças mecânicas ou calor)
    material = models.CharField('Material Recomendado', max_length=100, blank=True, null=True)
    
    # Cor padrão que o cliente mais costuma pedir ou para qual o modelo foi calibrado
    cor = models.CharField('Cor Recomendada', max_length=100, blank=True, null=True)
    
    # Quantidade de filamento em gramas necessária para imprimir este item (ex: 85.50 g).
    # Este número vem do software fatiador (Bambu Studio, Cura, PrusaSlicer).
    peso_estimado = models.DecimalField(
        'Peso Estimado (g)', 
        max_digits=8, 
        decimal_places=2, 
        help_text='Peso estimado em gramas obtido no software fatiador'
    )
    
    # Duração prevista da impressão (ex: 03:45:00 para 3 horas e 45 minutos).
    tempo_estimado = models.DurationField(
        'Tempo Estimado de Impressão', 
        blank=True, 
        null=True, 
        help_text='Formato: HH:MM:SS'
    )
    
    # -------------------------------------------------------------------------
    # ENGENHARIA DE CUSTOS E FORMAÇÃO DE PREÇO
    # -------------------------------------------------------------------------
    # Custo de fabricação calculado (matéria-prima gasta + energia + desgaste)
    custo_estimado = models.DecimalField('Custo Estimado', max_digits=10, decimal_places=2, default=0.00)
    
    # Preço final cobrado do cliente na venda
    preco_venda = models.DecimalField('Preço de Venda', max_digits=10, decimal_places=2, default=0.00)
    
    # Porcentagem de lucro sobre a venda (ex: 150.00 para 150% de margem)
    margem_lucro = models.DecimalField('Margem de Lucro (%)', max_digits=5, decimal_places=2, blank=True, null=True)
    
    # -------------------------------------------------------------------------
    # STATUS E OBSERVAÇÕES
    # -------------------------------------------------------------------------
    # Anotações livres da oficina (ex: "Precisa de suportes em árvore no fatiador")
    observacoes = models.TextField('Observações', blank=True, null=True)
    
    # Soft delete: inativa o produto sem quebrar histórico de vendas antigas
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

