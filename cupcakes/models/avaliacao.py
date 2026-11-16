from datetime import date

from cupcakes.erros import ErroNegocio
from cupcakes.extensions import db
from cupcakes.models.base import agora


class AvaliacaoTeste(db.Model):
    __tablename__ = "avaliacao_teste"

    id = db.Column(db.Integer, primary_key=True)
    nome_testador = db.Column(db.String(100), nullable=False)
    data_teste = db.Column(db.Date, nullable=False)
    funcionou = db.Column(db.Text, nullable=False)
    nao_funcionou = db.Column(db.Text, nullable=False, default="")
    nao_testado = db.Column(db.Text, nullable=False, default="")
    sugestoes = db.Column(db.Text, nullable=False, default="")
    link_evidencias = db.Column(db.String(500), nullable=False, default="")
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora)

    @classmethod
    def registrar(cls, dados):
        nome = (dados.get("nome_testador") or "").strip()
        funcionou = (dados.get("funcionou") or "").strip()
        link = (dados.get("link_evidencias") or "").strip()
        erros = []
        if len(nome) < 3:
            erros.append("Informe seu nome.")
        try:
            data_teste = date.fromisoformat(dados.get("data_teste") or "")
        except ValueError:
            erros.append("Informe a data do teste.")
            data_teste = None
        if not funcionou:
            erros.append("Conte o que você testou e funcionou.")
        if link and not link.startswith(("http://", "https://")):
            erros.append("O link das evidências deve começar com http:// ou https://.")
        if erros:
            raise ErroNegocio(" ".join(erros))
        avaliacao = cls(
            nome_testador=nome,
            data_teste=data_teste,
            funcionou=funcionou,
            nao_funcionou=(dados.get("nao_funcionou") or "").strip(),
            nao_testado=(dados.get("nao_testado") or "").strip(),
            sugestoes=(dados.get("sugestoes") or "").strip(),
            link_evidencias=link,
        )
        db.session.add(avaliacao)
        db.session.commit()
        return avaliacao
