import os
from decimal import Decimal
from urllib.parse import quote, unquote

from sqlalchemy.pool import NullPool


def codificar_senha(resto):
    if "@" not in resto:
        return resto
    credenciais, endereco = resto.rsplit("@", 1)
    if ":" not in credenciais:
        return resto
    usuario, senha = credenciais.split(":", 1)
    senha = senha.strip()
    if senha.startswith("[") and senha.endswith("]"):
        senha = senha[1:-1]
    return f"{usuario}:{quote(unquote(senha), safe='')}@{endereco}"


def normalizar_url_banco(url):
    url = url.strip()
    for prefixo in ("postgres://", "postgresql://", "postgresql+psycopg://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg://" + codificar_senha(url[len(prefixo):])
    return url


def opcoes_engine(url):
    if url.startswith("postgresql"):
        return {"poolclass": NullPool, "connect_args": {"prepare_threshold": None}}
    return {}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "chave-local-de-desenvolvimento")
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(os.environ.get("DATABASE_URL", "sqlite:///loja.db"))
    SQLALCHEMY_ENGINE_OPTIONS = opcoes_engine(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("VERCEL") == "1"
    NOME_LOJA = "Nuvem de Açúcar"
    TAXA_ENTREGA = Decimal("7.00")
    FRETE_GRATIS_A_PARTIR = Decimal("80.00")
    LIMITE_POR_ITEM = 20


class ConfigTeste(Config):
    TESTING = True
    SECRET_KEY = "chave-de-teste"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
