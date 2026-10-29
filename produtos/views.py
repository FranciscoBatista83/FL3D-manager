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

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count
import json

from .models import Produto, Categoria
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
        quanto pelo Código SKU (ex: 'CHV-001'), e filtrar por categoria.
        """
        queryset = super().get_queryset()
        busca = self.request.GET.get('q')
        categoria_id = self.request.GET.get('categoria')
        if busca:
            # O operador '|' significa 'OU': busca por nome OU por código
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
        context['categorias'] = Categoria.objects.all()
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        return context


class ProdutoCreateView(LoginRequiredMixin, CreateView):
    """
    Tela com formulário para cadastrar uma nova peça no catálogo.
    """
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/produto_form.html'
    success_url = reverse_lazy('produtos:lista')

    def get_initial(self):
        """
        Captura parâmetros repassados pela Calculadora de Precificação via URL.
        """
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
                    import json
                    try:
                        val = json.loads(val)
                    except json.JSONDecodeError:
                        pass
                initial[field] = val
        return initial

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

    def get_initial(self):
        """
        Captura eventuais parâmetros atualizados repassados pela Calculadora via URL.
        """
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
                    import json
                    try:
                        val = json.loads(val)
                    except json.JSONDecodeError:
                        pass
                initial[field] = val
        return initial

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



class ProdutoHardDeleteView(LoginRequiredMixin, DeleteView):
    """
    Exclusão definitiva e irreversível do produto do banco de dados.
    Requer confirmação dupla via POST com campo de texto 'EXCLUIR'.
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
    Abre o arquivo de impressao do produto com o programa padrao do Windows
    (ex: BambuStudio para .3mf, Notepad para .gcode, etc).
    Funciona pois o servidor Django roda localmente na maquina do usuario.
    """
    import subprocess
    from .models import Produto
    produto = get_object_or_404(Produto, pk=pk)
    if produto.arquivo_impressao:
        caminho = produto.arquivo_impressao.path
        try:
            subprocess.Popen(['cmd', '/c', 'start', '', caminho], shell=False)
            messages.success(request, 'Arquivo aberto com sucesso!')
        except Exception as e:
            messages.error(request, f'Nao foi possivel abrir o arquivo: {e}')
    else:
        messages.warning(request, 'Este produto nao possui arquivo de impressao cadastrado.')
    return redirect('produtos:detalhe', pk=pk)


@require_http_methods(["POST"])
def criar_categoria_api(request):
    """
    Endpoint AJAX para cadastrar rapidamente uma nova categoria.
    """
    try:
        try:
            data = json.loads(request.body)
            nome = str(data.get('nome', '')).strip()
        except Exception:
            nome = str(request.POST.get('nome', '')).strip()

        if not nome:
            return JsonResponse({'sucesso': False, 'erro': 'Informe o nome da categoria.'}, status=400)

        categoria, criada = Categoria.objects.get_or_create(nome=nome)
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
    Endpoint AJAX para listar todas as categorias com a contagem de produtos vinculados.
    """
    categorias = Categoria.objects.annotate(total_produtos=Count('produtos')).values('id', 'nome', 'total_produtos')
    return JsonResponse({'sucesso': True, 'categorias': list(categorias)})


@require_http_methods(["POST"])
def excluir_categoria_api(request, pk):
    """
    Endpoint AJAX para excluir uma categoria.
    Produtos associados terão categoria definida como NULL (sem perda de produtos).
    """
    try:
        categoria = get_object_or_404(Categoria, pk=pk)
        nome = categoria.nome
        categoria.delete()
        return JsonResponse({
            'sucesso': True,
            'mensagem': f'Categoria "{nome}" excluída com sucesso!'
        })
    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)
