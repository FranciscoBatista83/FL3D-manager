"""
=============================================================================
FL3D Manager - Formulários do Módulo de Estoque (forms.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Controla as telas de entrada de dados do estoque de filamentos:
  1. 'FilamentoForm': Cadastro do carretel novo. Note que o campo 'peso_atual'
     NÃO aparece na tela: quando você cadastra um carretel novo de 1000g,
     o sistema automaticamente define que o peso atual é 1000g e cria o
     registro oficial de entrada no histórico!
  2. 'AjusteEstoqueForm': Tela simples onde o operador coloca a bobina na
     balança de precisão, digita quantos gramas reais deram e escreve o motivo.
     O sistema faz a matemática sozinho para saber se faltou ou sobrou plástico.
=============================================================================
"""

from django import forms
from .models import Filamento


class FilamentoForm(forms.ModelForm):
    """
    Formulário de cadastro e edição de carretéis de filamento.
    
    REGRA DE NEGÓCIO DE OURO:
    O campo 'peso_atual' é excluído propositalmente deste formulário.
    Nenhum usuário pode simplesmente digitar um peso qualquer na edição.
    Toda alteração de gramas deve acontecer via movimentação registrada
    (impressão, perda ou ajuste de balança).
    """
    class Meta:
        model = Filamento
        fields = [
            'marca', 'material', 'cor',
            'peso_inicial', 'custo_rolo',
            'fornecedor', 'codigo_lote', 'localizacao', 'observacoes'
        ]

    def __init__(self, *args, **kwargs):
        """
        Aplica os estilos visuais modernos do Bootstrap 5 a todos os campos.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class AjusteEstoqueForm(forms.Form):
    """
    Formulário para aferição periódica do carretel na balança.
    O operador coloca a bobina na balança da oficina e digita o peso real.
    """
    # Valor numérico em gramas lido no visor da balança
    peso_fisico = forms.DecimalField(
        label='Peso Físico Real (g)',
        max_digits=8,
        decimal_places=2,
        min_value=0,
        help_text='Informe o peso atual do filamento ao pesá-lo na balança da oficina.',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    # Justificativa do operador (ex: "Sobras de suportes descartadas", "Carretel pesado após troca de bico")
    motivo = forms.CharField(
        label='Motivo do Ajuste',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Diferença encontrada na pesagem periódica'})
    )

