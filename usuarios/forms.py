"""
=============================================================================
FL3D Manager - Formulários do Módulo de Usuários (forms.py)
=============================================================================
Define os formulários para criação e edição de usuários do sistema.
Usa o modelo User nativo do Django (django.contrib.auth) — sem banco
de dados extra.

Formulários disponíveis:
  - UsuarioCriarForm   : cria um novo usuário com senha
  - UsuarioEditarForm  : edita dados do usuário (senha opcional)
=============================================================================
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class UsuarioCriarForm(forms.ModelForm):
    """
    Formulário de cadastro de novo usuário.
    Inclui os campos de senha e confirmação de senha com validação.
    """

    # Campo de senha (o texto digitado fica oculto com bolinhas)
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite a senha'}),
        help_text='Mínimo 8 caracteres. Não use senhas óbvias como "123456".',
    )

    # Campo de confirmação — o usuário digita a mesma senha para confirmar
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita a senha'}),
    )

    class Meta:
        # Usamos o modelo User padrão do Django
        model = User
        # Campos que aparecerão no formulário de criação
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username':   'Nome de Usuário (login)',
            'first_name': 'Nome',
            'last_name':  'Sobrenome',
            'email':      'E-mail',
        }
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: joao.silva'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Silva'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: joao@email.com'}),
        }

    def clean_password1(self):
        """
        Valida se a senha atende aos critérios mínimos de segurança do Django.
        """
        senha = self.cleaned_data.get('password1')
        if senha:
            validate_password(senha)
        return senha

    def clean_password2(self):
        """
        Verifica se as duas senhas digitadas são idênticas.
        """
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('As senhas não coincidem. Tente novamente.')
        return p2

    def save(self, commit=True):
        """
        Salva o usuário com a senha criptografada (nunca em texto puro).
        """
        usuario = super().save(commit=False)
        # set_password() criptografa a senha antes de gravar no banco
        usuario.set_password(self.cleaned_data['password1'])
        if commit:
            usuario.save()
        return usuario


class UsuarioEditarForm(forms.ModelForm):
    """
    Formulário de edição de usuário existente.
    A senha é opcional — se deixada em branco, a senha atual é mantida.
    """

    # Nova senha (opcional na edição)
    password1 = forms.CharField(
        label='Nova Senha (deixe em branco para manter a atual)',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nova senha (opcional)'}),
    )

    # Confirmação da nova senha
    password2 = forms.CharField(
        label='Confirmar Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita a nova senha'}),
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

    def clean(self):
        """
        Valida que, se uma nova senha foi digitada, as duas confirmações batem.
        """
        dados = super().clean()
        p1 = dados.get('password1')
        p2 = dados.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError('As senhas não coincidem. Tente novamente.')
            validate_password(p1)
        return dados

    def save(self, commit=True):
        """
        Salva as alterações. Se uma nova senha foi informada, ela é criptografada
        e aplicada. Caso contrário, a senha antiga é preservada.
        """
        usuario = super().save(commit=False)
        nova_senha = self.cleaned_data.get('password1')
        if nova_senha:
            usuario.set_password(nova_senha)
        if commit:
            usuario.save()
        return usuario
