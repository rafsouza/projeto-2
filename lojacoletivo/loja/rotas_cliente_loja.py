# Arquivo com as rotas relacionadas aos Clientes da Loja virtual
import os

from flask import Blueprint, redirect, render_template, request, url_for, flash, session
# from xlsxwriter import Workbook
from lojacoletivo import db, bcrypt
from lojacoletivo.models import Produto, Cliente, Pedido, Itens_Pedido
from .formulario import RegistraCliente, LoginCliente, AtualizaCliente, SenhaCliente
from lojacoletivo.loja.rotas_loja import cats

bp_loja_cl = Blueprint('/loja/cliente/', __name__, template_folder='templates')

# Login de cliente
@bp_loja_cl.route('/login', methods=['GET', 'POST'])
def login():
  form=LoginCliente(request.form)
  if request.method == 'GET':
    return render_template('/loja/cliente/login_cliente.html', title= 'Login - Morro das Panelas', categorias=cats(), form=form)

  if request.method == 'POST':
    if form.validate():
      cliente = Cliente.query.filter_by(email=form.email.data).first()

      if cliente: 
        if bcrypt.check_password_hash(cliente.senha, form.senha.data): # 
          print('Login efetuado em: '+str(form.email.data))
          session['email'] = form.email.data # necessita do app.secret_key para funcionar
          return redirect('/loja')
        else:
        #   print('Senha inválida')
          return render_template('/loja/cliente/login_cliente.html', title= 'Login - Morro das Panelas', msg= 'Senha inválida', categorias=cats(), form=form)
      else:
        print('E-mail não cadastrado')
        return render_template('/loja/cliente/login_cliente.html', title= 'Login - Morro das Panelas', msg= 'E-mail não cadastrado', categorias=cats(), form=form)
    else:
      return render_template('/loja/cliente/login_cliente.html', title= 'Login - Morro das Panelas', msg= 'Digite seu Login e Senha', categorias=cats(), form=form)
      


# Cadastrar um cliente 
@bp_loja_cl.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
  form=RegistraCliente(request.form)
  if request.method == 'GET':
    return render_template('/loja/cliente/cadastro_cliente.html', title="Cadastro Novo Cliente", categorias=cats(), form=form)

  if request.method == 'POST': # id, nome_cl, endereco, cidade, telefone, email, obs, senha 

    if form.validate():
      email = request.form.get('email')
      if Cliente.query.filter_by(email=form.email.data).first():
        print('Usuário já existe')
        return render_template('/loja/cliente/cadastro_cliente.html', title="Cadastro Novo Cliente", categorias=cats(), form=form, 
                               msg='Este e-mail já está registrado, por favor escolha outro para fazer o cadastro')
      else:
        nome_cl = request.form.get('nome')
        endereco = request.form.get('endereco')
        cidade = request.form.get('cidade')
        telefone = request.form.get('telefone')
        obs = request.form.get('obs')
        hash_senha = bcrypt.generate_password_hash(form.senha.data) #senha encriptada

        cl = Cliente(nome_cl, nome_cl, endereco, cidade, telefone, email, obs, hash_senha) # por enquanto a id vai ser igual ao nome 
        db.session.add(cl)
        db.session.commit()
    else:
      print('Erro de validação: validators = '+str(form.validate()))
      return render_template('/loja/cliente/cadastro_cliente.html', title="Cadastro Novo Cliente", categorias=cats(), form=form)
  return redirect('/loja/cliente/login')


# Acesso à conta de um cliente e atualiza informações
@bp_loja_cl.route('/conta/', methods=['GET', 'POST'])
def conta():
  if 'email' not in session:
    return redirect('/loja/cliente/login')
  id=session['email']
  cl = Cliente.query.filter_by(email=id).first()

  if request.method == 'GET':
    return render_template('/loja/cliente/conta_cliente.html', title='Morro da Panelas - Conta', categorias=cats(), cl=cl)

    

# Fazer logout
@bp_loja_cl.route('/logout')
def ClienteLogout():
  try:
    session.pop('email',None)
    # Esvaziar carrinho
    # print('Logout realizado com sucesso!')
    return redirect('/loja')
  except Exception as e:
      print(e) 


# Atualizar dados do cliente
@bp_loja_cl.route('/update/', methods=['GET', 'POST'])
def update():
  if 'email' not in session:
    return redirect('/loja/cliente/login')
  id=session['email']
  form = AtualizaCliente(request.form)
  form2 = SenhaCliente(request.form)
  cl = Cliente.query.filter_by(email=id).first()
