from cupcakes import create_app
from cupcakes.config import ConfigTeste
from cupcakes.extensions import db as banco
from cupcakes.models import AvaliacaoTeste, Cliente, Pedido
from cupcakes.services.pedidos import datas_para_agendar
from tests.conftest import CARTAO_TESTE, ENDERECO, fazer_login


def texto(resposta):
    return resposta.get_data(as_text=True)


def test_vitrine_lista_cupcakes_ativos(cliente_http, cupcake, outro_cupcake, db):
    outro_cupcake.ativo = False
    db.session.commit()
    resposta = cliente_http.get("/")
    assert resposta.status_code == 200
    assert "Chocolate" in texto(resposta)
    assert "Baunilha" not in texto(resposta)


def test_vitrine_busca_por_nome(cliente_http, cupcake, outro_cupcake):
    resposta = cliente_http.get("/?busca=baun")
    assert "Baunilha" in texto(resposta)
    assert "Chocolate" not in texto(resposta)


def test_detalhe_de_cupcake_inexistente_mostra_404(cliente_http):
    resposta = cliente_http.get("/cupcake/999")
    assert resposta.status_code == 404
    assert "Página não encontrada" in texto(resposta)


def test_cadastro_pela_tela_ja_entra_na_conta(cliente_http):
    resposta = cliente_http.post("/cadastro", data={"nome": "Paulo Reis", "email": "paulo@exemplo.test",
                                                    "senha": "senha123", "confirmacao": "senha123"},
                                 follow_redirects=True)
    assert "Conta criada" in texto(resposta)
    assert "Sair (Paulo)" in texto(resposta)


def test_cadastro_com_senhas_diferentes(cliente_http):
    resposta = cliente_http.post("/cadastro", data={"nome": "Paulo Reis", "email": "paulo@exemplo.test",
                                                    "senha": "senha123", "confirmacao": "outra123"})
    assert resposta.status_code == 422
    assert "não são iguais" in texto(resposta)


def test_login_invalido_mostra_erro(cliente_http, conta):
    resposta = fazer_login(cliente_http, "maria@exemplo.test", "errada")
    assert resposta.status_code == 401
    assert "E-mail ou senha incorretos" in texto(resposta)


def test_login_nao_redireciona_para_outro_site(cliente_http, conta):
    resposta = cliente_http.post("/entrar", data={"email": "maria@exemplo.test", "senha": "segredo123",
                                                  "proximo": "//site-malicioso.test"})
    assert resposta.headers["Location"] == "/"


def test_finalizar_exige_login(cliente_http, cupcake):
    cliente_http.post(f"/carrinho/adicionar/{cupcake.id}", data={"quantidade": 1})
    resposta = cliente_http.get("/pedidos/finalizar")
    assert resposta.status_code == 302
    assert "/entrar" in resposta.headers["Location"]


def test_compra_completa_com_cartao(cliente_http, conta, cupcake, outro_cupcake):
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    cliente_http.post(f"/carrinho/adicionar/{cupcake.id}", data={"quantidade": 2})
    cliente_http.post(f"/carrinho/adicionar/{outro_cupcake.id}", data={"quantidade": 1})
    carrinho = cliente_http.get("/carrinho/")
    assert "R$ 28,00" in texto(carrinho)
    dados = dict(ENDERECO, forma_entrega="entrega", forma_pagamento="cartao", titular=CARTAO_TESTE["titular"],
                 numero_cartao=CARTAO_TESTE["numero"], validade=CARTAO_TESTE["validade"], cvv=CARTAO_TESTE["cvv"])
    resposta = cliente_http.post("/pedidos/finalizar", data=dados, follow_redirects=True)
    pagina = texto(resposta)
    assert "confirmado" in pagina
    assert "R$ 35,00" in pagina
    assert "final 1111" in pagina
    assert Pedido.query.count() == 1
    assert "0</span>" in texto(cliente_http.get("/carrinho/"))


def test_finalizar_sem_endereco_mostra_erro(cliente_http, conta, cupcake):
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    cliente_http.post(f"/carrinho/adicionar/{cupcake.id}", data={"quantidade": 1})
    resposta = cliente_http.post("/pedidos/finalizar", data={"forma_entrega": "entrega", "forma_pagamento": "pix"})
    assert resposta.status_code == 422
    assert "Preencha o endereço" in texto(resposta)


def test_cliente_nao_ve_pedido_de_outro_cliente(cliente_http, conta, cupcake):
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    cliente_http.post(f"/carrinho/adicionar/{cupcake.id}", data={"quantidade": 1})
    cliente_http.post("/pedidos/finalizar", data={"forma_entrega": "retirada", "forma_pagamento": "pix"})
    pedido = Pedido.query.one()
    cliente_http.post("/sair")
    Cliente.cadastrar("Intruso Silva", "intruso@exemplo.test", "intruso123")
    fazer_login(cliente_http, "intruso@exemplo.test", "intruso123")
    assert cliente_http.get(f"/pedidos/{pedido.id}").status_code == 404


def test_painel_bloqueia_cliente_comum(cliente_http, conta):
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    resposta = cliente_http.get("/admin/")
    assert resposta.status_code == 403
    assert "Acesso negado" in texto(resposta)


def test_admin_avanca_status_do_pedido(cliente_http, conta, conta_admin, cupcake):
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    cliente_http.post(f"/carrinho/adicionar/{cupcake.id}", data={"quantidade": 1})
    cliente_http.post("/pedidos/finalizar", data={"forma_entrega": "retirada", "forma_pagamento": "pix"})
    cliente_http.post("/sair")
    fazer_login(cliente_http, "admin@exemplo.test", "admin12345")
    pedido = Pedido.query.one()
    resposta = cliente_http.post(f"/admin/pedidos/{pedido.id}/avancar", follow_redirects=True)
    assert "Em preparo" in texto(resposta)


