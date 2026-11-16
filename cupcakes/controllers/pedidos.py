from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from cupcakes.controllers.util import obter_carrinho, salvar_carrinho
from cupcakes.erros import ErroNegocio
from cupcakes.extensions import db
from cupcakes.models import Pedido
from cupcakes.models.pedido import FORMAS_PAGAMENTO
from cupcakes.seguranca import login_obrigatorio, usuario_atual
from cupcakes.services.pedidos import calcular_taxa_entrega, cancelar_pedido, criar_pedido

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


def _pedido_do_cliente(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None or pedido.cliente_id != usuario_atual().id:
        abort(404)
    return pedido


@pedidos_bp.route("/finalizar", methods=["GET", "POST"])
@login_obrigatorio
def finalizar():
    carrinho = obter_carrinho()
    itens = carrinho.itens()
    salvar_carrinho(carrinho)
    if not itens:
        flash("Seu carrinho está vazio. Escolha seus cupcakes primeiro.", "aviso")
        return redirect(url_for("loja.vitrine"))
    subtotal = sum((item["subtotal"] for item in itens), 0)
    config = current_app.config
    taxa = calcular_taxa_entrega(subtotal, "entrega", config["TAXA_ENTREGA"], config["FRETE_GRATIS_A_PARTIR"])
    contexto = {"itens": itens, "subtotal": subtotal, "taxa": taxa, "formas_pagamento": FORMAS_PAGAMENTO}
    if request.method == "POST":
        dados_cartao = {
            "titular": request.form.get("titular"),
            "numero": request.form.get("numero_cartao"),
            "validade": request.form.get("validade"),
            "cvv": request.form.get("cvv"),
        }
        try:
            pedido = criar_pedido(usuario_atual(), carrinho, request.form.get("forma_entrega"), request.form,
                                  request.form.get("forma_pagamento"), dados_cartao, request.form.get("observacao"),
                                  config)
        except ErroNegocio as erro:
            flash(erro.mensagem, "erro")
            return render_template("pedidos/finalizar.html", dados=request.form, **contexto), 422
        salvar_carrinho(carrinho)
        flash(f"Pedido #{pedido.id} confirmado! Acompanhe o status por aqui.", "sucesso")
        return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
    return render_template("pedidos/finalizar.html", dados={"forma_entrega": "entrega", "forma_pagamento": "pix"},
                           **contexto)


@pedidos_bp.get("/")
@login_obrigatorio
def lista():
    return render_template("pedidos/lista.html", pedidos=usuario_atual().pedidos)


@pedidos_bp.get("/<int:pedido_id>")
@login_obrigatorio
def detalhe(pedido_id):
    return render_template("pedidos/detalhe.html", pedido=_pedido_do_cliente(pedido_id))


@pedidos_bp.post("/<int:pedido_id>/cancelar")
@login_obrigatorio
def cancelar(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    try:
        cancelar_pedido(pedido)
    except ErroNegocio as erro:
        flash(erro.mensagem, "erro")
    else:
        flash(f"Pedido #{pedido.id} cancelado.", "sucesso")
    return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
