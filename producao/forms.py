"""
=============================================================================
FL3D Manager - Formulários do Módulo de Produção (forms.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo constrói as telas de formulário para os operadores do estúdio:
  1. 'ProducaoForm': Abertura e agendamento de uma Ordem de Produção (OP).
     Configura os seletores de data e hora com calendário interativo (datetime-local).
  2. 'RegistroImpressaoForm': Formulário rápido para registrar o término da
     impressão, informando o peso real na balança, a duração e se deu certo ou errado.
  3. 'PerdaForm': Apontamento de falhas e desperdícios de filamento com os motivos.
=============================================================================
"""

from django import forms
from .models import Producao, RegistroImpressao, Perda


class ProducaoForm(forms.ModelForm):
    """
    Formulário para criar ou editar uma Ordem de Produção.
    """
    class Meta:
        model = Producao
        fields = [
            'pedido', 'produto', 'quantidade',
            'impressora', 'filamento', 'cor',
            'peso_previsto', 'tempo_previsto',
            'data_inicio', 'data_conclusao',
            'status', 'observacoes'
        ]
        widgets = {
            # Habilita seletores com data e horário nativos do navegador
            'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'data_conclusao': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        """
        Aplica estilos visuais do Bootstrap 5 em todos os campos.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if hasattr(self.fields[field].widget, 'choices'):
                self.fields[field].widget.attrs['class'] = 'form-select'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-select'


class RegistroImpressaoForm(forms.ModelForm):
    """
    Formulário para apontamento de conclusão ou falha de uma impressão.
    """
    class Meta:
        model = RegistroImpressao
        fields = [
            'producao', 'pedido', 'produto',
            'impressora', 'filamento',
            'peso_utilizado', 'tempo_impressao',
            'resultado', 'observacoes'
        ]
        widgets = {
            'tempo_impressao': forms.TextInput(attrs={'placeholder': 'Ex: 02:30:00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if hasattr(self.fields[field].widget, 'choices'):
                self.fields[field].widget.attrs['class'] = 'form-select'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['resultado'].widget.attrs['class'] = 'form-select'


class PerdaForm(forms.ModelForm):
    """
    Formulário para lançamento avulso de perda de filamento.
    """
    class Meta:
        model = Perda
        fields = [
            'pedido', 'produto', 'filamento',
            'quantidade', 'motivo', 'observacao'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if hasattr(self.fields[field].widget, 'choices'):
                self.fields[field].widget.attrs['class'] = 'form-select'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['motivo'].widget.attrs['class'] = 'form-select'
