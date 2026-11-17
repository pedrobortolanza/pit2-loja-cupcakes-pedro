# Testes automatizados (Pytest)

**Resultado da última execução:** 92 testes, 92 aprovados, 0 falhas.

Como rodar:

```bash
.venv/bin/python -m pytest -v
```

Os testes usam um banco SQLite em memória criado do zero a cada teste, então não alteram o banco do Supabase.

| Arquivo | Camada testada | Quantidade |
|---|---|---|
| `tests/test_modelos.py` | Models (validações de Cliente, Cupcake e AvaliacaoTeste; Minha conta e foto do cupcake) | 20 |
| `tests/test_servicos.py` | Services (carrinho, frete, endereço, pagamento, pedido, cancelamento, status, agendamento, previsão, relatório de vendas) | 39 |
| `tests/test_rotas.py` | Controllers + Views (integração pelas rotas HTTP) | 24 |
| `tests/test_config.py` | Configuração (senha do banco com caracteres especiais, POSTGRES_URL da integração Supabase-Vercel) | 9 |

## O que cada grupo garante

### Models
| Teste | Regra verificada |
|---|---|
| test_cadastro_guarda_senha_criptografada | RNF02 senha nunca em texto puro |
| test_cadastro_normaliza_email | RN03 e-mail em minúsculas e sem espaços |
| test_cadastro_recusa_email_repetido | RN03 e-mail único |
| test_cadastro_valida_campos (3 casos) | nome, e-mail e RN02 senha mínima |
| test_autenticar_com_senha_errada / com_sucesso | HU06 login |
| test_cupcake_disponivel_depende_de_estoque_e_ativo | RN01 |
| test_cupcake_preencher_converte_preco_com_virgula | HU18 CA1 |
| test_cupcake_preencher_reune_todos_os_erros | HU18 CA2 |
| test_avaliacao_registra_campos_obrigatorios / recusa_link_sem_http | HU20 |

### Services
| Teste | Regra verificada |
|---|---|
| test_carrinho_soma_quantidades_do_mesmo_sabor | HU08 CA2 |
| test_carrinho_nao_passa_do_estoque | RN04 |
| test_carrinho_respeita_limite_por_item | RN05 |
| test_carrinho_recusa_cupcake_esgotado | HU01 CA2 |
| test_carrinho_atualizar_com_zero_remove_item | HU09 CA1 |
| test_carrinho_descarta_cupcake_retirado_da_vitrine | RN01 |
| test_carrinho_ignora_dados_corrompidos_da_sessao | robustez |
| test_taxa_de_entrega (3 casos) | RN06 |
| test_endereco_exige_campos_e_cep_valido / remove_mascara_do_cep | RN07 |
| test_cartao_teste_passa_na_validacao_luhn / test_validade_do_cartao | RN08 |
| test_pagamento_pix_aprovado_na_hora / dinheiro_fica_pendente | HU12 CA1 e CA3 |
| test_pagamento_cartao_guarda_so_os_ultimos_digitos | RN09 |
| test_pagamento_cartao_invalido_e_recusado | HU12 CA2 |
| test_criar_pedido_baixa_estoque_e_limpa_carrinho | HU13 CA1 e CA2, RN10 |
| test_criar_pedido_com_carrinho_vazio | UC07 pré-condição |
| test_criar_pedido_quando_estoque_acabou_no_meio_da_compra | UC07 alternativo D |
| test_pagamento_recusado_nao_cria_pedido_nem_baixa_estoque | UC07 alternativo E |
| test_cliente_cancela_pedido_recebido_e_estoque_volta | RN11, RN12 |
| test_cliente_nao_cancela_pedido_em_preparo | RN11 e UC11 alternativo B |
| test_fluxo_de_status_da_entrega / da_retirada | RN13, RN14 |

### Rotas (integração)
| Teste | O que simula |
|---|---|
| test_vitrine_lista_cupcakes_ativos / busca_por_nome | HU01, HU02 |
| test_detalhe_de_cupcake_inexistente_mostra_404 | HU04 CA3 |
| test_cadastro_pela_tela_ja_entra_na_conta / com_senhas_diferentes | UC05 |
| test_login_invalido_mostra_erro | HU06 CA1 |
| test_login_nao_redireciona_para_outro_site | RNF03 |
| test_finalizar_exige_login | UC07 alternativo A |
| test_compra_completa_com_cartao | UC07 + UC08 de ponta a ponta |
| test_finalizar_sem_endereco_mostra_erro | UC07 alternativo C |
| test_cliente_nao_ve_pedido_de_outro_cliente | HU14 CA2 |
| test_painel_bloqueia_cliente_comum | RNF05 |
| test_admin_avanca_status_do_pedido | UC11 |
| test_admin_cadastra_cupcake / cadastro_invalido_mostra_erros | UC12 |
| test_formulario_de_avaliacao_salva_resposta | HU20 |
| test_post_sem_token_csrf_e_recusado | proteção CSRF |

### Correções do laudo de qualidade
| Teste | Item do laudo |
|---|---|
| test_finalizar_mostra_cep_automatico_e_agendamento | B01 CEP e B02 agendamento na tela |
| test_agendamento_e_opcional / aceita_dia_e_horario_validos | B02 |
| test_agendamento_recusa_dia_fora_do_prazo (5 casos) / exige_horario_da_lista | B02 só de amanhã até 7 dias, horários da lista |
| test_datas_para_agendar_vao_de_amanha_ate_7_dias | B02 |
| test_pedido_agendado_guarda_dia_e_horario / test_pedido_agendado_pela_tela | B02 |
| test_previsao_de_chegada_depende_da_forma_de_entrega / test_pedido_sem_agendamento_mostra_previsao | S04 |
| test_cliente_atualiza_nome_e_telefone / nao_salva_dados_invalidos (2 casos) | S01 |
| test_minha_conta_edita_dados / test_minha_conta_exige_login | S01 |
| test_cupcake_guarda_link_da_foto / recusa_link_de_foto_invalido (3 casos) / test_vitrine_mostra_foto_quando_cadastrada | S02 |
| test_relatorio_soma_vendas_e_ignora_cancelados / test_relatorio_sem_vendas / test_relatorio_de_vendas_so_para_admin | S05 |

## Saída da execução

