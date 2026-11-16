from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from cupcakes.erros import ErroNegocio
from cupcakes.extensions import db
from cupcakes.models import AvaliacaoTeste, Categoria, Cupcake, Pedido
from cupcakes.models.pedido import STATUS_ROTULOS
from cupcakes.seguranca import admin_obrigatorio
from cupcakes.services.pedidos import avancar_status, cancelar_pedido

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _buscar(modelo, identificador):
    objeto = db.session.get(modelo, identificador)
    if objeto is None:
        abort(404)
    return objeto


@admin_bp.get("/")
@admin_obrigatorio
def pedidos():
    status = request.args.get("status", "")
    consulta = Pedido.query
    if status in STATUS_ROTULOS:
        consulta = consulta.filter_by(status=status)
    else:
        status = ""
    lista = consulta.order_by(Pedido.criado_em.desc()).all()
    abertos = Pedido.query.filter(Pedido.status.notin_(["entregue", "cancelado"])).count()
    return render_template("admin/pedidos.html", pedidos=lista, status=status, status_rotulos=STATUS_ROTULOS,
                           abertos=abertos)


@admin_bp.post("/pedidos/<int:pedido_id>/avancar")
@admin_obrigatorio
def avancar(pedido_id):
    pedido = _buscar(Pedido, pedido_id)
    try:
        avancar_status(pedido)
    except ErroNegocio as erro:
        flash(erro.mensagem, "erro")
    else:
        flash(f"Pedido #{pedido.id} agora está: {pedido.status_rotulo}.", "sucesso")
    return redirect(url_for("admin.pedidos", status=request.form.get("filtro", "")))


@admin_bp.post("/pedidos/<int:pedido_id>/cancelar")
@admin_obrigatorio
def cancelar(pedido_id):
    pedido = _buscar(Pedido, pedido_id)
    try:
        cancelar_pedido(pedido, por_administrador=True)
    except ErroNegocio as erro:
        flash(erro.mensagem, "erro")
    else:
        flash(f"Pedido #{pedido.id} cancelado e estoque devolvido.", "sucesso")
    return redirect(url_for("admin.pedidos", status=request.form.get("filtro", "")))


@admin_bp.get("/cupcakes")
@admin_obrigatorio
def cupcakes():
    lista = Cupcake.query.order_by(Cupcake.ativo.desc(), Cupcake.nome).all()
    return render_template("admin/cupcakes.html", cupcakes=lista)


def _formulario(cupcake, titulo):
    categorias = Categoria.query.order_by(Categoria.nome).all()
    if request.method == "POST":
        try:
            cupcake.preencher(request.form)
        except ErroNegocio as erro:
            db.session.rollback()
            flash(erro.mensagem, "erro")
            return render_template("admin/cupcake_form.html", cupcake=cupcake, dados=request.form,
                                   categorias=categorias, titulo=titulo), 422
        db.session.add(cupcake)
        db.session.commit()
        flash(f"{cupcake.nome} foi salvo.", "sucesso")
        return redirect(url_for("admin.cupcakes"))
    dados = {}
    if cupcake.id:
        dados = {"nome": cupcake.nome, "descricao": cupcake.descricao, "preco": f"{cupcake.preco:.2f}".replace(".", ","),
                 "estoque": cupcake.estoque, "cor": cupcake.cor, "categoria_id": cupcake.categoria_id,
                 "destaque": "on" if cupcake.destaque else ""}
    return render_template("admin/cupcake_form.html", cupcake=cupcake, dados=dados, categorias=categorias,
                           titulo=titulo)


@admin_bp.route("/cupcakes/novo", methods=["GET", "POST"])
@admin_obrigatorio
def novo_cupcake():
    return _formulario(Cupcake(), "Novo cupcake")


@admin_bp.route("/cupcakes/<int:cupcake_id>/editar", methods=["GET", "POST"])
@admin_obrigatorio
def editar_cupcake(cupcake_id):
    cupcake = _buscar(Cupcake, cupcake_id)
    return _formulario(cupcake, f"Editar {cupcake.nome}")


@admin_bp.post("/cupcakes/<int:cupcake_id>/alternar")
@admin_obrigatorio
def alternar_cupcake(cupcake_id):
    cupcake = _buscar(Cupcake, cupcake_id)
    cupcake.ativo = not cupcake.ativo
    db.session.commit()
    estado = "voltou para a vitrine" if cupcake.ativo else "saiu da vitrine"
    flash(f"{cupcake.nome} {estado}.", "sucesso")
    return redirect(url_for("admin.cupcakes"))


@admin_bp.get("/avaliacoes")
@admin_obrigatorio
def avaliacoes():
    lista = AvaliacaoTeste.query.order_by(AvaliacaoTeste.criado_em.desc()).all()
    return render_template("admin/avaliacoes.html", avaliacoes=lista)
