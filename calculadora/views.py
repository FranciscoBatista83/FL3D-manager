from decimal import Decimal
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import json

from . import services
from produtos.models import Produto, Categoria, VariacaoProduto


def index(request):
    """
    Renderiza a interface da Calculadora de Precificação do FL3D Manager.
    Pode receber 'produto_id' via GET para carregar os dados de uma peça já cadastrada.
    """
    produto = None
    horas_impressao = None
    dados_produto = None
    categorias = Categoria.objects.all()
    produto_id = request.GET.get('produto_id')
    if produto_id:
        try:
            produto = get_object_or_404(Produto, pk=produto_id)
            if produto.tempo_estimado:
                total_seg = produto.tempo_estimado.total_seconds()
                horas_impressao = round(total_seg / 3600, 2)

            filamentos_lista = produto.detalhes_filamentos or []
            if not filamentos_lista and produto.peso_estimado:
                filamentos_lista = [{
                    'peso_g': float(produto.peso_estimado),
                    'valor_kg': float(produto.valor_kg_filamento or 0)
                }]

            variacoes_lista = []
            for var in produto.variacoes.all():
                variacoes_lista.append({
                    'id': var.id,
                    'nome': var.nome,
                    'quantidade': var.quantidade,
                    'custo_embalagem': float(var.custo_embalagem or 0),
                    'custo_producao_total': float(var.custo_producao_total or 0),
                    'margem_lucro': float(var.margem_lucro or 0),
                    'preco_venda': float(var.preco_venda or 0),
                    'custo_taxas_marketplace': float(var.custo_taxas_marketplace or 0),
                    'lucro_liquido': float(var.lucro_liquido or 0),
                })

            dados_produto = {
                'id': produto.id,
                'nome': produto.nome or '',
                'categoria_id': produto.categoria_id or '',
                'horas_impressao': horas_impressao if horas_impressao is not None else '',
                'potencia_w': float(produto.potencia_impressora_w or 150),
                'kwh_preco': float(produto.custo_kwh_energia or 0.85),
                'custo_embalagem': float(produto.custo_embalagem or 0),
                'custo_insumos': float(produto.custo_insumos or 0),
                'custo_mao_de_obra': float(produto.custo_mao_de_obra or 0),
                'margem_alvo': float(produto.margem_lucro or 40),
                'marketplace': produto.marketplace or 'direto',
                'comissao_afiliado_percentual': float(produto.comissao_afiliado_percentual or 0),
                'filamentos': filamentos_lista,
                'variacoes': variacoes_lista,
            }
        except Exception:
            produto = None
            dados_produto = None

    context = {
        'produto': produto,
        'horas_impressao': horas_impressao,
        'categorias': categorias,
        'dados_produto_json': json.dumps(dados_produto) if dados_produto else 'null',
    }
    return render(request, 'calculadora/index.html', context)


