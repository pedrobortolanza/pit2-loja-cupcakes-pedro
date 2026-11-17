# Nuvem de Açúcar: loja virtual de cupcakes

Projeto Integrador Transdisciplinar em Engenharia de Software II.

Sistema web para uma loja de cupcakes gourmet: vitrine virtual, carrinho, pedido, pagamento (simulado) e acompanhamento da entrega, com painel para o lojista.

- **Antes de tudo, leia [COMO-CONTINUAR.md](COMO-CONTINUAR.md).**
- **Sistema no ar:** https://pit2-loja-cupcakes.vercel.app
- **Vídeo de demonstração:** (adicionar o link do YouTube depois de gravar)

| | |
|---|---|
| Back-end | Python 3 + Flask (padrão MVC) |
| Front-end | HTML, CSS e JavaScript |
| Banco de dados | PostgreSQL (Supabase) |
| Hospedagem | Vercel |
| Testes | Pytest (92 testes) |
| Modo de codificação | Tradicional |

## Documentação

| Situação | Conteúdo |
|---|---|
| [1 · Planejamento revisado](docs/situacao-1-planejamento/) | [Escopo](docs/situacao-1-planejamento/01-escopo.md) · [Histórias e backlog](docs/situacao-1-planejamento/02-historias-de-usuario.md) · [UML](docs/situacao-1-planejamento/03-uml.md) · [Interface](docs/situacao-1-planejamento/04-interface.md) · [Banco e dicionário de dados](docs/situacao-1-planejamento/05-banco-de-dados.md) |
| [2 · Codificação](docs/situacao-2-codificacao/) | [Arquitetura](docs/situacao-2-codificacao/01-arquitetura.md) · [Manual de uso](docs/situacao-2-codificacao/02-manual-de-uso.md) · [Testes automatizados](docs/situacao-2-codificacao/03-testes-unitarios.md) |
| [3 · Testes com usuários](docs/situacao-3-testes/) | [Plano de testes](docs/situacao-3-testes/01-plano-de-testes.md) · [Modelo de avaliação](docs/situacao-3-testes/02-modelo-de-avaliacao.md) · [Avaliações recebidas](docs/situacao-3-testes/03-avaliacoes-recebidas.md) · [Laudo de qualidade](docs/situacao-3-testes/04-laudo-de-qualidade.md) |

Capturas de tela: [docs/telas](docs/telas/). Scripts do banco: [database/](database/).

## Contas de teste

| Perfil | E-mail | Senha |
|---|---|---|
| Administrador | admin@nuvemdeacucar.test | r29jUCkk9ZC4 |
| Cliente | cliente@nuvemdeacucar.test | WQl1fP-geIeB |

Cartão de teste: `4111 1111 1111 1111`, validade futura, CVV `123`. Nenhum valor é cobrado.

## Rodar localmente

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/flask --app app criar-banco
.venv/bin/flask --app app run
```

Sem `DATABASE_URL`, o sistema usa SQLite local. Para usar o PostgreSQL, defina `DATABASE_URL` com a string de conexão do Supabase (modo *transaction pooler*) e `SECRET_KEY` com um valor aleatório.

```bash
.venv/bin/python -m pytest -v
```

## Publicar na Vercel

1. Importe este repositório na Vercel (o Flask é detectado automaticamente por `app.py`).
2. Em *Settings → Environment Variables*, crie `DATABASE_URL` e `SECRET_KEY`.
3. Rode `database/schema.sql` e `database/seed.sql` no SQL Editor do Supabase (só na primeira vez).
