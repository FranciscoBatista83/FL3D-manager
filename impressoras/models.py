"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Impressoras (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Na FL3D Studio, as impressoras 3D são os ativos mais valiosos do chão de fábrica.
Elas trabalham horas a fio derretendo filamento para transformar modelos digitais
em peças físicas.

Este arquivo define a estrutura da tabela 'Impressora':
  - Identificação: Nome da máquina (ex: "Bambu Lab X1-Carbon #01", "Ender 3 V3"),
    Fabricante (ex: Bambu Lab, Creality, Prusa), Modelo e Número de Série.
  - Controle Operacional:
    * Status em tempo real:
      - DISPONÍVEL: Máquina limpa e desocupada, pronta para receber a próxima impressão.
      - IMPRIMINDO: Máquina em operação, com mesa aquecida e cabeçote trabalhando.
      - EM MANUTENÇÃO: Máquina parada para troca de bico, lubrificação de eixos ou calibração.
      - INATIVA: Máquina desligada ou aposentada.
  - Histórico: Data de aquisição e anotações técnicas sobre modificações e upgrades.
=============================================================================
"""

from django.db import models


class Impressora(models.Model):
    """
    Representa uma impressora 3D física pertencente à oficina.
    """
    class StatusChoices(models.TextChoices):
        """
        Situações operacionais possíveis para a impressora.
        """
        DISPONIVEL = 'disponivel', 'Disponível'        # Livre para iniciar um novo trabalho
        IMPRIMINDO = 'imprimindo', 'Imprimindo'        # Executando um trabalho no momento
        MANUTENCAO = 'manutencao', 'Em Manutenção'    # Passando por reparos ou calibração
        INATIVA = 'inativa', 'Inativa'                # Desativada temporariamente ou aposentada

    # Nome de identificação dado à máquina na oficina (ex: "Bambu Lab P1S - Sala 1")
    nome = models.CharField('Nome', max_length=100)
    
    # Marca da impressora (ex: Bambu Lab, Creality, Elegoo, Anycubic, Prusa)
    fabricante = models.CharField('Fabricante', max_length=100, blank=True, null=True)
    
    # Modelo específico (ex: "K1 Max", "Ender 3 S1 Pro", "A1 Mini")
    modelo = models.CharField('Modelo', max_length=100, blank=True, null=True)
    
    # Número de patrimônio ou número de série do equipamento
    numero_identificacao = models.CharField('Número de Identificação', max_length=50, blank=True, null=True)
    
    # Data em que o equipamento foi comprado e incorporado ao estúdio
    data_aquisicao = models.DateField('Data de Aquisição', blank=True, null=True)
    
    # Estado operacional atual (o padrão ao cadastrar é DISPONÍVEL)
    status = models.CharField(
        'Status', 
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.DISPONIVEL
    )
    
    # Histórico de revisões, troca de peças ou upgrades (ex: "Instalado bico de aço endurecido 0.4mm")
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Impressora'
        verbose_name_plural = 'Impressoras'
        ordering = ['nome']

    def __str__(self):
        # Exibe o nome acompanhado do status atual (ex: "Ender 3 (Imprimindo)")
        return f"{self.nome} ({self.get_status_display()})"
