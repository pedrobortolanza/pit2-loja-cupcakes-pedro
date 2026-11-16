# Plano de testes: verificação e validação

## Verificação (o produto foi construído certo?)

Feita durante o desenvolvimento, comparando o código com a especificação.

| Atividade | Como foi feita | Evidência |
|---|---|---|
| Revisão das histórias contra o código | Cada regra de negócio (RN01 a RN14) foi conferida no model ou service que a implementa | [testes-unitarios](../situacao-2-codificacao/03-testes-unitarios.md), coluna "Regra verificada" |
| Testes unitários | Pytest nos models e services | 39 testes |
| Testes de integração | Pytest com o cliente HTTP do Flask, percorrendo rotas, controllers, views e banco | 17 testes |
| Teste de sistema manual | Navegação no site rodando localmente: vitrine, carrinho, login, finalização com erro e com sucesso, painel e versão de celular | [capturas de tela](../telas/) |
| Revisão de segurança | CSRF, hash de senha, permissão de admin, isolamento de pedidos e RLS no banco conferidos (o Supabase Advisor não aponta alertas de risco) | [arquitetura](../situacao-2-codificacao/01-arquitetura.md#segurança-e-tratamento-de-erros) |

## Validação (construímos o produto certo?)

Feita com 5 colegas (dublês de usuários), que usam o sistema publicado como clientes de verdade.

### Roteiro enviado aos testadores

1. Abra o site: **https://pit2-loja-cupcakes.vercel.app**
2. Navegue pela vitrine, busque um sabor e filtre por categoria.
3. Abra um cupcake e adicione 2 unidades ao carrinho.
4. Tente adicionar mais do que o estoque disponível.
5. No carrinho, mude quantidades e remova um item.
6. Clique em Finalizar pedido, crie uma conta e finalize:
   - uma vez com **entrega + Pix**;
   - uma vez com **retirada + cartão** (use `4111 1111 1111 1111`, validade `12/30`, CVV `123`);
   - tente também com um cartão inválido e sem endereço, para ver as mensagens de erro.
7. Abra "Meus pedidos", veja a linha do tempo e cancele um dos pedidos.
8. (Opcional) Entre como administrador (`admin@nuvemdeacucar.test` / `r29jUCkk9ZC4`), avance o status de um pedido e cadastre um cupcake.
9. Teste também pelo celular.
10. Preencha o formulário: **https://pit2-loja-cupcakes.vercel.app/avaliacao/**. Para mostrar um erro, tire um print, suba no Google Drive com o link aberto e cole no campo de evidências.

### Critérios de aceitação da validação

- Pelo menos 4 dos 5 testadores conseguem finalizar um pedido sem ajuda.
- Nenhum erro que impeça a compra fica sem correção.
- Toda sugestão recebida é registrada no laudo, com a decisão (corrigida, adiada ou não aplicável) e o motivo.

## Rastreabilidade (modelo V)

| Nível do desenvolvimento | Teste correspondente |
|---|---|
| Requisitos (histórias e regras) | Teste de aceitação com os 5 colegas |
| Análise (casos de uso) | Teste de sistema manual + `test_compra_completa_com_cartao` |
| Arquitetura (MVC, banco) | Testes de integração em `test_rotas.py` |
| Código (models e services) | Testes unitários em `test_modelos.py` e `test_servicos.py` |
