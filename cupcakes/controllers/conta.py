from flask import Blueprint, flash, redirect, render_template, request, url_for

from cupcakes.erros import ErroNegocio
from cupcakes.extensions import db
from cupcakes.seguranca import login_obrigatorio, usuario_atual

conta_bp = Blueprint("conta", __name__, url_prefix="/conta")


@conta_bp.route("/", methods=["GET", "POST"])
@login_obrigatorio
def minha_conta():
    cliente = usuario_atual()
    if request.method == "POST":
        try:
            cliente.atualizar_dados(request.form.get("nome"), request.form.get("telefone"))
        except ErroNegocio as erro:
            db.session.rollback()
            flash(erro.mensagem, "erro")
            return render_template("conta/minha_conta.html", cliente=cliente, dados=request.form), 422
        flash("Seus dados foram atualizados.", "sucesso")
        return redirect(url_for("conta.minha_conta"))
    return render_template("conta/minha_conta.html", cliente=cliente,
                           dados={"nome": cliente.nome, "telefone": cliente.telefone})
