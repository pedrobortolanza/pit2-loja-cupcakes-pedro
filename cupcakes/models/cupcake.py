import re
from decimal import Decimal, InvalidOperation

from cupcakes.erros import ErroNegocio
from cupcakes.extensions import db
from cupcakes.models.base import agora

PADRAO_COR = re.compile(r"^#[0-9a-fA-F]{6}$")


class Cupcake(db.Model):
    __tablename__ = "cupcake"
    __table_args__ = (
        db.CheckConstraint("preco > 0", name="ck_cupcake_preco_positivo"),
        db.CheckConstraint("estoque >= 0", name="ck_cupcake_estoque_nao_negativo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text, nullable=False, default="")
    preco = db.Column(db.Numeric(8, 2), nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    cor = db.Column(db.String(7), nullable=False, default="#f4a6c1")
    destaque = db.Column(db.Boolean, nullable=False, default=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False, index=True)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora)

    categoria = db.relationship("Categoria", back_populates="cupcakes")

    @property
    def disponivel(self):
        return bool(self.ativo) and self.estoque > 0

    def preencher(self, dados):
        erros = []
        nome = (dados.get("nome") or "").strip()
        if len(nome) < 3:
            erros.append("Informe um nome com pelo menos 3 letras.")
        try:
            preco = Decimal(str(dados.get("preco", "")).replace(",", ".")).quantize(Decimal("0.01"))
            if preco <= 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            erros.append("Informe um preço maior que zero, por exemplo 9,90.")
            preco = None
        try:
            estoque = int(dados.get("estoque", ""))
            if estoque < 0:
                raise ValueError
        except ValueError:
            erros.append("O estoque deve ser um número inteiro igual ou maior que zero.")
            estoque = None
        cor = (dados.get("cor") or "#f4a6c1").strip()
        if not PADRAO_COR.match(cor):
            erros.append("Escolha uma cor válida para a cobertura.")
        try:
            categoria_id = int(dados.get("categoria_id", ""))
        except ValueError:
            erros.append("Escolha uma categoria.")
            categoria_id = None
        if erros:
            raise ErroNegocio(" ".join(erros))
        self.nome = nome
        self.descricao = (dados.get("descricao") or "").strip()
        self.preco = preco
        self.estoque = estoque
        self.cor = cor
        self.categoria_id = categoria_id
        self.destaque = dados.get("destaque") in ("on", "1", "true", True)

    def __repr__(self):
        return f"<Cupcake {self.nome}>"
