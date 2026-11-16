import re

from werkzeug.security import check_password_hash, generate_password_hash

from cupcakes.erros import ErroNegocio
from cupcakes.extensions import db
from cupcakes.models.base import agora

PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TAMANHO_MINIMO_SENHA = 6


class Cliente(db.Model):
    __tablename__ = "cliente"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=False, default="")
    administrador = db.Column(db.Boolean, nullable=False, default=False)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora)

    pedidos = db.relationship("Pedido", back_populates="cliente", order_by="Pedido.criado_em.desc()")

    @staticmethod
    def normalizar_email(email):
        return (email or "").strip().lower()

    @classmethod
    def cadastrar(cls, nome, email, senha, telefone=""):
        nome = (nome or "").strip()
        email = cls.normalizar_email(email)
        erros = []
        if len(nome) < 3:
            erros.append("Informe seu nome completo.")
        if not PADRAO_EMAIL.match(email):
            erros.append("Informe um e-mail válido.")
        if len(senha or "") < TAMANHO_MINIMO_SENHA:
            erros.append(f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres.")
        if erros:
            raise ErroNegocio(" ".join(erros))
        if cls.query.filter_by(email=email).first():
            raise ErroNegocio("Já existe uma conta com este e-mail. Tente entrar.")
        cliente = cls(nome=nome, email=email, telefone=(telefone or "").strip())
        cliente.definir_senha(senha)
        db.session.add(cliente)
        db.session.commit()
        return cliente

    @classmethod
    def autenticar(cls, email, senha):
        cliente = cls.query.filter_by(email=cls.normalizar_email(email)).first()
        if cliente is None or not cliente.verificar_senha(senha or ""):
            raise ErroNegocio("E-mail ou senha incorretos.")
        return cliente

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha, method="pbkdf2:sha256:600000")

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def primeiro_nome(self):
        return self.nome.split()[0] if self.nome else ""

    def __repr__(self):
        return f"<Cliente {self.email}>"
