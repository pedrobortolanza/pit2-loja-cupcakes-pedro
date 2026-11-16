from decimal import Decimal

from cupcakes.erros import ErroNegocio
from cupcakes.extensions import db
from cupcakes.models import Cupcake


class Carrinho:
    def __init__(self, dados=None, limite_por_item=20):
        self.limite_por_item = limite_por_item
        self._quantidades = {}
        for chave, quantidade in (dados or {}).items():
            try:
                quantidade = int(quantidade)
            except (TypeError, ValueError):
                continue
            if quantidade > 0:
                self._quantidades[str(chave)] = quantidade

    def para_sessao(self):
        return dict(self._quantidades)

    def quantidade_de(self, cupcake_id):
        return self._quantidades.get(str(cupcake_id), 0)

    def _validar(self, cupcake, quantidade):
        if cupcake is None or not cupcake.ativo:
            raise ErroNegocio("Este cupcake não está mais disponível.")
        if quantidade < 1:
            raise ErroNegocio("A quantidade precisa ser pelo menos 1.")
        if quantidade > self.limite_por_item:
            raise ErroNegocio(f"O limite é de {self.limite_por_item} unidades por sabor em cada pedido.")
        if quantidade > cupcake.estoque:
            if cupcake.estoque == 0:
                raise ErroNegocio(f"{cupcake.nome} está esgotado no momento.")
            raise ErroNegocio(f"Só temos {cupcake.estoque} unidade(s) de {cupcake.nome} em estoque.")

    def adicionar(self, cupcake, quantidade=1):
        nova = self.quantidade_de(cupcake.id if cupcake else 0) + quantidade
        if quantidade < 1:
            raise ErroNegocio("A quantidade precisa ser pelo menos 1.")
        self._validar(cupcake, nova)
        self._quantidades[str(cupcake.id)] = nova

    def atualizar(self, cupcake, quantidade):
        if quantidade <= 0:
            self.remover(cupcake.id)
            return
        self._validar(cupcake, quantidade)
        self._quantidades[str(cupcake.id)] = quantidade

    def remover(self, cupcake_id):
        self._quantidades.pop(str(cupcake_id), None)

    def limpar(self):
        self._quantidades.clear()

    @property
    def vazio(self):
        return not self._quantidades

    @property
    def quantidade_total(self):
        return sum(self._quantidades.values())

    def itens(self):
        if not self._quantidades:
            return []
        ids = [int(chave) for chave in self._quantidades]
        cupcakes = {c.id: c for c in db.session.query(Cupcake).filter(Cupcake.id.in_(ids)).all()}
        resultado = []
        for chave in list(self._quantidades):
            cupcake = cupcakes.get(int(chave))
            if cupcake is None or not cupcake.ativo:
                self._quantidades.pop(chave)
                continue
            quantidade = self._quantidades[chave]
            resultado.append({"cupcake": cupcake, "quantidade": quantidade, "subtotal": cupcake.preco * quantidade})
        return resultado

    def subtotal(self):
        return sum((item["subtotal"] for item in self.itens()), Decimal("0.00"))
