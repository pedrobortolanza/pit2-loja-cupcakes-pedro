from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from cupcakes.models.base import FUSO, como_utc, hoje_local

QUANTIDADE_MAIS_VENDIDOS = 5


def resumo_vendas(pedidos, hoje=None):
    """Totais para o painel do lojista. Pedidos cancelados não contam como venda."""
    hoje = hoje or hoje_local()
    inicio_semana = hoje - timedelta(days=6)
    validos = [pedido for pedido in pedidos if pedido.status != "cancelado"]

    def dia(pedido):
        return como_utc(pedido.criado_em).astimezone(FUSO).date()

    de_hoje = [pedido for pedido in validos if dia(pedido) == hoje]
    da_semana = [pedido for pedido in validos if inicio_semana <= dia(pedido) <= hoje]
    vendas_hoje = sum((pedido.total for pedido in de_hoje), Decimal("0.00"))

    sabores = defaultdict(lambda: {"quantidade": 0, "receita": Decimal("0.00")})
    for pedido in validos:
        for item in pedido.itens:
            sabores[item.nome_cupcake]["quantidade"] += item.quantidade
            sabores[item.nome_cupcake]["receita"] += item.subtotal
    mais_vendidos = sorted(
        ({"nome": nome, **valores} for nome, valores in sabores.items()),
        key=lambda sabor: (-sabor["quantidade"], sabor["nome"]),
    )[:QUANTIDADE_MAIS_VENDIDOS]

    return {
        "hoje": hoje,
        "vendas_hoje": vendas_hoje,
        "pedidos_hoje": len(de_hoje),
        "ticket_medio_hoje": (vendas_hoje / len(de_hoje)).quantize(Decimal("0.01")) if de_hoje else Decimal("0.00"),
        "vendas_semana": sum((pedido.total for pedido in da_semana), Decimal("0.00")),
        "pedidos_semana": len(da_semana),
        "em_aberto": sum(1 for pedido in validos if not pedido.finalizado),
        "cancelados": len(pedidos) - len(validos),
        "mais_vendidos": mais_vendidos,
    }
