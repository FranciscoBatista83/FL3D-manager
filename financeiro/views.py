"""
=============================================================================
FL3D Manager - Visualizações do Módulo Financeiro (views.py)
=============================================================================
Dashboard e movimentações financeiras com suporte Multi-Empresa.
=============================================================================
"""

import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone

from core.mixins import EmpresaScopedMixin
from .models import MovimentacaoFinanceira
from .forms import MovimentacaoFinanceiraForm, RelatorioFiltroForm


class DashboardFinanceiroView(LoginRequiredMixin, View):
    """
    Painel Financeiro com indicadores da empresa logada.
    """
    template_name = 'financeiro/financeiro_dashboard.html'

    def get(self, request):
        empresa = getattr(request, 'empresa', None)
        base_qs = MovimentacaoFinanceira.objects.filter(empresa=empresa) if empresa else MovimentacaoFinanceira.objects.all()

        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)

        receitas_mes = base_qs.filter(
            tipo=MovimentacaoFinanceira.TipoChoices.ENTRADA,
            data__gte=inicio_mes,
            data__lte=hoje,
        ).aggregate(total=Sum('valor'))['total'] or 0

        despesas_mes = base_qs.filter(
            tipo=MovimentacaoFinanceira.TipoChoices.SAIDA,
            data__gte=inicio_mes,
            data__lte=hoje,
        ).aggregate(total=Sum('valor'))['total'] or 0

        saldo_mes = receitas_mes - despesas_mes

        labels, dados_receitas, dados_despesas = [], [], []
        for i in range(5, -1, -1):
            ref = hoje - relativedelta(months=i)
            inicio = ref.replace(day=1)
            if i > 0:
                fim = (inicio + relativedelta(months=1)) - timedelta(days=1)
            else:
                fim = hoje

            r = base_qs.filter(
                tipo=MovimentacaoFinanceira.TipoChoices.ENTRADA,
                data__gte=inicio,
                data__lte=fim,
            ).aggregate(total=Sum('valor'))['total'] or 0

            d = base_qs.filter(
                tipo=MovimentacaoFinanceira.TipoChoices.SAIDA,
                data__gte=inicio,
                data__lte=fim,
            ).aggregate(total=Sum('valor'))['total'] or 0

            labels.append(inicio.strftime('%b/%Y'))
            dados_receitas.append(float(r))
            dados_despesas.append(float(d))

        return render(request, self.template_name, {
            'receitas_mes': receitas_mes,
            'despesas_mes': despesas_mes,
            'saldo_mes': saldo_mes,
            'pendentes': [],
            'chart_labels': json.dumps(labels),
            'chart_receitas': json.dumps(dados_receitas),
            'chart_despesas': json.dumps(dados_despesas),
        })


class MovimentacaoFinanceiraListView(EmpresaScopedMixin, ListView):
    """
    Extrato de Lançamentos Financeiros da empresa logada.
    """
    model = MovimentacaoFinanceira
    template_name = 'financeiro/lancamento_list.html'
    context_object_name = 'lancamentos'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('pedido')
        tipo = self.request.GET.get('tipo')
        mes = self.request.GET.get('mes')
        
        if tipo:
            qs = qs.filter(tipo=tipo)
        if mes:
            try:
                ano, m = mes.split('-')
                qs = qs.filter(data__year=ano, data__month=m)
            except ValueError:
                pass
        return qs.order_by('-data')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx['total_receitas'] = qs.filter(tipo='entrada').aggregate(t=Sum('valor'))['t'] or 0
        ctx['total_despesas'] = qs.filter(tipo='saida').aggregate(t=Sum('valor'))['t'] or 0
        ctx['tipo_filtro'] = self.request.GET.get('tipo', '')
        ctx['mes_filtro'] = self.request.GET.get('mes', '')
        ctx['tipo_choices'] = MovimentacaoFinanceira.TipoChoices.choices
        return ctx


class MovimentacaoFinanceiraCreateView(EmpresaScopedMixin, CreateView):
    """
    Lançamento manual para a empresa logada.
    """
    model = MovimentacaoFinanceira
    form_class = MovimentacaoFinanceiraForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Lançamento financeiro registrado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Lançamento'
        return ctx


class MovimentacaoFinanceiraUpdateView(EmpresaScopedMixin, UpdateView):
    """
    Edição de lançamento da empresa.
    """
    model = MovimentacaoFinanceira
    form_class = MovimentacaoFinanceiraForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Lançamento atualizado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar Lançamento: {self.object.descricao}'
        return ctx


class MovimentacaoFinanceiraDeleteView(EmpresaScopedMixin, DeleteView):
    """
    Exclusão de lançamento da empresa.
    """
    model = MovimentacaoFinanceira
    template_name = 'financeiro/lancamento_confirm_delete.html'
    success_url = reverse_lazy('financeiro:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Lançamento financeiro excluído com sucesso!')
        return super().form_valid(form)


class RelatorioView(LoginRequiredMixin, View):
    """
    Relatório Financeiro filtrado pela empresa.
    """
    template_name = 'financeiro/relatorio.html'

    def get(self, request):
        form = RelatorioFiltroForm(request.GET or None)
        empresa = getattr(request, 'empresa', None)
        base_qs = MovimentacaoFinanceira.objects.filter(empresa=empresa) if empresa else MovimentacaoFinanceira.objects.all()

        lancamentos = None
        total_receitas = total_despesas = saldo = 0
        por_categoria = []

        if form.is_valid():
            qs = base_qs.filter(
                data__gte=form.cleaned_data['data_inicio'],
                data__lte=form.cleaned_data['data_fim'],
            ).select_related('pedido').order_by('data')

            tipo = form.cleaned_data.get('tipo')
            if tipo:
                qs = qs.filter(tipo=tipo)

            lancamentos = qs
            total_receitas = qs.filter(tipo='entrada').aggregate(t=Sum('valor'))['t'] or 0
            total_despesas = qs.filter(tipo='saida').aggregate(t=Sum('valor'))['t'] or 0
            saldo = total_receitas - total_despesas

            categorias = {}
            for l in qs:
                cat_nome = l.get_categoria_display()
                if cat_nome not in categorias:
                    categorias[cat_nome] = {'receitas': 0, 'despesas': 0}
                if l.tipo == 'entrada':
                    categorias[cat_nome]['receitas'] += float(l.valor)
                else:
                    categorias[cat_nome]['despesas'] += float(l.valor)
            por_categoria = [(k, v) for k, v in categorias.items()]

        return render(request, self.template_name, {
            'form': form,
            'lancamentos': lancamentos,
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'saldo': saldo,
            'por_categoria': por_categoria,
        })
