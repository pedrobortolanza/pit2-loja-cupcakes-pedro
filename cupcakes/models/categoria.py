from cupcakes.extensions import db


class Categoria(db.Model):
    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False, unique=True)
    descricao = db.Column(db.String(255), nullable=False, default="")

    cupcakes = db.relationship("Cupcake", back_populates="categoria", order_by="Cupcake.nome")

    def __repr__(self):
        return f"<Categoria {self.nome}>"
