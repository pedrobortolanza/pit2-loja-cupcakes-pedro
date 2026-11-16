from flask import current_app, session

from cupcakes.services.carrinho import Carrinho


def obter_carrinho():
    return Carrinho(session.get("carrinho"), current_app.config["LIMITE_POR_ITEM"])


def salvar_carrinho(carrinho):
    session["carrinho"] = carrinho.para_sessao()
    session.modified = True


def ler_inteiro(valor, padrao=0):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return padrao
