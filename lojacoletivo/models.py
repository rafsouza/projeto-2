#from sqlalchemy import MetaData
# from database import db
from lojacoletivo import db

from datetime import datetime
import pytz

####################### Banco de dados - Tabelas  principais #######################

# Registra (relacionamento Produtor com Produto)
# metadata_obj = MetaData()#metadata_obj,
registra = db.Table(
    'registra',
    db.Column('produtor_cpf',
              db.Integer,
              db.ForeignKey('produtor.CPF'),
              primary_key=True),
    db.Column('produto_id',
              db.Integer,
              db.ForeignKey('produto.id'),
              primary_key=True))


# Produto
class Produto(db.Model):
  __tablename__ = "produto"
  id = db.Column(db.Integer, primary_key=True)
  nome_produto = db.Column(db.String(128), nullable=False)
  qtd = db.Column(db.Float, nullable=False)
  porcao = db.Column(db.String(20), nullable=False)
  preco = db.Column(db.Float, nullable=False)
  categoria = db.Column(db.String(64), nullable=False)
  descricao = db.Column(db.Text, nullable=False)

  im_1 = db.Column(db.String(256), nullable=True, default='MorroPanelas.jpg') # nullable=False
  # im_2 = db.Column(db.String(256), nullable=True, default='MorroPanelas.jpg') # nullable=False
  # im_3 = db.Column(db.String(256), nullable=True, default='MorroPanelas.jpg') # nullable=False

  # Construtor padrão
  def __init__(self, nome_produto, qtd, porcao, preco, categoria, descricao, im_1):
    self.nome_produto = nome_produto
    self.qtd = qtd
    self.porcao = porcao
    self.preco = preco
    self.categoria = categoria
    self.descricao = descricao
    self.im_1 = im_1

 #  Construtor curto
  def __call__(self, nome_produto, qtd, porcao, preco, categoria):
    self.nome_produto = nome_produto
    self.qtd = qtd
    self.porcao = porcao
    self.preco = preco
    self.categoria = categoria

  def __repr__(self):
    return "{} ({})".format(self.nome_produto, self.porcao)


# Produtor
class Produtor(db.Model):
  __tablename__ = "produtor"
  CPF = db.Column(db.Integer, primary_key=True)
  nome_pr = db.Column(db.String(100), nullable=False)
  endereco = db.Column(db.String(100), nullable=False)
  telefone = db.Column(db.Integer, nullable=False)
  email = db.Column(db.String(100), nullable=False)
  registra = db.relationship(
      'Produto',
      secondary=registra,
      lazy='joined',
      backref=db.backref('registro', lazy=True))  # relacionamento: registra


  def __init__(self, CPF, nome_pr, endereco, telefone, email):
    self.CPF = CPF
    self.nome_pr = nome_pr
    self.endereco = endereco
    self.telefone = telefone
    self.email = email
  
  def __repr__(self):
    return "Produtor: {}".format(self.nome_pr)


# Cliente
class Cliente(db.Model):
  __tablename__ = "cliente"
  id = db.Column(db.String(100), primary_key=True)
  nome_cl = db.Column(db.String(100), nullable=False)
  endereco = db.Column(db.String(100), nullable=False)
  cidade = db.Column(db.String(100), nullable=False)
  telefone = db.Column(db.Integer, nullable=False)
  email = db.Column(db.String(100), nullable=False, unique=True)
  obs = db.Column(db.String(128), nullable=True)
  senha = db.Column(db.String(180), nullable=True) # novo 

  compra = db.relationship('Pedido',
                           backref='cliente')  # relacionamento: pedido

  def __init__(self, id, nome_cl, endereco, cidade, telefone, email, obs, senha):
    self.id = id
    self.nome_cl = nome_cl
    self.endereco = endereco
    self.cidade = cidade
    self.telefone = telefone
    self.email = email
    self.obs = obs
    self.senha = senha

  def __repr__(self):
    return "Cliente: {}".format(self.nome_cl)


# Pedido
class Pedido(db.Model):
  __tablename__ = "pedido"
  N_pedido = db.Column(db.Integer, primary_key=True)
  cliente_id = db.Column(db.String(100),
                         db.ForeignKey('cliente.id', ondelete='SET NULL'),
                         nullable=True)  # FK
  status = db.Column(db.String(32), default='Em aberto')
  data_pedido = db.Column(
      db.DateTime,
      nullable=False,
      default=datetime.now(
          pytz.timezone('America/Sao_Paulo')).replace(microsecond=0))
  data_entrega = db.Column(db.DateTime, nullable=True)
  obs = db.Column(db.String(128), nullable=True)

  itens = db.relationship(
      'Itens_Pedido', backref='pedido',
      cascade="all, delete")  # relacionamento: itens_pedido

  #  Construtor padrão
  def __init__(self, cliente_id, N_pedido, obs):
    self.cliente_id = cliente_id
    self.N_pedido = N_pedido
    self.obs = obs

  #  Construtor com parâmetros
  def __call__(self, cliente_id, N_pedido, status, data_entrega, obs):
    self.cliente_id = cliente_id
    self.N_pedido = N_pedido
    self.status = status
    self.data_entrega = data_entrega
    self.obs = obs

  def __repr__(self):
    return "Pedido No.: {}".format(self.N_pedido)


# Itens Pedidos (Campo multivalorado de Pedido)
class Itens_Pedido(db.Model):
  __tablename__ = "itens_pedido"
  id = db.Column(db.Integer, primary_key=True)
  produto_id = db.Column(db.Integer,
                         db.ForeignKey('produto.id', ondelete='SET NULL'),
                         nullable=True)  # <-----------------
  nome = db.Column(
      db.String(127), nullable=False
  )  # caso o nome e porção do produto mudem depois, aqui ficam registrados o nome e porção antigos
  preco = db.Column(
      db.Float, nullable=False
  )  # caso o preço do produto mude depois, aqui fica registrado o preço antigo
  qtd = db.Column(db.Integer, nullable=False)

  N_pedido = db.Column(db.Integer,
                       db.ForeignKey('pedido.N_pedido'),
                       nullable=True)  # FK pedido

  def __init__(self, N_pedido, nome, produto_id, preco, qtd):
    self.N_pedido = N_pedido
    self.produto_id = produto_id
    self.nome = nome
    self.preco = preco
    self.qtd = qtd

  def __repr__(self):
    return "Produto pedido: {}".format(self.nome)

# Administrador 
class Admin(db.Model):
  __tablename__ = "administrador"
  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String(100), nullable=False)
  usuario_adm = db.Column(db.String(100), nullable=False, unique=True)
  email_adm = db.Column(db.String(100), nullable=False)
  # telefone = db.Column(db.Integer, nullable=False)
  senha = db.Column(db.String(180), nullable=False)
  principal = db.Column(db.Integer, nullable=True) # Administrador dos administradores (Susete)
  obs = db.Column(db.String(128), nullable=True)


  def __init__(self, nome, usuario_adm, email_adm, senha, obs):
    self.nome = nome
    self.usuario_adm = usuario_adm
    self.email_adm = email_adm
    self.senha = senha
    self.principal = 0
    self.obs = obs

      #  Construtor com parâmetros
  def __call__(self, nome, usuario_adm, email_adm, senha, principal, obs):
    self.nome = nome
    self.usuario_adm = usuario_adm
    self.email_adm = email_adm
    self.senha = senha
    self.principal = principal
    self.obs = obs

  def __repr__(self):
    return "Administrador: {}".format(self.nome)


