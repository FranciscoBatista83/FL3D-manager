"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Pedidos (views.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Controla todas as operações comerciais de vendas e orçamentos:
  1. LISTA DE PEDIDOS: busca pedidos pelo número ou pelo nome do cliente e
     permite filtrar por status (ex: mostrar apenas pedidos 'Em Produção').
  2. NOVO PEDIDO: tela avançada que recebe os dados da venda, salva os itens
     do carrinho, calcula a soma das peças, subtrai o desconto e gera o total líquido.
  3. EDIÇÃO DE PEDIDO: permite adicionar mais itens, remover produtos e recalcular
     os valores automaticamente.
  4. DETALHE DO PEDIDO: visualização completa da ordem de venda com itens e totais.
  5. CANCELAMENTO: cancela o pedido sem apagá-lo do banco de dados.
=============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal

from .models import Pedido, ItemPedido
from .forms import PedidoForm, ItemPedidoFormSet
from produtos.models import Produto


class PedidoListView(LoginRequiredMixin, ListView):
    """
    Lista todos os pedidos com paginação (15 por página), busca rápida e filtro por status.
    """
    model = Pedido
    template_name = 'pedidos/pedido_list.html'
    context_object_name = 'pedidos'
    paginate_by = 15

    def get_queryset(self):
        """
        Otimiza a busca trazendo os dados do cliente com `select_related('cliente')`
        (evita consultas repetitivas ao banco de dados) e aplica os filtros de texto e status.
        """
        queryset = super().get_queryset().select_related('cliente')
        busca = self.request.GET.get('q')
        status = self.request.GET.get('status')
        
        # Filtra por nome do cliente ou número do pedido
        if busca:
            queryset = queryset.filter(
                Q(cliente__nome__icontains=busca) | Q(numero__icontains=busca)
            )
        
        # Filtra pelo status selecionado (ex: orcamento, aprovado, pronto)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Envia a lista de opções de status para preencher o menu dropdown de filtro na tela.
        """
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Pedido.StatusChoices.choices
        context['status_filtro'] = self.request.GET.get('status', '')
        return context


class PedidoCreateView(LoginRequiredMixin, View):
    """
    Criação de pedido com itens dinâmicos na mesma página.
    """
    template_name = 'pedidos/pedido_form.html'

    def get(self, request):
        """
        Exibe a tela com o formulário limpo e a lista de produtos ativos em JSON
        para que o JavaScript preencha os preços na tela instantaneamente ao selecionar um item.
        """
        form = PedidoForm()
        formset = ItemPedidoFormSet()
        produtos_json = list(Produto.objects.filter(ativo=True).values('id', 'nome', 'preco_venda'))
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'produtos_json': produtos_json,
            'titulo': 'Novo Pedido',
        })

    def post(self, request):
        """
        Processa e valida os dados do formulário e de todas as linhas de itens enviadas.
        """
        form = PedidoForm(request.POST)
        formset = ItemPedidoFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # 1. Salva o pedido primeiro para gerar o número primário (#ID)
            pedido = form.save(commit=False)
            pedido.save()
            
            # 2. Salva os itens vinculando cada um ao pedido recém-criado
            instancias = formset.save(commit=False)
            valor_produtos = Decimal('0.00')
            for item in instancias:
                item.pedido = pedido
                item.save()
                valor_produtos += item.valor_total
            
            # 3. Remove linhas que foram marcadas para exclusão no formset
            for obj in formset.deleted_objects:
                obj.delete()
            
            # 4. Faz a matemática financeira do pedido:
            # Valor Final = (Soma dos Produtos) - (Desconto)
            desconto = pedido.desconto or Decimal('0.00')
            pedido.valor_produtos = valor_produtos
            pedido.valor_final = valor_produtos - desconto
            pedido.save()
            
            messages.success(request, f'Pedido #{pedido.numero} criado com sucesso!')
            return redirect('pedidos:detalhe', pk=pedido.pk)
        
        # Se houver erro de validação, reexibe o formulário com os erros apontados
        produtos_json = list(Produto.objects.filter(ativo=True).values('id', 'nome', 'preco_venda'))
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'produtos_json': produtos_json,
            'titulo': 'Novo Pedido',
        })


class PedidoUpdateView(LoginRequiredMixin, View):
    """
    Edição de pedidos já existentes, permitindo alterar itens, descontos e status.
    """
    template_name = 'pedidos/pedido_form.html'

    def get(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        form = PedidoForm(instance=pedido)
        formset = ItemPedidoFormSet(instance=pedido)
        produtos_json = list(Produto.objects.filter(ativo=True).values('id', 'nome', 'preco_venda'))
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'pedido': pedido,
            'produtos_json': produtos_json,
            'titulo': f'Editar Pedido #{pedido.numero}',
        })

    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        form = PedidoForm(request.POST, instance=pedido)
        formset = ItemPedidoFormSet(request.POST, instance=pedido)
        
        if form.is_valid() and formset.is_valid():
            pedido = form.save()
            instancias = formset.save(commit=False)
            
            for item in instancias:
                item.pedido = pedido
                item.save()
            
            for obj in formset.deleted_objects:
                obj.delete()
            
            # Recalcula a soma de todos os itens ativos do pedido
            valor_produtos = Decimal('0.00')
            for item in pedido.itens.all():
                valor_produtos += item.valor_total
            
            # Atualiza o total com o desconto aplicado
            desconto = pedido.desconto or Decimal('0.00')
            pedido.valor_produtos = valor_produtos
            pedido.valor_final = valor_produtos - desconto
            pedido.save()
            
            messages.success(request, f'Pedido #{pedido.numero} atualizado com sucesso!')
            return redirect('pedidos:detalhe', pk=pedido.pk)
        
        produtos_json = list(Produto.objects.filter(ativo=True).values('id', 'nome', 'preco_venda'))
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'pedido': pedido,
            'produtos_json': produtos_json,
            'titulo': f'Editar Pedido #{pedido.numero}',
        })


class PedidoDetailView(LoginRequiredMixin, DetailView):
    """
    Ficha de detalhes do pedido (resumo completo para impressão ou conferência).
    """
    model = Pedido
    template_name = 'pedidos/pedido_detail.html'
    context_object_name = 'pedido'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Traz os itens do pedido otimizando a consulta dos produtos vinculados
        context['itens'] = self.object.itens.select_related('produto').all()
        return context


class PedidoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Cancelamento de pedido.
    """
    model = Pedido
    template_name = 'pedidos/pedido_confirm_delete.html'
    success_url = reverse_lazy('pedidos:lista')

    def form_valid(self, form):
        """
        Em vez de deletar fisicamente do banco de dados, marca o status como 'CANCELADO'.
        Isso mantém a auditoria e numeração intactas.
        """
        pedido = self.get_object()
        pedido.status = Pedido.StatusChoices.CANCELADO
        pedido.save()
        messages.success(self.request, f'Pedido #{pedido.numero} cancelado com sucesso!')
        return redirect(self.success_url)
