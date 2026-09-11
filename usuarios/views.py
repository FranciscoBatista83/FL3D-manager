"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Usuários (views.py)
=============================================================================
Controla as telas de gerenciamento de usuários do sistema:
  1. Lista de usuários cadastrados
  2. Criação de novo usuário
  3. Edição de usuário existente
  4. Ativação / Desativação de usuário (sem excluir do banco)

Todas as views exigem que o operador esteja logado (LoginRequiredMixin).
Usa o modelo User nativo do Django — sem modelos extras.
=============================================================================
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect

from .forms import UsuarioCriarForm, UsuarioEditarForm


class UsuarioListView(LoginRequiredMixin, ListView):
    """
    Tela de listagem de todos os usuários cadastrados no sistema.
    Exibe: login, nome completo, e-mail e status (ativo/inativo).
    """
    model = User
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        """
        Retorna todos os usuários ordenados por nome de usuário (login),
        ignorando a ordem de criação.
        """
        return User.objects.all().order_by('username')


class UsuarioCriarView(LoginRequiredMixin, CreateView):
    """
    Tela de cadastro de um novo usuário no sistema.
    Após o cadastro bem-sucedido, redireciona para a lista.
    """
    model = User
    form_class = UsuarioCriarForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuarios:lista')

    def form_valid(self, form):
        """
        Chamado quando o formulário passou em todas as validações.
        Exibe mensagem de sucesso na tela.
        """
        messages.success(self.request, 'Usuário criado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Chamado quando há erro no formulário (ex: senhas diferentes).
        Exibe mensagem de erro na tela.
        """
        messages.error(self.request, 'Corrija os erros abaixo antes de salvar.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Título que aparece no topo do formulário
        ctx['titulo'] = 'Novo Usuário'
        ctx['acao'] = 'Cadastrar'
        return ctx


class UsuarioEditarView(LoginRequiredMixin, UpdateView):
    """
    Tela de edição de um usuário já existente.
    Permite alterar nome, e-mail, status e senha (opcional).
    """
    model = User
    form_class = UsuarioEditarForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuarios:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Usuário atualizado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Corrija os erros abaixo antes de salvar.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar Usuário: {self.object.username}'
        ctx['acao'] = 'Salvar Alterações'
        return ctx


class UsuarioToggleAtivoView(LoginRequiredMixin, View):
    """
    Alterna o status do usuário entre Ativo e Inativo.
    Funciona como um botão de liga/desliga — sem excluir o usuário do banco.

    Regra de segurança: o usuário não pode desativar a si mesmo.
    """

    def post(self, request, pk):
        # Busca o usuário pelo ID (pk). Retorna erro 404 se não existir.
        usuario = get_object_or_404(User, pk=pk)

        # Impede que o operador desative sua própria conta (ficaria preso fora do sistema)
        if usuario == request.user:
            messages.warning(request, 'Você não pode desativar sua própria conta.')
            return redirect('usuarios:lista')

        # Inverte o status: se estava ativo, fica inativo e vice-versa
        usuario.is_active = not usuario.is_active
        usuario.save()

        # Mensagem de feedback com o novo estado
        status = 'ativado' if usuario.is_active else 'desativado'
        messages.success(request, f'Usuário "{usuario.username}" foi {status} com sucesso.')
        return redirect('usuarios:lista')


class UsuarioExcluirView(LoginRequiredMixin, DeleteView):
    """
    Tela de confirmação para excluir definitivamente um usuário.
    Impede que o usuário logado exclua a si mesmo.
    """
    model = User
    template_name = 'usuarios/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuarios:lista')

    def dispatch(self, request, *args, **kwargs):
        # Validação extra antes de exibir a página ou processar o POST
        usuario = self.get_object()
        if usuario == request.user:
            messages.error(request, 'Ação negada: Você não pode excluir a sua própria conta.')
            return redirect('usuarios:lista')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Para DeleteView, form_valid faz a exclusão de fato
        usuario = self.get_object()
        messages.success(self.request, f'Usuário "{usuario.username}" excluído permanentemente.')
        return super().form_valid(form)
