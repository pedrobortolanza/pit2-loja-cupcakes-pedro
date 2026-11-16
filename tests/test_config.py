import pytest

from cupcakes.config import normalizar_url_banco

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


def test_url_sqlite_nao_muda():
    assert normalizar_url_banco("sqlite:///loja.db") == "sqlite:///loja.db"
