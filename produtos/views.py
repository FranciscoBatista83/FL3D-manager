"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Produtos (views.py)
=============================================================================
Controla todas as telas do catálogo de produtos com suporte Multi-Empresa:
  1. LISTA DE PRODUTOS: isolada por empresa.
  2. CADASTRO / EDIÇÃO: vincula à empresa do usuário.
  3. DETALHES / EXCLUSÃO: com trava por empresa.
  4. CATEGORIAS (AJAX): filtradas e criadas para a empresa do usuário.
=============================================================================
"""

import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count

from core.mixins import EmpresaScopedMixin
from .models import Produto, Categoria
from .forms import ProdutoForm


class ProdutoListView(EmpresaScopedMixin, ListView):
    """
    Lista todos os produtos ativos do catálogo da empresa do usuário logado.
    """
    model = Produto
    template_name = 'produtos/produto_list.html'
    context_object_name = 'produtos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get('q')
        categoria_id = self.request.GET.get('categoria')
        if busca:
            queryset = queryset.filter(nome__icontains=busca) | queryset.filter(codigo__icontains=busca)
        if categoria_id:
            if categoria_id == 'sem_categoria':
                queryset = queryset.filter(categoria__isnull=True)
            else:
                try:
                    queryset = queryset.filter(categoria_id=int(categoria_id))
                except (ValueError, TypeError):
                    pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = getattr(self.request, 'empresa', None)
        if empresa:
            context['categorias'] = Categoria.objects.filter(empresa=empresa)
        else:
            context['categorias'] = Categoria.objects.all()
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        return context


class ProdutoCreateView(EmpresaScopedMixin, CreateView):
    """
    Tela com formulário para cadastrar uma nova peça no catálogo.
    """
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/produto_form.html'
    success_url = reverse_lazy('produtos:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = getattr(self.request, 'empresa', None)
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        fields_to_transfer = [
            'nome', 'categoria', 'peso_estimado', 'tempo_estimado',
            'valor_kg_filamento', 'detalhes_filamentos', 'potencia_impressora_w', 'custo_kwh_energia',
            'custo_embalagem', 'custo_insumos', 'custo_mao_de_obra',
            'marketplace', 'comissao_afiliado_percentual', 'custo_taxas_marketplace',
            'custo_estimado', 'preco_venda', 'margem_lucro'
        ]
        for field in fields_to_transfer:
            val = self.request.GET.get(field)
            if val is not None and val != '':
                if field == 'detalhes_filamentos':
                    try:
                        val = json.loads(val)
                    except json.JSONDecodeError:
                        pass
                initial[field] = val
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Produto cadastrado com sucesso!')
        return super().form_valid(form)


class ProdutoUpdateView(EmpresaScopedMixin, UpdateView):
    """
    Tela para editar as informações técnicas ou comerciais de um produto.
    """
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/produto_form.html'
    success_url = reverse_lazy('produtos:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = getattr(self.request, 'empresa', None)
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return super().form_valid(form)


class ProdutoDetailView(EmpresaScopedMixin, DetailView):
    """
    Tela com a ficha técnica completa do produto.
    """
    model = Produto
    template_name = 'produtos/produto_detail.html'
    context_object_name = 'produto'


class ProdutoDeleteView(EmpresaScopedMixin, DeleteView):
    """
    Inativação segura do produto (Soft Delete).
    """
    model = Produto
    template_name = 'produtos/produto_confirm_delete.html'
    success_url = reverse_lazy('produtos:lista')

    def form_valid(self, form):
        produto = self.get_object()
        produto.ativo = False
        produto.save()
        messages.success(self.request, 'Produto inativado com sucesso!')
        return redirect(self.success_url)


class ProdutoHardDeleteView(EmpresaScopedMixin, DeleteView):
    """
    Exclusão definitiva e irreversível do produto do banco de dados.
    """
    model = Produto
    success_url = reverse_lazy('produtos:lista')

    def post(self, request, *args, **kwargs):
        confirmacao = request.POST.get('confirmacao', '')
        if confirmacao != 'EXCLUIR':
            messages.error(request, 'Confirmação inválida. Digite exatamente "EXCLUIR" para confirmar.')
            return redirect('produtos:lista')
        produto = self.get_object()
        nome = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome}" excluído definitivamente do sistema.')
        return redirect(self.success_url)


def abrir_arquivo_impressao(request, pk):
    """
    Abre o arquivo de impressão do produto.
    """
    import subprocess
    empresa = getattr(request, 'empresa', None)
    qs = Produto.objects.filter(empresa=empresa) if empresa else Produto.objects.all()
    produto = get_object_or_404(qs, pk=pk)
    if produto.arquivo_impressao:
        caminho = produto.arquivo_impressao.path
        try:
            subprocess.Popen(['cmd', '/c', 'start', '', caminho], shell=False)
            messages.success(request, 'Arquivo aberto com sucesso!')
        except Exception as e:
            messages.error(request, f'Não foi possível abrir o arquivo: {e}')
    else:
        messages.warning(request, 'Este produto não possui arquivo de impressão cadastrado.')
    return redirect('produtos:detalhe', pk=pk)


@require_http_methods(["POST"])
def criar_categoria_api(request):
    """
    Endpoint AJAX para cadastrar categoria para a empresa do usuário logado.
    """
    try:
        try:
            data = json.loads(request.body)
            nome = str(data.get('nome', '')).strip()
        except Exception:
            nome = str(request.POST.get('nome', '')).strip()

        if not nome:
            return JsonResponse({'sucesso': False, 'erro': 'Informe o nome da categoria.'}, status=400)

        empresa = getattr(request, 'empresa', None)
        categoria, criada = Categoria.objects.get_or_create(empresa=empresa, nome=nome)
        return JsonResponse({
            'sucesso': True,
            'id': categoria.id,
            'nome': categoria.nome,
            'criada': criada,
            'mensagem': f'Categoria "{categoria.nome}" pronta para uso!'
        })
    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)


@require_http_methods(["GET"])
def listar_categorias_api(request):
    """
    Endpoint AJAX para listar categorias da empresa atual com contagem de produtos.
    """
    empresa = getattr(request, 'empresa', None)
    qs = Categoria.objects.filter(empresa=empresa) if empresa else Categoria.objects.all()
    categorias = qs.annotate(total_produtos=Count('produtos')).values('id', 'nome', 'total_produtos')
    return JsonResponse({'sucesso': True, 'categorias': list(categorias)})


@require_http_methods(["POST"])
def excluir_categoria_api(request, pk):
    """
    Endpoint AJAX para excluir categoria da empresa atual.
    """
    try:
        empresa = getattr(request, 'empresa', None)
        qs = Categoria.objects.filter(empresa=empresa) if empresa else Categoria.objects.all()
        categoria = get_object_or_404(qs, pk=pk)
        nome = categoria.nome
        categoria.delete()
        return JsonResponse({
            'sucesso': True,
            'mensagem': f'Categoria "{nome}" excluída com sucesso!'
        })
    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)
