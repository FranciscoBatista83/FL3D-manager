"""
=============================================================================
FL3D Manager - Visualizações do Módulo Core (views.py)
=============================================================================
Gerenciamento de Empresas clientes pelo Super Administrador (Painel Master).
=============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib import messages
from django.db.models import Count

from .models import Empresa, PerfilUsuario
from .forms import EmpresaForm, EmpresaComResponsavelForm
from .mixins import MasterRequiredMixin


class EmpresaListView(MasterRequiredMixin, ListView):
    """
    Tela do Painel Master listando todas as empresas clientes da plataforma.
    """
    model = Empresa
    template_name = 'core/empresa_list.html'
    context_object_name = 'empresas'
    paginate_by = 15

    def get_queryset(self):
        qs = Empresa.objects.annotate(
            total_usuarios=Count('usuarios', distinct=True),
            total_produtos=Count('produtos', distinct=True),
            total_pedidos=Count('pedidos', distinct=True)
        ).order_by('-criado_em')
        busca = self.request.GET.get('q')
        if busca:
            qs = qs.filter(nome__icontains=busca) | qs.filter(nome_fantasia__icontains=busca)
        return qs


class EmpresaCreateView(MasterRequiredMixin, CreateView):
    """
    Cadastro de nova empresa e do seu primeiro gestor responsável.
    """
    model = Empresa
    form_class = EmpresaComResponsavelForm
    template_name = 'core/empresa_form.html'
    success_url = reverse_lazy('core:empresas_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa e Gestor Responsável cadastrados com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Cadastrar Nova Empresa Cliente'
        ctx['com_responsavel'] = True
        return ctx


class EmpresaUpdateView(MasterRequiredMixin, UpdateView):
    """
    Edição dos dados cadastrais de uma empresa cliente existente.
    """
    model = Empresa
    form_class = EmpresaForm
    template_name = 'core/empresa_form.html'
    success_url = reverse_lazy('core:empresas_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Dados da empresa atualizados com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar Empresa: {self.object.nome}'
        ctx['com_responsavel'] = False
        return ctx


class EmpresaToggleAtivoView(MasterRequiredMixin, View):
    """
    Bloqueio / Ativação de acesso de uma empresa cliente (ex: suspensão por mensalidade).
    """
    def post(self, request, pk):
        empresa = get_object_or_404(Empresa, pk=pk)
        empresa.ativo = not empresa.ativo
        empresa.save()

        status = 'ativada' if empresa.ativo else 'suspensa / desativada'
        messages.success(request, f'Empresa "{empresa.nome}" foi {status} com sucesso.')
        return redirect('core:empresas_lista')
