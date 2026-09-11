"""
=============================================================================
FL3D Manager - Modelos de Dados do Módulo de Produção (models.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este é o módulo que controla o "chão de fábrica" da FL3D Studio.
Aqui transformamos os pedidos comerciais em ordens de serviço executadas
pelas impressoras 3D físicas.

O arquivo gerencia 3 tabelas fundamentais:
  1. 'Producao' (Ordem de Serviço):
     - Planejamento da impressão: qual pedido está sendo produzido, qual produto,
       qual impressora foi escalada, qual filamento/cor será usado, previsão de
       peso (g), estimativa de tempo e status (Aguardando, Imprimindo, Concluído, Falhou).
  2. 'RegistroImpressao' (Execução Real):
     - O que aconteceu de fato quando a máquina terminou de rodar: quanto filamento
       real foi gasto na balança, quantas horas/minutos durou e se o resultado
       foi SUCESSO ou FALHA.
  3. 'Perda' (Controle de Desperdício):
     - Registra quando uma peça falha ou se perde (descolamento da mesa, falta de luz,
       bico entupido, teste de filamento), permitindo calcular o prejuízo em gramas e em Reais.
=============================================================================
"""

from django.db import models
from pedidos.models import Pedido
from produtos.models import Produto
from impressoras.models import Impressora
from estoque.models import Filamento


class Producao(models.Model):
    """
    Ordem de Produção (OP): planeja e acompanha a fabricação de uma peça 3D.
    """
    class StatusChoices(models.TextChoices):
        """
        Fases pelas quais uma ordem de produção passa na oficina.
        """
        AGUARDANDO = 'aguardando', 'Aguardando'    # Na fila de espera por uma máquina livre
        IMPRIMINDO = 'imprimindo', 'Imprimindo'    # Atualmente em execução física na impressora
        CONCLUIDO = 'concluido', 'Concluído'      # Peça finalizada e retirada da mesa
        FALHOU = 'falhou', 'Falhou'                # Impressão interrompida por erro técnico
        CANCELADO = 'cancelado', 'Cancelado'      # Ordem abortada pelo operador ou cliente

    # Pedido de venda ao qual esta ordem de produção pertence
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name='producoes')
    
    # Produto específico que será impresso
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='producoes')
    
    # Quantidade de peças que serão produzidas nesta ordem
    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    
    # Impressora 3D encarregada de imprimir esta peça (pode ser definida depois)
    impressora = models.ForeignKey(
        Impressora, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='producoes'
    )
    
    # Carretel de filamento que será utilizado
    filamento = models.ForeignKey(
        Filamento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='producoes'
    )
    
    # Cor do filamento escolhida para o acabamento da peça
    cor = models.CharField('Cor', max_length=50, blank=True, null=True)
    
    # Estimativa de plástico em gramas calculada previamente no fatiador
    peso_previsto = models.DecimalField('Peso Previsto (g)', max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Tempo previsto no fatiador para a peça ficar pronta (formato HH:MM:SS)
    tempo_previsto = models.DurationField('Tempo Previsto', blank=True, null=True)
    
    # Data e hora em que a máquina começou a imprimir
    data_inicio = models.DateTimeField('Data de Início', blank=True, null=True)
    
    # Data e hora em que a impressão foi finalizada
    data_conclusao = models.DateTimeField('Data de Conclusão', blank=True, null=True)
    
    # Situação operacional atual da ordem
    status = models.CharField('Status', max_length=20, choices=StatusChoices.choices, default=StatusChoices.AGUARDANDO)
    
    # Instruções técnicas especiais (ex: "Usar adesivo líquido na mesa de vidro")
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Produção'
        verbose_name_plural = 'Produções'
        ordering = ['-data_inicio']

    def __str__(self):
        return f"Produção do Pedido #{self.pedido.numero} - {self.produto.nome}"


class RegistroImpressao(models.Model):
    """
    Registro real pós-impressão: aponta os dados efetivos de tempo e peso utilizados.
    """
    class ResultadoChoices(models.TextChoices):
        """
        Resultado final obtido na mesa da impressora.
        """
        SUCESSO = 'sucesso', 'Sucesso'  # Peça perfeita, pronta para acabamento
        FALHA = 'falha', 'Falha'        # Peça deu defeito e foi descartada

    # Ordem de produção de origem
    producao = models.ForeignKey(Producao, on_delete=models.CASCADE, related_name='impressoes')
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    impressora = models.ForeignKey(Impressora, on_delete=models.PROTECT)
    filamento = models.ForeignKey(Filamento, on_delete=models.PROTECT)
    
    # Peso real aferido na balança após a impressão (peça + suportes descartáveis)
    peso_utilizado = models.DecimalField('Peso Utilizado (g)', max_digits=8, decimal_places=2)
    
    # Tempo real que a máquina levou para concluir o arquivo G-code
    tempo_impressao = models.DurationField('Tempo de Impressão')
    
    # Data e hora em que este registro foi inserido no sistema
    data = models.DateTimeField('Data', auto_now_add=True)
    
    # Se a peça deu certo ou deu errado
    resultado = models.CharField('Resultado', max_length=20, choices=ResultadoChoices.choices)
    
    # Relato do operador sobre a qualidade da camada ou defeitos
    observacoes = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name = 'Registro de Impressão'
        verbose_name_plural = 'Registros de Impressões'
        ordering = ['-data']

    def __str__(self):
        return f"Impressão em {self.data.strftime('%d/%m/%Y')} - {self.produto.nome} ({self.get_resultado_display()})"


class Perda(models.Model):
    """
    Controle de perdas e falhas de impressão para cálculo de refugo e desperdício de plástico.
    """
    class MotivoChoices(models.TextChoices):
        """
        Causas mais comuns de falha na impressão 3D FDM.
        """
        SOLTOU_MESA = 'soltou_mesa', 'Peça soltou da mesa'                # Falta de adesão / empenamento (warping)
        FALHA_IMPRESSAO = 'falha_impressao', 'Falha de impressão'        # Camadas desalinhadas (layer shift)
        ERRO_FATIAMENTO = 'erro_fatiamento', 'Erro de fatiamento'        # Faltou suporte ou velocidade errada
        ERRO_CONFIGURACAO = 'erro_configuracao', 'Erro de configuração'  # Temperatura inadequada para o material
        BICO_ENTUPIDO = 'bico_entupido', 'Bico entupido'                # Obstrução no hotend
        PROBLEMA_IMPRESSORA = 'problema_impressora', 'Problema na impressora' # Correia frouxa, falha no motor
        TESTE = 'teste', 'Teste'                                        # Calibração de fluxo ou torre de temperatura
        OUTRO = 'outro', 'Outro'                                        # Queda de energia elétrica, etc.

    data = models.DateTimeField('Data', auto_now_add=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True)
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True)
    filamento = models.ForeignKey(Filamento, on_delete=models.PROTECT)
    
    # Peso em gramas do plástico que foi perdido e jogado fora
    quantidade = models.DecimalField('Quantidade Perdida (g)', max_digits=8, decimal_places=2)
    
    # Categoria da falha
    motivo = models.CharField('Motivo', max_length=50, choices=MotivoChoices.choices)
    
    # Descrição livre do ocorrido (ex: "Acabou a luz quando a peça estava em 75%")
    observacao = models.TextField('Observação', blank=True, null=True)

    class Meta:
        verbose_name = 'Perda'
        verbose_name_plural = 'Perdas'
        ordering = ['-data']

    def __str__(self):
        return f"Perda {self.quantidade}g - {self.get_motivo_display()}"
