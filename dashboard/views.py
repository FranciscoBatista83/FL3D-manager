"""
=============================================================================
FL3D Manager - Visualização do Painel Principal (views.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo é o cérebro por trás da tela inicial que você vê assim que entra
no sistema. Ele vai até os outros departamentos (Vendas, Estoque, Chão de Fábrica,
Caixa) e resume as informações mais importantes em cartões coloridos e listas:

1. Quantos pedidos foram feitos este mês.
2. Quanto dinheiro entrou no caixa da oficina este mês (Faturamento).
3. Quantas impressoras 3D estão rodando agora mesmo.
4. Quais carretéis de filamento estão acabando (menos de 20% do peso inicial).
5. Quais são os últimos 5 pedidos cadastrados.
6. Quais peças estão atualmente em processo de impressão nas máquinas.
=============================================================================
"""

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Sum, F

# Importamos os modelos dos outros módulos para buscar as informações em tempo real
from pedidos.models import Pedido
from financeiro.models import MovimentacaoFinanceira
from producao.models import Producao
from estoque.models import Filamento


class DashboardPrincipalView(LoginRequiredMixin, View):
    """
    View baseada em classe que monta o Painel de Controle Principal (Dashboard).
    
    O 'LoginRequiredMixin' garante que apenas pessoas logadas com usuário e senha
    consigam visualizar estes dados estratégicos da empresa.
    """
    # Indica qual arquivo HTML desenha a tela bonita na frente do usuário
    template_name = 'dashboard/dashboard.html'

    def get(self, request):
        """
        Método executado automaticamente quando o usuário acessa a página inicial (via GET).
        Aqui fazemos as contas e coletamos as estatísticas do mês atual.
        """
        # 1. Pega o dia de hoje e calcula o primeiro dia do mês corrente (ex: 01/09/2026)
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)

        # 2. Total de Pedidos do Mês:
        # Conta quantos pedidos foram realizados desde o dia 1 até a data de hoje.
        pedidos_mes = Pedido.objects.filter(
            data_pedido__gte=inicio_mes,
            data_pedido__lte=hoje
        ).count()

        # 3. Faturamento/Receita do Mês:
        # Busca todas as movimentações financeiras marcadas como "ENTRADA" (dinheiro recebido)
        # ocorridas neste mês e soma todos os valores monetários. Se não houver nada, retorna 0.
        receita_mes = MovimentacaoFinanceira.objects.filter(
            tipo=MovimentacaoFinanceira.TipoChoices.ENTRADA,
            data__gte=inicio_mes,
            data__lte=hoje
        ).aggregate(total=Sum('valor'))['total'] or 0

        # 4. Impressões Ativas:
        # Conta quantas ordens de produção estão com o status 'IMPRIMINDO' neste exato minuto.
        em_producao = Producao.objects.filter(
            status=Producao.StatusChoices.IMPRIMINDO
        ).count()

        # 5. Alerta de Estoque Baixo de Filamento:
        # Percorre todos os carretéis de filamento cadastrados no estoque.
        # Se um carretel tiver menos de 20% do seu peso inicial restante (ex: menos de 200g em um rolo de 1kg),
        # ele é adicionado na lista de alerta para que o operador saiba que precisa comprar mais filamento!
        estoque_baixo = []
        for f in Filamento.objects.all():
            if f.peso_inicial > 0 and (f.peso_atual / f.peso_inicial) <= 0.2:
                estoque_baixo.append(f)
        estoque_baixo_count = len(estoque_baixo)

        # 6. Últimos 5 Pedidos:
        # Pega os 5 pedidos mais recentes cadastrados no sistema para exibir em uma tabela rápida.
        pedidos_recentes = Pedido.objects.all().order_by('-data_pedido')[:5]

        # 7. Peças Sendo Impressas Agora:
        # Lista as produções em andamento por ordem de data e hora de início.
        producao_andamento = Producao.objects.filter(
            status=Producao.StatusChoices.IMPRIMINDO
        ).order_by('data_inicio')

        # 8. Empacota todas essas informações calculadas e envia para a página HTML exibir
        return render(request, self.template_name, {
            'pedidos_mes': pedidos_mes,
            'receita_mes': receita_mes,
            'em_producao': em_producao,
            'estoque_baixo_count': estoque_baixo_count,
            'estoque_baixo': estoque_baixo,
            'pedidos_recentes': pedidos_recentes,
            'producao_andamento': producao_andamento,
        })

