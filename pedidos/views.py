"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Pedidos (views.py)
=============================================================================
Gerenciamento de pedidos com suporte Multi-Empresa.
=============================================================================
"""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q

from core.mixins import EmpresaScopedMixin
from .models import Pedido, ItemPedido
from .forms import PedidoForm, ItemPedidoFormSet
from produtos.models import Produto


class PedidoListView(EmpresaScopedMixin, ListView):
    """
    Lista todos os pedidos da empresa do usuário logado.
    """
    model = Pedido
    template_name = 'pedidos/pedido_list.html'
    context_object_name = 'pedidos'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente')
        busca = self.request.GET.get('q')
        status = self.request.GET.get('status')
        
        if busca:
            queryset = queryset.filter(
                Q(cliente__nome__icontains=busca) | Q(numero__icontains=busca)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Pedido.StatusChoices.choices
        context['status_filtro'] = self.request.GET.get('status', '')
        return context


class PedidoCreateView(LoginRequiredMixin, View):
    """
    Criação de pedido com itens dinâmicos associados à empresa do usuário.
    """
    template_name = 'pedidos/pedido_form.html'

    def get(self, request):
        empresa = getattr(request, 'empresa', None)
        form = PedidoForm(empresa=empresa)
        formset = ItemPedidoFormSet(form_kwargs={'empresa': empresa})
        produtos_qs = Produto.objects.filter(empresa=empresa, ativo=True) if empresa else Produto.objects.filter(ativo=True)
        produtos_json = list(produtos_qs.values('id', 'nome', 'preco_venda'))
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'produtos_json': produtos_json,
            'titulo': 'Novo Pedido',
        })

    def post(self, request):
        empresa = getattr(request, 'empresa', None)
        form = PedidoForm(request.POST, empresa=empresa)
        formset = ItemPedidoFormSet(request.POST, form_kwargs={'empresa': empresa})
        
        if form.is_valid() and formset.is_valid():
            pedido = form.save(commit=False)
            pedido.empresa = empresa
            pedido.save()
            
            instancias = formset.save(commit=False)
            valor_produtos = Decimal('0.00')
            for item in instancias:
                item.pedido = pedido
                item.save()
                valor_produtos += item.valor_total
            
            for obj in formset.deleted_objects:
                obj.delete()
            
            desconto = pedido.desconto or Decimal('0.00')
            pedido.valor_produtos = valor_produtos
            pedido.valor_final = valor_produtos - desconto
            pedido.save()
            
            messages.success(request, f'Pedido #{pedido.numero} criado com sucesso!')
            return redirect('pedidos:detalhe', pk=pedido.pk)
        
        produtos_qs = Produto.objects.filter(empresa=empresa, ativo=True) if empresa else Produto.objects.filter(ativo=True)
        produtos_json = list(produtos_qs.values('id', 'nome', 'preco_venda'))
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'produtos_json': produtos_json,
            'titulo': 'Novo Pedido',
        })


class PedidoUpdateView(LoginRequiredMixin, View):
    """
    Edição de pedidos existentes da empresa.
    """
    template_name = 'pedidos/pedido_form.html'

    def get_pedido(self, request, pk):
        empresa = getattr(request, 'empresa', None)
        qs = Pedido.objects.filter(empresa=empresa) if empresa else Pedido.objects.all()
        return get_object_or_404(qs, pk=pk)

    def get(self, request, pk):
        empresa = getattr(request, 'empresa', None)
        pedido = self.get_pedido(request, pk)
        form = PedidoForm(instance=pedido, empresa=empresa)
        formset = ItemPedidoFormSet(instance=pedido, form_kwargs={'empresa': empresa})
        produtos_qs = Produto.objects.filter(empresa=empresa, ativo=True) if empresa else Produto.objects.filter(ativo=True)
        produtos_json = list(produtos_qs.values('id', 'nome', 'preco_venda'))
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'pedido': pedido,
            'produtos_json': produtos_json,
            'titulo': f'Editar Pedido #{pedido.numero}',
        })

    def post(self, request, pk):
        empresa = getattr(request, 'empresa', None)
        pedido = self.get_pedido(request, pk)
        form = PedidoForm(request.POST, instance=pedido, empresa=empresa)
        formset = ItemPedidoFormSet(request.POST, instance=pedido, form_kwargs={'empresa': empresa})
        
        if form.is_valid() and formset.is_valid():
            pedido = form.save()
            instancias = formset.save(commit=False)
            
            for item in instancias:
                item.pedido = pedido
                item.save()
            
            for obj in formset.deleted_objects:
                obj.delete()
            
            valor_produtos = Decimal('0.00')
            for item in pedido.itens.all():
                valor_produtos += item.valor_total
            
            desconto = pedido.desconto or Decimal('0.00')
            pedido.valor_produtos = valor_produtos
            pedido.valor_final = valor_produtos - desconto
            pedido.save()
            
            messages.success(request, f'Pedido #{pedido.numero} atualizado com sucesso!')
            return redirect('pedidos:detalhe', pk=pedido.pk)
        
        produtos_qs = Produto.objects.filter(empresa=empresa, ativo=True) if empresa else Produto.objects.filter(ativo=True)
        produtos_json = list(produtos_qs.values('id', 'nome', 'preco_venda'))
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'pedido': pedido,
            'produtos_json': produtos_json,
            'titulo': f'Editar Pedido #{pedido.numero}',
        })


class PedidoDetailView(EmpresaScopedMixin, DetailView):
    """
    Ficha de detalhes do pedido.
    """
    model = Pedido
    template_name = 'pedidos/pedido_detail.html'
    context_object_name = 'pedido'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['itens'] = self.object.itens.select_related('produto').all()
        return context


class PedidoDeleteView(EmpresaScopedMixin, DeleteView):
    """
    Cancelamento de pedido.
    """
    model = Pedido
    template_name = 'pedidos/pedido_confirm_delete.html'
    success_url = reverse_lazy('pedidos:lista')

    def form_valid(self, form):
        pedido = self.get_object()
        pedido.status = Pedido.StatusChoices.CANCELADO
        pedido.save()
        messages.success(self.request, f'Pedido #{pedido.numero} cancelado com sucesso!')
        return redirect(self.success_url)
