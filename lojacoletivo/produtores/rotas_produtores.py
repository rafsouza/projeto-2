# Arquivo com as rotas relacionadas aos produtores
from flask import Blueprint, redirect, render_template, request, session

# from database import db
from lojacoletivo import db
from lojacoletivo.models import Produto, Produtor
from xlsxwriter import Workbook
import os

bp_produtor = Blueprint('produtor', __name__, template_folder='templates')


# Rota de cadastro de produtores
# Cadastrar um produtor
@bp_produtor.route('/create', methods=['GET', 'POST'])
def create():
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  if request.method == 'GET':
    return render_template('produtor/produtor_create.html', title='Cadastro de produtores')

  if request.method == 'POST':
    CPF = request.form.get('CPF')
    nome_pr = request.form.get('nome_pr')
    endereco = request.form.get('endereco')
    telefone = request.form.get('telefone')
    email = request.form.get('email')

    pr = Produtor(CPF, nome_pr, endereco, telefone, email)
    db.session.add(pr)
    db.session.commit()

  #return 'Cadastro efetuado com sucesso!'
  return redirect('/produtor/registra/'+str(pr.CPF))



# Lista de produtores
@bp_produtor.route('/read')
def read():
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  pr = Produtor.query.all()
  return render_template('produtor/produtor_read.html', title='Lista de produtores cadastrados', pr=pr)



# Gerar tabela excell
@bp_produtor.route('/gerar_excel')
def gerar_excel():
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  pr = Produtor.query.all()
  if os.path.exists('arquivos/gerados/ListaProdutores.xlsx'):
    os.remove('arquivos/gerados/ListaProdutores.xlsx')
  excel=Workbook('arquivos/gerados/ListaProdutores.xlsx')
  ws=excel.add_worksheet('Produtores')
  ws.write(0,0,'Lista dos Produtores cadastrados - Coletivo Morro das Panelas')
  ws.write(3,0,'CPF')
  ws.write(3,1,'Nome')
  ws.write(3,2,'Endereço')
  ws.write(3,3,'Telefone')
  ws.write(3,4,'Email')
  ws.write(3,6,'Produtos registrados')# 6a. coluna
  i=4 # 4a. linha
  for p in pr:
    ws.write(i,0,int(p.CPF))
    ws.write(i,1,p.nome_pr)
    ws.write(i,2,p.endereco)
    ws.write(i,3,int(p.telefone))
    ws.write(i,4,p.email)
    ja_tem = pr[i-4].registra
    j=6 # 6a. coluna
    for tem in ja_tem: # Produtos que o produtor tem registrados
      # print(i-4,'p = ',pr[i-4]," -> ",tem.nome_produto+' '+tem.porcao)
      ws.write(i,j,str(tem.nome_produto+' ('+tem.porcao+')'))
      j+=1
    i+=1 
  excel.close()
  # return print('Download da planilha desabilitado porque estou testando')
  return redirect('/arquivos/baixar/ListaProdutores.xlsx')
  


# Atualizar dados de um produtor
@bp_produtor.route('/update/<int:CPF>', methods=['GET', 'POST'])
def update(CPF):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  pr = Produtor.query.get(CPF)
  #print(pr, ' ', type(pr)) # verif

  if request.method == 'GET':
    return render_template('produtor/produtor_update.html', title='Atualização de dados de Produtores', pr=pr)

  if request.method == 'POST':
    CPF = request.form.get('CPF')
    nome_pr = request.form.get('nome_pr')
    endereco = request.form.get('endereco')
    telefone = request.form.get('telefone')
    email = request.form.get('email')

    pr.CPF = CPF
    pr.nome_pr = nome_pr
    pr.endereco = endereco
    pr.telefone = telefone
    pr.email = email
    db.session.add(pr)
    db.session.commit()
    return redirect('/produtor/read')


# Deletar um produtor
@bp_produtor.route('/delete/<int:CPF>', methods=['GET', 'POST'])
def delete(CPF):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  pr = Produtor.query.get(CPF)
  if request.method == 'GET':
    return render_template('produtor/produtor_delete.html', title='Remover produtor', pr=pr)

  if request.method == 'POST':
    db.session.delete(pr)
    db.session.commit()
    return redirect('/produtor/read')



# Produtor Registra um produto
@bp_produtor.route('/registra/<int:CPF>', methods=['GET', 'POST'])
def registra(CPF):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  pr = Produtor.query.get(CPF)
  
  if request.method == 'GET':
      pd = Produto.query.all()
      ja_tem = pr.registra # Não funciona o loop com pr.registra no html 
      return render_template('produtor/produtor_registra.html', 
                            pr=pr, pd=pd, ja_tem=ja_tem)
    
  if request.method == 'POST':
    sel = request.form.getlist('selecaoproduto')
    print(sel)
    for s in sel: 
      print(s)
    #   pd = Produto.query.filter_by(id=s).first() # child
    #   pr.registra.append(pd) # parent.relacionamento.append(child)
    #   db.session.add(pr)
    #   db.session.commit()
    return redirect('/produtor/read')



# Produtor Desregistra um produto
@bp_produtor.route('/desregistra/<int:CPF>', methods=['GET', 'POST'])
def desregistra(CPF):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  pr = Produtor.query.get(CPF)
  
  if request.method == 'GET':
      pd = Produto.query.all()
      ja_tem = pr.registra  
      return render_template('produtor/produtor_desregistra.html', pr=pr, ja_tem=ja_tem)

  if request.method == 'POST':
    sel = request.form.getlist('selecaoproduto')
    for s in sel: 
      pd = Produto.query.filter_by(id=s).first() # child
      pr.registra.remove(pd) # parent.relacionamento.append(child)
      db.session.add(pr)
      db.session.commit()
    return redirect('/produtor/read')
