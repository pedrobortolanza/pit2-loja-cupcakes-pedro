from datetime import date
from decimal import Decimal

import pytest

from cupcakes.erros import ErroNegocio
from cupcakes.models import AvaliacaoTeste, Cliente, Cupcake


def test_cadastro_guarda_senha_criptografada(conta):
    assert conta.senha_hash != "segredo123"
    assert conta.verificar_senha("segredo123")
    assert not conta.verificar_senha("errada")


def test_cadastro_normaliza_email(db):
    cliente = Cliente.cadastrar("João Lima", "  JOAO@Exemplo.TEST ", "senha123")
    assert cliente.email == "joao@exemplo.test"


def test_cadastro_recusa_email_repetido(conta):
    with pytest.raises(ErroNegocio, match="Já existe uma conta"):
        Cliente.cadastrar("Outra Maria", "MARIA@exemplo.test", "outrasenha")


@pytest.mark.parametrize("nome,email,senha,trecho", [
    ("Al", "al@exemplo.test", "senha123", "nome completo"),
    ("Ana Paula", "email-invalido", "senha123", "e-mail válido"),
    ("Ana Paula", "ana@exemplo.test", "123", "pelo menos 6"),
])
def test_cadastro_valida_campos(db, nome, email, senha, trecho):
    with pytest.raises(ErroNegocio, match=trecho):
        Cliente.cadastrar(nome, email, senha)


def test_autenticar_com_senha_errada(conta):
    with pytest.raises(ErroNegocio, match="E-mail ou senha incorretos"):
        Cliente.autenticar("maria@exemplo.test", "errada")


def test_autenticar_com_sucesso(conta):
    assert Cliente.autenticar("Maria@Exemplo.test", "segredo123").id == conta.id


def test_cupcake_disponivel_depende_de_estoque_e_ativo(cupcake):
    assert cupcake.disponivel
    cupcake.estoque = 0
    assert not cupcake.disponivel
    cupcake.estoque = 3
    cupcake.ativo = False
    assert not cupcake.disponivel


def test_cupcake_preencher_converte_preco_com_virgula(categoria):
    cupcake = Cupcake()
    cupcake.preencher({"nome": "Pistache", "preco": "14,90", "estoque": "7", "cor": "#b7d39a",
                       "categoria_id": str(categoria.id), "destaque": "on"})
    assert cupcake.preco == Decimal("14.90")
    assert cupcake.estoque == 7
    assert cupcake.destaque is True


def test_cupcake_preencher_reune_todos_os_erros(categoria):
    with pytest.raises(ErroNegocio) as erro:
        Cupcake().preencher({"nome": "A", "preco": "-1", "estoque": "x", "cor": "rosa", "categoria_id": ""})
    mensagem = erro.value.mensagem
    for trecho in ("nome", "preço", "estoque", "cor", "categoria"):
        assert trecho in mensagem


def test_avaliacao_registra_campos_obrigatorios(db):
    avaliacao = AvaliacaoTeste.registrar({"nome_testador": "Carlos Dias", "data_teste": "2026-11-20",
                                          "funcionou": "Cadastro e carrinho"})
    assert avaliacao.id is not None
    assert avaliacao.data_teste == date(2026, 11, 20)


def test_avaliacao_recusa_link_sem_http(db):
    with pytest.raises(ErroNegocio, match="http"):
        AvaliacaoTeste.registrar({"nome_testador": "Carlos Dias", "data_teste": "2026-11-20",
                                  "funcionou": "Tudo", "link_evidencias": "drive.google.com/x"})
