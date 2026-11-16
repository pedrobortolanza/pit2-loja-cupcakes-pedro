# Como continuar o trabalho (leia primeiro)

Este arquivo explica onde o PIT II parou e o que falta fazer, para continuar em qualquer computador.

## 1. Onde está cada coisa

| O quê | Onde |
|---|---|
| Código e documentação | este repositório: https://github.com/pedrobortolanza/pit2-loja-cupcakes-pedro |
| Site no ar | https://pit2-loja-cupcakes.vercel.app |
| Painel da Vercel | vercel.com → time **ARKAN** → projeto **pit2-loja-cupcakes** |
| Banco de dados | supabase.com → organização **arkanpagesGEP** → projeto **loja-cupcakes** |
| Documento de entrega (docx) | [`entrega/PIT_atividade_preenchido.docx`](entrega/PIT_atividade_preenchido.docx) |
| Avaliações dos colegas | no site: entrar como admin → **Painel → Avaliações de teste** |

Contas de teste do site:

| Perfil | E-mail | Senha |
|---|---|---|
| Administrador | admin@nuvemdeacucar.test | r29jUCkk9ZC4 |
| Cliente | cliente@nuvemdeacucar.test | WQl1fP-geIeB |

Cartão de teste: `4111 1111 1111 1111`, validade `12/30`, CVV `123`.

## 2. O que já está pronto

- [x] Banco PostgreSQL no Supabase com tabelas e dados iniciais
- [x] Site completo em Python/Flask (MVC): vitrine, carrinho, login, pedido, pagamento simulado, acompanhamento, painel do lojista, formulário de avaliação
- [x] 56 testes automatizados passando
- [x] Documentação das 3 situações em [`docs/`](docs/) (histórias, UML, telas, banco, dicionário de dados, arquitetura, manual, plano de testes, modelo do laudo)
- [x] Projeto criado na Vercel e ligado a este repositório (cada `git push` publica o site)
- [x] Docx de entrega preenchido com nome, links e dados técnicos

## 3. O que falta (em ordem)

### Passo 1: ligar o site ao banco (uma vez só, 5 minutos)
Sem isso, o site no ar mostra erro.
1. No Supabase, abra o projeto **loja-cupcakes** → botão **Connect** (no topo) → aba **Connection string** → escolha **Transaction pooler**.
2. Copie a string (começa com `postgresql://postgres.hjqdsyrfzikjeqsttocp:`). Onde estiver `[YOUR-PASSWORD]`, coloque a senha do banco. Se não souber a senha: **Project Settings → Database → Reset database password**.
3. Na Vercel, projeto **pit2-loja-cupcakes** → **Settings → Environment Variables** → **Add**:
   - Key: `DATABASE_URL`
   - Value: a string do passo 2
   - Environments: Production e Preview
4. Ainda em **Settings**, vá em **Deployment Protection** → **Vercel Authentication** e troque para **Standard Protection** (ou desligue). Do jeito que o time ARKAN veio configurado, só quem tem login na Vercel consegue abrir o site, e os colegas e o tutor veriam uma tela de login da Vercel. Com Standard Protection, o endereço principal fica aberto para todos.
5. Em **Deployments**, clique nos três pontinhos do último deploy → **Redeploy**.
6. Abra o site, entre como admin e faça um pedido de teste. Se aparecer a vitrine com os cupcakes, está funcionando.

> `SECRET_KEY` já está configurada na Vercel. Não precisa mexer.

### Passo 2: gravar o vídeo 1 (no mínimo 5 minutos, narrado)
Roteiro sugerido (~6 min):
1. **(30 s)** Apresentação: seu nome, o PIT II, a loja de cupcakes e o que mudou desde o PIT I (no PIT I você fez os wireframes; agora virou um sistema funcionando).
2. **(1 min)** GitHub: mostre a pasta `docs` com as 3 situações, abra o UML (os diagramas aparecem desenhados) e o dicionário de dados.
3. **(2 min)** Como cliente: vitrine, busca, filtro, detalhes, carrinho (tente passar do estoque para mostrar o erro), criar conta, finalizar com entrega + Pix, mostrar a linha do tempo. Faça também um pedido com cartão inválido para mostrar a recusa.
4. **(1 min 30 s)** Como admin: painel de pedidos, avançar o status (volte na conta do cliente e mostre que mudou), cadastrar um cupcake novo e tirar um da vitrine.
5. **(40 s)** Testes: no terminal, rode `.venv/bin/python -m pytest -v` e mostre os 56 aprovados. Mostre o Supabase com as tabelas.
6. **(20 s)** Tecnologias: Python + Flask MVC, PostgreSQL no Supabase, Vercel, Pytest.

Suba no YouTube como **Não listado** e cole o link no docx (campo "Link do vídeo narrado") e no `README.md`.

### Passo 3: testes com os 5 colegas
1. Mande para cada colega a mensagem da seção 5 abaixo.
2. Eles preenchem o formulário no próprio site. As respostas aparecem em **Painel → Avaliações de teste**.
3. Copie cada avaliação para as 5 tabelas do docx e para [`docs/situacao-3-testes/03-avaliacoes-recebidas.md`](docs/situacao-3-testes/03-avaliacoes-recebidas.md).

