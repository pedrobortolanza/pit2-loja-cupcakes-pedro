import os
import sys
from decimal import Decimal

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cupcakes import create_app
from cupcakes.config import ConfigTeste
from cupcakes.extensions import db as banco
from cupcakes.models import Categoria, Cliente, Cupcake


@pytest.fixture()
def app():
    aplicacao = create_app(ConfigTeste)
    with aplicacao.app_context():
        banco.create_all()
        yield aplicacao
        banco.session.remove()
        banco.drop_all()


@pytest.fixture()
def db(app):
    return banco


@pytest.fixture()
def cliente_http(app):
    return app.test_client()


@pytest.fixture()
def categoria(db):
    item = Categoria(nome="Clássicos", descricao="Sabores tradicionais")
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def cupcake(db, categoria):
    item = Cupcake(nome="Chocolate", descricao="Massa de cacau", preco=Decimal("10.00"), estoque=5,
                   cor="#6b3e26", categoria=categoria)
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def outro_cupcake(db, categoria):
    item = Cupcake(nome="Baunilha", descricao="Massa de baunilha", preco=Decimal("8.00"), estoque=50,
                   cor="#f7e3b5", categoria=categoria)
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture()
def conta(db):
    return Cliente.cadastrar("Maria Souza", "maria@exemplo.test", "segredo123", "41999990000")


@pytest.fixture()
def conta_admin(db):
    admin = Cliente(nome="Admin da Loja", email="admin@exemplo.test", administrador=True)
    admin.definir_senha("admin12345")
    db.session.add(admin)
    db.session.commit()
    return admin


def fazer_login(cliente_http, email, senha):
    return cliente_http.post("/entrar", data={"email": email, "senha": senha})


ENDERECO = {"cep": "80010-000", "logradouro": "Rua das Flores", "numero": "100", "bairro": "Centro", "cidade": "Curitiba"}
CARTAO_TESTE = {"titular": "MARIA SOUZA", "numero": "4111 1111 1111 1111", "validade": "12/40", "cvv": "123"}
