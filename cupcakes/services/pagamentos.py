import re
import secrets
from datetime import date

from cupcakes.erros import ErroNegocio
from cupcakes.models import Pagamento
from cupcakes.models.base import agora


def numero_cartao_valido(numero):
    digitos = re.sub(r"\D", "", numero or "")
    if not 13 <= len(digitos) <= 19:
        return False
    soma = 0
    for posicao, digito in enumerate(reversed(digitos)):
        valor = int(digito)
        if posicao % 2 == 1:
            valor *= 2
            if valor > 9:
                valor -= 9
        soma += valor
    return soma % 10 == 0


def validade_cartao_valida(validade, hoje=None):
    hoje = hoje or date.today()
    combinacao = re.match(r"^(\d{2})/(\d{2})$", (validade or "").strip())
    if not combinacao:
        return False
    mes, ano = int(combinacao.group(1)), 2000 + int(combinacao.group(2))
    if not 1 <= mes <= 12:
        return False
    return (ano, mes) >= (hoje.year, hoje.month)


def processar_pagamento(forma, valor, dados_cartao=None, hoje=None):
    if forma == "pix":
        return Pagamento(forma="pix", status="aprovado", valor=valor,
                         codigo_transacao="PIX-" + secrets.token_hex(6).upper(), pago_em=agora())
    if forma == "dinheiro":
        return Pagamento(forma="dinheiro", status="pendente", valor=valor)
    if forma == "cartao":
        dados_cartao = dados_cartao or {}
        numero = re.sub(r"\D", "", dados_cartao.get("numero") or "")
        problemas = []
        if len((dados_cartao.get("titular") or "").strip()) < 3:
            problemas.append("informe o nome impresso no cartão")
        if not numero_cartao_valido(numero):
            problemas.append("o número do cartão é inválido")
        if not validade_cartao_valida(dados_cartao.get("validade"), hoje):
            problemas.append("a validade deve estar no formato MM/AA e não pode estar vencida")
        if not re.match(r"^\d{3,4}$", (dados_cartao.get("cvv") or "").strip()):
            problemas.append("o código de segurança deve ter 3 ou 4 números")
        if problemas:
            raise ErroNegocio("Pagamento recusado: " + "; ".join(problemas) + ".")
        return Pagamento(forma="cartao", status="aprovado", valor=valor, final_cartao=numero[-4:],
                         codigo_transacao="CARD-" + secrets.token_hex(6).upper(), pago_em=agora())
    raise ErroNegocio("Escolha uma forma de pagamento.")
