from decimal import Decimal

from cupcakes.extensions import db
from cupcakes.models.base import agora

STATUS_ROTULOS = {
    "recebido": "Recebido",
    "em_preparo": "Em preparo",
    "saiu_para_entrega": "Saiu para entrega",
    "pronto_para_retirada": "Pronto para retirada",
    "entregue": "Entregue",
    "cancelado": "Cancelado",
}

FLUXO_ENTREGA = ["recebido", "em_preparo", "saiu_para_entrega", "entregue"]
FLUXO_RETIRADA = ["recebido", "em_preparo", "pronto_para_retirada", "entregue"]

FORMAS_ENTREGA = {"entrega": "Entrega em casa", "retirada": "Retirar na loja"}
FORMAS_PAGAMENTO = {"pix": "Pix", "cartao": "Cartão de crédito", "dinheiro": "Dinheiro na entrega"}
STATUS_PAGAMENTO = {"pendente": "Pendente", "aprovado": "Aprovado", "recusado": "Recusado", "estornado": "Estornado"}


class Pedido(db.Model):
    __tablename__ = "pedido"
    __table_args__ = (
        db.CheckConstraint("forma_entrega in ('entrega', 'retirada')", name="ck_pedido_forma_entrega"),
        db.CheckConstraint(
            "status in ('recebido', 'em_preparo', 'saiu_para_entrega', 'pronto_para_retirada', 'entregue', 'cancelado')",
            name="ck_pedido_status",
        ),
        db.CheckConstraint("total >= 0", name="ck_pedido_total"),
    )

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False, index=True)
    status = db.Column(db.String(25), nullable=False, default="recebido", index=True)
    forma_entrega = db.Column(db.String(10), nullable=False)
    cep = db.Column(db.String(8))
    logradouro = db.Column(db.String(120))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(60))
    bairro = db.Column(db.String(60))
    cidade = db.Column(db.String(60))
    observacao = db.Column(db.String(255), nullable=False, default="")
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    taxa_entrega = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total = db.Column(db.Numeric(10, 2), nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora)
    atualizado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora, onupdate=agora)

    cliente = db.relationship("Cliente", back_populates="pedidos")
    itens = db.relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    pagamento = db.relationship("Pagamento", back_populates="pedido", uselist=False, cascade="all, delete-orphan")

    @property
    def fluxo(self):
        return FLUXO_RETIRADA if self.forma_entrega == "retirada" else FLUXO_ENTREGA

    @property
    def status_rotulo(self):
        return STATUS_ROTULOS.get(self.status, self.status)

    @property
    def forma_entrega_rotulo(self):
        return FORMAS_ENTREGA.get(self.forma_entrega, self.forma_entrega)

    @property
    def finalizado(self):
        return self.status in ("entregue", "cancelado")

    @property
    def pode_ser_cancelado_pelo_cliente(self):
        return self.status == "recebido"

    @property
    def proximo_status(self):
        if self.finalizado:
            return None
        posicao = self.fluxo.index(self.status)
        return self.fluxo[posicao + 1]

    @property
    def etapas(self):
        if self.status == "cancelado":
            return []
        atual = self.fluxo.index(self.status)
        return [
            {"rotulo": STATUS_ROTULOS[codigo], "feito": indice <= atual, "atual": indice == atual}
            for indice, codigo in enumerate(self.fluxo)
        ]

    @property
    def quantidade_itens(self):
        return sum(item.quantidade for item in self.itens)

    @property
    def endereco_formatado(self):
        if self.forma_entrega != "entrega":
            return ""
        complemento = f", {self.complemento}" if self.complemento else ""
        return f"{self.logradouro}, {self.numero}{complemento} - {self.bairro}, {self.cidade} - CEP {self.cep[:5]}-{self.cep[5:]}"


class ItemPedido(db.Model):
    __tablename__ = "item_pedido"
    __table_args__ = (
        db.CheckConstraint("quantidade > 0", name="ck_item_quantidade"),
        db.CheckConstraint("preco_unitario > 0", name="ck_item_preco"),
    )

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id", ondelete="CASCADE"), nullable=False, index=True)
    cupcake_id = db.Column(db.Integer, db.ForeignKey("cupcake.id"), nullable=False, index=True)
    nome_cupcake = db.Column(db.String(80), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(8, 2), nullable=False)

    pedido = db.relationship("Pedido", back_populates="itens")
    cupcake = db.relationship("Cupcake")

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade


class Pagamento(db.Model):
    __tablename__ = "pagamento"
    __table_args__ = (
        db.CheckConstraint("forma in ('pix', 'cartao', 'dinheiro')", name="ck_pagamento_forma"),
        db.CheckConstraint("status in ('pendente', 'aprovado', 'recusado', 'estornado')", name="ck_pagamento_status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id", ondelete="CASCADE"), nullable=False, unique=True)
    forma = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10), nullable=False, default="pendente")
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    codigo_transacao = db.Column(db.String(40))
    final_cartao = db.Column(db.String(4))
    pago_em = db.Column(db.DateTime(timezone=True))

    pedido = db.relationship("Pedido", back_populates="pagamento")

    @property
    def forma_rotulo(self):
        return FORMAS_PAGAMENTO.get(self.forma, self.forma)

    @property
    def status_rotulo(self):
        return STATUS_PAGAMENTO.get(self.status, self.status)