#   print('Sessão: '+str(session['email'])+' | Check :'+str(session['email']==id))
  modo = request.args.get('modo') # Filtro do status do pedido

  if request.method == 'GET':
    # print('Get modo '+str(modo))
    return render_template('/loja/cliente/update_cliente.html', title='Morro da Panelas - Conta', categorias=cats(), cl=cl, form=form, form2=form2, modo=modo)

  if request.method == 'POST':
    # print(str(session['email'])+' '+str(session['email'] == cl.email))
    if form2.senha.data != None:
         if form2.validate():
           cl.senha = bcrypt.generate_password_hash(form2.senha.data) #senha encriptada
           print('Senha atualizada')
         else:
           print('Erro na atualização da senha')
           return render_template('/loja/cliente/update_cliente.html', title='Morro da Panelas - Conta', categorias=cats(), cl=cl, msg='Erro na senha', 
                                  form2=form2, modo='2')
    else:
        if form.validate():
            m = request.form.get('email') # form.email.data
            if Cliente.query.filter_by(email=m).first() and m != session['email']:
                print('Usuário já existe')
                return render_template('/loja/cliente/update_cliente.html', title='Morro da Panelas - Conta', categorias=cats(), cl=cl, 
                                    msg='Este e-mail já está registrado em outro usuário, por favor escolha outro e-mail para sua conta', form=form, modo='1')
            cl.id = request.form.get('nome')
            cl.nome_cl = request.form.get('nome')
            cl.endereco = request.form.get('endereco')
            cl.cidade = request.form.get('cidade')
            cl.telefone = request.form.get('telefone')
            cl.email = m
            cl.obs = request.form.get('obs')
            print('Dados atualizados')
        else:
          print('Erro na validação dos dados')
          return render_template('/loja/cliente/update_cliente.html', title='Morro da Panelas - Conta', categorias=cats(), cl=cl, msg='Erro na Atualização dos dados', 
                                  form=form, modo='1')
    
    db.session.add(cl)
    db.session.commit()

    # Caso altere o e-mail, atualiza a sessão
    if session['email'] != cl.email:
      try:
        session.pop('email',None)
        session['email'] = form.email.data 
      except Exception as e:
          print(e)
        

    return redirect('/loja/cliente/conta/') 
    # return redirect(url_for('home')) 
  

# Deletar conta
@bp_loja_cl.route('/delete/', methods=['GET', 'POST'])
def delete():
  if 'email' not in session:
    return redirect('/loja/cliente/login')
  
  id=session['email']
  cl = Cliente.query.filter_by(email=id).first()
  form=LoginCliente(request.form)

  if request.method == 'GET':
    return render_template('/loja/cliente/delete_cliente.html', title='Remover conta', cl=cl, form= form)

  if request.method == 'POST':
    # print('Validação: '+str(form.validate()))
    if session['email']== form.email.data:
        if form.validate() and bcrypt.check_password_hash(cl.senha, form.senha.data):
            db.session.delete(cl)
            db.session.commit()
            print('Conta '+str(cl.nome_cl)+' removida do sistema')
        else:
            print('Erro na senha - Exclusão de conta')
            return render_template('/loja/cliente/delete_cliente.html', title='Remover conta', cl=cl, form= form, msg='Erro na senha - a conta não foi excluida')
    else:
      print('Erro no e-mail - Exclusão de conta')
      return render_template('/loja/cliente/delete_cliente.html', title='Remover conta', cl=cl, form= form, msg='Erro no e-mail do usuário - a conta não foi excluida')

    return redirect('/loja/cliente/logout')

# Ver pedidos realizados
@bp_loja_cl.route('/pedidos', methods=['GET', 'POST'])
def ver_pedidos():
  if 'email' not in session:
      return redirect('/loja/cliente/login')
  id=session['email']
  cl = Cliente.query.filter_by(email=id).first()

  if request.method == 'GET': # Pagina com os pedidos feitos pelo cliente
      pd = Pedido.query.filter_by(cliente_id=cl.id).all()
      # for p in pd:
        # print('N pedido = ',p,p.data_entrega)
      # print('N pedido = ',pd[0].N_pedido)
      # it = 'Itens_Pedido.query.filter_by(N_pedido=pd.N_pedido).all()'
      # pd = 
      return render_template('/loja/cliente/ver_pedidos.html', title='Pedidos - Morro das Panelas', cl=cl, pd=pd)
  
  if request.method == 'POST': # Pagina com os itens do pedido selecinado
    N_pedido = request.form.get('N_pedido')
    ped = Pedido.query.get(N_pedido)
    it = Itens_Pedido.query.filter_by(N_pedido=N_pedido)

    total=0 # Calcula o valor total
      # qtt=0 # Calcula a quantidade total, caso queira implementar 
    for i in it:
      # print(i.nome, ' - ID produto ', i.produto_id)
      total += float(i.preco)*float(i.qtd)
    total = round(total, 2) # deixar com 2 casas decimais

    return render_template('/loja/cliente/veritens_cliente.html', title='Pedidos - Morro das Panelas', ped=ped, it=it, cl=cl, total=total, N_pedido=N_pedido)
