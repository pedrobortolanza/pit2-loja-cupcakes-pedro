import re
from decimal import Decimal

from cupcakes.erros import ErroNegocio
from cupcakes.extensions import db
from cupcakes.models import Cupcake, ItemPedido, Pedido
from cupcakes.models.base import agora
from cupcakes.services.pagamentos import processar_pagamento

CAMPOS_ENDERECO = {
    "logradouro": "rua",
    "numero": "número",
    "bairro": "bairro",
    "cidade": "cidade",
}


def calcular_taxa_entrega(subtotal, forma_entrega, taxa, frete_gratis_a_partir):
    if forma_entrega == "retirada":
        return Decimal("0.00")
    if subtotal >= frete_gratis_a_partir:
        return Decimal("0.00")
    return taxa


def validar_endereco(dados):
    endereco = {campo: (dados.get(campo) or "").strip() for campo in ("cep", "logradouro", "numero", "complemento", "bairro", "cidade")}
    endereco["cep"] = re.sub(r"\D", "", endereco["cep"])
    faltando = [rotulo for campo, rotulo in CAMPOS_ENDERECO.items() if not endereco[campo]]
    erros = []
    if faltando:
        erros.append("Preencha o endereço: " + ", ".join(faltando) + ".")
    if len(endereco["cep"]) != 8:
        erros.append("O CEP precisa ter 8 números.")
    if erros:
        raise ErroNegocio(" ".join(erros))
    return endereco


def criar_pedido(cliente, carrinho, forma_entrega, dados_endereco, forma_pagamento, dados_cartao, observacao, config):
    itens = carrinho.itens()
    if not itens:
        raise ErroNegocio("Seu carrinho está vazio.")
    if forma_entrega not in ("entrega", "retirada"):
        raise ErroNegocio("Escolha entre entrega em casa ou retirada na loja.")
    if forma_pagamento not in ("pix", "cartao", "dinheiro"):
        raise ErroNegocio("Escolha uma forma de pagamento.")
    endereco = validar_endereco(dados_endereco) if forma_entrega == "entrega" else {}

    bloqueados = []
    subtotal = Decimal("0.00")
    for item in itens:
        cupcake = db.session.query(Cupcake).filter_by(id=item["cupcake"].id).with_for_update().one()
        if not cupcake.ativo or cupcake.estoque < item["quantidade"]:
            bloqueados.append(f"{cupcake.nome} (disponível: {cupcake.estoque if cupcake.ativo else 0})")
        item["cupcake"] = cupcake
        subtotal += cupcake.preco * item["quantidade"]
    if bloqueados:
        db.session.rollback()
        raise ErroNegocio("O estoque mudou enquanto você comprava. Ajuste estes itens: " + ", ".join(bloqueados) + ".")

    taxa = calcular_taxa_entrega(subtotal, forma_entrega, config["TAXA_ENTREGA"], config["FRETE_GRATIS_A_PARTIR"])
    total = subtotal + taxa
    try:
        pagamento = processar_pagamento(forma_pagamento, total, dados_cartao)
    except ErroNegocio:
        db.session.rollback()
        raise

    pedido = Pedido(
        cliente=cliente,
        forma_entrega=forma_entrega,
        observacao=(observacao or "").strip()[:255],
        subtotal=subtotal,
        taxa_entrega=taxa,
        total=total,
        **endereco,
    )
    for item in itens:
        cupcake = item["cupcake"]
        pedido.itens.append(ItemPedido(cupcake=cupcake, nome_cupcake=cupcake.nome,
                                       quantidade=item["quantidade"], preco_unitario=cupcake.preco))
        cupcake.estoque -= item["quantidade"]
    pedido.pagamento = pagamento
    db.session.add(pedido)
    db.session.commit()
    carrinho.limpar()
    return pedido


def cancelar_pedido(pedido, por_administrador=False):
    if pedido.finalizado:
        raise ErroNegocio("Este pedido já foi finalizado e não pode ser cancelado.")
    if not por_administrador and not pedido.pode_ser_cancelado_pelo_cliente:
        raise ErroNegocio("O pedido já está em preparo. Fale com a loja para cancelar.")
    for item in pedido.itens:
        item.cupcake.estoque += item.quantidade
    pedido.status = "cancelado"
    if pedido.pagamento is not None:
        pedido.pagamento.status = "estornado" if pedido.pagamento.status == "aprovado" else "recusado"
    db.session.commit()
    return pedido


def avancar_status(pedido):
    proximo = pedido.proximo_status
    if proximo is None:
        raise ErroNegocio("Este pedido já foi finalizado.")
    pedido.status = proximo
    if proximo == "entregue" and pedido.pagamento is not None and pedido.pagamento.status == "pendente":
        pedido.pagamento.status = "aprovado"
        pedido.pagamento.pago_em = agora()
    db.session.commit()
    return pedido
