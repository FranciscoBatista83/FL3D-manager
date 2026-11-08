"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Clientes (models.py)
=============================================================================
Armazena as fichas cadastrais dos clientes da empresa de impressão 3D.
Agora com suporte Multi-Empresa.
=============================================================================
"""

from django.db import models
from core.models import Empresa


class Cliente(models.Model):
    """
    Tabela que armazena os clientes da empresa de impressão 3D.
    Isolada por empresa.
    """
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='clientes',
        verbose_name='Empresa',
        null=True,
        blank=True
    )

    # -------------------------------------------------------------------------
    # DADOS PESSOAIS E DE IDENTIFICAÇÃO
    # -------------------------------------------------------------------------
    nome = models.CharField('Nome', max_length=200)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=20, blank=True, null=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True, null=True)
    email = models.EmailField('E-mail', blank=True, null=True)

    # -------------------------------------------------------------------------
    # ENDEREÇO PARA ENVIO OU RETIRADA
    # -------------------------------------------------------------------------
    cep = models.CharField('CEP', max_length=10, blank=True, null=True)
    endereco = models.CharField('Endereço', max_length=255, blank=True, null=True)
    numero = models.CharField('Número', max_length=20, blank=True, null=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True, null=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True, null=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True, null=True)
    estado = models.CharField('Estado', max_length=2, blank=True, null=True)

    # -------------------------------------------------------------------------
    # CAMPOS ADMINISTRATIVOS E DE AUDITORIA
    # -------------------------------------------------------------------------
    observacoes = models.TextField('Observações', blank=True, null=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome
