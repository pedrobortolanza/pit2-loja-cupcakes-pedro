# Laudo de qualidade

**Sistema:** Nuvem de Açúcar, loja virtual de cupcakes
**Versão avaliada:** publicação de 16/11/2026 (antes das correções). **Versão corrigida:** atualização com as correções deste laudo.
**Período de testes:** 28/10/2026 a 17/11/2026
**Responsável:** Pedro Rosa Bortolanza

## 1. Resumo

| Item | Resultado |
|---|---|
| Testes automatizados | 65 de 65 aprovados antes das correções; 92 de 92 depois (27 testes novos) |
| Testadores | 5 ([avaliações recebidas](03-avaliacoes-recebidas.md)) |
| Testadores que finalizaram um pedido sem ajuda | 4 de 5 (o testador 3 escolheu só montar o carrinho) |
| Erros que impedem a compra | Nenhum |
| Problemas encontrados | 2 |
| Problemas corrigidos | 2 de 2 |
| Sugestões recebidas | 5: 3 implementadas, 1 implementada em parte, 1 adiada |

Os prints de antes e depois estão em [docs/telas/laudo](../telas/laudo/). Foram tirados no sistema rodando localmente, com o mesmo código publicado e os dados de teste do `seed.py`.

## 2. Problemas encontrados e correções

| ID | Encontrado por | Tela / funcionalidade | Descrição do problema | Gravidade | Evidência (antes) | Correção feita | Evidência (depois) | Situação |
|---|---|---|---|---|---|---|---|---|
| B01 | Testador 1 | Finalizar pedido / endereço | No celular, era preciso digitar rua, bairro e cidade à mão mesmo depois de informar o CEP | Média | [antes-02](../telas/laudo/antes-02-finalizar-pedido.png) | Ao digitar os 8 números do CEP, o sistema consulta o serviço público ViaCEP e preenche rua, bairro e cidade, avisando o cliente para conferir e informar o número. Se o CEP não existir ou o serviço estiver fora do ar, aparece um aviso e o preenchimento manual continua funcionando | [depois-02](../telas/laudo/depois-02-finalizar-pedido.png) | Corrigido |
| B02 | Testador 4 | Finalizar pedido / entrega | Não era possível escolher o dia nem o horário da entrega, o que atrapalha encomendas para festas | Média | [antes-02](../telas/laudo/antes-02-finalizar-pedido.png), [antes-03](../telas/laudo/antes-03-pedido-confirmado.png) | Novo bloco "Quando?" na finalização: "O quanto antes" ou "Agendar dia e horário", com os próximos 7 dias e 4 faixas de horário. O agendamento aparece na tela do pedido e no painel do lojista. Duas colunas novas na tabela `pedido` (`data_agendada`, `faixa_horario`) | [depois-02](../telas/laudo/depois-02-finalizar-pedido.png), [depois-03](../telas/laudo/depois-03-pedido-confirmado.png), [depois-05](../telas/laudo/depois-05-painel-admin.png) | Corrigido |

**Gravidade:** Alta impede a compra ou expõe dados; Média atrapalha, mas tem contorno; Baixa é visual ou de texto.

## 3. Sugestões de melhoria

| ID | Sugerido por | Sugestão | Decisão | Motivo e evidência |
|---|---|---|---|---|
| S01 | Testador 2 | Tela "Minha conta" para editar nome e telefone | Implementada | Novo item "Minha conta" no menu, onde o cliente altera nome e telefone. O e-mail fica fixo porque é o login. Antes: [antes-01](../telas/laudo/antes-01-menu-cliente.png). Depois: [depois-04](../telas/laudo/depois-04-minha-conta.png) |
| S02 | Testadores 3 e 5 | Foto real do cupcake no cadastro e na vitrine | Implementada em parte | O lojista pode informar o link (https) de uma foto já publicada, e a vitrine, os detalhes, o carrinho e o painel passam a mostrar a foto; sem link, continua o desenho. O envio do arquivo direto do computador foi adiado: a Vercel não guarda arquivos enviados, e seria preciso contratar e configurar um armazenamento de imagens (ex.: Supabase Storage). Antes: [antes-06](../telas/laudo/antes-06-cadastro-cupcake.png). Depois: [depois-06b](../telas/laudo/depois-06b-cadastro-com-foto.png), [depois-08](../telas/laudo/depois-08-vitrine-com-foto.png) |
| S03 | Testador 3 | Frete por bairro em vez de valor fixo de R$ 7,00 | Adiada | Depende de a loja definir a área de entrega e o preço de cada bairro ou distância, o que é decisão de negócio e não existe no escopo atual. A regra atual (R$ 7,00 e grátis a partir de R$ 80,00) continua e é configurável em `cupcakes/config.py` |
| S04 | Testador 4 | Previsão de chegada na tela do pedido | Implementada | Pedidos "o quanto antes" mostram o horário previsto: entrega em até 60 minutos e retirada em até 30 minutos (prazos configuráveis em `cupcakes/config.py`). Pedidos agendados mostram o dia e a faixa escolhidos. Antes: [antes-03](../telas/laudo/antes-03-pedido-confirmado.png). Depois: [depois-03b](../telas/laudo/depois-03b-previsao-de-chegada.png) |
| S05 | Testador 5 | Relatório de vendas no painel (total do dia e sabores mais vendidos) | Implementada | Nova aba "Relatório de vendas": vendas e ticket médio do dia, total dos últimos 7 dias, pedidos em aberto e os 5 sabores mais vendidos. Pedidos cancelados não contam. Antes: [antes-05](../telas/laudo/antes-05-painel-admin.png). Depois: [depois-07](../telas/laudo/depois-07-relatorio-vendas.png) |

## 4. Funcionalidades não testadas

| Funcionalidade | Por que não foi testada | Ação |
|---|---|---|
| Pagamento com cartão (testador 1) | O testador optou só pelo Pix | Coberto pelo testador 2 e pelos testes automatizados |
| Finalização do pedido (testador 3) | O testador focou na vitrine e no carrinho | Coberto pelos testadores 1, 2 e 4 |

## 5. Testes automatizados após as correções

Cada correção ganhou testes novos, para não voltar a falhar. A lista completa está em [testes automatizados](../situacao-2-codificacao/03-testes-unitarios.md#correções-do-laudo-de-qualidade).

```
.venv/bin/python -m pytest
92 passed
```

| Item | Testes novos |
|---|---|
| B01 CEP automático | O campo e o aviso aparecem na finalização (a consulta ao ViaCEP roda no navegador e foi conferida no print depois-02) |
| B02 Agendamento | 11 testes: opcional, dia e horário válidos, dias fora do prazo, horário fora da lista, pedido agendado salvo e exibido |
| S01 Minha conta | 5 testes: edição, dados inválidos, exige login |
| S02 Foto | 5 testes: link salvo, links inválidos recusados (inclusive `http://` e `javascript:`), foto exibida na vitrine |
| S04 Previsão | 2 testes: prazo por forma de entrega e exibição na tela |
| S05 Relatório | 3 testes: soma ignorando cancelados, sem vendas, acesso só do administrador |

## 6. Conclusão

O sistema atende aos objetivos definidos no planejamento: vitrine, carrinho, pedido, pagamento simulado, acompanhamento da entrega e painel do lojista. Nos testes com 5 usuários, nenhum erro impediu a compra, e 4 testadores finalizaram pedidos sem ajuda.

Os 2 problemas de usabilidade apontados (endereço sem CEP automático e falta de agendamento) foram corrigidos. Das 5 sugestões, 3 foram implementadas por completo, a foto do cupcake foi implementada por link e o frete por bairro ficou para uma próxima versão. Os testes automatizados passaram de 65 para 92, todos aprovados.

Para uma próxima versão ficam: envio de foto direto do computador, frete por bairro ou distância e um pagamento real integrado a um provedor de pagamentos.
