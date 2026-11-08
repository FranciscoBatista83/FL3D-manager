"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Impressoras (views.py)
=============================================================================
Gerenciamento de impressoras com suporte Multi-Empresa.
=============================================================================
"""

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib import messages

from core.mixins import EmpresaScopedMixin
from .models import Impressora
from .forms import ImpressoraForm


class ImpressoraListView(EmpresaScopedMixin, ListView):
    """
    Tela principal que lista todo o parque de impressoras 3D da empresa.
    """
    model = Impressora
    template_name = 'impressoras/impressora_list.html'
    context_object_name = 'impressoras'


class ImpressoraCreateView(EmpresaScopedMixin, CreateView):
    """
    Tela para cadastrar uma nova impressora 3D para a empresa.
    """
    model = Impressora
    form_class = ImpressoraForm
    template_name = 'impressoras/impressora_form.html'
    success_url = reverse_lazy('impressoras:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Impressora cadastrada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nova Impressora'
        return ctx


class ImpressoraUpdateView(EmpresaScopedMixin, UpdateView):
    """
    Tela para alterar dados técnicos ou o status da impressora.
    """
    model = Impressora
    form_class = ImpressoraForm
    template_name = 'impressoras/impressora_form.html'
    success_url = reverse_lazy('impressoras:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Impressora atualizada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.nome}'
        return ctx


class ImpressoraDetailView(EmpresaScopedMixin, DetailView):
    """
    Tela de visão detalhada de uma máquina específica.
    """
    model = Impressora
    template_name = 'impressoras/impressora_detail.html'
    context_object_name = 'impressora'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['impressoes'] = self.object.producoes.all().order_by('-data_inicio')[:20]
        return ctx


class ImpressoraDeleteView(EmpresaScopedMixin, DeleteView):
    """
    Tela de confirmação para remover uma impressora da empresa.
    """
    model = Impressora
    template_name = 'impressoras/impressora_confirm_delete.html'
    success_url = reverse_lazy('impressoras:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Impressora excluída com sucesso!')
        return super().form_valid(form)
