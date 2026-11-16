import os
from decimal import Decimal

from sqlalchemy.pool import NullPool


def normalizar_url_banco(url):
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
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
