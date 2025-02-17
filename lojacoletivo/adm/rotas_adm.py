# Arquivo com as rotas relacionadas administração
import os

from flask import Blueprint, redirect, render_template, request, session
# from xlsxwriter import Workbook
from lojacoletivo import db, bcrypt, app
from lojacoletivo.models import Admin
# from models import Produto
from .formulario import RegistraFormulario, LoginFormulario, AtualizaAdm, SenhaAdm

bp_adm = Blueprint('adm', __name__, template_folder='templates')

# Acessar página principal de administração
@bp_adm.route('/home', methods=['GET', 'POST'])
def adm_home():
  if request.method == 'GET':
    if 'email_adm' not in session:
     return redirect('/adm/login_adm')
    else:
      return render_template('adm/home_adm.html', title= 'Administração - Morro das Panelas')

 
# Login de administrador
@bp_adm.route('/login_adm', methods=['GET', 'POST'])
def login_adm():
  form=LoginFormulario(request.form)
  if request.method == 'GET':
    return render_template('adm/login_adm.html', title= 'Login - Morro das Panelas', form=form)

  if request.method == 'POST':
    if form.validate():
      administrador = Admin.query.filter_by(email_adm=form.email_adm.data).first()
      if administrador and bcrypt.check_password_hash(administrador.senha, form.senha.data): # 
        session['email_adm'] = form.email_adm.data # necessita do app.secret_key para funcionar
        if administrador.principal == 1:
          session['adm_principal'] = 1 # Administrador principal na sessão
        # else:
        #    session['adm_principal'] = 0
        return redirect('/adm/home')
      else:
        print('Usuário ou senha inválidos')
        return render_template('adm/login_adm.html', title= 'Login - Morro das Panelas', form=form, msg= 'Usuário ou senha inválidos')
    

# Cadastrar um administrador
@bp_adm.route('/create', methods=['GET', 'POST'])
def create():
  form=RegistraFormulario(request.form)
  if request.method == 'GET':
    return render_template('adm/adm_create.html', form=form, title='Cadastro de Administradores')

  if request.method == 'POST': 
    if form.validate():
      nome = request.form.get('nome')
      usuario_adm = request.form.get('usuario_adm')
      email_adm = request.form.get('email_adm')
      obs=request.form.get('obs')
      # print(form.senha.data)
      hash_senha = bcrypt.generate_password_hash(form.senha.data) #senha encriptada #
      # print(hash_senha)

      adm = Admin(nome, usuario_adm, email_adm, hash_senha, obs)
      db.session.add(adm)
      db.session.commit()
    else:
      print('Erro de validação: validators = '+str(form.validate()))
      return render_template('adm/adm_create.html', form=form, title='Cadastro de Administradores')

  #return 'Cadastro efetuado com sucesso!'
  # return redirect('/adm/registra/'+str(adm.usuario_adm))
  return redirect('/adm/read')


# Lista de administradores
@bp_adm.route('/read')
def read():
  if request.method == 'GET':
    if 'email_adm' not in session:
     if 'adm_principal' not in session:
       return redirect('/adm/login_adm')
  adm = Admin.query.all()
  return render_template('adm/adm_read.html', title='Lista de Administradores cadastrados', adm=adm)


