import os
from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from flask import Flask, render_template

from cupcakes.config import Config
from cupcakes.controllers import BLUEPRINTS
from cupcakes.controllers.util import obter_carrinho
from cupcakes.extensions import db
from cupcakes.seguranca import token_csrf, usuario_atual, verificar_csrf

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUSO = ZoneInfo("America/Sao_Paulo")

ERROS = {
    400: ("Requisição inválida", "O formulário expirou ou veio incompleto. Volte, recarregue a página e tente de novo."),
    403: ("Acesso negado", "Esta área é só para administradores da loja."),
    404: ("Página não encontrada", "O endereço não existe ou o cupcake saiu da vitrine."),
    500: ("Algo deu errado", "Tivemos um problema do nosso lado. Tente novamente em alguns instantes."),
}


def moeda(valor):
    texto = f"{Decimal(valor or 0):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def data_hora(valor):
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        if valor.tzinfo is None:
            valor = valor.replace(tzinfo=timezone.utc)
        return valor.astimezone(FUSO).strftime("%d/%m/%Y %H:%M")
    return valor.strftime("%d/%m/%Y")


def create_app(configuracao=Config):
    app = Flask(__name__, template_folder="views", static_folder=os.path.join(RAIZ, "public", "static"),
                static_url_path="/static")
    app.config.from_object(configuracao)
    if os.environ.get("VERCEL") and app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        raise RuntimeError("Variável DATABASE_URL não configurada na Vercel. Veja o passo 1 do COMO-CONTINUAR.md.")
    db.init_app(app)

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    app.before_request(verificar_csrf)
    app.add_template_filter(moeda, "moeda")
    app.add_template_filter(data_hora, "data_hora")

    @app.context_processor
    def contexto_global():
        return {
            "usuario": usuario_atual(),
            "csrf_token": token_csrf,
            "itens_no_carrinho": obter_carrinho().quantidade_total,
            "nome_loja": app.config["NOME_LOJA"],
            "frete_gratis": app.config["FRETE_GRATIS_A_PARTIR"],
        }

    def pagina_de_erro(erro):
        codigo = getattr(erro, "code", 500) or 500
        if codigo == 500:
            db.session.rollback()
            causa = getattr(erro, "original_exception", None) or erro
            app.logger.error("CAUSA DO ERRO 500: %s: %s", type(causa).__name__, str(causa).splitlines()[0][:300] if str(causa) else "")
        titulo, mensagem = ERROS.get(codigo, ERROS[500])
        return render_template("erros/erro.html", codigo=codigo, titulo=titulo, mensagem=mensagem), codigo

    for codigo in ERROS:
        app.register_error_handler(codigo, pagina_de_erro)

    @app.cli.command("criar-banco")
    def criar_banco():
        from cupcakes.seed import popular
        db.create_all()
        popular()
        print("Banco criado e populado.")

    return app
