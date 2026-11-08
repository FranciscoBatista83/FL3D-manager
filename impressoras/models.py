"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Impressoras (models.py)
=============================================================================
Cadastro e controle do parque de impressoras 3D.
Agora com suporte Multi-Empresa.
=============================================================================
"""

from django.db import models
from core.models import Empresa


class Impressora(models.Model):
    """
    Representa uma impressora 3D física pertencente à oficina.
    Isolada por empresa.
    """
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='impressoras',
        verbose_name='Empresa',
        null=True,
        blank=True
    )
    nome = models.CharField('Nome', max_length=100)
    fabricante = models.CharField('Fabricante', max_length=100, blank=True, null=True)
    modelo = models.CharField('Modelo', max_length=100, blank=True, null=True)
    potencia_w = models.DecimalField('Potência (W)', max_digits=8, decimal_places=2, blank=True, null=True, help_text='Potência consumida pela impressora em Watts (W)')
    data_aquisicao = models.DateField('Data de Aquisição', blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Impressora'
        verbose_name_plural = 'Impressoras'
        ordering = ['nome']

    def __str__(self):
        return self.nome