@require_http_methods(["POST"])
def calcular_api(request):
    """
    Endpoint AJAX/API para processamento de cálculos no servidor.
    """
    try:
        data = json.loads(request.body)
        
        filamentos = data.get('filamentos', [])
        horas_impressao = Decimal(str(data.get('horas_impressao', 0) or 0))
        potencia_w = Decimal(str(data.get('potencia_w', 0) or 0))
        kwh_preco = Decimal(str(data.get('kwh_preco', 0) or 0))
        
        custo_embalagem = Decimal(str(data.get('custo_embalagem', 0) or 0))
        custo_insumos = Decimal(str(data.get('custo_insumos', 0) or 0))
        custo_mao_de_obra = Decimal(str(data.get('custo_mao_de_obra', 0) or 0))
        
        margem_alvo = Decimal(str(data.get('margem_alvo', 0) or 0))
        marketplace = str(data.get('marketplace', 'direto'))
        afiliado_percentual = Decimal(str(data.get('afiliado_percentual', 0) or 0))
        preco_venda_manual = Decimal(str(data.get('preco_venda_manual', 0) or 0))

        # 1. Custo de Produção
        producao = services.calcular_custo_producao(
            filamentos=filamentos,
            horas_impressao=horas_impressao,
            potencia_w=potencia_w,
            kwh_preco=kwh_preco,
            custo_embalagem=custo_embalagem,
            custo_insumos=custo_insumos,
            custo_mao_de_obra=custo_mao_de_obra,
        )

        # 2. Determina o preço de venda (sugerido ou informado)
        if preco_venda_manual > Decimal("0.00"):
            preco_venda = preco_venda_manual
        else:
            preco_venda = services.calcular_preco_sugerido(
                custo_producao=producao["total"],
                margem_alvo=margem_alvo,
                marketplace=marketplace,
                afiliado_percentual=afiliado_percentual,
            )

        # 3. Comissão e Taxas conforme o Marketplace
        if marketplace == "shopee":
            comissao_info = services.calcular_comissao_shopee(preco_venda, afiliado_percentual)
            taxas_total = comissao_info["total"]
        elif marketplace == "tiktok":
            comissao_info = services.calcular_comissao_tiktok(preco_venda, Decimal("0"), afiliado_percentual)
            taxas_total = comissao_info["total"]
        else:
            comissao_info = {"total": Decimal("0.00"), "percentual": Decimal("0.00")}
            taxas_total = Decimal("0.00")

        # 4. Lucro Líquido e Margem Real
        lucro_liquido = services.quantize(preco_venda - producao["total"] - taxas_total)
        margem_real = services.quantize((lucro_liquido / preco_venda * Decimal("100"))) if preco_venda > 0 else Decimal("0.00")

        return JsonResponse({
            'sucesso': True,
            'custo_producao': {
                'filamento': str(producao['filamento']),
                'energia': str(producao['energia']),
                'embalagem': str(producao['embalagem']),
                'insumos': str(producao['insumos']),
                'mao_de_obra': str(producao['mao_de_obra']),
                'total': str(producao['total']),
            },
            'taxas_marketplace': {
                'total': str(taxas_total),
                'detalhe': {k: str(v) for k, v in comissao_info.items()}
            },
            'preco_venda': str(preco_venda),
            'lucro_liquido': str(lucro_liquido),
            'margem_real': str(margem_real),
        })

    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)


