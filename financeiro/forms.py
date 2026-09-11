"""
=============================================================================
FL3D Manager - Formulários do Módulo Financeiro (forms.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Controla as telas de entrada de dados financeiros:
  1. 'MovimentacaoFinanceiraForm': Tela para cadastrar uma receita ou despesa no caixa.
     Possui seletor de calendário e menus suspensos com as categorias de custos.
  2. 'RelatorioFiltroForm': Filtro de período para o relatório financeiro
     (permite escolher Data Inicial, Data Final e Tipo para emitir o DRE do período).
=============================================================================
"""

from django import forms
from .models import MovimentacaoFinanceira


class MovimentacaoFinanceiraForm(forms.ModelForm):
    """
    Formulário para registrar uma entrada ou saída no fluxo de caixa.
    """
    class Meta:
        model = MovimentacaoFinanceira
        fields = [
            'descricao', 'tipo', 'categoria',
            'valor', 'data', 'pedido', 'observacoes',
        ]
        widgets = {
            # Calendário interativo para seleção rápida da data do lançamento
            'data': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Estiliza os campos com as classes visuais do Bootstrap 5.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field in ('tipo', 'categoria', 'pedido'):
                self.fields[field].widget.attrs['class'] = 'form-select'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['pedido'].required = False
        self.fields['observacoes'].required = False


class RelatorioFiltroForm(forms.Form):
    """
    Formulário para filtrar o Relatório Financeiro por intervalo de datas.
    """
    # Data de início do período a ser analisado
    data_inicio = forms.DateField(
        label='Data Inicial',
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'})
    )
    
    # Data final do período
    data_fim = forms.DateField(
        label='Data Final',
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'})
    )
    
    # Filtro opcional por tipo (Todos, Somente Entradas ou Somente Saídas)
    tipo = forms.ChoiceField(
        label='Tipo',
        required=False,
        choices=[('', 'Todos'), ('entrada', 'Entradas'), ('saida', 'Saídas')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
