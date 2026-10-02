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
# REGRAS SHOPEE — Vendedores CNPJ (vigência: 01/10/2026)
# Tabela de comissão por faixa de preço:
#   Até R$ 79,99          → 20% + R$ 4,50
#   R$ 80,00 a R$ 99,99   → 14% + R$ 16,00
#   R$ 100,00 a R$ 199,99 → 14% + R$ 20,00
#   R$ 200,00 a R$ 499,99 → 14% + R$ 26,00
#   Acima de R$ 500,00    → 14% + R$ 26,00
# Nota: O Subsídio Pix (5%-8%) é oferecido pela Shopee ao comprador e
#        não afeta o valor líquido recebido pelo vendedor.
# =============================================================================
def calcular_comissao_shopee(preco_venda: Decimal) -> dict:
    """
    Calcula a comissão Shopee para vendedores CNPJ com base na faixa de preço do item.
    Regras vigentes a partir de 01/10/2026.
    """
    preco = quantize(preco_venda)

    if preco <= Decimal("79.99"):
        taxa_percentual = Decimal("0.20")
        taxa_fixa = Decimal("4.50")
    elif preco <= Decimal("99.99"):
        taxa_percentual = Decimal("0.14")
        taxa_fixa = Decimal("16.00")
    elif preco <= Decimal("199.99"):
        taxa_percentual = Decimal("0.14")
        taxa_fixa = Decimal("20.00")
    else:
        # R$ 200,00 a R$ 499,99 e acima de R$ 500,00 — mesma estrutura
        taxa_percentual = Decimal("0.14")
        taxa_fixa = Decimal("26.00")

    comissao_percentual = quantize(preco * taxa_percentual)
    total = comissao_percentual + taxa_fixa

    return {
        "percentual": taxa_percentual * Decimal("100"),
        "comissao_percentual_valor": comissao_percentual,
        "taxa_fixa": taxa_fixa,
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
    filamentos: list,
    horas_impressao: Decimal,
    potencia_w: Decimal,
    kwh_preco: Decimal,
    custo_embalagem: Decimal = Decimal("0"),
    custo_insumos: Decimal = Decimal("0"),
    custo_mao_de_obra: Decimal = Decimal("0")
) -> dict:
    """Calcula os custos diretos de fabricação da peça em impressão 3D."""
    custo_filamento = Decimal("0")
    for f in filamentos:
        peso = Decimal(str(f.get('peso_g', 0) or 0))
        valor_kg = Decimal(str(f.get('valor_kg', 0) or 0))
        custo_filamento += (peso / Decimal("1000")) * valor_kg
        
    filamento = quantize(custo_filamento)
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
            comissao = calcular_comissao_shopee(preco)
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
