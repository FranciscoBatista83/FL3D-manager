"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Estoque (views.py)
=============================================================================
Lógica de estoque de filamentos com suporte Multi-Empresa.
=============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from core.mixins import EmpresaScopedMixin
from .models import Filamento, MovimentacaoEstoque
from .forms import FilamentoForm, AjusteEstoqueForm


class FilamentoListView(EmpresaScopedMixin, ListView):
    """
    Tela principal do estoque de filamentos da empresa logada.
    """
    model = Filamento
    template_name = 'estoque/filamento_list.html'
    context_object_name = 'filamentos'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        busca = self.request.GET.get('q')
        if busca:
            qs = qs.filter(
                Q(nome__icontains=busca) |
                Q(marca__icontains=busca) |
                Q(material__icontains=busca) |
                Q(cor__icontains=busca) |
                Q(fornecedor__icontains=busca)
            )
        return qs


class FilamentoCreateView(EmpresaScopedMixin, CreateView):
    """
    Tela de cadastro de um novo item no estoque da empresa.
    """
    model = Filamento
    form_class = FilamentoForm
    template_name = 'estoque/filamento_form.html'
    success_url = reverse_lazy('estoque:lista')

    def form_valid(self, form):
        filamento = form.save(commit=False)
        filamento.empresa = getattr(self.request, 'empresa', None)
        filamento.peso_inicial = filamento.quantidade
        filamento.peso_atual = filamento.quantidade
        filamento.custo_rolo = filamento.preco
        filamento.save()

        messages.success(self.request, f'Produto "{filamento}" cadastrado com sucesso!')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Produto'
        return ctx


class FilamentoUpdateView(EmpresaScopedMixin, UpdateView):
    """
    Tela para editar informações do produto no estoque.
    """
    model = Filamento
    form_class = FilamentoForm
    template_name = 'estoque/filamento_form.html'
    success_url = reverse_lazy('estoque:lista')

    def form_valid(self, form):
        filamento = form.save(commit=False)
        filamento.save()
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar Produto: {self.object}'
        return ctx


class FilamentoDetailView(EmpresaScopedMixin, DetailView):
    """
    Ficha de detalhes de um carretel de filamento.
    """
    model = Filamento
    template_name = 'estoque/filamento_detail.html'
    context_object_name = 'filamento'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['movimentacoes'] = self.object.movimentacoes.all().order_by('-data')
        
        peso_ini = self.object.peso_inicial or 0
        peso_at = self.object.peso_atual or 0
        if peso_ini > 0:
            ctx['percentual_restante'] = round((peso_at / peso_ini) * 100, 1)
        else:
            ctx['percentual_restante'] = 0
        return ctx


@login_required
def ajuste_estoque_view(request, pk):
    """
    Ajuste de Estoque por Pesagem na Balança Física com isolamento por empresa.
    """
    empresa = getattr(request, 'empresa', None)
    qs = Filamento.objects.filter(empresa=empresa) if empresa else Filamento.objects.all()
    filamento = get_object_or_404(qs, pk=pk)

    if request.method == 'POST':
        form = AjusteEstoqueForm(request.POST)
        if form.is_valid():
            peso_fisico = form.cleaned_data['peso_fisico']
            motivo = form.cleaned_data['motivo']
            peso_anterior = filamento.peso_atual or 0
            diferenca = peso_fisico - peso_anterior

            MovimentacaoEstoque.objects.create(
                filamento=filamento,
                tipo=MovimentacaoEstoque.TipoChoices.AJUSTE,
                quantidade=diferenca,
                quantidade_anterior=peso_anterior,
                quantidade_nova=peso_fisico,
                motivo=f'Ajuste manual. Motivo: {motivo}',
                usuario=request.user,
            )

            filamento.peso_atual = peso_fisico
            filamento.save()

            sinal = '+' if diferenca >= 0 else ''
            messages.success(
                request,
                f'Ajuste realizado com sucesso! Estoque atualizado de {peso_anterior}g para {peso_fisico}g '
                f'(diferença: {sinal}{diferenca}g).'
            )
            return redirect('estoque:detalhe', pk=filamento.pk)
    else:
        form = AjusteEstoqueForm()

    return render(request, 'estoque/ajuste_form.html', {
        'form': form,
        'filamento': filamento,
    })
