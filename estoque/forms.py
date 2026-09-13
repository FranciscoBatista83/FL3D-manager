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
    Formulário de cadastro e edição de produtos/itens no estoque.
    """
    class Meta:
        model = Filamento
        fields = [
            'nome', 'marca', 'cor', 'quantidade', 'preco',
            'fornecedor', 'observacoes'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'nome': 'Nome do Produto',
            'marca': 'Marca',
            'cor': 'Cor',
            'quantidade': 'Quantidade',
            'preco': 'Preço (R$)',
            'fornecedor': 'Fornecedor',
            'observacoes': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        """
        Aplica estilos CSS para harmonizar os campos com o Bootstrap 5 e garante tela limpa em novos cadastros.
        """
        super().__init__(*args, **kwargs)
        # Força labels em português para evitar tradução automática incorreta do Django
        self.fields['fornecedor'].label = 'Fornecedor'
        is_new = not self.instance.pk
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if is_new:
                field.initial = None



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

