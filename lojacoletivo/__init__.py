#  Dependencias (instalação via terminal)
'''
# Criar um arquivo .flaskenv e inserir: FLASK_APP=main:app
# Comandos para inicialização do banco de dados (rodar o primeiro só uma vez, os dois últimos a cada alteração do arquivo models.py)
flask db init
flask db migrate -m "mensagem"
flask db upgrade
'''

from flask import Flask, render_template, redirect

from werkzeug.utils import secure_filename # corrigir esta linha e a seguinte em flask_uploads.py
from werkzeug.datastructures import  FileStorage 

from flask_migrate import Migrate, migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads#, patch_request_class # substituido por MAX_CONTENT_LENGTH
import os
# from database import db



# Criação de diretório para base de dados (de upload)
basedir = os.path.abspath(os.path.dirname(__file__))

# Dados da conexão
# app = Flask(__name__, static_url_path="/static") # Readequado
app = Flask(__name__)

# Configurando o banco de dados
conexao = 'sqlite:///banco.db'
app.secret_key='7uyhX4regdg' # Necessário para criar uma session
app.config['SECRET-KEY'] = '7uyhX4regdg'
app.config['SQLALCHEMY_DATABASE_URI'] = conexao
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db.init_app(app)  # Precisa ficar em baixo do app.config para funcionar # Readequado
db = SQLAlchemy(app) # Banco de dados
bcrypt = Bcrypt(app) # Encriptação de senhas
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')# Diretório onde serão salvos os arquivos de upload


# Configurações de upload
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
# patch_request_class(app)  


# Associação do banco de dados com o aplicativo
migrate = Migrate(app, db)



# Importando demais rotas 

from lojacoletivo.produtores import rotas_produtores
from lojacoletivo.produtos import rotas_produtos
from lojacoletivo.clientes import rotas_cliente
from lojacoletivo.pedidos import rotas_pedidos
from lojacoletivo.arquivos import op_arquivos
from lojacoletivo.adm import rotas_adm
from lojacoletivo.loja import rotas_loja  
from lojacoletivo.loja import rotas_cliente_loja
from lojacoletivo.loja import rotas_carrinho


# Registrando os blueprints
app.register_blueprint(rotas_produtores.bp_produtor, url_prefix='/produtor')
app.register_blueprint(rotas_produtos.bp_produto, url_prefix='/produto')
app.register_blueprint(rotas_cliente.bp_cliente, url_prefix='/cliente')
app.register_blueprint(rotas_pedidos.bp_pedido, url_prefix='/pedidos')
app.register_blueprint(op_arquivos.bp_arquivos, url_prefix='/arquivos')
app.register_blueprint(rotas_adm.bp_adm, url_prefix='/adm')
app.register_blueprint(rotas_loja .bp_loja, url_prefix='/loja')
app.register_blueprint(rotas_cliente_loja.bp_loja_cl, url_prefix='/loja/cliente') 
app.register_blueprint(rotas_carrinho.bp_carro, url_prefix='/carrinho')


# Rota principal
@app.route('/')
def home():
    #    return 'Hello from Flask!'
    # return render_template('home.html', title='Coletivo Morro das Panelas')
    return redirect('/loja')
