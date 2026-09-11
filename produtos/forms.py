"""
=============================================================================
FL3D Manager - Formulários do Módulo de Produtos (forms.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Constrói a tela de cadastro e edição de produtos, cuidando para que todos
os campos de texto, números, upload de fotos e seleções fiquem bonitos e fáceis
de usar, aplicando o estilo visual do Bootstrap 5.
=============================================================================
"""

from django import forms
from .models import Produto


class ProdutoForm(forms.ModelForm):
    """
    Formulário para cadastrar e editar Produtos 3D.
    """
    class Meta:
        # Modelo do banco de dados que será preenchido
        model = Produto
        
        # Lista dos campos que o operador da oficina vai preencher
        fields = [
            'nome', 'codigo', 'categoria', 'descricao', 'foto',
            'material', 'cor', 'peso_estimado', 'tempo_estimado',
            'custo_estimado', 'preco_venda', 'margem_lucro',
            'observacoes', 'ativo'
        ]
        
    def __init__(self, *args, **kwargs):
        """
        Customiza os elementos visuais HTML (inputs) com classes do Bootstrap 5.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'ativo':
                # Checkbox ganha estilo específico de interruptor/caixa de marcação
                field.widget.attrs['class'] = 'form-check-input'
            elif field_name == 'foto':
                # Campo de envio de arquivo/imagem
                field.widget.attrs['class'] = 'form-control'
            else:
                # Demais campos de texto, número e datas
                field.widget.attrs['class'] = 'form-control'

