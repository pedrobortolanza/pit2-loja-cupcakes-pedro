from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from cupcakes.erros import ErroNegocio
from cupcakes.models import AvaliacaoTeste

avaliacao_bp = Blueprint("avaliacao", __name__, url_prefix="/avaliacao")


@avaliacao_bp.route("/", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":
        try:
            AvaliacaoTeste.registrar(request.form)
        except ErroNegocio as erro:
            flash(erro.mensagem, "erro")
            return render_template("avaliacao/formulario.html", dados=request.form), 422
        return redirect(url_for("avaliacao.obrigado"))
    return render_template("avaliacao/formulario.html", dados={"data_teste": date.today().isoformat()})


@avaliacao_bp.get("/obrigado")
def obrigado():
    return render_template("avaliacao/obrigado.html")
