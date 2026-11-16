INSERT INTO categoria (nome, descricao) VALUES
  ('Clássicos', 'Os sabores de sempre, feitos todos os dias.'),
  ('Frutados', 'Coberturas leves com frutas frescas da estação.'),
  ('Especiais', 'Receitas da casa com recheio surpresa.'),
  ('Veganos', 'Sem ingredientes de origem animal.');

INSERT INTO cupcake (nome, descricao, preco, estoque, cor, destaque, ativo, categoria_id, criado_em) VALUES
  ('Baunilha com Chantilly', 'Massa de baunilha fofinha com chantilly batido na hora.', 8.90, 30, '#f7e3b5', true, true, (SELECT id FROM categoria WHERE nome = 'Clássicos'), now()),
  ('Chocolate Belga', 'Massa de cacau 50% com ganache de chocolate belga.', 10.90, 25, '#6b3e26', true, true, (SELECT id FROM categoria WHERE nome = 'Clássicos'), now()),
  ('Red Velvet', 'Massa aveludada vermelha com cobertura de cream cheese.', 11.50, 20, '#e9d6d0', false, true, (SELECT id FROM categoria WHERE nome = 'Clássicos'), now()),
  ('Morango do Campo', 'Massa de baunilha, recheio de geleia e cobertura de morango.', 10.50, 18, '#f4a6c1', true, true, (SELECT id FROM categoria WHERE nome = 'Frutados'), now()),
  ('Limão Siciliano', 'Massa cítrica com merengue maçaricado.', 9.90, 15, '#f3eb8c', false, true, (SELECT id FROM categoria WHERE nome = 'Frutados'), now()),
  ('Maracujá', 'Massa de baunilha com mousse de maracujá.', 9.90, 12, '#f6c453', false, true, (SELECT id FROM categoria WHERE nome = 'Frutados'), now()),
  ('Doce de Leite com Flor de Sal', 'Recheio de doce de leite artesanal e toque de flor de sal.', 12.90, 14, '#d9a066', true, true, (SELECT id FROM categoria WHERE nome = 'Especiais'), now()),
  ('Pistache', 'Massa de pistache com creme e pistache torrado.', 14.90, 10, '#b7d39a', false, true, (SELECT id FROM categoria WHERE nome = 'Especiais'), now()),
  ('Brigadeiro Gourmet', 'Massa de chocolate recheada de brigadeiro cremoso.', 11.90, 22, '#4a2a1c', false, true, (SELECT id FROM categoria WHERE nome = 'Especiais'), now()),
  ('Cacau Vegano', 'Massa de cacau com cobertura de chocolate 70%, sem leite e sem ovos.', 11.90, 12, '#5b3a29', false, true, (SELECT id FROM categoria WHERE nome = 'Veganos'), now()),
  ('Coco e Banana Vegano', 'Massa de banana com cobertura de creme de coco.', 10.90, 0, '#f4efe1', false, true, (SELECT id FROM categoria WHERE nome = 'Veganos'), now());

INSERT INTO cliente (nome, email, senha_hash, telefone, administrador, criado_em) VALUES
  ('Administrador da Loja', 'admin@nuvemdeacucar.test', 'pbkdf2:sha256:600000$nHIihWaZx0FG3jcl$2509e1968d775f2ee4aa95c4a821caa4b14f48d3940af901df6d82df4cf0945c', '', true, now()),
  ('Cliente de Teste', 'cliente@nuvemdeacucar.test', 'pbkdf2:sha256:600000$OqsEmkhVr7kuiLZN$ecc01b58825cee8c9777b095202d5eb31e989536786662b0233e69afe1253a66', '', false, now());
