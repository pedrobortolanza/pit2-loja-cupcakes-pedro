from datetime import date
from decimal import Decimal

import pytest

from cupcakes.erros import ErroNegocio
from cupcakes.services.carrinho import Carrinho
from cupcakes.services.pagamentos import numero_cartao_valido, processar_pagamento, validade_cartao_valida
from cupcakes.services.pedidos import avancar_status, calcular_taxa_entrega, cancelar_pedido, criar_pedido, validar_endereco
from tests.conftest import CARTAO_TESTE, ENDERECO

CONFIG = {"TAXA_ENTREGA": Decimal("7.00"), "FRETE_GRATIS_A_PARTIR": Decimal("80.00")}


def test_carrinho_soma_quantidades_do_mesmo_sabor(cupcake):
    carrinho = Carrinho()
    carrinho.adicionar(cupcake, 2)
    carrinho.adicionar(cupcake, 1)
    assert carrinho.quantidade_de(cupcake.id) == 3
    assert carrinho.subtotal() == Decimal("30.00")


def test_carrinho_nao_passa_do_estoque(cupcake):
    carrinho = Carrinho()
    with pytest.raises(ErroNegocio, match="Só temos 5"):
        carrinho.adicionar(cupcake, 6)


def test_carrinho_respeita_limite_por_item(outro_cupcake):
    carrinho = Carrinho(limite_por_item=20)
    with pytest.raises(ErroNegocio, match="limite é de 20"):
        carrinho.adicionar(outro_cupcake, 21)


def test_carrinho_recusa_cupcake_esgotado(db, cupcake):
    cupcake.estoque = 0
    db.session.commit()
    with pytest.raises(ErroNegocio, match="esgotado"):
        Carrinho().adicionar(cupcake, 1)


def test_carrinho_atualizar_com_zero_remove_item(cupcake):
    carrinho = Carrinho()
    carrinho.adicionar(cupcake, 2)
    carrinho.atualizar(cupcake, 0)
    assert carrinho.vazio


def test_carrinho_descarta_cupcake_retirado_da_vitrine(db, cupcake, outro_cupcake):
    carrinho = Carrinho({str(cupcake.id): 1, str(outro_cupcake.id): 2})
    cupcake.ativo = False
    db.session.commit()
    itens = carrinho.itens()
    assert [item["cupcake"].id for item in itens] == [outro_cupcake.id]
    assert carrinho.quantidade_total == 2


def test_carrinho_ignora_dados_corrompidos_da_sessao():
    carrinho = Carrinho({"1": "abc", "2": -3, "3": "2"})
    assert carrinho.para_sessao() == {"3": 2}


@pytest.mark.parametrize("subtotal,forma,esperado", [
    (Decimal("30.00"), "entrega", Decimal("7.00")),
    (Decimal("80.00"), "entrega", Decimal("0.00")),
    (Decimal("30.00"), "retirada", Decimal("0.00")),
])
def test_taxa_de_entrega(subtotal, forma, esperado):
    assert calcular_taxa_entrega(subtotal, forma, CONFIG["TAXA_ENTREGA"], CONFIG["FRETE_GRATIS_A_PARTIR"]) == esperado


def test_endereco_exige_campos_e_cep_valido():
    with pytest.raises(ErroNegocio) as erro:
        validar_endereco({"cep": "123", "logradouro": "", "numero": "", "bairro": "Centro", "cidade": "Curitiba"})
    assert "rua" in erro.value.mensagem and "número" in erro.value.mensagem and "CEP" in erro.value.mensagem


def test_endereco_remove_mascara_do_cep():
    assert validar_endereco(ENDERECO)["cep"] == "80010000"


def test_cartao_teste_passa_na_validacao_luhn():
    assert numero_cartao_valido("4111 1111 1111 1111")
    assert not numero_cartao_valido("4111 1111 1111 1112")
    assert not numero_cartao_valido("1234")


def test_validade_do_cartao():
    hoje = date(2026, 11, 16)
    assert validade_cartao_valida("11/26", hoje)
    assert not validade_cartao_valida("10/26", hoje)
    assert not validade_cartao_valida("13/30", hoje)
    assert not validade_cartao_valida("1230", hoje)


def test_pagamento_pix_aprovado_na_hora():
    pagamento = processar_pagamento("pix", Decimal("20.00"))
    assert pagamento.status == "aprovado"
    assert pagamento.codigo_transacao.startswith("PIX-")


