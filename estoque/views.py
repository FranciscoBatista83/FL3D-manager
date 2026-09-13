"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Estoque (views.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este arquivo comanda toda a lógica de estoque de filamentos da oficina:
  1. LISTAGEM DE FILAMENTOS: tabela com todos os carretéis, com barra de pesquisa
     que permite filtrar por Marca, Material (PLA, PETG) ou Cor.
  2. NOVO FILAMENTO: grava o carretel, iguala o peso_atual ao peso_inicial e
     gera automaticamente a primeira Movimentação de Estoque do tipo 'ENTRADA'.
  3. EDIÇÃO DE FILAMENTO: altera fornecedor ou localização, mas blindando o
     'peso_atual' para que ninguém trapaceie a contabilidade de peso.
  4. DETALHE DO FILAMENTO: exibe a barra de progresso visual com a porcentagem
     restante do rolo (ex: 78.4%) e o histórico completo de movimentações.
  5. AJUSTE DE ESTOQUE: calcula a diferença entre a balança física e o sistema,
     atualiza o saldo e grava a justificativa com o nome do operador.
=============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Filamento, MovimentacaoEstoque
from .forms import FilamentoForm, AjusteEstoqueForm


class FilamentoListView(LoginRequiredMixin, ListView):
    """
    Tela principal do estoque de filamentos.
    Lista todas as bobinas com paginação e busca por texto.
    """
    model = Filamento
    template_name = 'estoque/filamento_list.html'
    context_object_name = 'filamentos'
    paginate_by = 20  # 20 bobinas por página

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


class FilamentoCreateView(LoginRequiredMixin, CreateView):
    """
    Tela de cadastro de um novo produto / item no estoque.
    """
    model = Filamento
    form_class = FilamentoForm
    template_name = 'estoque/filamento_form.html'
    success_url = reverse_lazy('estoque:lista')

    def form_valid(self, form):
        filamento = form.save(commit=False)
        # Sincroniza campos para compatibilidade
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


class FilamentoUpdateView(LoginRequiredMixin, UpdateView):
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


class FilamentoDetailView(LoginRequiredMixin, DetailView):
    """
    Ficha de detalhes de um carretel de filamento específico.
    Exibe dados, custo por grama, barra de vida do carretel e histórico de gastos.
    """
    model = Filamento
    template_name = 'estoque/filamento_detail.html'
    context_object_name = 'filamento'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Lista todo o extrato de movimentações deste rolo (das mais novas para as mais antigas)
        ctx['movimentacoes'] = self.object.movimentacoes.all().order_by('-data')
        
        # Calcula a porcentagem restante para preencher a barra de progresso visual
        if self.object.peso_inicial > 0:
            ctx['percentual_restante'] = round(
                (self.object.peso_atual / self.object.peso_inicial) * 100, 1
            )
        else:
            ctx['percentual_restante'] = 0
        return ctx


@login_required
def ajuste_estoque_view(request, pk):
    """
    Tela de Ajuste de Estoque por Pesagem na Balança Física.
    
    COMO FUNCIONA A LÓGICA:
    1. O sistema busca a bobina no banco.
    2. O operador informa o peso lido na balança física (`peso_fisico`).
    3. O sistema calcula: diferenca = peso_fisico - peso_anterior.
    4. Grava a movimentação do tipo 'AJUSTE' com a diferença e o motivo.
    5. Atualiza o saldo real da bobina no sistema.
    """
    filamento = get_object_or_404(Filamento, pk=pk)

    if request.method == 'POST':
        form = AjusteEstoqueForm(request.POST)
        if form.is_valid():
            peso_fisico = form.cleaned_data['peso_fisico']
            motivo = form.cleaned_data['motivo']
            peso_anterior = filamento.peso_atual
            
            # Diferença calculada: se peso_fisico for menor que antes, diferença é negativa (perda)
            # Se for maior (ex: rolo cadastrado errado), diferença é positiva
            diferenca = peso_fisico - peso_anterior

            # 1. Registra no histórico de movimentações com auditoria
            MovimentacaoEstoque.objects.create(
                filamento=filamento,
                tipo=MovimentacaoEstoque.TipoChoices.AJUSTE,
                quantidade=diferenca,
                quantidade_anterior=peso_anterior,
                quantidade_nova=peso_fisico,
                motivo=f'Ajuste manual. Motivo: {motivo}',
                usuario=request.user,
            )

            # 2. Atualiza o peso oficial do filamento
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
        # Quando abre a tela pela primeira vez (GET), mostra o formulário em branco
        form = AjusteEstoqueForm()

    return render(request, 'estoque/ajuste_form.html', {
        'form': form,
        'filamento': filamento,
    })

