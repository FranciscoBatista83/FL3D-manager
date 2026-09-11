"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Clientes (views.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo gerencia todas as telas e ações que o usuário pode fazer com clientes:
  1. LISTAR clientes cadastrados, com paginação de 10 em 10 e campo de busca rápida por nome.
  2. CADASTRAR um novo cliente com validação de dados e mensagem de sucesso.
  3. EDITAR os dados de um cliente já existente.
  4. VER OS DETALHES do cliente, exibindo todo o histórico de pedidos que ele já fez na FL3D.
  5. EXCLUIR um cliente usando "Soft Delete" (inativação sem deletar do banco de dados,
     para não corromper o histórico financeiro e fiscal).
=============================================================================
"""

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Cliente
from .forms import ClienteForm


class ClienteListView(LoginRequiredMixin, ListView):
    """
    Tela que lista todos os clientes cadastrados no sistema.
    Possui paginação (10 clientes por página) e suporte a barra de pesquisa.
    """
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10  # Exibe 10 clientes por página para carregar rápido

    def get_queryset(self):
        """
        Personaliza a consulta no banco de dados.
        Se o usuário digitou algo na barra de pesquisa (parâmetro 'q' na URL),
        filtra os clientes cujo nome contenha o texto digitado (busca sem diferenciar maiúsculas).
        """
        queryset = super().get_queryset()
        busca = self.request.GET.get('q')
        if busca:
            queryset = queryset.filter(nome__icontains=busca)
        return queryset


class ClienteCreateView(LoginRequiredMixin, CreateView):
    """
    Tela com o formulário para cadastrar um novo cliente na oficina.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    # Ao salvar com sucesso, redireciona para a lista de clientes
    success_url = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        """
        Executado quando todos os dados digitados estão corretos.
        Gera um aviso verde no topo da tela: "Cliente cadastrado com sucesso!"
        """
        messages.success(self.request, 'Cliente cadastrado com sucesso!')
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    """
    Tela para editar as informações de um cliente já cadastrado.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        """
        Executado quando a edição é salva com sucesso.
        Gera a notificação de confirmação.
        """
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return super().form_valid(form)


class ClienteDetailView(LoginRequiredMixin, DetailView):
    """
    Ficha detalhada do cliente.
    Mostra os dados de contato, endereço e o histórico completo de pedidos feitos por ele.
    """
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        """
        Envia informações complementares para o arquivo HTML.
        Aqui buscamos todos os pedidos vinculados a este cliente e ordenamos
        dos mais recentes para os mais antigos.
        """
        context = super().get_context_data(**kwargs)
        # self.object é o cliente atual sendo visualizado na tela
        context['pedidos'] = self.object.pedidos.all().order_by('-data_pedido')
        return context


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    """
    Tela de confirmação para exclusão de um cliente.
    IMPORTANTE: Adotamos a prática profissional de 'Soft Delete' (Exclusão Suave).
    """
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        """
        Sobrescrevemos o método de exclusão padrão do Django.
        Em vez de usar `cliente.delete()` (que apagaria o registro para sempre e
        quebraria o histórico financeiro dos pedidos antigos dele), nós apenas
        alteramos `cliente.ativo = False`.
        """
        cliente = self.get_object()
        cliente.ativo = False
        cliente.save()
        messages.success(self.request, 'Cliente removido (inativado) com sucesso!')
        return redirect(self.success_url)

