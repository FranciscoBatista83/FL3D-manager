"""
=============================================================================
FL3D Manager - Formulários do Módulo de Produtos (forms.py)
=============================================================================
"""

from django import forms
from .models import Produto


class ProdutoForm(forms.ModelForm):
    """
    Formulário para cadastrar e editar Produtos 3D (integrado à Calculadora).
    """
    class Meta:
        model = Produto
        fields = [
            # Identificação
            'nome', 'codigo', 'descricao', 'foto', 'material',
            # Parâmetros de impressão e custos
            'peso_estimado', 'tempo_estimado',
            'valor_kg_filamento', 'potencia_impressora_w', 'custo_kwh_energia',
            'custo_embalagem', 'custo_insumos', 'custo_mao_de_obra',
            # Marketplace e precificação
            'marketplace', 'custo_taxas_marketplace',
            'custo_estimado', 'preco_venda', 'margem_lucro',
            # Status
            'ativo',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_new = not self.instance.pk
        for field_name, field in self.fields.items():
            if field_name == 'ativo':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
            
            if is_new and field_name not in ['ativo', 'foto']:
                if field_name not in self.initial or self.initial.get(field_name) is None:
                    field.initial = None
