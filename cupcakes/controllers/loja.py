from flask import Blueprint, abort, render_template, request
from sqlalchemy import or_

from cupcakes.extensions import db
from cupcakes.models import Categoria, Cupcake

loja_bp = Blueprint("loja", __name__)


@loja_bp.get("/")
def vitrine():
    busca = (request.args.get("busca") or "").strip()
    categoria_id = request.args.get("categoria", type=int)
    consulta = Cupcake.query.filter_by(ativo=True)
    if categoria_id:
        consulta = consulta.filter_by(categoria_id=categoria_id)
    if busca:
        termo = f"%{busca}%"
        consulta = consulta.filter(or_(Cupcake.nome.ilike(termo), Cupcake.descricao.ilike(termo)))
    cupcakes = consulta.order_by(Cupcake.destaque.desc(), Cupcake.nome).all()
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template("loja/vitrine.html", cupcakes=cupcakes, categorias=categorias,
                           busca=busca, categoria_id=categoria_id)


@loja_bp.get("/cupcake/<int:cupcake_id>")
def detalhe(cupcake_id):
    cupcake = db.session.get(Cupcake, cupcake_id)
    if cupcake is None or not cupcake.ativo:
        abort(404)
    relacionados = (Cupcake.query.filter(Cupcake.categoria_id == cupcake.categoria_id, Cupcake.id != cupcake.id,
                                         Cupcake.ativo.is_(True)).limit(3).all())
    return render_template("loja/detalhe.html", cupcake=cupcake, relacionados=relacionados)
