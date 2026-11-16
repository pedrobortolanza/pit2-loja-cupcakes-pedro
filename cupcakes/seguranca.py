import hmac
import secrets
from functools import wraps

from flask import abort, current_app, flash, g, redirect, request, session, url_for

from cupcakes.extensions import db
from cupcakes.models import Cliente


def usuario_atual():
    if "usuario" not in g:
        cliente_id = session.get("cliente_id")
        g.usuario = db.session.get(Cliente, cliente_id) if cliente_id else None
        if cliente_id and g.usuario is None:
            session.pop("cliente_id", None)
    return g.usuario


def entrar(cliente):
    carrinho = session.get("carrinho", {})
    session.clear()
    session["carrinho"] = carrinho
    session["cliente_id"] = cliente.id
    g.usuario = cliente


def sair():
    session.clear()
    g.usuario = None


def destino_seguro(destino, padrao):
    if destino and destino.startswith("/") and not destino.startswith("//") and "\\" not in destino:
        return destino
    return padrao


def login_obrigatorio(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if usuario_atual() is None:
            flash("Entre na sua conta para continuar.", "aviso")
            return redirect(url_for("auth.entrar", proximo=request.full_path.rstrip("?")))
        return funcao(*args, **kwargs)
    return protegida


def admin_obrigatorio(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        usuario = usuario_atual()
        if usuario is None:
            flash("Entre com uma conta de administrador.", "aviso")
            return redirect(url_for("auth.entrar", proximo=request.full_path.rstrip("?")))
        if not usuario.administrador:
            abort(403)
        return funcao(*args, **kwargs)
    return protegida


def token_csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def verificar_csrf():
    if request.method != "POST" or not current_app.config.get("CSRF_ENABLED", True):
        return
    enviado = request.form.get("csrf_token", "")
    esperado = session.get("csrf", "")
    if not esperado or not hmac.compare_digest(enviado, esperado):
        abort(400)
