"""
=============================================================================
FL3D Manager - Formulários do Módulo de Impressoras (forms.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo constrói os formulários de cadastro e edição de impressoras 3D.
Ele cuida para que o campo de data de aquisição exiba o seletor de calendário nativo
do navegador e estiliza as caixas com Bootstrap 5.
=============================================================================
"""

from django import forms
from .models import Impressora


class ImpressoraForm(forms.ModelForm):
    """
    Formulário para registrar novas máquinas ou atualizar o status e observações.
    """
    class Meta:
        model = Impressora
        fields = [
            'nome', 'fabricante', 'modelo', 'numero_identificacao',
            'data_aquisicao', 'status', 'observacoes'
        ]
        widgets = {
            # Habilita o calendário interativo no campo de data de aquisição
            'data_aquisicao': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Aplica estilos CSS para harmonizar os campos com o design moderno do Bootstrap 5.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'status':
                # O campo de seleção ganha o estilo específico 'form-select'
                self.fields[field].widget.attrs['class'] = 'form-select'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
