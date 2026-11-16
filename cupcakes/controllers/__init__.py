from cupcakes.controllers.admin import admin_bp
from cupcakes.controllers.auth import auth_bp
from cupcakes.controllers.avaliacao import avaliacao_bp
from cupcakes.controllers.carrinho import carrinho_bp
from cupcakes.controllers.loja import loja_bp
from cupcakes.controllers.pedidos import pedidos_bp

BLUEPRINTS = [loja_bp, auth_bp, carrinho_bp, pedidos_bp, admin_bp, avaliacao_bp]
