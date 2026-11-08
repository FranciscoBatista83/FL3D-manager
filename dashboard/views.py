"""
=============================================================================
FL3D Manager - Visualização do Painel Principal (views.py)
=============================================================================
Dashboard com suporte Multi-Empresa.
=============================================================================
"""

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Sum

from pedidos.models import Pedido
from financeiro.models import MovimentacaoFinanceira
from producao.models import Producao
from estoque.models import Filamento


class DashboardPrincipalView(LoginRequiredMixin, View):
    """
    Painel de Controle Principal filtrado pela empresa do usuário.
    """
    template_name = 'dashboard/dashboard.html'

    def get(self, request):
        empresa = getattr(request, 'empresa', None)
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)

        # Filtros por empresa
        pedidos_qs = Pedido.objects.filter(empresa=empresa) if empresa else Pedido.objects.all()
        finan_qs = MovimentacaoFinanceira.objects.filter(empresa=empresa) if empresa else MovimentacaoFinanceira.objects.all()
        filamentos_qs = Filamento.objects.filter(empresa=empresa) if empresa else Filamento.objects.all()
        
        # Produções ligadas a pedidos da empresa
        if empresa:
            producao_qs = Producao.objects.filter(pedido__empresa=empresa)
        else:
            producao_qs = Producao.objects.all()

        pedidos_mes = pedidos_qs.filter(
            data_pedido__gte=inicio_mes,
            data_pedido__lte=hoje
        ).count()

        receita_mes = finan_qs.filter(
            tipo=MovimentacaoFinanceira.TipoChoices.ENTRADA,
            data__gte=inicio_mes,
            data__lte=hoje
        ).aggregate(total=Sum('valor'))['total'] or 0

        em_producao = producao_qs.filter(
            status=Producao.StatusChoices.IMPRIMINDO
        ).count()

        estoque_baixo = []
        for f in filamentos_qs:
            peso_ini = f.peso_inicial or 0
            peso_at = f.peso_atual or 0
            if peso_ini > 0 and (peso_at / peso_ini) <= 0.2:
                estoque_baixo.append(f)
        estoque_baixo_count = len(estoque_baixo)

        pedidos_recentes = pedidos_qs.order_by('-data_pedido')[:5]

        producao_andamento = producao_qs.filter(
            status=Producao.StatusChoices.IMPRIMINDO
        ).order_by('data_inicio')

        return render(request, self.template_name, {
            'pedidos_mes': pedidos_mes,
            'receita_mes': receita_mes,
            'em_producao': em_producao,
            'estoque_baixo_count': estoque_baixo_count,
            'estoque_baixo': estoque_baixo,
            'pedidos_recentes': pedidos_recentes,
            'producao_andamento': producao_andamento,
        })
