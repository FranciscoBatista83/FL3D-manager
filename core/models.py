"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo Core (models.py)
=============================================================================
Gerencia os conceitos globais e multi-empresa (Multi-Tenant) do FL3D Manager:
  1. Empresa: Cadastro de cada cliente/gráfica/empresa que usa o sistema.
  2. PerfilUsuario: Extensão do usuário do Django para associá-lo a uma Empresa
     e definir seu nível de permissão (Master, Gestor da Empresa ou Operador).
=============================================================================
"""

from django.db import models
from django.contrib.auth.models import User


class Empresa(models.Model):
    """
    Representa uma empresa (cliente da plataforma FL3D Manager).
    Cada empresa possui seus próprios produtos, clientes, impressoras,
    filamentos e pedidos de forma 100% isolada.
    """
    nome = models.CharField('Nome da Empresa / Razão Social', max_length=150)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=150, blank=True, null=True)
    documento = models.CharField('CNPJ ou CPF', max_length=30, blank=True, null=True)
    telefone = models.CharField('Telefone / WhatsApp', max_length=30, blank=True, null=True)
    email = models.EmailField('E-mail de Contato', blank=True, null=True)
    ativo = models.BooleanField('Empresa Ativa', default=True, help_text='Se desativada, nenhum usuário desta empresa consegue acessar.')
    criado_em = models.DateTimeField('Cadastrada em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizada em', auto_now=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome']

    def __str__(self):
        return self.nome_fantasia or self.nome


class PerfilUsuario(models.Model):
    """
    Perfil estendido para cada usuário do sistema, ligando-o a uma Empresa
    e definindo seu papel na plataforma.
    """
    class NivelAcesso(models.TextChoices):
        MASTER = 'master', 'Super Administrador (Acesso Geral)'
        GESTOR = 'gestor', 'Gestor da Empresa (Dono/Administrador)'
        OPERADOR = 'operador', 'Operador / Funcionário'

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuário'
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='usuarios',
        verbose_name='Empresa',
        null=True,
        blank=True,
        help_text='Empresa à qual este usuário pertence. Deixe em branco se for Super Admin Master sem empresa fixa.'
    )
    nivel = models.CharField(
        'Nível de Acesso',
        max_length=20,
        choices=NivelAcesso.choices,
        default=NivelAcesso.OPERADOR
    )
    telefone = models.CharField('Telefone / Celular', max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        empresa_nome = self.empresa.nome if self.empresa else 'Sem empresa (Master)'
        return f"{self.usuario.username} ({self.get_nivel_display()}) - {empresa_nome}"

    @property
    def is_master(self):
        return self.nivel == self.NivelAcesso.MASTER or self.usuario.is_superuser

    @property
    def is_gestor(self):
        return self.nivel in (self.NivelAcesso.GESTOR, self.NivelAcesso.MASTER) or self.usuario.is_superuser
