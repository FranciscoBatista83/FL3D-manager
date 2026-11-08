"""
=============================================================================
FL3D Manager - Formulários do Módulo de Usuários (forms.py)
=============================================================================
Gerenciamento de usuários da empresa pelo Gestor/Master.
=============================================================================
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from core.models import PerfilUsuario, Empresa


class UsuarioCriarForm(forms.ModelForm):
    """
    Formulário para cadastrar um novo usuário/funcionário para a empresa.
    """
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite a senha', 'autocomplete': 'new-password'}),
        help_text='Mínimo 8 caracteres.',
    )
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita a senha', 'autocomplete': 'new-password'}),
    )
    nivel = forms.ChoiceField(
        label='Nível de Acesso',
        choices=[
            (PerfilUsuario.NivelAcesso.OPERADOR, 'Operador / Funcionário'),
            (PerfilUsuario.NivelAcesso.GESTOR, 'Gestor da Empresa'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial=PerfilUsuario.NivelAcesso.OPERADOR
    )
    telefone = forms.CharField(
        label='Telefone / WhatsApp',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999', 'autocomplete': 'off'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username':   'Nome de Usuário (login)',
            'first_name': 'Nome',
            'last_name':  'Sobrenome',
            'email':      'E-mail',
        }
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: joao.operador', 'autocomplete': 'off'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João', 'autocomplete': 'off'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Silva', 'autocomplete': 'off'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: joao@empresa.com', 'autocomplete': 'off'}),
        }

    def clean_password1(self):
        senha = self.cleaned_data.get('password1')
        if senha:
            validate_password(senha)
        return senha

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('As senhas não coincidem. Tente novamente.')
        return p2

    def save(self, commit=True, empresa=None):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password1'])
        if commit:
            usuario.save()
            perfil = usuario.perfil
            perfil.empresa = empresa
            perfil.nivel = self.cleaned_data.get('nivel', PerfilUsuario.NivelAcesso.OPERADOR)
            perfil.telefone = self.cleaned_data.get('telefone', '')
            perfil.save()
        return usuario


class UsuarioEditarForm(forms.ModelForm):
    """
    Formulário de edição de usuário da empresa.
    """
    password1 = forms.CharField(
        label='Nova Senha (deixe em branco para manter a atual)',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nova senha (opcional)'}),
    )
    password2 = forms.CharField(
        label='Confirmar Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita a nova senha'}),
    )
    nivel = forms.ChoiceField(
        label='Nível de Acesso',
        choices=[
            (PerfilUsuario.NivelAcesso.OPERADOR, 'Operador / Funcionário'),
            (PerfilUsuario.NivelAcesso.GESTOR, 'Gestor da Empresa'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    telefone = forms.CharField(
        label='Telefone / WhatsApp',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        labels = {
            'username':   'Nome de Usuário (login)',
            'first_name': 'Nome',
            'last_name':  'Sobrenome',
            'email':      'E-mail',
            'is_active':  'Usuário Ativo',
        }
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and hasattr(self.instance, 'perfil'):
            self.fields['nivel'].initial = self.instance.perfil.nivel
            self.fields['telefone'].initial = self.instance.perfil.telefone

    def clean(self):
        dados = super().clean()
        p1 = dados.get('password1')
        p2 = dados.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError('As senhas não coincidem. Tente novamente.')
            validate_password(p1)
        return dados

    def save(self, commit=True):
        usuario = super().save(commit=False)
        nova_senha = self.cleaned_data.get('password1')
        if nova_senha:
            usuario.set_password(nova_senha)
        if commit:
            usuario.save()
            perfil = usuario.perfil
            if self.cleaned_data.get('nivel'):
                perfil.nivel = self.cleaned_data.get('nivel')
            if 'telefone' in self.cleaned_data:
                perfil.telefone = self.cleaned_data.get('telefone')
            perfil.save()
        return usuario
