from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from cupcakes.controllers.util import ler_inteiro, obter_carrinho, salvar_carrinho
from cupcakes.erros import ErroNegocio
from cupcakes.extensions import db
from cupcakes.models import Cupcake
from cupcakes.seguranca import destino_seguro
from cupcakes.services.pedidos import calcular_taxa_entrega

carrinho_bp = Blueprint("carrinho", __name__, url_prefix="/carrinho")


@carrinho_bp.get("/")
def ver():
    carrinho = obter_carrinho()
    itens = carrinho.itens()
    salvar_carrinho(carrinho)
    subtotal = sum((item["subtotal"] for item in itens), 0)
    taxa = calcular_taxa_entrega(subtotal, "entrega", current_app.config["TAXA_ENTREGA"],
                                 current_app.config["FRETE_GRATIS_A_PARTIR"]) if itens else 0
    falta_frete_gratis = max(current_app.config["FRETE_GRATIS_A_PARTIR"] - subtotal, 0) if itens else 0
    return render_template("carrinho/ver.html", itens=itens, subtotal=subtotal, taxa=taxa,
                           falta_frete_gratis=falta_frete_gratis)


@carrinho_bp.post("/adicionar/<int:cupcake_id>")
def adicionar(cupcake_id):
    carrinho = obter_carrinho()
    cupcake = db.session.get(Cupcake, cupcake_id)
    voltar = destino_seguro(request.form.get("voltar"), url_for("loja.vitrine"))
    try:
        carrinho.adicionar(cupcake, ler_inteiro(request.form.get("quantidade"), 1))
    except ErroNegocio as erro:
        flash(erro.mensagem, "erro")
        return redirect(voltar)
    salvar_carrinho(carrinho)
    flash(f"{cupcake.nome} foi adicionado ao carrinho.", "sucesso")
    return redirect(voltar)


@carrinho_bp.post("/atualizar/<int:cupcake_id>")
def atualizar(cupcake_id):
    carrinho = obter_carrinho()
    cupcake = db.session.get(Cupcake, cupcake_id)
    if cupcake is None:
        carrinho.remover(cupcake_id)
        salvar_carrinho(carrinho)
        flash("Este cupcake não está mais disponível e saiu do carrinho.", "aviso")
        return redirect(url_for("carrinho.ver"))
    try:
        carrinho.atualizar(cupcake, ler_inteiro(request.form.get("quantidade"), -1))
    except ErroNegocio as erro:
        flash(erro.mensagem, "erro")
        return redirect(url_for("carrinho.ver"))
    salvar_carrinho(carrinho)
    flash("Carrinho atualizado.", "sucesso")
    return redirect(url_for("carrinho.ver"))


@carrinho_bp.post("/remover/<int:cupcake_id>")
def remover(cupcake_id):
    carrinho = obter_carrinho()
    carrinho.remover(cupcake_id)
    salvar_carrinho(carrinho)
    flash("Item removido do carrinho.", "sucesso")
    return redirect(url_for("carrinho.ver"))