def test_admin_cadastra_cupcake(cliente_http, conta_admin, categoria):
    fazer_login(cliente_http, "admin@exemplo.test", "admin12345")
    resposta = cliente_http.post("/admin/cupcakes/novo", data={"nome": "Café", "descricao": "Com espresso",
                                                               "preco": "12,50", "estoque": "8", "cor": "#7b4b2a",
                                                               "categoria_id": str(categoria.id)},
                                 follow_redirects=True)
    assert "Café foi salvo" in texto(resposta)
    assert "R$ 12,50" in texto(cliente_http.get("/"))


def test_admin_cadastro_invalido_mostra_erros(cliente_http, conta_admin, categoria):
    fazer_login(cliente_http, "admin@exemplo.test", "admin12345")
    resposta = cliente_http.post("/admin/cupcakes/novo", data={"nome": "", "preco": "abc", "estoque": "-2",
                                                               "cor": "#ffffff", "categoria_id": str(categoria.id)})
    assert resposta.status_code == 422
    assert "preço maior que zero" in texto(resposta)


def test_formulario_de_avaliacao_salva_resposta(cliente_http):
    resposta = cliente_http.post("/avaliacao/", data={"nome_testador": "Ana Testadora", "data_teste": "2026-11-20",
                                                      "funcionou": "Cadastro e pedido com Pix",
                                                      "nao_funcionou": "Filtro de categoria no celular"},
                                 follow_redirects=True)
    assert "Avaliação enviada" in texto(resposta)
    assert AvaliacaoTeste.query.count() == 1


def test_post_sem_token_csrf_e_recusado():
    class ConfigComCsrf(ConfigTeste):
        CSRF_ENABLED = True
    aplicacao = create_app(ConfigComCsrf)
    with aplicacao.app_context():
        banco.create_all()
        resposta = aplicacao.test_client().post("/avaliacao/", data={"nome_testador": "Sem Token"})
        assert resposta.status_code == 400
        assert "Requisição inválida" in texto(resposta)
        banco.drop_all()


# Correções do laudo de qualidade

def test_finalizar_mostra_cep_automatico_e_agendamento(cliente_http, conta, cupcake):
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    cliente_http.post(f"/carrinho/adicionar/{cupcake.id}", data={"quantidade": 1})
    pagina = texto(cliente_http.get("/pedidos/finalizar"))
    assert "preenchemos rua, bairro e cidade" in pagina
    assert "Agendar dia e horário" in pagina
    assert "15h às 18h" in pagina


def test_pedido_agendado_pela_tela(cliente_http, conta, cupcake):
    dia = datas_para_agendar()[1]
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    cliente_http.post(f"/carrinho/adicionar/{cupcake.id}", data={"quantidade": 1})
    resposta = cliente_http.post("/pedidos/finalizar", data={"forma_entrega": "retirada", "forma_pagamento": "pix",
                                                             "quando": "agendado", "data_agendada": dia.isoformat(),
                                                             "faixa_horario": "15h às 18h"}, follow_redirects=True)
    assert "Agendado para" in texto(resposta)
    assert "15h às 18h" in texto(resposta)


def test_pedido_sem_agendamento_mostra_previsao(cliente_http, conta, cupcake):
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    cliente_http.post(f"/carrinho/adicionar/{cupcake.id}", data={"quantidade": 1})
    resposta = cliente_http.post("/pedidos/finalizar", data={"forma_entrega": "retirada", "forma_pagamento": "pix",
                                                             "quando": "agora"}, follow_redirects=True)
    assert "Previsão: pronto para retirar até" in texto(resposta)


def test_minha_conta_edita_dados(cliente_http, conta):
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    assert "Minha conta" in texto(cliente_http.get("/"))
    resposta = cliente_http.post("/conta/", data={"nome": "Maria Souza Lima", "telefone": "(41) 98888-7777"},
                                 follow_redirects=True)
    assert "Seus dados foram atualizados" in texto(resposta)
    assert Cliente.query.one().telefone == "(41) 98888-7777"


def test_minha_conta_exige_login(cliente_http):
    resposta = cliente_http.get("/conta/")
    assert resposta.status_code == 302
    assert "/entrar" in resposta.headers["Location"]


def test_relatorio_de_vendas_so_para_admin(cliente_http, conta, conta_admin, cupcake):
    fazer_login(cliente_http, "maria@exemplo.test", "segredo123")
    cliente_http.post(f"/carrinho/adicionar/{cupcake.id}", data={"quantidade": 2})
    cliente_http.post("/pedidos/finalizar", data={"forma_entrega": "retirada", "forma_pagamento": "pix"})
    assert cliente_http.get("/admin/relatorio").status_code == 403
    cliente_http.post("/sair")
    fazer_login(cliente_http, "admin@exemplo.test", "admin12345")
    pagina = texto(cliente_http.get("/admin/relatorio"))
    assert "Vendas de hoje" in pagina
    assert "R$ 20,00" in pagina
    assert "Chocolate" in pagina


def test_vitrine_mostra_foto_quando_cadastrada(cliente_http, cupcake, db):
    cupcake.foto_url = "https://exemplo.test/chocolate.jpg"
    db.session.commit()
    assert 'src="https://exemplo.test/chocolate.jpg"' in texto(cliente_http.get("/"))
