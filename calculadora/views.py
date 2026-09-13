from decimal import Decimal
from datetime import timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from . import services
from produtos.models import Produto


def index(request):
    """
    Renderiza a interface da Calculadora de Precificação do FL3D Manager.
    """
    return render(request, 'calculadora/index.html')


@require_http_methods(["POST"])
def calcular_api(request):
    """
    Endpoint AJAX/API para processamento de cálculos no servidor.
    """
    try:
        data = json.loads(request.body)
        
        peso_g = Decimal(str(data.get('peso_g', 0) or 0))
        valor_kg_filamento = Decimal(str(data.get('valor_kg_filamento', 0) or 0))
        horas_impressao = Decimal(str(data.get('horas_impressao', 0) or 0))
        potencia_w = Decimal(str(data.get('potencia_w', 0) or 0))
        kwh_preco = Decimal(str(data.get('kwh_preco', 0) or 0))
        
        custo_embalagem = Decimal(str(data.get('custo_embalagem', 0) or 0))
        custo_insumos = Decimal(str(data.get('custo_insumos', 0) or 0))
        custo_mao_de_obra = Decimal(str(data.get('custo_mao_de_obra', 0) or 0))
        
        margem_alvo = Decimal(str(data.get('margem_alvo', 0) or 0))
        marketplace = str(data.get('marketplace', 'direto'))
        tipo_vendedor = str(data.get('tipo_vendedor', 'cnpj'))
        cpf_acima_450 = bool(data.get('cpf_acima_450', False))
        afiliado_percentual = Decimal(str(data.get('afiliado_percentual', 0) or 0))
        preco_venda_manual = Decimal(str(data.get('preco_venda_manual', 0) or 0))

        # 1. Custo de Produção
        producao = services.calcular_custo_producao(
            peso_g=peso_g,
            valor_kg_filamento=valor_kg_filamento,
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
                tipo_vendedor=tipo_vendedor,
                cpf_acima_450=cpf_acima_450,
                afiliado_percentual=afiliado_percentual,
            )

        # 3. Comissão e Taxas conforme o Marketplace
        if marketplace == "shopee":
            comissao_info = services.calcular_comissao_shopee(preco_venda, tipo_vendedor, cpf_acima_450)
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
    Endpoint AJAX para salvar a peça orçada como um novo Produto no catálogo.
    """
    try:
        data = json.loads(request.body)
        
        nome = str(data.get('nome', '')).strip()
        if not nome:
            return JsonResponse({'sucesso': False, 'erro': 'Por favor, informe o Nome do Produto.'}, status=400)

        peso_g = Decimal(str(data.get('peso_g', 0) or 0))
        horas_impressao = float(data.get('horas_impressao', 0) or 0)
        custo_total = Decimal(str(data.get('custo_total', 0) or 0))
        preco_venda = Decimal(str(data.get('preco_venda', 0) or 0))
        margem_lucro = Decimal(str(data.get('margem_lucro', 0) or 0))

        # Converte horas float em DurationField (timedelta)
        tempo_estimado = timedelta(hours=horas_impressao) if horas_impressao > 0 else None

        # Cria o Produto no Banco de Dados
        produto = Produto.objects.create(
            nome=nome,
            peso_estimado=peso_g,
            tempo_estimado=tempo_estimado,
            custo_estimado=custo_total,
            preco_venda=preco_venda,
            margem_lucro=margem_lucro,
            ativo=True
        )

        return JsonResponse({
            'sucesso': True,
            'mensagem': f'Produto "{produto.nome}" salvo no catálogo com sucesso!',
            'produto_id': produto.id
        })

    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)
