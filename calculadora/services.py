"""
Calculadora de precificação para impressão 3D (Venda Direta, Shopee e TikTok Shop).
Portado do motor LucraAi para o FL3D Manager.
"""

from decimal import Decimal, ROUND_HALF_UP


def quantize(value: Decimal) -> Decimal:
    """Arredonda Decimal para 2 casas decimais usando ROUND_HALF_UP."""
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# =============================================================================
# REGRAS SHOPEE
# =============================================================================
def calcular_comissao_shopee(preco_venda: Decimal, tipo_vendedor: str = "cnpj", cpf_acima_450: bool = False) -> dict:
    """
    Calcula comissão Shopee:
    - Padrão: 14% (ou 20% com Frete Grátis)
    - Limite máximo de comissão por item: R$ 100,00
    - Taxa fixa por item: R$ 4,00
    - CPF com > 450 pedidos nos últimos 90 dias: +R$ 5,00 por item
    """
    preco = quantize(preco_venda)
    
    # Define percentual da comissão baseada no tipo de frete / programa
    # Aqui consideramos o programa padrão de comissão Shopee (14% com limite R$100 + R$4 taxa)
    taxa_percentual = Decimal("0.14")
    if tipo_vendedor == "frete_gratis":
        taxa_percentual = Decimal("0.20")

    comissao_percentual = quantize(preco * taxa_percentual)
    if comissao_percentual > Decimal("100.00"):
        comissao_percentual = Decimal("100.00")

    taxa_fixa = Decimal("4.00")
    adicional_cpf = Decimal("5.00") if (tipo_vendedor == "cpf" and cpf_acima_450) else Decimal("0.00")

    total = comissao_percentual + taxa_fixa + adicional_cpf

    return {
        "percentual": taxa_percentual * Decimal("100"),
        "comissao_percentual_valor": comissao_percentual,
        "taxa_fixa": taxa_fixa,
        "adicional_cpf": adicional_cpf,
        "total": quantize(total)
    }


# =============================================================================
# REGRAS TIKTOK SHOP
# =============================================================================
def calcular_comissao_tiktok(preco_venda: Decimal, desconto_vendedor: Decimal = Decimal("0"), afiliado_percentual: Decimal = Decimal("0")) -> dict:
    """
    Calcula comissão TikTok Shop:
    - Taxa de transação: 5% sobre (Preço - Desconto)
    - Taxa fixa por item: R$ 2,00
    - Comissão de Afiliado (opcional)
    """
    preco = quantize(preco_venda)
    desconto = quantize(desconto_vendedor)
    afiliado_pct = quantize(afiliado_percentual)

    preco_efetivo = max(Decimal("0.00"), preco - desconto)

    taxa_transacao = quantize(preco_efetivo * Decimal("0.05"))
    taxa_fixa = Decimal("2.00") if preco_efetivo > Decimal("0.00") else Decimal("0.00")
    comissao_afiliado = quantize(preco_efetivo * (afiliado_pct / Decimal("100")))

    total = taxa_transacao + taxa_fixa + comissao_afiliado

    return {
        "percentual": Decimal("5.00"),
        "taxa_transacao": taxa_transacao,
        "taxa_fixa": taxa_fixa,
        "comissao_afiliado": comissao_afiliado,
        "total": quantize(total)
    }


# =============================================================================
# CUSTO DE PRODUÇÃO
# =============================================================================
def calcular_custo_producao(
    peso_g: Decimal,
    valor_kg_filamento: Decimal,
    horas_impressao: Decimal,
    potencia_w: Decimal,
    kwh_preco: Decimal,
    custo_embalagem: Decimal = Decimal("0"),
    custo_insumos: Decimal = Decimal("0"),
    custo_mao_de_obra: Decimal = Decimal("0")
) -> dict:
    """Calcula os custos diretos de fabricação da peça em impressão 3D."""
    filamento = quantize((Decimal(str(peso_g)) / Decimal("1000")) * Decimal(str(valor_kg_filamento)))
    energia = quantize((Decimal(str(potencia_w)) / Decimal("1000")) * Decimal(str(horas_impressao)) * Decimal(str(kwh_preco)))
    embalagem = quantize(custo_embalagem)
    insumos = quantize(custo_insumos)
    mao_de_obra = quantize(custo_mao_de_obra)

    total = quantize(filamento + energia + embalagem + insumos + mao_de_obra)

    return {
        "filamento": filamento,
        "energia": energia,
        "embalagem": embalagem,
        "insumos": insumos,
        "mao_de_obra": mao_de_obra,
        "total": total
    }


# =============================================================================
# PRECIFICAÇÃO REVERSA / PREÇO SUGERIDO
# =============================================================================
def calcular_preco_sugerido(
    custo_producao: Decimal,
    margem_alvo: Decimal,
    marketplace: str = "direto",
    tipo_vendedor: str = "cnpj",
    cpf_acima_450: bool = False,
    afiliado_percentual: Decimal = Decimal("0")
) -> Decimal:
    """Calcula o preço sugerido de venda para atingir a margem de lucro desejada."""
    margem_alvo = max(Decimal("-99"), min(Decimal("99"), Decimal(str(margem_alvo))))
    margem_frac = margem_alvo / Decimal("100")

    if marketplace == "direto" or margem_frac >= Decimal("1"):
        if margem_frac >= Decimal("1"):
            margem_frac = Decimal("0.99")
        return quantize(custo_producao / (Decimal("1") - margem_frac))

    # Estimativa inicial para iteração
    preco = quantize(custo_producao * (Decimal("1") + margem_frac) * Decimal("1.25"))

    for _ in range(25):
        if marketplace == "shopee":
            comissao = calcular_comissao_shopee(preco, tipo_vendedor, cpf_acima_450)
            custo_taxa = comissao["total"]
        elif marketplace == "tiktok":
            comissao = calcular_comissao_tiktok(preco, Decimal("0"), afiliado_percentual)
            custo_taxa = comissao["total"]
        else:
            custo_taxa = Decimal("0")

        custos_totais = custo_producao + custo_taxa
        lucro_desejado = quantize(preco * margem_frac)
        novo_preco = quantize(custos_totais + lucro_desejado)

        if novo_preco == preco:
            break
        preco = novo_preco

    return preco