# Atualizar dados de um administrador
@bp_adm.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
  if 'email_adm' not in session:
    if 'adm_principal' not in session:
      return redirect('/adm/login_adm')
  form=AtualizaAdm(request.form)
  form2 =SenhaAdm(request.form)
  adm = Admin.query.get(id)
  modo = request.args.get('modo') # Filtro do status do pedido
  #print(pr, ' ', type(pr)) # verif

  if request.method == 'GET':
    return render_template('adm/adm_update.html', title='Atualização de dados - Administrador', form=form, form2=form2, adm=adm, modo=modo)

  if request.method == 'POST':
    # print(str(session['email'])+' '+str(session['email'] == adm.email))
    if form2.senha.data != None:
         if form2.validate():
           adm.senha = bcrypt.generate_password_hash(form2.senha.data) #senha encriptada
           print('Senha atualizada')
         else:
           print('Erro na atualização da senha')
           return render_template('adm/adm_update.html', title='Atualização de dados - Administrador', form2=form2, adm=adm,
                                   msg='Erro na senha', modo='2')
    else:
        if form.validate():
            m = request.form.get('email') # form.email.data
            if Admin.query.filter_by(email_adm=m).first() and m != session['email']:
                print('Usuário já existe')
                return render_template('adm/adm_update.html', title='Atualização de dados - Administrador', form=form, adm=adm, 
                                       msg='Este e-mail já está registrado em outro usuário, por favor escolha outro e-mail para sua conta', modo='1')
            nome = request.form.get('nome')
            usuario_adm = request.form.get('usuario_adm')
            email_adm = request.form.get('email_adm')
            principal = bool(request.form.get('principal'))
            obs = request.form.get('obs')
            # print(nome, usuario_adm, email_adm, principal, obs)
            # print("Principal: "+str(principal))

            adm.nome = nome
            adm.usuario_adm = usuario_adm
            adm.email_adm = email_adm
            adm.principal = principal
            adm.obs = obs
            # print('Dados atualizados')

              # Caso altere o e-mail, atualiza a sessão
            if session['email_adm'] != adm.email_adm:
              try:
                session.pop('email_adm',None)
                session['email_adm'] = form.email_adm.data 
              except Exception as e:
                  print(e)

        else:
          print('Erro na validação dos dados')
          return render_template('adm/adm_update.html', title='Atualização de dados - Administrador', adm=adm, msg='Erro na Atualização dos dados', 
                                  form=form, modo='1')
    
    db.session.add(adm)
    db.session.commit()

  

    return redirect('/adm/read')
# (nome, usuario_adm, email_adm, senha, principal, obs)


# Deletar conta
@bp_adm.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
  if 'email_adm' not in session:
    if 'adm_principal' not in session:
      return redirect('/adm/login_adm')
  
  adm = Admin.query.get(id)
  form=LoginFormulario(request.form)

  if request.method == 'GET':
    return render_template('/adm/adm_delete.html', title='Remover conta', adm=adm, form= form)

  if request.method == 'POST':
    # print('Validação: '+str(form.validate()))
    # if session['email_adm']== form.email_admm.data:
      adm_pr = Admin.query.filter_by(email_adm=session['email_adm']).first() #  Buscar adm principal
      # print('ID : ',adm_pr.id,' | Adm pr: ',adm_pr,' | e-mail: ', session['email_adm'])
      if form.validate() and bcrypt.check_password_hash(adm_pr.senha, form.senha.data):
          db.session.delete(adm)
          db.session.commit()
          print('Conta '+str(adm.nome)+' removida do sistema')
      else:
          print('Erro na senha - Exclusão de conta')
          return render_template('/adm/adm_delete.html', title='Remover conta', adm=adm, form= form, 
                                 msg='Erro na senha - a conta de '+str(adm.nome)+' não foi excluida')
    # else:
    #   print('Erro no e-mail - Exclusão de conta')
    #   return render_template('/adm/adm_delete.html', title='Remover conta', adm=adm, form= form, msg='Erro no e-mail do usuário - a conta não foi excluida')
      if session['email_adm']== adm.email_adm:
        print('Exclusão da própria conta')
        return redirect('/adm/logout')
      
  return redirect('/adm/read')


# Indice adm
@bp_adm.route('/index')
def index():
  if request.method == 'GET':
    if 'email_adm' not in session:
     return redirect('/adm/login_adm')
  return (render_template('adm/index_adm.html'))


# Fazer logout
@bp_adm.route('/logout')
def AdmLogout():
  try:
    session.pop('email_adm',None)
    session.pop('adm_principal',None)
    # Esvaziar carrinho
    # print('Logout realizado com sucesso!')
    return redirect('/adm/home')
  except Exception as e:
      print(e) 
