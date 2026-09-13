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
    Formulário para registrar novas máquinas ou atualizar dados técnicos.
    """
    class Meta:
        model = Impressora
        fields = [
            'nome', 'fabricante', 'modelo', 'potencia_w',
            'data_aquisicao', 'observacoes'
        ]
        widgets = {
            'data_aquisicao': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """
        Aplica estilos CSS para harmonizar os campos com o Bootstrap 5.
        """
        super().__init__(*args, **kwargs)
        is_new = not self.instance.pk
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if is_new:
                field.initial = None
