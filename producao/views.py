"""
=============================================================================
FL3D Manager - Visualizações do Módulo de Produção (views.py)
=============================================================================
VISÃO GERAL E CONCEITO:
Este é o cérebro operacional da fábrica 3D. Ele integra Pedidos, Impressoras e Estoque:
  1. AUTOMAÇÃO DE IMPRESSORAS: Quando uma ordem de produção entra no status 'IMPRIMINDO',
     o sistema muda automaticamente o status da máquina correspondente para 'IMPRIMINDO'.
     Quando a produção acaba ou falha, a máquina volta a ficar 'DISPONÍVEL' na hora!
  2. BAIXA AUTOMÁTICA DE FILAMENTO: Quando uma impressão termina com SUCESSO, o peso
     gasto é debitado do carretel de filamento como 'CONSUMO'.
  3. REGISTRO AUTOMÁTICO DE FALHAS: Se a impressão deu FALHA, o sistema cria
     automaticamente uma linha na tabela de Perdas e debita o plástico do estoque
     como 'PERDA'.
  4. CONTROLE MANUAL DE PERDAS: Permite apontar sobras, purgas de troca de cor
     ou testes de fatiamento.
=============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q

from .models import Producao, RegistroImpressao, Perda
from .forms import ProducaoForm, RegistroImpressaoForm, PerdaForm
from estoque.models import Filamento, MovimentacaoEstoque
from impressoras.models import Impressora


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES DE REGRAS DE NEGÓCIO AUTOMATIZADAS
# ─────────────────────────────────────────────────────────────────────────────

def _atualizar_status_impressora(impressora, status_producao):
    """
    REGRA DE NEGÓCIO: Sincroniza a situação da máquina com a ordem de serviço.
    
    - Se a produção está 'IMPRIMINDO', a impressora fica com status 'IMPRIMINDO'.
    - Se a produção foi 'CONCLUÍDA', 'FALHOU' ou 'CANCELADA', a impressora
      fica com status 'DISPONÍVEL', pronta para o próximo trabalho.
    """
    if impressora is None:
        return
    if status_producao == Producao.StatusChoices.IMPRIMINDO:
        impressora.status = Impressora.StatusChoices.IMPRIMINDO
    elif status_producao in (
        Producao.StatusChoices.CONCLUIDO,
        Producao.StatusChoices.FALHOU,
        Producao.StatusChoices.CANCELADO,
    ):
        impressora.status = Impressora.StatusChoices.DISPONIVEL
    impressora.save()


def _registrar_movimentacao_estoque(filamento, tipo, quantidade, motivo, usuario):
    """
    REGRA DE NEGÓCIO: Movimenta o estoque de filamento com auditoria completa.
    
    - Subtrai as gramas gastas do carretel físico (`peso_atual`).
    - Grava o registro imutável em `MovimentacaoEstoque` com data, motivo e quem operou.
    """
    anterior = filamento.peso_atual
    
    # Consumos e Perdas diminuem o peso do carretel; Entradas aumentam
    if tipo in (MovimentacaoEstoque.TipoChoices.CONSUMO, MovimentacaoEstoque.TipoChoices.PERDA):
        novo_peso = anterior - quantidade
    else:
        novo_peso = anterior + quantidade

    # Cria o extrato oficial de movimentação
    MovimentacaoEstoque.objects.create(
        filamento=filamento,
        tipo=tipo,
        quantidade=-quantidade if tipo in (
            MovimentacaoEstoque.TipoChoices.CONSUMO,
            MovimentacaoEstoque.TipoChoices.PERDA,
        ) else quantidade,
        quantidade_anterior=anterior,
        quantidade_nova=novo_peso,
        motivo=motivo,
        usuario=usuario,
    )
    
    # Atualiza o saldo do filamento no banco de dados
    filamento.peso_atual = novo_peso
    filamento.save()


# ─────────────────────────────────────────────────────────────────────────────
# TELAS E VISUALIZAÇÕES DE ORDENS DE PRODUÇÃO
# ─────────────────────────────────────────────────────────────────────────────

class ProducaoListView(LoginRequiredMixin, ListView):
    """
    Painel geral de ordens de produção.
    Permite filtrar por status (Aguardando, Imprimindo, Concluído) e buscar por número do pedido ou nome da peça.
    """
    model = Producao
    template_name = 'producao/producao_list.html'
    context_object_name = 'producoes'
    paginate_by = 15

    def get_queryset(self):
        # Carrega dados relacionados em uma única consulta otimizada (select_related)
        qs = super().get_queryset().select_related('pedido', 'produto', 'impressora', 'filamento')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        busca = self.request.GET.get('q')
        if busca:
            qs = qs.filter(
                Q(pedido__numero__icontains=busca) |
                Q(produto__nome__icontains=busca)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Producao.StatusChoices.choices
        ctx['status_filtro'] = self.request.GET.get('status', '')
        return ctx


class ProducaoCreateView(LoginRequiredMixin, CreateView):
    """
    Criação de uma nova Ordem de Produção para impressão 3D.
    """
    model = Producao
    form_class = ProducaoForm
    template_name = 'producao/producao_form.html'
    success_url = reverse_lazy('producao:lista')

    def form_valid(self, form):
        producao = form.save()
        # Atualiza a impressora se a ordem já for iniciada imediatamente como 'Imprimindo'
        _atualizar_status_impressora(producao.impressora, producao.status)
        messages.success(self.request, 'Ordem de produção criada com sucesso!')
        return redirect('producao:detalhe', pk=producao.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nova Ordem de Produção'
        return ctx


class ProducaoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Edição de uma ordem de produção existente (ex: mudar status ou trocar impressora).
    """
    model = Producao
    form_class = ProducaoForm
    template_name = 'producao/producao_form.html'

    def form_valid(self, form):
        producao = form.save()
        # Sincroniza o status da máquina correspondente
        _atualizar_status_impressora(producao.impressora, producao.status)
        messages.success(self.request, 'Produção atualizada com sucesso!')
        return redirect('producao:detalhe', pk=producao.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar Produção #{self.object.pk}'
        return ctx


class ProducaoDetailView(LoginRequiredMixin, DetailView):
    """
    Ficha completa da ordem de produção com histórico de impressões e apontamentos.
    """
    model = Producao
    template_name = 'producao/producao_detail.html'
    context_object_name = 'producao'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['impressoes'] = self.object.impressoes.all().order_by('-data')
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
# APONTAMENTO DE FINALIZAÇÃO DA IMPRESSÃO (SUCESSO OU FALHA)
# ─────────────────────────────────────────────────────────────────────────────

class RegistroImpressaoCreateView(LoginRequiredMixin, View):
    """
    Tela onde o operador registra o término físico do trabalho da impressora 3D.
    """
    template_name = 'producao/registro_impressao_form.html'

    def get(self, request, producao_pk=None):
        """
        Ao abrir o formulário, pré-preenche os campos com os dados previstos da Ordem de Produção
        para agilizar a digitação pelo operador da máquina.
        """
        initial = {}
        producao = None
        if producao_pk:
            producao = get_object_or_404(Producao, pk=producao_pk)
            initial = {
                'producao': producao,
                'pedido': producao.pedido,
                'produto': producao.produto,
                'impressora': producao.impressora,
                'filamento': producao.filamento,
                'peso_utilizado': producao.peso_previsto,
                'tempo_impressao': producao.tempo_previsto,
            }
        form = RegistroImpressaoForm(initial=initial)
        return render(request, self.template_name, {'form': form, 'producao': producao})

    def post(self, request, producao_pk=None):
        """
        Processa o resultado do trabalho:
        - Se SUCESSO: registra 'CONSUMO' no estoque e diminui o peso da bobina.
        - Se FALHA: cria registro em 'Perda' e lança saída no estoque como 'PERDA'.
        """
        producao = get_object_or_404(Producao, pk=producao_pk) if producao_pk else None
        form = RegistroImpressaoForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.save()

            filamento = registro.filamento
            peso = registro.peso_utilizado
            usuario = request.user

            if registro.resultado == RegistroImpressao.ResultadoChoices.SUCESSO:
                # 1. Dá baixa por consumo normal de produção
                _registrar_movimentacao_estoque(
                    filamento,
                    MovimentacaoEstoque.TipoChoices.CONSUMO,
                    peso,
                    f'Consumo da impressão #{registro.pk} — Produção #{registro.producao.pk}',
                    usuario,
                )
                messages.success(request, f'Impressão registrada com sucesso! {peso}g consumidos do estoque de filamento.')

            elif registro.resultado == RegistroImpressao.ResultadoChoices.FALHA:
                # 2. Cria registro na tabela de Perdas
                Perda.objects.create(
                    pedido=registro.pedido,
                    produto=registro.produto,
                    filamento=filamento,
                    quantidade=peso,
                    motivo=Perda.MotivoChoices.FALHA_IMPRESSAO,
                    observacao=f'Perda automática gerada pela impressão #{registro.pk} com resultado: Falha.',
                )
                # 3. Dá baixa no estoque classificada como PERDA
                _registrar_movimentacao_estoque(
                    filamento,
                    MovimentacaoEstoque.TipoChoices.PERDA,
                    peso,
                    f'Perda da impressão #{registro.pk} — Produção #{registro.producao.pk}',
                    usuario,
                )
                messages.warning(request, f'Impressão com falha registrada. {peso}g registrados como perda no estoque.')

            return redirect('producao:detalhe', pk=registro.producao.pk)

        return render(request, self.template_name, {'form': form, 'producao': producao})


# ─────────────────────────────────────────────────────────────────────────────
# GESTÃO DE DESPERDÍCIOS E PERDAS
# ─────────────────────────────────────────────────────────────────────────────

class PerdaListView(LoginRequiredMixin, ListView):
    """
    Lista todas as perdas e refugos registrados na oficina com paginação.
    """
    model = Perda
    template_name = 'producao/perda_list.html'
    context_object_name = 'perdas'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('pedido', 'produto', 'filamento')


class PerdaCreateView(LoginRequiredMixin, CreateView):
    """
    Lançamento manual de perda de filamento (purga de troca de cor, suportes ou testes).
    """
    model = Perda
    form_class = PerdaForm
    template_name = 'producao/perda_form.html'
    success_url = reverse_lazy('producao:perdas')

    def form_valid(self, form):
        perda = form.save()
        # Dá baixa no estoque de filamento automaticamente
        _registrar_movimentacao_estoque(
            perda.filamento,
            MovimentacaoEstoque.TipoChoices.PERDA,
            perda.quantidade,
            f'Perda manual — Motivo: {perda.get_motivo_display()}. {perda.observacao or ""}',
            self.request.user,
        )
        messages.success(self.request, f'Perda de {perda.quantidade}g registrada e estoque atualizado!')
        return redirect(self.success_url)
