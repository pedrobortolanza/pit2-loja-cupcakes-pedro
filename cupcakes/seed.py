from decimal import Decimal

from cupcakes.extensions import db
from cupcakes.models import Categoria, Cliente, Cupcake

CATEGORIAS = [
    ("Clássicos", "Os sabores de sempre, feitos todos os dias."),
    ("Frutados", "Coberturas leves com frutas frescas da estação."),
    ("Especiais", "Receitas da casa com recheio surpresa."),
    ("Veganos", "Sem ingredientes de origem animal."),
]

CUPCAKES = [
    ("Baunilha com Chantilly", "Massa de baunilha fofinha com chantilly batido na hora.", "8.90", 30, "#f7e3b5", True, "Clássicos"),
    ("Chocolate Belga", "Massa de cacau 50% com ganache de chocolate belga.", "10.90", 25, "#6b3e26", True, "Clássicos"),
    ("Red Velvet", "Massa aveludada vermelha com cobertura de cream cheese.", "11.50", 20, "#e9d6d0", False, "Clássicos"),
    ("Morango do Campo", "Massa de baunilha, recheio de geleia e cobertura de morango.", "10.50", 18, "#f4a6c1", True, "Frutados"),
    ("Limão Siciliano", "Massa cítrica com merengue maçaricado.", "9.90", 15, "#f3eb8c", False, "Frutados"),
    ("Maracujá", "Massa de baunilha com mousse de maracujá.", "9.90", 12, "#f6c453", False, "Frutados"),
    ("Doce de Leite com Flor de Sal", "Recheio de doce de leite artesanal e toque de flor de sal.", "12.90", 14, "#d9a066", True, "Especiais"),
    ("Pistache", "Massa de pistache com creme e pistache torrado.", "14.90", 10, "#b7d39a", False, "Especiais"),
    ("Brigadeiro Gourmet", "Massa de chocolate recheada de brigadeiro cremoso.", "11.90", 22, "#4a2a1c", False, "Especiais"),
    ("Cacau Vegano", "Massa de cacau com cobertura de chocolate 70%, sem leite e sem ovos.", "11.90", 12, "#5b3a29", False, "Veganos"),
    ("Coco e Banana Vegano", "Massa de banana com cobertura de creme de coco.", "10.90", 0, "#f4efe1", False, "Veganos"),
]

CONTAS_DE_TESTE = [
    ("Administrador da Loja", "admin@nuvemdeacucar.test", "r29jUCkk9ZC4", True),
    ("Cliente de Teste", "cliente@nuvemdeacucar.test", "WQl1fP-geIeB", False),
]


def popular():
    if Categoria.query.first():
        return
    categorias = {}
    for nome, descricao in CATEGORIAS:
        categoria = Categoria(nome=nome, descricao=descricao)
        db.session.add(categoria)
        categorias[nome] = categoria
    for nome, descricao, preco, estoque, cor, destaque, categoria in CUPCAKES:
        db.session.add(Cupcake(nome=nome, descricao=descricao, preco=Decimal(preco), estoque=estoque, cor=cor,
                               destaque=destaque, categoria=categorias[categoria]))
    for nome, email, senha, administrador in CONTAS_DE_TESTE:
        conta = Cliente(nome=nome, email=email, administrador=administrador)
        conta.definir_senha(senha)
        db.session.add(conta)
    db.session.commit()