@require_http_methods(["POST"])
def salvar_produto_api(request):
    """
    Endpoint AJAX para salvar a peça orçada:
    - Se informado 'produto_id', atualiza o produto existente.
    - Caso contrário, cria um novo Produto no catálogo.
    """
    try:
        data = json.loads(request.body)
        
        nome = str(data.get('nome', '')).strip()
        if not nome:
            return JsonResponse({'sucesso': False, 'erro': 'Por favor, informe o Nome do Produto.'}, status=400)

        produto_id = data.get('produto_id')
        categoria_id = data.get('categoria_id')
        categoria = Categoria.objects.filter(pk=categoria_id).first() if categoria_id else None

        peso_g = Decimal(str(data.get('peso_g', 0) or 0))
        horas_impressao = float(data.get('horas_impressao', 0) or 0)
        custo_total = Decimal(str(data.get('custo_total', 0) or 0))
        preco_venda = Decimal(str(data.get('preco_venda', 0) or 0))
        margem_lucro = Decimal(str(data.get('margem_lucro', 0) or 0))
        marketplace = str(data.get('marketplace', 'direto'))
        afiliado_percentual = Decimal(str(data.get('afiliado_percentual', 0) or 0))
        detalhes_filamentos = data.get('detalhes_filamentos', [])

        potencia_w = Decimal(str(data.get('potencia_w', 150) or 150))
        kwh_preco = Decimal(str(data.get('kwh_preco', 0.85) or 0.85))
        custo_embalagem = Decimal(str(data.get('custo_embalagem', 0) or 0))
        custo_insumos = Decimal(str(data.get('custo_insumos', 0) or 0))
        custo_mao_de_obra = Decimal(str(data.get('custo_mao_de_obra', 0) or 0))
        custo_taxas_marketplace = Decimal(str(data.get('custo_taxas_marketplace', 0) or 0))
        variacoes_data = data.get('variacoes', [])

        # Converte horas float em DurationField (timedelta)
        tempo_estimado = timedelta(hours=horas_impressao) if horas_impressao > 0 else None

        if produto_id:
            produto = get_object_or_404(Produto, pk=produto_id)
            produto.nome = nome
            produto.categoria = categoria
            produto.peso_estimado = peso_g
            produto.tempo_estimado = tempo_estimado
            produto.detalhes_filamentos = detalhes_filamentos
            produto.potencia_impressora_w = potencia_w
            produto.custo_kwh_energia = kwh_preco
            produto.custo_embalagem = custo_embalagem
            produto.custo_insumos = custo_insumos
            produto.custo_mao_de_obra = custo_mao_de_obra
            produto.marketplace = marketplace
            produto.comissao_afiliado_percentual = afiliado_percentual
            produto.custo_taxas_marketplace = custo_taxas_marketplace
            produto.custo_estimado = custo_total
            produto.preco_venda = preco_venda
            produto.margem_lucro = margem_lucro
            produto.save()

            # Sincroniza variações/pacotes do produto
            produto.variacoes.all().delete()
            for v in variacoes_data:
                VariacaoProduto.objects.create(
                    produto=produto,
                    nome=v.get('nome') or f"Pacote com {v.get('quantidade', 1)} un",
                    quantidade=int(v.get('quantidade', 1) or 1),
                    sku_sufixo=v.get('sku_sufixo', ''),
                    custo_embalagem=Decimal(str(v.get('custo_embalagem', 0) or 0)),
                    custo_producao_total=Decimal(str(v.get('custo_producao_total', 0) or 0)),
                    margem_lucro=Decimal(str(v.get('margem_lucro', 0) or 0)),
                    preco_venda=Decimal(str(v.get('preco_venda', 0) or 0)),
                    custo_taxas_marketplace=Decimal(str(v.get('custo_taxas_marketplace', 0) or 0)),
                    lucro_liquido=Decimal(str(v.get('lucro_liquido', 0) or 0)),
                )

            return JsonResponse({
                'sucesso': True,
                'mensagem': f'Produto "{produto.nome}" atualizado com sucesso!',
                'produto_id': produto.id,
                'redirect_url': reverse('produtos:detalhe', kwargs={'pk': produto.id})
            })
        else:
            # Cria o Produto no Banco de Dados
            produto = Produto.objects.create(
                nome=nome,
                categoria=categoria,
                peso_estimado=peso_g,
                tempo_estimado=tempo_estimado,
                detalhes_filamentos=detalhes_filamentos,
                potencia_impressora_w=potencia_w,
                custo_kwh_energia=kwh_preco,
                custo_embalagem=custo_embalagem,
                custo_insumos=custo_insumos,
                custo_mao_de_obra=custo_mao_de_obra,
                marketplace=marketplace,
                comissao_afiliado_percentual=afiliado_percentual,
                custo_taxas_marketplace=custo_taxas_marketplace,
                custo_estimado=custo_total,
                preco_venda=preco_venda,
                margem_lucro=margem_lucro,
                ativo=True
            )

            # Salva as variações/pacotes criadas
            for v in variacoes_data:
                VariacaoProduto.objects.create(
                    produto=produto,
                    nome=v.get('nome') or f"Pacote com {v.get('quantidade', 1)} un",
                    quantidade=int(v.get('quantidade', 1) or 1),
                    sku_sufixo=v.get('sku_sufixo', ''),
                    custo_embalagem=Decimal(str(v.get('custo_embalagem', 0) or 0)),
                    custo_producao_total=Decimal(str(v.get('custo_producao_total', 0) or 0)),
                    margem_lucro=Decimal(str(v.get('margem_lucro', 0) or 0)),
                    preco_venda=Decimal(str(v.get('preco_venda', 0) or 0)),
                    custo_taxas_marketplace=Decimal(str(v.get('custo_taxas_marketplace', 0) or 0)),
                    lucro_liquido=Decimal(str(v.get('lucro_liquido', 0) or 0)),
                )

            return JsonResponse({
                'sucesso': True,
                'mensagem': f'Produto "{produto.nome}" salvo no catálogo com sucesso!',
                'produto_id': produto.id,
                'redirect_url': reverse('produtos:detalhe', kwargs={'pk': produto.id})
            })

    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)
