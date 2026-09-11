"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Clientes (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Aqui definimos como as informações dos clientes da FL3D Studio são salvas no banco
de dados. Pense nesta classe 'Cliente' como uma ficha de cadastro digital completa.

Cada cliente possui:
  - Dados de Contato: Nome, CPF ou CNPJ, Telefone, WhatsApp (muito usado para
    mandar fotos do produto 3D pronto) e E-mail.
  - Endereço de Entrega: CEP, Rua, Número, Complemento, Bairro, Cidade e Estado
    (essencial para saber para onde enviar as encomendas pelos Correios ou Motoboy).
  - Controle Interno: Campo de observações (preferências do cliente), data em que
    se cadastrou e se a conta dele está "Ativa" ou arquivada.
=============================================================================
"""

from django.db import models


class Cliente(models.Model):
    """
    Tabela que armazena os clientes da empresa de impressão 3D.
    """
    # -------------------------------------------------------------------------
    # DADOS PESSOAIS E DE IDENTIFICAÇÃO
    # -------------------------------------------------------------------------
    # Nome completo da pessoa física ou razão social da empresa (obrigatório, até 200 letras)
    nome = models.CharField('Nome', max_length=200)
    
    # Documento fiscal para nota ou contrato (opcional: blank=True, null=True)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=20, blank=True, null=True)
    
    # Telefone fixo ou de recado
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    
    # Número de WhatsApp (canal prioritário para orçamento e envio de fotos do fatiamento 3D)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True, null=True)
    
    # E-mail para envio de orçamentos formais e faturas em PDF
    email = models.EmailField('E-mail', blank=True, null=True)
    
    # -------------------------------------------------------------------------
    # ENDEREÇO PARA ENVIO OU RETIRADA
    # -------------------------------------------------------------------------
    # Código Postal para cálculo de frete
    cep = models.CharField('CEP', max_length=10, blank=True, null=True)
    
    # Logradouro (ex: Rua das Flores, Avenida Brasil)
    endereco = models.CharField('Endereço', max_length=255, blank=True, null=True)
    
    # Número da residência ou prédio
    numero = models.CharField('Número', max_length=20, blank=True, null=True)
    
    # Complemento (ex: Apto 102, Bloco B, Sala Comercial)
    complemento = models.CharField('Complemento', max_length=100, blank=True, null=True)
    
    # Bairro
    bairro = models.CharField('Bairro', max_length=100, blank=True, null=True)
    
    # Cidade
    cidade = models.CharField('Cidade', max_length=100, blank=True, null=True)
    
    # Sigla do Estado com 2 letras (ex: SP, RJ, MG, PR)
    estado = models.CharField('Estado', max_length=2, blank=True, null=True)
    
    # -------------------------------------------------------------------------
    # CAMPOS ADMINISTRATIVOS E DE AUDITORIA
    # -------------------------------------------------------------------------
    # Campo aberto para anotações livres (ex: "Cliente prefere peças na cor preta", "Pede desconto em lote")
    observacoes = models.TextField('Observações', blank=True, null=True)
    
    # Grava automaticamente a data e a hora exatas em que o cliente foi cadastrado pela primeira vez
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    
    # Flag que indica se o cliente está ativo no sistema.
    # Usado para o "Soft Delete": quando 'excluímos' um cliente, nós apenas mudamos este campo para False,
    # preservando todo o histórico de compras e financeiro intacto no banco de dados.
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        """
        Configurações extras da tabela no banco de dados.
        """
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        # Garante que a lista de clientes venha sempre em ordem alfabética de A a Z
        ordering = ['nome']

    def __str__(self):
        """
        Define como o cliente aparece quando é referenciado em outros lugares
        (por exemplo, ao escolher o cliente na tela de pedidos, aparecerá o nome dele).
        """
        return self.nome

