"""
=============================================================================
FL3D Manager - Formulários do Módulo Core (forms.py)
=============================================================================
Formulários para gestão de Empresas e Cadastro de Responsável da Empresa
pelo Administrador Geral (Master).
=============================================================================
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Empresa, PerfilUsuario


class EmpresaForm(forms.ModelForm):
    """
    Formulário para o Super Administrador cadastrar ou editar Empresas clientes.
    """
    class Meta:
        model = Empresa
        fields = ['nome', 'nome_fantasia', 'documento', 'telefone', 'email', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Impressões 3D Criativas LTDA'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Criativa 3D'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ ou CPF'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contato@empresa.com'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmpresaComResponsavelForm(forms.ModelForm):
    """
    Formulário especial para criar uma Empresa e já cadastrar simultaneamente
    o primeiro usuário (o Responsável/Gestor da Empresa) com senha inicial.
    """
    # Dados do Responsável
    responsavel_username = forms.CharField(
        label='Login do Responsável',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: joao.gestor'}),
        help_text='Nome de usuário único para o responsável acessar o sistema.'
    )
    responsavel_nome = forms.CharField(
        label='Nome Completo',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João da Silva'})
    )
    responsavel_email = forms.EmailField(
        label='E-mail do Responsável',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'joao@empresa.com'})
    )
    responsavel_senha = forms.CharField(
        label='Senha de Acesso',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite a senha inicial'}),
        help_text='Mínimo de 8 caracteres.'
    )

    class Meta:
        model = Empresa
        fields = ['nome', 'nome_fantasia', 'documento', 'telefone', 'email', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Oficina 3D Pro'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Oficina 3D'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ ou CPF'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 98888-7777'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'comercial@empresa.com'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_responsavel_username(self):
        username = self.cleaned_data.get('responsavel_username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Já existe um usuário cadastrado com este nome de login. Escolha outro.')
        return username

    def clean_responsavel_senha(self):
        senha = self.cleaned_data.get('responsavel_senha')
        if senha:
            validate_password(senha)
        return senha

    def save(self, commit=True):
        empresa = super().save(commit=commit)
        if commit:
            # Cria o usuário responsável
            username = self.cleaned_data['responsavel_username']
            nome_completo = self.cleaned_data['responsavel_nome'].strip().split(' ', 1)
            first_name = nome_completo[0]
            last_name = nome_completo[1] if len(nome_completo) > 1 else ''
            email = self.cleaned_data['responsavel_email']
            senha = self.cleaned_data['responsavel_senha']

            user = User.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=first_name,
                last_name=last_name
            )

            # Atualiza o perfil para GESTOR da nova empresa
            perfil = user.perfil
            perfil.empresa = empresa
            perfil.nivel = PerfilUsuario.NivelAcesso.GESTOR
            perfil.save()

        return empresa

