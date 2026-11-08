"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Usuários (views.py)
=============================================================================
Controla as telas de gerenciamento de usuários com isolamento por empresa:
  - O Gestor da empresa cadastra e gerencia apenas os usuários da empresa dele.
  - O Master pode gerenciar todos.
=============================================================================
"""

from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect

from core.mixins import GestorRequiredMixin
from .forms import UsuarioCriarForm, UsuarioEditarForm


class UsuarioListView(GestorRequiredMixin, ListView):
    """
    Lista os usuários da empresa do usuário logado.
    """
    model = User
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        empresa = getattr(self.request, 'empresa', None)
        perfil = getattr(self.request, 'perfil', None)
        empresa_id_filtro = self.request.GET.get('empresa_id')

        # Se for Master, pode filtrar por uma empresa específica ou ver todos
        if perfil and perfil.is_master:
            qs = User.objects.all().select_related('perfil', 'perfil__empresa').order_by('username')
            if empresa_id_filtro:
                qs = qs.filter(perfil__empresa_id=empresa_id_filtro)
            return qs

        if empresa:
            return User.objects.filter(perfil__empresa=empresa).select_related('perfil', 'perfil__empresa').order_by('username')

        return User.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        perfil = getattr(self.request, 'perfil', None)
        if perfil and perfil.is_master:
            from core.models import Empresa
            ctx['todas_empresas'] = Empresa.objects.all()
            ctx['empresa_id_filtro'] = self.request.GET.get('empresa_id', '')
        return ctx


class UsuarioCriarView(GestorRequiredMixin, CreateView):
    """
    Cadastro de um novo usuário para a empresa atual.
    """
    model = User
    form_class = UsuarioCriarForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuarios:lista')

    def form_valid(self, form):
        empresa = getattr(self.request, 'empresa', None)
        form.save(commit=True, empresa=empresa)
        messages.success(self.request, 'Usuário cadastrado com sucesso!')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Corrija os erros abaixo antes de salvar.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Usuário'
        ctx['acao'] = 'Cadastrar'
        return ctx


class UsuarioEditarView(GestorRequiredMixin, UpdateView):
    """
    Edição de um usuário da empresa atual.
    """
    model = User
    form_class = UsuarioEditarForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuarios:lista')

    def get_queryset(self):
        empresa = getattr(self.request, 'empresa', None)
        perfil = getattr(self.request, 'perfil', None)
        if perfil and perfil.is_master:
            return User.objects.all()
        if empresa:
            return User.objects.filter(perfil__empresa=empresa)
        return User.objects.none()

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


class UsuarioToggleAtivoView(GestorRequiredMixin, View):
    """
    Alterna o status do usuário entre Ativo e Inativo.
    """
    def post(self, request, pk):
        empresa = getattr(request, 'empresa', None)
        perfil = getattr(request, 'perfil', None)
        if perfil and perfil.is_master:
            usuario = get_object_or_404(User, pk=pk)
        else:
            usuario = get_object_or_404(User, pk=pk, perfil__empresa=empresa)

        if usuario == request.user:
            messages.warning(request, 'Você não pode desativar sua própria conta.')
            return redirect('usuarios:lista')

        usuario.is_active = not usuario.is_active
        usuario.save()

        status = 'ativado' if usuario.is_active else 'desativado'
        messages.success(request, f'Usuário "{usuario.username}" foi {status} com sucesso.')
        return redirect('usuarios:lista')


class UsuarioExcluirView(GestorRequiredMixin, DeleteView):
    """
    Exclusão definitiva de um usuário da empresa.
    """
    model = User
    template_name = 'usuarios/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuarios:lista')

    def get_queryset(self):
        empresa = getattr(self.request, 'empresa', None)
        perfil = getattr(self.request, 'perfil', None)
        if perfil and perfil.is_master:
            return User.objects.all()
        if empresa:
            return User.objects.filter(perfil__empresa=empresa)
        return User.objects.none()

    def dispatch(self, request, *args, **kwargs):
        usuario = self.get_object()
        if usuario == request.user:
            messages.error(request, 'Ação negada: Você não pode excluir a sua própria conta.')
            return redirect('usuarios:lista')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        usuario = self.get_object()
        messages.success(self.request, f'Usuário "{usuario.username}" excluído permanentemente.')
        return super().form_valid(form)
