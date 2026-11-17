from datetime import date, timedelta
from decimal import Decimal

import pytest

from cupcakes.erros import ErroNegocio
from cupcakes.models import Pedido
from cupcakes.models.base import agora, como_utc, hoje_local
from cupcakes.services.carrinho import Carrinho
from cupcakes.services.pagamentos import numero_cartao_valido, processar_pagamento, validade_cartao_valida
from cupcakes.services.pedidos import (FAIXAS_HORARIO, avancar_status, calcular_taxa_entrega, cancelar_pedido,
                                       criar_pedido, datas_para_agendar, validar_agendamento, validar_endereco)
from cupcakes.services.relatorio import resumo_vendas
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


# Correções do laudo de qualidade (B02, S04, S05)

HOJE = date(2026, 11, 18)


def test_agendamento_e_opcional():
    assert validar_agendamento({}, HOJE) == (None, None)
    assert validar_agendamento({"quando": "agora", "data_agendada": "2026-11-19"}, HOJE) == (None, None)


def test_agendamento_aceita_dia_e_horario_validos():
    dados = {"quando": "agendado", "data_agendada": "2026-11-20", "faixa_horario": FAIXAS_HORARIO[2]}
    assert validar_agendamento(dados, HOJE) == (date(2026, 11, 20), FAIXAS_HORARIO[2])


@pytest.mark.parametrize("data", ["2026-11-18", "2026-11-26", "2026-11-17", "amanha", ""])
def test_agendamento_recusa_dia_fora_do_prazo(data):
    with pytest.raises(ErroNegocio, match="Escolha um dia"):
        validar_agendamento({"quando": "agendado", "data_agendada": data, "faixa_horario": FAIXAS_HORARIO[0]}, HOJE)


def test_agendamento_exige_horario_da_lista():
    with pytest.raises(ErroNegocio, match="horário"):
        validar_agendamento({"quando": "agendado", "data_agendada": "2026-11-19", "faixa_horario": "03h às 04h"}, HOJE)


def test_datas_para_agendar_vao_de_amanha_ate_7_dias():
    datas = datas_para_agendar(HOJE)
    assert datas[0] == date(2026, 11, 19)
    assert datas[-1] == date(2026, 11, 25)
    assert len(datas) == 7


def test_pedido_agendado_guarda_dia_e_horario(db, conta, cupcake):
    agendamento = {"quando": "agendado", "data_agendada": "2026-11-21", "faixa_horario": FAIXAS_HORARIO[3]}
    pedido = criar_pedido(conta, Carrinho({str(cupcake.id): 1}), "retirada", {}, "pix", {}, "", CONFIG,
                          dados_agendamento=agendamento, hoje=HOJE)
    assert pedido.agendado
    assert pedido.data_agendada == date(2026, 11, 21)
    assert pedido.faixa_horario == FAIXAS_HORARIO[3]
    assert pedido.previsao(60, 30) is None


def test_previsao_de_chegada_depende_da_forma_de_entrega(db, conta, cupcake):
    entrega = criar_pedido(conta, Carrinho({str(cupcake.id): 1}), "entrega", ENDERECO, "pix", {}, "", CONFIG)
    retirada = criar_pedido(conta, Carrinho({str(cupcake.id): 1}), "retirada", {}, "pix", {}, "", CONFIG)
    assert entrega.previsao(60, 30) - como_utc(entrega.criado_em) == timedelta(minutes=60)
    assert retirada.previsao(60, 30) - como_utc(retirada.criado_em) == timedelta(minutes=30)
    cancelar_pedido(entrega)
    assert entrega.previsao(60, 30) is None


def test_relatorio_soma_vendas_e_ignora_cancelados(db, conta, cupcake, outro_cupcake):
    criar_pedido(conta, Carrinho({str(cupcake.id): 2}), "retirada", {}, "pix", {}, "", CONFIG)
    criar_pedido(conta, Carrinho({str(outro_cupcake.id): 3}), "retirada", {}, "pix", {}, "", CONFIG)
    cancelado = criar_pedido(conta, Carrinho({str(cupcake.id): 1}), "retirada", {}, "pix", {}, "", CONFIG)
    cancelar_pedido(cancelado)
    antigo = criar_pedido(conta, Carrinho({str(outro_cupcake.id): 1}), "retirada", {}, "pix", {}, "", CONFIG)
    antigo.criado_em = agora() - timedelta(days=30)
    db.session.commit()

    resumo = resumo_vendas(Pedido.query.all(), hoje_local())
    assert resumo["vendas_hoje"] == Decimal("44.00")
    assert resumo["pedidos_hoje"] == 2
    assert resumo["ticket_medio_hoje"] == Decimal("22.00")
    assert resumo["pedidos_semana"] == 2
    assert resumo["cancelados"] == 1
    assert resumo["em_aberto"] == 3
    assert [sabor["nome"] for sabor in resumo["mais_vendidos"]] == ["Baunilha", "Chocolate"]
    assert resumo["mais_vendidos"][0]["quantidade"] == 4


def test_relatorio_sem_vendas():
    resumo = resumo_vendas([], HOJE)
    assert resumo["vendas_hoje"] == Decimal("0.00")
    assert resumo["ticket_medio_hoje"] == Decimal("0.00")
    assert resumo["mais_vendidos"] == []