```
tests/test_config.py::test_url_do_banco_codifica_a_senha[postgresql://postgres.abc:SenhaSimples1@aws-0-sa-east-1.pooler.supabase.com:6543/postgres-SenhaSimples1] PASSED
tests/test_config.py::test_url_do_banco_codifica_a_senha[postgresql://postgres.abc:p@ss#w/rd?@aws-0-sa-east-1.pooler.supabase.com:6543/postgres-p%40ss%23w%2Frd%3F] PASSED
tests/test_config.py::test_url_do_banco_codifica_a_senha[postgresql://postgres.abc:[minhasenha]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres-minhasenha] PASSED
tests/test_config.py::test_url_do_banco_codifica_a_senha[postgres://postgres.abc:ja%40codificada@aws-0-sa-east-1.pooler.supabase.com:6543/postgres-ja%40codificada] PASSED
tests/test_config.py::test_url_do_banco_codifica_a_senha[  postgresql://postgres.abc:espaco@aws-0-sa-east-1.pooler.supabase.com:6543/postgres\n-espaco] PASSED
tests/test_config.py::test_url_da_integracao_perde_parametros_extras PASSED
tests/test_config.py::test_senha_com_interrogacao_nao_e_confundida_com_parametros PASSED
tests/test_config.py::test_postgres_url_da_integracao_tem_prioridade PASSED
tests/test_config.py::test_url_sqlite_nao_muda PASSED
tests/test_modelos.py::test_cadastro_guarda_senha_criptografada PASSED
tests/test_modelos.py::test_cadastro_normaliza_email PASSED
tests/test_modelos.py::test_cadastro_recusa_email_repetido PASSED
tests/test_modelos.py::test_cadastro_valida_campos[Al-al@exemplo.test-senha123-nome completo] PASSED
tests/test_modelos.py::test_cadastro_valida_campos[Ana Paula-email-invalido-senha123-e-mail v\xe1lido] PASSED
tests/test_modelos.py::test_cadastro_valida_campos[Ana Paula-ana@exemplo.test-123-pelo menos 6] PASSED
tests/test_modelos.py::test_autenticar_com_senha_errada PASSED
tests/test_modelos.py::test_autenticar_com_sucesso PASSED
tests/test_modelos.py::test_cupcake_disponivel_depende_de_estoque_e_ativo PASSED
tests/test_modelos.py::test_cupcake_preencher_converte_preco_com_virgula PASSED
tests/test_modelos.py::test_cupcake_preencher_reune_todos_os_erros PASSED
tests/test_modelos.py::test_avaliacao_registra_campos_obrigatorios PASSED
tests/test_modelos.py::test_avaliacao_recusa_link_sem_http PASSED
tests/test_modelos.py::test_cliente_atualiza_nome_e_telefone PASSED
tests/test_modelos.py::test_cliente_nao_salva_dados_invalidos[Ma--nome] PASSED
tests/test_modelos.py::test_cliente_nao_salva_dados_invalidos[Maria Souza-abc-telefone] PASSED
tests/test_modelos.py::test_cupcake_guarda_link_da_foto PASSED
tests/test_modelos.py::test_cupcake_recusa_link_de_foto_invalido[http://exemplo.test/a.jpg] PASSED
tests/test_modelos.py::test_cupcake_recusa_link_de_foto_invalido[javascript:alert(1)] PASSED
tests/test_modelos.py::test_cupcake_recusa_link_de_foto_invalido[https://exemplo.test/a b.jpg] PASSED
tests/test_rotas.py::test_vitrine_lista_cupcakes_ativos PASSED
tests/test_rotas.py::test_vitrine_busca_por_nome PASSED
tests/test_rotas.py::test_detalhe_de_cupcake_inexistente_mostra_404 PASSED
tests/test_rotas.py::test_cadastro_pela_tela_ja_entra_na_conta PASSED
tests/test_rotas.py::test_cadastro_com_senhas_diferentes PASSED
tests/test_rotas.py::test_login_invalido_mostra_erro PASSED
tests/test_rotas.py::test_login_nao_redireciona_para_outro_site PASSED
tests/test_rotas.py::test_finalizar_exige_login PASSED
tests/test_rotas.py::test_compra_completa_com_cartao PASSED
tests/test_rotas.py::test_finalizar_sem_endereco_mostra_erro PASSED
tests/test_rotas.py::test_cliente_nao_ve_pedido_de_outro_cliente PASSED
tests/test_rotas.py::test_painel_bloqueia_cliente_comum PASSED
tests/test_rotas.py::test_admin_avanca_status_do_pedido PASSED
tests/test_rotas.py::test_admin_cadastra_cupcake PASSED
tests/test_rotas.py::test_admin_cadastro_invalido_mostra_erros PASSED
tests/test_rotas.py::test_formulario_de_avaliacao_salva_resposta PASSED
tests/test_rotas.py::test_post_sem_token_csrf_e_recusado PASSED
tests/test_rotas.py::test_finalizar_mostra_cep_automatico_e_agendamento PASSED
tests/test_rotas.py::test_pedido_agendado_pela_tela PASSED
tests/test_rotas.py::test_pedido_sem_agendamento_mostra_previsao PASSED
tests/test_rotas.py::test_minha_conta_edita_dados PASSED
tests/test_rotas.py::test_minha_conta_exige_login PASSED
tests/test_rotas.py::test_relatorio_de_vendas_so_para_admin PASSED
tests/test_rotas.py::test_vitrine_mostra_foto_quando_cadastrada PASSED
tests/test_servicos.py::test_carrinho_soma_quantidades_do_mesmo_sabor PASSED
tests/test_servicos.py::test_carrinho_nao_passa_do_estoque PASSED
tests/test_servicos.py::test_carrinho_respeita_limite_por_item PASSED
tests/test_servicos.py::test_carrinho_recusa_cupcake_esgotado PASSED
tests/test_servicos.py::test_carrinho_atualizar_com_zero_remove_item PASSED
tests/test_servicos.py::test_carrinho_descarta_cupcake_retirado_da_vitrine PASSED
tests/test_servicos.py::test_carrinho_ignora_dados_corrompidos_da_sessao PASSED
tests/test_servicos.py::test_taxa_de_entrega[subtotal0-entrega-esperado0] PASSED
tests/test_servicos.py::test_taxa_de_entrega[subtotal1-entrega-esperado1] PASSED
tests/test_servicos.py::test_taxa_de_entrega[subtotal2-retirada-esperado2] PASSED
tests/test_servicos.py::test_endereco_exige_campos_e_cep_valido PASSED
tests/test_servicos.py::test_endereco_remove_mascara_do_cep PASSED
tests/test_servicos.py::test_cartao_teste_passa_na_validacao_luhn PASSED
tests/test_servicos.py::test_validade_do_cartao PASSED
tests/test_servicos.py::test_pagamento_pix_aprovado_na_hora PASSED
tests/test_servicos.py::test_pagamento_dinheiro_fica_pendente PASSED
tests/test_servicos.py::test_pagamento_cartao_guarda_so_os_ultimos_digitos PASSED
tests/test_servicos.py::test_pagamento_cartao_invalido_e_recusado PASSED
tests/test_servicos.py::test_criar_pedido_baixa_estoque_e_limpa_carrinho PASSED
tests/test_servicos.py::test_criar_pedido_com_carrinho_vazio PASSED
tests/test_servicos.py::test_criar_pedido_quando_estoque_acabou_no_meio_da_compra PASSED
tests/test_servicos.py::test_pagamento_recusado_nao_cria_pedido_nem_baixa_estoque PASSED
tests/test_servicos.py::test_cliente_cancela_pedido_recebido_e_estoque_volta PASSED
tests/test_servicos.py::test_cliente_nao_cancela_pedido_em_preparo PASSED
tests/test_servicos.py::test_fluxo_de_status_da_entrega PASSED
tests/test_servicos.py::test_fluxo_de_status_da_retirada PASSED
tests/test_servicos.py::test_agendamento_e_opcional PASSED
tests/test_servicos.py::test_agendamento_aceita_dia_e_horario_validos PASSED
tests/test_servicos.py::test_agendamento_recusa_dia_fora_do_prazo[2026-11-18] PASSED
tests/test_servicos.py::test_agendamento_recusa_dia_fora_do_prazo[2026-11-26] PASSED
tests/test_servicos.py::test_agendamento_recusa_dia_fora_do_prazo[2026-11-17] PASSED
tests/test_servicos.py::test_agendamento_recusa_dia_fora_do_prazo[amanha] PASSED
tests/test_servicos.py::test_agendamento_recusa_dia_fora_do_prazo[] PASSED
tests/test_servicos.py::test_agendamento_exige_horario_da_lista PASSED
tests/test_servicos.py::test_datas_para_agendar_vao_de_amanha_ate_7_dias PASSED
tests/test_servicos.py::test_pedido_agendado_guarda_dia_e_horario PASSED
tests/test_servicos.py::test_previsao_de_chegada_depende_da_forma_de_entrega PASSED
tests/test_servicos.py::test_relatorio_soma_vendas_e_ignora_cancelados PASSED
tests/test_servicos.py::test_relatorio_sem_vendas PASSED
============================= 92 passed in 22.51s =============================
```
