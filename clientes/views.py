"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Clientes (views.py)
=============================================================================
Gerenciamento de clientes com suporte Multi-Empresa.
=============================================================================
"""

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages

from core.mixins import EmpresaScopedMixin
from .models import Cliente
from .forms import ClienteForm


class ClienteListView(EmpresaScopedMixin, ListView):
    """
    Tela que lista todos os clientes cadastrados para a empresa do usuário logado.
    """
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get('q')
        if busca:
            queryset = queryset.filter(nome__icontains=busca)
        return queryset


class ClienteCreateView(EmpresaScopedMixin, CreateView):
    """
    Tela com o formulário para cadastrar um novo cliente na empresa.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente cadastrado com sucesso!')
        return super().form_valid(form)


class ClienteUpdateView(EmpresaScopedMixin, UpdateView):
    """
    Tela para editar as informações de um cliente da empresa.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return super().form_valid(form)


class ClienteDetailView(EmpresaScopedMixin, DetailView):
    """
    Ficha detalhada do cliente da empresa.
    """
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pedidos'] = self.object.pedidos.all().order_by('-data_pedido')
        return context


class ClienteDeleteView(EmpresaScopedMixin, DeleteView):
    """
    Tela de confirmação para inativação de um cliente (Soft Delete).
    """
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        cliente = self.get_object()
        cliente.ativo = False
        cliente.save()
        messages.success(self.request, 'Cliente removido (inativado) com sucesso!')
        return redirect(self.success_url)
