CREATE TABLE avaliacao_teste (
	id SERIAL NOT NULL, 
	nome_testador VARCHAR(100) NOT NULL, 
	data_teste DATE NOT NULL, 
	funcionou TEXT NOT NULL, 
	nao_funcionou TEXT NOT NULL, 
	nao_testado TEXT NOT NULL, 
	sugestoes TEXT NOT NULL, 
	link_evidencias VARCHAR(500) NOT NULL, 
	criado_em TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE categoria (
	id SERIAL NOT NULL, 
	nome VARCHAR(60) NOT NULL, 
	descricao VARCHAR(255) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
);

CREATE TABLE cliente (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	senha_hash VARCHAR(255) NOT NULL, 
	telefone VARCHAR(20) NOT NULL, 
	administrador BOOLEAN NOT NULL, 
	criado_em TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);

CREATE TABLE cupcake (
	id SERIAL NOT NULL, 
	nome VARCHAR(80) NOT NULL, 
	descricao TEXT NOT NULL, 
	preco NUMERIC(8, 2) NOT NULL, 
	estoque INTEGER NOT NULL, 
	cor VARCHAR(7) NOT NULL, 
	foto_url VARCHAR(500), 
	destaque BOOLEAN NOT NULL, 
	ativo BOOLEAN NOT NULL, 
	categoria_id INTEGER NOT NULL, 
	criado_em TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_cupcake_preco_positivo CHECK (preco > 0), 
	CONSTRAINT ck_cupcake_estoque_nao_negativo CHECK (estoque >= 0), 
	FOREIGN KEY(categoria_id) REFERENCES categoria (id)
);

CREATE INDEX ix_cupcake_categoria_id ON cupcake (categoria_id);

CREATE TABLE pedido (
	id SERIAL NOT NULL, 
	cliente_id INTEGER NOT NULL, 
	status VARCHAR(25) NOT NULL, 
	forma_entrega VARCHAR(10) NOT NULL, 
	cep VARCHAR(8), 
	logradouro VARCHAR(120), 
	numero VARCHAR(10), 
	complemento VARCHAR(60), 
	bairro VARCHAR(60), 
	cidade VARCHAR(60), 
	observacao VARCHAR(255) NOT NULL, 
	data_agendada DATE, 
	faixa_horario VARCHAR(20), 
	subtotal NUMERIC(10, 2) NOT NULL, 
	taxa_entrega NUMERIC(10, 2) NOT NULL, 
	total NUMERIC(10, 2) NOT NULL, 
	criado_em TIMESTAMP WITH TIME ZONE NOT NULL, 
	atualizado_em TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_pedido_forma_entrega CHECK (forma_entrega in ('entrega', 'retirada')), 
	CONSTRAINT ck_pedido_status CHECK (status in ('recebido', 'em_preparo', 'saiu_para_entrega', 'pronto_para_retirada', 'entregue', 'cancelado')), 
	CONSTRAINT ck_pedido_total CHECK (total >= 0), 
	FOREIGN KEY(cliente_id) REFERENCES cliente (id)
);

CREATE INDEX ix_pedido_cliente_id ON pedido (cliente_id);

CREATE INDEX ix_pedido_status ON pedido (status);

CREATE TABLE item_pedido (
	id SERIAL NOT NULL, 
	pedido_id INTEGER NOT NULL, 
	cupcake_id INTEGER NOT NULL, 
	nome_cupcake VARCHAR(80) NOT NULL, 
	quantidade INTEGER NOT NULL, 
	preco_unitario NUMERIC(8, 2) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_item_quantidade CHECK (quantidade > 0), 
	CONSTRAINT ck_item_preco CHECK (preco_unitario > 0), 
	FOREIGN KEY(pedido_id) REFERENCES pedido (id) ON DELETE CASCADE, 
	FOREIGN KEY(cupcake_id) REFERENCES cupcake (id)
);

CREATE INDEX ix_item_pedido_cupcake_id ON item_pedido (cupcake_id);

CREATE INDEX ix_item_pedido_pedido_id ON item_pedido (pedido_id);

CREATE TABLE pagamento (
	id SERIAL NOT NULL, 
	pedido_id INTEGER NOT NULL, 
	forma VARCHAR(10) NOT NULL, 
	status VARCHAR(10) NOT NULL, 
	valor NUMERIC(10, 2) NOT NULL, 
	codigo_transacao VARCHAR(40), 
	final_cartao VARCHAR(4), 
	pago_em TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_pagamento_forma CHECK (forma in ('pix', 'cartao', 'dinheiro')), 
	CONSTRAINT ck_pagamento_status CHECK (status in ('pendente', 'aprovado', 'recusado', 'estornado')), 
	UNIQUE (pedido_id), 
	FOREIGN KEY(pedido_id) REFERENCES pedido (id) ON DELETE CASCADE
);

ALTER TABLE avaliacao_teste ENABLE ROW LEVEL SECURITY;

ALTER TABLE categoria ENABLE ROW LEVEL SECURITY;

ALTER TABLE cliente ENABLE ROW LEVEL SECURITY;

ALTER TABLE cupcake ENABLE ROW LEVEL SECURITY;

ALTER TABLE pedido ENABLE ROW LEVEL SECURITY;

ALTER TABLE item_pedido ENABLE ROW LEVEL SECURITY;

ALTER TABLE pagamento ENABLE ROW LEVEL SECURITY;
