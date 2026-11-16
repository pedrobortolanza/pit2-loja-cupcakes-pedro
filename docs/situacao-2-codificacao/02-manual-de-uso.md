# Manual de uso

**Endereço do sistema:** LINK_DA_VERCEL

> Ambiente de demonstração: nenhum pagamento é cobrado de verdade.

## Contas de teste

| Perfil | E-mail | Senha |
|---|---|---|
| Administrador | admin@nuvemdeacucar.test | r29jUCkk9ZC4 |
| Cliente | cliente@nuvemdeacucar.test | WQl1fP-geIeB |

Você também pode criar sua própria conta em **Entrar → Cadastre-se**.

**Cartão de teste:** número `4111 1111 1111 1111`, qualquer nome, validade futura (ex.: `12/30`) e CVV `123`.

## Para o cliente

### 1. Escolher os cupcakes
1. Na **Vitrine**, use **Buscar sabor** ou o filtro de **Categoria** e clique em **Filtrar**.
2. Clique em **Adicionar** para colocar 1 unidade no carrinho, ou abra o cupcake para escolher a quantidade.
3. Sabores com a etiqueta **Esgotado** não podem ser comprados.

### 2. Revisar o carrinho
1. Clique em **Carrinho** no topo. O número ao lado mostra quantos itens há.
2. Mude a quantidade e clique em **Atualizar**, ou clique em **Remover**.
3. O resumo mostra o subtotal, o frete (R$ 7,00, grátis a partir de R$ 80,00) e quanto falta para o frete grátis.

### 3. Finalizar o pedido
1. Clique em **Finalizar pedido**. Se não estiver logado, entre ou crie uma conta. O carrinho é mantido.
2. Escolha **Entrega em casa** (preencha o endereço) ou **Retirar na loja** (sem frete).
3. Escolha **Pix**, **Cartão de crédito** (preencha os dados do cartão de teste) ou **Dinheiro na entrega**.
4. Clique em **Confirmar pedido**. Se faltar algo, a mensagem vermelha no topo diz o que corrigir.

### 4. Acompanhar e cancelar
1. Depois de confirmar, a tela do pedido mostra a linha do tempo: Recebido → Em preparo → Saiu para entrega (ou Pronto para retirada) → Entregue.
2. Em **Meus pedidos** ficam todos os seus pedidos.
3. Enquanto o pedido estiver **Recebido**, o botão **Cancelar pedido** fica disponível. Depois disso, só a loja pode cancelar.

## Para o administrador

1. Entre com a conta de administrador. Você vai direto para o **Painel**.
2. **Pedidos:** veja todos os pedidos, filtre por status e clique em **Avançar** para mudar a etapa, ou **Cancelar** para cancelar e devolver o estoque.
3. **Cupcakes:** clique em **Cadastrar cupcake** ou **Editar**. Preencha nome, descrição, preço (pode usar vírgula), estoque, categoria e cor da cobertura (a prévia muda na hora). Use **Tirar da vitrine** para esconder um sabor sem apagá-lo.
4. **Avaliações de teste:** veja tudo o que os testadores enviaram pelo formulário.

## Para os testadores

Abra **LINK_DA_VERCEL/avaliacao/** (ou o link "Testou o site? Deixe sua avaliação" no rodapé) e preencha:
- seu nome e a data do teste;
- o que testou e funcionou;
- o que testou e não funcionou, e o que deve ser corrigido;
- o que não testou ou faltou, e por quê;
- sugestões;
- link dos prints (suba as imagens no Google Drive e cole o link compartilhado).

## Rodar no computador (desenvolvedor)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/flask --app app criar-banco
.venv/bin/flask --app app run
```

Abra http://localhost:5000. Sem a variável `DATABASE_URL`, o sistema usa um arquivo SQLite local.

Testes:

```bash
.venv/bin/python -m pytest
```
