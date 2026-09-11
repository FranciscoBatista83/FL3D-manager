"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Produtos (views.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Controla todas as telas do catálogo de produtos da FL3D Studio:
  1. LISTA DE PRODUTOS: mostra as peças com foto, preço, material e tempo de impressão,
     permitindo filtrar por nome ou código SKU na barra de pesquisa.
  2. CADASTRO: salva um novo produto e sua foto no sistema.
  3. EDIÇÃO: altera preços, tempos ou descrições.
  4. DETALHES: abre a ficha técnica completa da peça 3D.
  5. EXCLUSÃO SUAVE: desativa o produto sem apagar o histórico de vendas.
=============================================================================
"""

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Produto
from .forms import ProdutoForm


class ProdutoListView(LoginRequiredMixin, ListView):
    """
    Lista todos os produtos ativos do catálogo, com suporte a busca por nome ou código.
    """
    model = Produto
    template_name = 'produtos/produto_list.html'
    context_object_name = 'produtos'
    paginate_by = 10  # Carrega 10 itens por página

    def get_queryset(self):
        """
        Permite pesquisar produtos tanto pelo Nome (ex: 'Chaveiro')
        quanto pelo Código SKU (ex: 'CHV-001').
        """
        queryset = super().get_queryset()
        busca = self.request.GET.get('q')
        if busca:
            # O operador '|' significa 'OU': busca por nome OU por código
            queryset = queryset.filter(nome__icontains=busca) | queryset.filter(codigo__icontains=busca)
        return queryset


class ProdutoCreateView(LoginRequiredMixin, CreateView):
    """
    Tela com formulário para cadastrar uma nova peça no catálogo.
    """
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/produto_form.html'
    success_url = reverse_lazy('produtos:lista')

    def form_valid(self, form):
        """
        Disparado quando o produto foi cadastrado com sucesso.
        """
        messages.success(self.request, 'Produto cadastrado com sucesso!')
        return super().form_valid(form)


class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Tela para editar as informações técnicas ou comerciais de um produto.
    """
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/produto_form.html'
    success_url = reverse_lazy('produtos:lista')

    def form_valid(self, form):
        """
        Disparado quando a atualização do produto foi salva com sucesso.
        """
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return super().form_valid(form)


class ProdutoDetailView(LoginRequiredMixin, DetailView):
    """
    Tela com a ficha técnica completa do produto (foto grande, parâmetros do fatiador,
    margem de lucro e tempo estimado).
    """
    model = Produto
    template_name = 'produtos/produto_detail.html'
    context_object_name = 'produto'


class ProdutoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Inativação segura do produto (Soft Delete).
    """
    model = Produto
    template_name = 'produtos/produto_confirm_delete.html'
    success_url = reverse_lazy('produtos:lista')

    def form_valid(self, form):
        """
        Altera `ativo = False` para que o item suma das listagens comuns,
        mas os relatórios de pedidos passados continuem funcionando.
        """
        produto = self.get_object()
        produto.ativo = False
        produto.save()
        messages.success(self.request, 'Produto inativado com sucesso!')
        return redirect(self.success_url)

