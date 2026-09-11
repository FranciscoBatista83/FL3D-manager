"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Impressoras (views.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo gerencia todas as operações relacionadas às máquinas da oficina:
  1. LISTAGEM: exibe a lista completa de impressoras com seus status operacionais
     (verde para disponível, azul para imprimindo, amarelo para manutenção).
  2. CADASTRO: adiciona uma nova máquina ao parque fabril.
  3. EDIÇÃO: atualiza informações, troca status para manutenção e inclui notas de reparo.
  4. DETALHE DA MÁQUINA: mostra as especificações da impressora e as últimas 20
     peças impressas nela (histórico de produção).
  5. EXCLUSÃO: remove a máquina do sistema quando for descartada ou vendida.
=============================================================================
"""

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Impressora
from .forms import ImpressoraForm


class ImpressoraListView(LoginRequiredMixin, ListView):
    """
    Tela principal que lista todo o parque de impressoras 3D da oficina.
    """
    model = Impressora
    template_name = 'impressoras/impressora_list.html'
    context_object_name = 'impressoras'


class ImpressoraCreateView(LoginRequiredMixin, CreateView):
    """
    Tela para cadastrar uma nova impressora 3D comprada pela FL3D Studio.
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


class ImpressoraUpdateView(LoginRequiredMixin, UpdateView):
    """
    Tela para alterar dados técnicos ou o status da impressora (ex: colocar em manutenção).
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


class ImpressoraDetailView(LoginRequiredMixin, DetailView):
    """
    Tela de visão detalhada de uma máquina específica.
    Permite consultar as últimas 20 impressões realizadas por ela.
    """
    model = Impressora
    template_name = 'impressoras/impressora_detail.html'
    context_object_name = 'impressora'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Recupera as 20 produções mais recentes feitas nesta impressora
        ctx['impressoes'] = self.object.producoes.all().order_by('-data_inicio')[:20]
        return ctx


class ImpressoraDeleteView(LoginRequiredMixin, DeleteView):
    """
    Tela de confirmação para remover uma impressora do sistema.
    """
    model = Impressora
    template_name = 'impressoras/impressora_confirm_delete.html'
    success_url = reverse_lazy('impressoras:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Impressora excluída com sucesso!')
        return super().form_valid(form)
