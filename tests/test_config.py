import pytest

from cupcakes.config import normalizar_url_banco, url_do_banco

BASE = "postgresql+psycopg://postgres.abc:{}@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"


@pytest.mark.parametrize("entrada,senha_esperada", [
    ("postgresql://postgres.abc:SenhaSimples1@aws-0-sa-east-1.pooler.supabase.com:6543/postgres", "SenhaSimples1"),
    ("postgresql://postgres.abc:p@ss#w/rd?@aws-0-sa-east-1.pooler.supabase.com:6543/postgres", "p%40ss%23w%2Frd%3F"),
    ("postgresql://postgres.abc:[minhasenha]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres", "minhasenha"),
    ("postgres://postgres.abc:ja%40codificada@aws-0-sa-east-1.pooler.supabase.com:6543/postgres", "ja%40codificada"),
    ("  postgresql://postgres.abc:espaco@aws-0-sa-east-1.pooler.supabase.com:6543/postgres\n", "espaco"),
])
def test_url_do_banco_codifica_a_senha(entrada, senha_esperada):
    assert normalizar_url_banco(entrada) == BASE.format(senha_esperada)


def test_url_da_integracao_perde_parametros_extras():
    entrada = ("postgres://postgres.abc:Senha1@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"
               "?sslmode=require&supa=base-pooler.x")
    assert normalizar_url_banco(entrada) == BASE.format("Senha1") + "?sslmode=require"


def test_senha_com_interrogacao_nao_e_confundida_com_parametros():
    entrada = "postgresql://postgres.abc:a?supa=1@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?supa=x"
    assert normalizar_url_banco(entrada) == BASE.format("a%3Fsupa%3D1")


def test_postgres_url_da_integracao_tem_prioridade(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://manual")
    monkeypatch.setenv("POSTGRES_URL", "postgresql://integracao")
    assert url_do_banco() == "postgresql://integracao"
    monkeypatch.delenv("POSTGRES_URL")
    assert url_do_banco() == "postgresql://manual"
    monkeypatch.delenv("DATABASE_URL")
    assert url_do_banco() == "sqlite:///loja.db"


def test_url_sqlite_nao_muda():
    assert normalizar_url_banco("sqlite:///loja.db") == "sqlite:///loja.db"
