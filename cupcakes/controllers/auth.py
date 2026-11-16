from flask import Blueprint, flash, redirect, render_template, request, url_for

from cupcakes.erros import ErroNegocio
from cupcakes.models import Cliente
from cupcakes.seguranca import destino_seguro, entrar as iniciar_sessao, sair as encerrar_sessao, usuario_atual

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if usuario_atual():
        return redirect(url_for("loja.vitrine"))
    proximo = request.values.get("proximo", "")
    if request.method == "POST":
        if request.form.get("senha") != request.form.get("confirmacao"):
            flash("As senhas digitadas não são iguais.", "erro")
            return render_template("auth/cadastro.html", dados=request.form, proximo=proximo), 422
        try:
            cliente = Cliente.cadastrar(request.form.get("nome"), request.form.get("email"),
                                        request.form.get("senha"), request.form.get("telefone"))
        except ErroNegocio as erro:
            flash(erro.mensagem, "erro")
            return render_template("auth/cadastro.html", dados=request.form, proximo=proximo), 422
        iniciar_sessao(cliente)
        flash(f"Conta criada! Bem-vindo(a), {cliente.primeiro_nome}.", "sucesso")
        return redirect(destino_seguro(proximo, url_for("loja.vitrine")))
    return render_template("auth/cadastro.html", dados={}, proximo=proximo)


@auth_bp.route("/entrar", methods=["GET", "POST"])
def entrar():
    if usuario_atual():
        return redirect(url_for("loja.vitrine"))
    proximo = request.values.get("proximo", "")
    if request.method == "POST":
        try:
            cliente = Cliente.autenticar(request.form.get("email"), request.form.get("senha"))
        except ErroNegocio as erro:
            flash(erro.mensagem, "erro")
            return render_template("auth/entrar.html", email=request.form.get("email", ""), proximo=proximo), 401
        iniciar_sessao(cliente)
        flash(f"Olá, {cliente.primeiro_nome}!", "sucesso")
        padrao = url_for("admin.pedidos") if cliente.administrador else url_for("loja.vitrine")
        return redirect(destino_seguro(proximo, padrao))
    return render_template("auth/entrar.html", email="", proximo=proximo)


@auth_bp.post("/sair")
def sair():
    encerrar_sessao()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("loja.vitrine"))