### Passo 4: corrigir e preencher o laudo
1. Para cada problema ou sugestão, decida: corrigir, adiar ou não aplicar (com o motivo).
2. Corrija o que for pertinente (veja a seção 6 para trabalhar no código).
3. Preencha [`docs/situacao-3-testes/04-laudo-de-qualidade.md`](docs/situacao-3-testes/04-laudo-de-qualidade.md) com prints de antes e depois, e copie o laudo para o campo "Laudo de Qualidade" do docx.

### Passo 5: gravar o vídeo 2 (até 5 minutos)
Mostre o que os colegas apontaram e como ficou depois da correção (antes e depois de cada item). Cole o link no campo "Vídeo da Solução atualizada" do docx.

### Passo 6: entregar
- Preencha o **RGM** no docx (deixei em branco porque este repositório é público).
- Exporte o docx em PDF.
- Entregue no AVA, junto com o link do GitHub.

## 4. Precisa ter erro para os colegas acharem?

**Não coloque erros de propósito.** O material pede para não esconder falhas, e um erro plantado e depois "descoberto" aparece no vídeo de correções como algo forçado. Testes com pessoas reais quase sempre encontram coisas de verdade (textos confusos, algo que não funciona no celular de alguém, um fluxo que não ficou óbvio).

Além disso, o sistema tem **limitações reais conhecidas**, que os colegas devem apontar como "faltou" ou "sugestão". São ótimas para o laudo e fáceis de resolver depois:

| Limitação | Possível melhoria |
|---|---|
| Não existe "esqueci minha senha" | Tela para redefinir a senha |
| O endereço não é preenchido pelo CEP | Buscar o endereço automaticamente (API ViaCEP) |
| O cliente não consegue editar o nome e o telefone depois do cadastro | Tela "Minha conta" |
| O cupcake é um desenho, não uma foto | Upload de foto no cadastro do cupcake |
| A taxa de entrega é fixa (R$ 7,00) | Frete por bairro ou distância |
| O pedido não avisa por e-mail quando muda de status | Notificação por e-mail |
| O administrador não vê relatório de vendas | Totais do dia e sabores mais vendidos |

Se um colega não apontar nada, registre no laudo que não houve falha naquele teste. Isso também é resultado.

## 5. Mensagem pronta para os colegas

> Oi! Estou fazendo o Projeto Integrador e preciso que você teste meu sistema, uma loja virtual de cupcakes. Leva uns 10 minutos.
>
> 1. Abra: https://pit2-loja-cupcakes.vercel.app
> 2. Navegue, coloque cupcakes no carrinho, crie uma conta e faça um pedido. Teste com Pix e com cartão (use o cartão de teste 4111 1111 1111 1111, validade 12/30, CVV 123; nada é cobrado). Tente também errar de propósito: endereço vazio, cartão inválido, quantidade maior que o estoque.
> 3. Veja o pedido em "Meus pedidos" e tente cancelar.
> 4. Se possível, teste no celular também.
> 5. No fim, preencha a avaliação: https://pit2-loja-cupcakes.vercel.app/avaliacao/
>    Se algo der errado, tire um print, suba no Google Drive com o link aberto e cole no formulário.
>
> Pode ser bem sincero(a), os erros me ajudam. Obrigado!

## 6. Trabalhar no código em outro computador

Precisa de **Git** e **Python 3.9 ou mais novo**.

```bash
git clone https://github.com/pedrobortolanza/pit2-loja-cupcakes-pedro.git
cd pit2-loja-cupcakes-pedro
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/flask --app app criar-banco
.venv/bin/flask --app app run
```

No Windows, troque `.venv/bin/` por `.venv\Scripts\`.

Abra http://localhost:5000. Localmente o site usa um banco SQLite próprio (arquivo `instance/loja.db`), com os mesmos dados iniciais e as mesmas contas de teste, então dá para testar à vontade sem mexer no banco real.

Depois de mudar algo:

```bash
.venv/bin/python -m pytest
git add -A
git commit -m "Descreva a correção"
git push
```

O `git push` publica o site na Vercel sozinho em cerca de 1 minuto.

Se for usar o Claude no outro computador, peça para ele ler este arquivo (`COMO-CONTINUAR.md`) primeiro.

### Onde mexer para cada tipo de correção

| Quero mudar... | Arquivo |
|---|---|
| Textos e telas | `cupcakes/views/` (HTML) |
| Cores e layout | `public/static/css/style.css` |
| Comportamento na tela (mostrar/esconder campos) | `public/static/js/app.js` |
| Regras: frete, limite por item | `cupcakes/config.py` |
| Regras do carrinho, pedido e pagamento | `cupcakes/services/` |
| Validações de cadastro e cupcake | `cupcakes/models/` |
| Rotas e mensagens de sucesso e erro | `cupcakes/controllers/` |
| Sabores e contas iniciais | `cupcakes/seed.py` e `database/seed.sql` |

Se mudar a estrutura de uma tabela (`cupcakes/models/`), também é preciso alterar o banco no Supabase (SQL Editor) e atualizar `database/schema.sql`.

## 7. Cuidados

- **O Supabase gratuito pausa o projeto depois de 7 dias sem uso.** Enquanto o trabalho estiver em avaliação, abra o site de vez em quando. Se pausar, entre no Supabase e clique em **Restore project**.
- As senhas de teste estão públicas neste repositório, então qualquer pessoa pode entrar como admin. Para um trabalho acadêmico não tem problema, mas se alguém bagunçar os dados, é só restaurar pelo SQL Editor do Supabase.
- Nunca coloque a `DATABASE_URL` (que contém a senha do banco) em nenhum arquivo do repositório. Ela fica só na Vercel.
