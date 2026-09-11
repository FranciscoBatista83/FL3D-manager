"""
=============================================================================
FL3D Manager - Visualizações do Módulo Financeiro (views.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo cuida de toda a contabilidade e inteligência financeira da oficina:
  1. DASHBOARD FINANCEIRO: calcula faturamento mensal, total de despesas e o saldo
     líquido (lucro). Além disso, prepara os dados dos últimos 6 meses em formato JSON
     para desenhar gráficos comparativos na tela (Barras de Receitas vs Despesas).
  2. LISTA DE LANÇAMENTOS: extrato completo de todas as movimentações, com filtros
     por tipo (entradas/saídas) e mês, somando o total acumulado na tela.
  3. NOVO LANÇAMENTO: registro de receitas ou despesas com categoria e pedido vinculado.
  4. RELATÓRIO ANALÍTICO DE CAIXA: tela que gera o balanço de qualquer período
     escolhido (ex: últimos 3 meses) agrupando as despesas por categoria
     (quanto foi gasto em filamento, quanto em energia, quanto em fretes).
=============================================================================
"""

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from .models import MovimentacaoFinanceira
from .forms import MovimentacaoFinanceiraForm, RelatorioFiltroForm


class DashboardFinanceiroView(LoginRequiredMixin, View):
    """
    Painel Financeiro com indicadores do mês corrente e gráfico dos últimos 6 meses.
    """
    template_name = 'financeiro/financeiro_dashboard.html'

    def get(self, request):
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)

        # 1. Total de Receitas do Mês Atual (Entradas)
        receitas_mes = MovimentacaoFinanceira.objects.filter(
            tipo=MovimentacaoFinanceira.TipoChoices.ENTRADA,
            data__gte=inicio_mes,
            data__lte=hoje,
        ).aggregate(total=Sum('valor'))['total'] or 0

        # 2. Total de Despesas do Mês Atual (Saídas)
        despesas_mes = MovimentacaoFinanceira.objects.filter(
            tipo=MovimentacaoFinanceira.TipoChoices.SAIDA,
            data__gte=inicio_mes,
            data__lte=hoje,
        ).aggregate(total=Sum('valor'))['total'] or 0

        # 3. Lucro Líquido do Mês = Receitas - Despesas
        saldo_mes = receitas_mes - despesas_mes

        # 4. Histórico dos Últimos 6 Meses para o Gráfico Visual (Chart.js)
        labels, dados_receitas, dados_despesas = [], [], []
        for i in range(5, -1, -1):
            ref = hoje - relativedelta(months=i)
            inicio = ref.replace(day=1)
            if i > 0:
                fim = (inicio + relativedelta(months=1)) - timedelta(days=1)
            else:
                fim = hoje

            # Receitas daquele mês específico
            r = MovimentacaoFinanceira.objects.filter(
                tipo=MovimentacaoFinanceira.TipoChoices.ENTRADA,
                data__gte=inicio,
                data__lte=fim,
            ).aggregate(total=Sum('valor'))['total'] or 0

            # Despesas daquele mês específico
            d = MovimentacaoFinanceira.objects.filter(
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


class MovimentacaoFinanceiraListView(LoginRequiredMixin, ListView):
    """
    Extrato de Lançamentos Financeiros com filtros por tipo e mês, além de somatório automático.
    """
    model = MovimentacaoFinanceira
    template_name = 'financeiro/lancamento_list.html'
    context_object_name = 'lancamentos'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('pedido')
        tipo = self.request.GET.get('tipo')
        mes = self.request.GET.get('mes')
        
        # Filtra por tipo (Entrada ou Saída)
        if tipo:
            qs = qs.filter(tipo=tipo)
        
        # Filtra por Ano-Mês selecionado no cabeçalho (ex: '2026-09')
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
        # Calcula as somas totais com base nos filtros ativos
        ctx['total_receitas'] = qs.filter(tipo='entrada').aggregate(t=Sum('valor'))['t'] or 0
        ctx['total_despesas'] = qs.filter(tipo='saida').aggregate(t=Sum('valor'))['t'] or 0
        ctx['tipo_filtro'] = self.request.GET.get('tipo', '')
        ctx['mes_filtro'] = self.request.GET.get('mes', '')
        ctx['tipo_choices'] = MovimentacaoFinanceira.TipoChoices.choices
        return ctx


class MovimentacaoFinanceiraCreateView(LoginRequiredMixin, CreateView):
    """
    Tela para lançamento manual de uma nova entrada ou saída de caixa.
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


class MovimentacaoFinanceiraUpdateView(LoginRequiredMixin, UpdateView):
    """
    Tela para retificação ou edição de um lançamento financeiro já existente.
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


class MovimentacaoFinanceiraDeleteView(LoginRequiredMixin, DeleteView):
    """
    Exclusão de um lançamento financeiro indevido ou incorreto.
    """
    model = MovimentacaoFinanceira
    template_name = 'financeiro/lancamento_confirm_delete.html'
    success_url = reverse_lazy('financeiro:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Lançamento financeiro excluído com sucesso!')
        return super().form_valid(form)


class RelatorioView(LoginRequiredMixin, View):
    """
    Relatório Financeiro por Período Personalizado com Demonstração por Categorias.
    """
    template_name = 'financeiro/relatorio.html'

    def get(self, request):
        form = RelatorioFiltroForm(request.GET or None)
        lancamentos = None
        total_receitas = total_despesas = saldo = 0
        por_categoria = []

        if form.is_valid():
            # 1. Filtra as movimentações dentro da janela de datas
            qs = MovimentacaoFinanceira.objects.filter(
                data__gte=form.cleaned_data['data_inicio'],
                data__lte=form.cleaned_data['data_fim'],
            ).select_related('pedido').order_by('data')

            tipo = form.cleaned_data.get('tipo')
            if tipo:
                qs = qs.filter(tipo=tipo)

            lancamentos = qs
            
            # 2. Totalizadores do período selecionado
            total_receitas = qs.filter(tipo='entrada').aggregate(t=Sum('valor'))['t'] or 0
            total_despesas = qs.filter(tipo='saida').aggregate(t=Sum('valor'))['t'] or 0
            saldo = total_receitas - total_despesas

            # 3. Agrupamento por Categoria (Filamento, Energia, Embalagens, Vendas)
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
