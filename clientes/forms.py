"""
=============================================================================
FL3D Manager - Formulários do Módulo de Clientes (forms.py)
=============================================================================
VISÃO GERAL E CONCEITO:
No Django, um 'Form' (Formulário) é o responsável por desenhar as caixas de texto,
botões e campos de preenchimento na tela do navegador, além de garantir que ninguém
digite dados inválidos (como um e-mail sem '@' ou um campo obrigatório em branco).

Neste arquivo:
- Conectamos o formulário diretamente com a tabela 'Cliente' (`ModelForm`).
- Formatamos os campos com o visual do Bootstrap (classes CSS como 'form-control'
  para caixas bonitas e 'form-check-input' para caixas de marcação).
=============================================================================
"""

from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    """
    Formulário para Criação e Edição de Clientes.
    Gera automaticamente os campos na tela com base no modelo 'Cliente'.
    """
    class Meta:
        # Aponta qual modelo do banco de dados este formulário vai preencher
        model = Cliente
        
        # Lista dos campos que aparecerão na tela para o usuário preencher
        fields = [
            'nome', 'cpf_cnpj', 'telefone', 'whatsapp', 'email',
            'cep', 'endereco', 'numero', 'complemento', 'bairro', 
            'cidade', 'estado', 'observacoes', 'ativo'
        ]
        
    def __init__(self, *args, **kwargs):
        """
        Método de inicialização do formulário.
        Aqui estilizamos cada campo com o Bootstrap 5 para que os inputs fiquem
        modernos, arredondados e responsivos em telas de celular e computador.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'ativo':
                # Campo do tipo caixa de seleção (checkbox)
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})
            else:
                # Caixas de texto padrão ganham a classe 'form-control' do Bootstrap
                self.fields[field].widget.attrs.update({'class': 'form-control'})

