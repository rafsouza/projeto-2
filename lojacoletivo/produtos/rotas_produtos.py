# Arquivo com as rotas relacionadas aos produtos
import os, secrets

from flask import Blueprint, redirect, render_template, request, session, current_app
from xlsxwriter import Workbook

from lojacoletivo import db, photos
from lojacoletivo.models import Produto

bp_produto = Blueprint('produto', __name__, template_folder='templates')


# Rota de cadastro de produtos
# Cadastrar um produto
@bp_produto.route('/create', methods=['GET', 'POST'])
def create():
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  if request.method == 'GET':
    return render_template('produto/produto_create.html', title= 'Cadastrar novo produto')
    
  if request.method == 'POST':
    nome_produto = request.form.get('nome_produto')
    qtd = request.form.get('qtd').replace(',','.')# Substituir vírgula por ponto
    porcao = request.form.get('porcao')
    preco = request.form.get('preco')
    categoria = request.form.get('categoria')
    descricao = request.form.get('descricao')

    if request.files.get('im_1'):
      im_1 = photos.save(request.files.get('im_1'), name = secrets.token_hex(10)+".")
    else:
      im_1 = 'MorroPanelas.jpg'

    # qtd = [a.replace(',','.') for a in qtd] # Substituir vírgula por ponto

    pd = Produto(nome_produto, qtd, porcao, preco, categoria, descricao, im_1)
    db.session.add(pd)
    db.session.commit()
  return redirect('/produto/read/1')


# Lista de produtos
@bp_produto.route('/read/<int:ver>', methods=['GET', 'POST'])
def read(ver):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  if request.method == 'GET':
    pd = Produto.query.order_by(Produto.nome_produto.asc()).all()
    categorias = Produto.query.with_entities(Produto.categoria).group_by(Produto.categoria).distinct()
    # subq= db.session.query(Produto).order_by(Produto.nome_produto).with_entities(Produto.categoria).subquery()
    # categorias = db.session.query().with_entities(Produto.categoria).add_entity(Produto, alias=subq).group_by(Produto.categoria).distinct() # Tentativa de ordenar e depois agrupar por categoria
    
    # print(categorias)
    # for u in categorias:
    #     print(u.categoria,' ',type(u.categoria))

    # Salvar no excell
    if ver == 3:
      if os.path.exists('arquivos/gerados/ListaProdutores.xlsx'):
        os.remove('arquivos/gerados/ListaProdutores.xlsx')
      excel=Workbook('arquivos/gerados/EstoqueProdutos.xlsx')
      ws=excel.add_worksheet('Produtos')
      ws.write(0,0,'Lista dos Produtos cadastrados - Coletivo Morro das Panelas') 
      ws.write(3,0, 'Nome')
      ws.write(3,1, 'Quantidade')
      ws.write(3,2, 'Porção')
      ws.write(3,3, 'Preço (R$)')
      ws.write(3,4, 'Categoria')
      ws.write(3,5, 'Descrição')
      i=4
      for u in pd:
        ws.write(i,0,u.nome_produto)
        ws.write(i,1,u.qtd)
        ws.write(i,2,u.porcao)
        ws.write(i,3,u.preco)
        ws.write(i,4,u.categoria)
        ws.write(i,5,u.descricao)
        i=i+1
      excel.close()
      # print('Arquivo produto.xlsx criado com sucesso!')
      return redirect('/arquivos/baixar/EstoqueProdutos.xlsx')

    
    return render_template('produto/produto_read.html', title= 'Produtos cadastrados', 
                           pd=pd, categorias=categorias, ver=ver)

  if request.method == 'POST':
    id= request.form.get('id')
    qtd = request.form.get('qtd')
    p = Produto.query.get(id)
    # print('Estoque ',p.nome_produto, ' alterado: ', p.qtd,' -> ',qtd)
    p.qtd = qtd
    db.session.add(p)
    db.session.commit()
    return redirect('/produto/read/0')



# Atualizar dados de um produto
@bp_produto.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  p = Produto.query.get(id)

  if request.method == 'GET':
    return render_template('produto/produto_update.html', title='Atualização de dados - Produto', p=p)

  if request.method == 'POST':
    nome_produto = request.form.get('nome_produto')
    qtd = request.form.get('qtd')
    porcao = request.form.get('porcao')
    preco = request.form.get('preco')
    categoria = request.form.get('categoria')
    descricao = request.form.get('descricao')

    p.nome_produto = nome_produto
    p.qtd = qtd
    p.porcao = porcao
    p.preco = preco
    p.categoria = categoria
    p.descricao = descricao

    if request.files.get('im_1'):
      # print('detectado if 1')
      try:
        print(str(os.path.join(current_app.root_path,"static/images/"+p.im_1)))
        if p.im_1 != 'MorroPanelas.jpg':
          os.unlink(os.path.join(current_app.root_path,"static/images/"+p.im_1))
        p.im_1 = photos.save(request.files.get('im_1'), name = secrets.token_hex(10)+".")
      except:
        p.im_1 = photos.save(request.files.get('im_1'), name = secrets.token_hex(10)+".")

    db.session.add(p)
    db.session.commit()
    return redirect('/produto/read/1')



# Atualizar categoria
@bp_produto.route('/categoria_update/', methods=['GET', 'POST'])
def categoria_update():
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  if request.method == 'GET':
    categorias = Produto.query.with_entities(Produto.categoria).group_by(Produto.categoria).distinct()
    # for a in categorias:
      # print(a.categoria,' ',type(a.categoria))
    return render_template('produto/produto_categoria_update.html', title='Atualização de categoria - Produto', categorias=categorias)
    
  if request.method == 'POST':
    anterior = request.form.get('anterior')
    novo = request.form.get('novo')
    # print('Antigo: ',anterior,' ',type(anterior),' Novo: ',novo, ' ',type(novo))
    p = Produto.query.filter_by(categoria=anterior).all()
    for a in p:
      a.categoria = novo
      # print("  --> ", a.categoria," atualizado em : ",a.nome_produto)
      db.session.add(a)
      db.session.commit()
    return redirect('/produto/read/1')



# Deletar um produto
@bp_produto.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  p = Produto.query.get(id)
  if request.method == 'GET':
    return render_template('produto/produto_delete.html', title='Remover produto', p=p)

  if request.method == 'POST':
    try:
      # print(str(os.path.join(current_app.root_path,"static/images/"+prod.im_3)))
      if p.im_1 != 'MorroPanelas.jpg':
        os.unlink(os.path.join(current_app.root_path,"static/images/"+p.im_1))
      # os.unlink(os.path.join(current_app.root_path,"static/images/"+p.im_2))
      # os.unlink(os.path.join(current_app.root_path,"static/images/"+p.im_3))
      print('Arquivos de ',str(p.nome_produto),' removidos')
    except Exception as e:
      print(e)
    
    db.session.delete(p)
    db.session.commit()
    return redirect('/produto/read/1')
