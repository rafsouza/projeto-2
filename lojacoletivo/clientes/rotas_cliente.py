# Arquivo com as rotas relacionadas aos clientes
from flask import Blueprint, redirect, render_template, request, session

from lojacoletivo import db, bcrypt
from lojacoletivo.models import Cliente, Pedido
from xlsxwriter import Workbook
import os

bp_cliente = Blueprint('cliente', __name__, template_folder='templates/cliente')


# Rota de cadastro de clientes
# Cadastrar um cliente
@bp_cliente.route('/create', methods=['GET', 'POST'])
def create():
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  if request.method == 'GET':
    return render_template('cliente/cliente_create.html', title='Cadastro de clientes')

  if request.method == 'POST':
    id = request.form.get('id')
    nome_cl = request.form.get('nome_cl')
    endereco = request.form.get('endereco')
    cidade = request.form.get('cidade')
    telefone = request.form.get('telefone')
    email = request.form.get('email')
    obs = request.form.get('obs')  

    if request.form.get('senha') != request.form.get('confirma'):
      return render_template('cliente/cliente_create.html', title='Cadastro de clientes', msg='As senhas devem ser iguias', 
                             id=id, nome_cl=nome_cl, endereco=endereco, cidade=cidade, telefone=telefone, email=email, obs=obs)

    if Cliente.query.filter_by(email=email).first():
        print('Usuário já existe')
        return render_template('cliente/cliente_create.html', title='Cadastro de clientes', 
                               msg='Este e-mail já está registrado, escolha outro para fazer o cadastro', id=id, nome_cl=nome_cl, endereco=endereco, 
                               cidade=cidade, telefone=telefone, email=email, obs=obs)

    hash_senha = bcrypt.generate_password_hash(request.form.get('senha')) #senha encriptada #

    cl = Cliente(id, nome_cl, endereco, cidade, telefone, email, obs, hash_senha) # 
    db.session.add(cl)
    db.session.commit()

  #return 'Cadastro efetuado com sucesso!'
  return redirect('/cliente/read')


# Lista de cliente
@bp_cliente.route('/read')
def read():
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  cl = Cliente.query.all()
  return render_template('cliente/cliente_read.html', title='Lista de clientes cadastrados', cl=cl)



# Gerar tabela excell
@bp_cliente.route('/gerar_excel')
def gerar_excel():
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  cl = Cliente.query.all()
  if os.path.exists('arquivos/gerados/ListaClientes.xlsx'):
    os.remove('arquivos/gerados/ListaClientes.xlsx')
  excel=Workbook('arquivos/gerados/ListaClientes.xlsx')
  #   print('Arquivo ListaClientes.xlsx deletado')
  # else:
  #     print("Novo arquivo ListaClientes.xlsx")
  ws=excel.add_worksheet()
  ws.write(0,0,'Lista dos Clientes cadastrados - Coletivo Morro das Panelas')
  ws.write(3,0,'ID')
  ws.write(3,1,'Nome')
  ws.write(3,2,'Endereço')
  ws.write(3,3,'Cidade')
  ws.write(3,4,'Telefone')
  ws.write(3,5,'Email')
  ws.write(3,6,'Observações')
  ws.write(3,8,'Pedidos')
  i=4
  for c in cl:
    ws.write(i,0,c.id)
    ws.write(i,1,c.nome_cl)
    ws.write(i,2,c.endereco)
    ws.write(i,3,c.cidade)
    ws.write(i,4,int(c.telefone))
    ws.write(i,5,c.email)
    ws.write(i,6,c.obs)
    pd = Pedido.query.filter_by(cliente_id=c.id).all()
    j=8
    for p in pd:
      ws.write(i,j,int(p.N_pedido))
      j+=1
    i+=1 
    # excel.save('arquivos/gerados/ListaClientes.xlsx')
  excel.close()
  return redirect('/arquivos/baixar/ListaClientes.xlsx')



# Atualizar dados de um cliente
@bp_cliente.route('/update/<string:id>', methods=['GET', 'POST'])
def update(id):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  cl = Cliente.query.get(id)

  if request.method == 'GET':
    return render_template('cliente/cliente_update.html', title='Atualização de dados de Clientes', cl=cl)

  if request.method == 'POST':
    id = request.form.get('id')
    nome_cl = request.form.get('nome_cl')
    endereco = request.form.get('endereco')
    cidade = request.form.get('cidade')
    telefone = request.form.get('telefone')
    email = request.form.get('email')
    obs = request.form.get('obs')
    senha = request.form.get('senha')

    cl.id = id
    cl.nome_cl = nome_cl
    cl.endereco = endereco
    cl.cidade = cidade
    cl.telefone = telefone
    cl.email = email
    cl.obs = obs
    if senha != '':
      cl.senha = bcrypt.generate_password_hash(request.form.get('senha')) #senha encriptada #
      # print('Senha modificada')
    db.session.add(cl)
    db.session.commit()
    return redirect('/cliente/read')
    #return 'Dados atualizados com sucesso!'


# Deletar um cliente
@bp_cliente.route('/delete/<string:id>', methods=['GET', 'POST'])
def delete(id):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  cl = Cliente.query.get(id)
  if request.method == 'GET':
    return render_template('cliente/cliente_delete.html', title='Remover cliente', cl=cl)

  if request.method == 'POST':
    db.session.delete(cl)
    db.session.commit()
    return redirect('/cliente/read')