def test_pagamento_dinheiro_fica_pendente():
    assert processar_pagamento("dinheiro", Decimal("20.00")).status == "pendente"


def test_pagamento_cartao_guarda_so_os_ultimos_digitos():
    pagamento = processar_pagamento("cartao", Decimal("20.00"), CARTAO_TESTE)
    assert pagamento.status == "aprovado"
    assert pagamento.final_cartao == "1111"


def test_pagamento_cartao_invalido_e_recusado():
    with pytest.raises(ErroNegocio, match="Pagamento recusado"):
        processar_pagamento("cartao", Decimal("20.00"), {"titular": "X", "numero": "123", "validade": "01/20", "cvv": "1"})


def test_criar_pedido_baixa_estoque_e_limpa_carrinho(db, conta, cupcake):
    carrinho = Carrinho()
    carrinho.adicionar(cupcake, 3)
    pedido = criar_pedido(conta, carrinho, "entrega", ENDERECO, "pix", {}, "Sem cebola", CONFIG)
    assert pedido.status == "recebido"
    assert pedido.subtotal == Decimal("30.00")
    assert pedido.taxa_entrega == Decimal("7.00")
    assert pedido.total == Decimal("37.00")
    assert pedido.itens[0].nome_cupcake == "Chocolate"
    assert cupcake.estoque == 2
    assert carrinho.vazio


def test_criar_pedido_com_carrinho_vazio(conta):
    with pytest.raises(ErroNegocio, match="vazio"):
        criar_pedido(conta, Carrinho(), "entrega", ENDERECO, "pix", {}, "", CONFIG)


def test_criar_pedido_quando_estoque_acabou_no_meio_da_compra(db, conta, cupcake):
    carrinho = Carrinho({str(cupcake.id): 4})
    cupcake.estoque = 2
    db.session.commit()
    with pytest.raises(ErroNegocio, match="estoque mudou"):
        criar_pedido(conta, carrinho, "retirada", {}, "pix", {}, "", CONFIG)
    assert cupcake.estoque == 2


def test_pagamento_recusado_nao_cria_pedido_nem_baixa_estoque(db, conta, cupcake):
    carrinho = Carrinho({str(cupcake.id): 2})
    with pytest.raises(ErroNegocio, match="Pagamento recusado"):
        criar_pedido(conta, carrinho, "retirada", {}, "cartao", {"numero": "1"}, "", CONFIG)
    assert cupcake.estoque == 5
    assert conta.pedidos == []
    assert not carrinho.vazio


def test_cliente_cancela_pedido_recebido_e_estoque_volta(db, conta, cupcake):
    pedido = criar_pedido(conta, Carrinho({str(cupcake.id): 2}), "retirada", {}, "pix", {}, "", CONFIG)
    cancelar_pedido(pedido)
    assert pedido.status == "cancelado"
    assert pedido.pagamento.status == "estornado"
    assert cupcake.estoque == 5


def test_cliente_nao_cancela_pedido_em_preparo(db, conta, cupcake):
    pedido = criar_pedido(conta, Carrinho({str(cupcake.id): 1}), "retirada", {}, "pix", {}, "", CONFIG)
    avancar_status(pedido)
    with pytest.raises(ErroNegocio, match="em preparo"):
        cancelar_pedido(pedido)
    cancelar_pedido(pedido, por_administrador=True)
    assert pedido.status == "cancelado"


def test_fluxo_de_status_da_entrega(db, conta, cupcake):
    pedido = criar_pedido(conta, Carrinho({str(cupcake.id): 1}), "entrega", ENDERECO, "dinheiro", {}, "", CONFIG)
    vistos = []
    while pedido.proximo_status:
        vistos.append(avancar_status(pedido).status)
    assert vistos == ["em_preparo", "saiu_para_entrega", "entregue"]
    assert pedido.pagamento.status == "aprovado"
    with pytest.raises(ErroNegocio):
        avancar_status(pedido)


def test_fluxo_de_status_da_retirada(db, conta, cupcake):
    pedido = criar_pedido(conta, Carrinho({str(cupcake.id): 1}), "retirada", {}, "pix", {}, "", CONFIG)
    assert pedido.fluxo == ["recebido", "em_preparo", "pronto_para_retirada", "entregue"]
