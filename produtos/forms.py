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
            'nome', 'categoria', 'codigo', 'descricao', 'foto', 'arquivo_impressao',
            # Parâmetros de impressão e custos
            'peso_estimado', 'tempo_estimado',
            'detalhes_filamentos', 'potencia_impressora_w', 'custo_kwh_energia',
            'custo_embalagem', 'custo_insumos', 'custo_mao_de_obra',
            # Marketplace e precificação
            'marketplace', 'comissao_afiliado_percentual', 'custo_taxas_marketplace',
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
            elif field_name == 'categoria':
                field.widget.attrs['class'] = 'form-select'
                field.empty_label = 'Selecione uma Categoria...'
            else:
                field.widget.attrs['class'] = 'form-control'
            
            if is_new and field_name not in ['ativo', 'foto', 'arquivo_impressao']:
                if field_name not in self.initial or self.initial.get(field_name) is None:
                    field.initial = None
