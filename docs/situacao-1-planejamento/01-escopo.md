# 1. Escopo do projeto (revisado)

## Contexto

Uma loja de cupcakes gourmet quer vender pela internet. Na tentativa anterior, com outra empresa, os requisitos foram mal levantados, o aplicativo não funcionava e os clientes reclamaram tanto que ele foi retirado do ar. Este projeto parte do protótipo de telas feito no PIT I (Situação-problema 3: wireframes de login, catálogo, carrinho e perfil, mapa conceitual e mapa navegacional) e o transforma em um sistema web funcional.

**Nome fictício da loja:** Nuvem de Açúcar.

## O que mudou em relação ao PIT I (ciclo Kaizen)

| PIT I | PIT II (revisado) | Motivo |
|---|---|---|
| Só protótipo de baixa fidelidade das telas no Figma | Sistema web funcional com banco de dados | Entrega exigida no PIT II |
| Telas de login, catálogo, carrinho e perfil | Incluídas finalização do pedido, pagamento, acompanhamento da entrega, painel do lojista e páginas de erro | O briefing pede foco em vitrine, pedido, pagamento e entrega; faltavam as três últimas |
| Sem histórias de usuário, UML e banco | Histórias, backlog, casos de uso, classes, sequência, atividades, modelos do banco e dicionário de dados | A documentação precisava cobrir as três situações do PIT I |
| "Perfil do usuário" como tela separada | Substituído por "Meus pedidos", que é o que o cliente realmente consulta | Simplifica a navegação e foca no acompanhamento da entrega |
| Aplicativo mobile | Site responsivo (funciona no celular e no computador) | Um único código serve às duas plataformas, sem exigir instalação |

## Objetivo

Permitir que clientes escolham cupcakes numa vitrine virtual, façam o pedido, paguem (Pix, cartão ou dinheiro na entrega) e acompanhem a entrega, e que o lojista gerencie cardápio, estoque e status dos pedidos.

## Dentro do escopo

- Vitrine com busca por nome e filtro por categoria.
- Página de detalhes do cupcake.
- Cadastro, login e logout de clientes.
- Carrinho com alteração de quantidade e remoção de itens.
- Finalização com entrega em casa ou retirada na loja, cálculo de frete e frete grátis.
- Pagamento **simulado** (Pix, cartão de crédito com validação, dinheiro na entrega).
- Acompanhamento do pedido por linha do tempo e cancelamento enquanto não estiver em preparo.
- Painel do lojista: pedidos (avançar status e cancelar), cadastro e edição de cupcakes, controle de estoque e da vitrine.
- Formulário de avaliação para os testadores (Situação 3).

## Fora do escopo

- Cobrança real com operadora de pagamento (Pix e cartão são simulados).
- Cálculo de frete por distância (a taxa é fixa).
- Envio de e-mail ou SMS.
- Upload de fotos (cada cupcake é ilustrado por um desenho com a cor da cobertura).

## Partes interessadas

| Parte interessada | Interesse |
|---|---|
| Dono da loja | Vender mais pela internet sem repetir o fracasso do app anterior |
| Cliente | Comprar rápido, saber o preço final e acompanhar a entrega |
| Atendente/confeiteiro (administrador) | Ver os pedidos do dia e atualizar o andamento |
| Testadores (colegas) | Validar a solução e apontar falhas |

## Tecnologias

| Camada | Escolha |
|---|---|
| Front-end | HTML5, CSS3 e JavaScript puro, renderizados pelo Flask (Jinja2) |
| Back-end | Python 3 + Flask, padrão MVC |
| Banco de dados | PostgreSQL 17 no Supabase (em produção) e SQLite (local e nos testes) |
| ORM | SQLAlchemy |
| Testes | Pytest |
| Hospedagem | Vercel |
| Versionamento | Git + GitHub |
| Modo de codificação | Tradicional |
