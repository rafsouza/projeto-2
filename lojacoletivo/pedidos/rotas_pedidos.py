# Arquivo com as rotas relacionadas aos pedidos
import os
from datetime import datetime
from random import randint

import pytz
from flask import Blueprint, redirect, render_template, request, session
from xlsxwriter import Workbook

from lojacoletivo import db
from lojacoletivo.models import Cliente, Itens_Pedido, Pedido, Produto, Produtor

bp_pedido = Blueprint('pedidos', __name__, template_folder='templates')


# Rota de pedidos
# Escolha do cliente
@bp_pedido.route('/cliente', methods=['GET'])
def cliente():
  if request.method == 'GET':
    if 'email_adm' not in session:
     return redirect('/adm/login_adm')
    
    cl = Cliente.query.all()
    return render_template('pedidos/pedido_cliente.html', title='Pedido - Escolha do cliente', cl=cl)



# Cadastrar um pedido
@bp_pedido.route('/create/<string:id>', methods=['GET', 'POST'])
def create(id):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  cl = Cliente.query.get(id)
  pd = Produto.query.order_by(Produto.nome_produto.asc()).all()
  categorias = Produto.query.with_entities(Produto.categoria).group_by(Produto.categoria).distinct()
  if request.method == 'GET':
    return render_template('pedidos/pedido_create.html', title='Cadastro de pedidos', 
                           pd=pd, cl=cl, categorias=categorias)

  if request.method == 'POST': 
    
    npd = randint(10000000, 99999999) 
    while Pedido.query.filter_by(N_pedido=npd).first() != None: # Verificar esta linha ao criar um banco de dados do zero
      npd = randint(10000000, 99999999)
    
    pr_id = request.form.getlist('produto_id')
    nome = request.form.getlist('nome')
    porcao= request.form.getlist('porcao')
    qtd = request.form.getlist('qtd')
    preco = request.form.getlist('preco')
    obs = request.form.get('obs')
    ped = Pedido(id, npd, obs) # id = cliente_id
    qtd = [a.replace(',','.') for a in qtd] # Substituir vírgula por ponto
   
    db.session.add(ped)
    db.session.commit() # Registra o pedido (por enquanto sem itens)
    # print(npd,' foi criado. Situação:  Em aberto ') 
    
    for a in range(len(qtd)):
      if float(qtd[a]) !=0:
        it = Itens_Pedido(npd, str(nome[a])+' ('+str(porcao[a])+')', 
                          pr_id[a], preco[a], qtd[a])
        db.session.add(it)
        db.session.commit() # Registra os itens do pedido

  return redirect('/pedidos/read')



# Lista de pedidos 
@bp_pedido.route('/read', methods= ['GET', 'POST'])
def read():
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  st= request.form.get('st') # Filtro do status do pedido
  
  if st == None or st == "Ativos": # Filtro do status do pedido
    # ped = Pedido.query.order_by(Pedido.data_pedido.desc()).all()
    ped = Pedido.query.filter(Pedido.status!="Arquivado").order_by(Pedido.data_pedido.desc()).all()
    st = "Ativos"
  else:
    ped = Pedido.query.filter_by(status=st).all()
  
  if request.method == 'GET':
    return render_template('pedidos/pedido_read.html', title='Pedidos realizados', ped=ped, st=st)
    
  if request.method == 'POST':
    st = request.form.get('st') # Estado da busca, repassado para a função
    stat= request.form.get('stat') # Atualização de status do pedido
    N_pedido = request.form.get('N_pedido')
    anterior= request.form.get('anterior')
    
    if stat != None: # Status do pedido é atualizado
      modo= int(request.form.get('modo'))
      sequencia = ["Cancelado","Em aberto","Em separação","Finalizado", "Arquivado"]
      index= sequencia.index(stat)
      ped_selec = Pedido.query.get(N_pedido)
      
      if modo == 1 and index>=1 and index<=2:
        index += 1 # muda index
        stat=sequencia[index] # muda stat
        # print(N_pedido,' avançou na sequencia para: ',stat)
      
      if sequencia.index(anterior) <= 1 and sequencia.index(stat)>1:
        print(N_pedido,' estava em aberto e avançou na sequencia')
        it = Itens_Pedido.query.filter_by(N_pedido=N_pedido)
        for i in it:
          it_pd =Produto.query.get(i.produto_id)
          it_pd.qtd = it_pd.qtd - i.qtd # Remove do estoque
          # print('(-) Estoque de',it_pd.nome_produto,'de ',it_pd.qtd + i.qtd,' para ',it_pd.qtd) # pr
          db.session.add(it_pd)
          db.session.commit()
      
      if sequencia.index(anterior)>1 and sequencia.index(stat)<2: 
        print(N_pedido,' foi cancelado ou voltou estar em aberto')
        it = Itens_Pedido.query.filter_by(N_pedido=N_pedido)
        for i in it:
          it_pd =Produto.query.get(i.produto_id)
          it_pd.qtd = it_pd.qtd + i.qtd # Adiciona de volta ao estoque
          # print('(+) Estoque de',it_pd.nome_produto,': ',it_pd.qtd)
          # print('Estoque de',it_pd.nome_produto,'de ',it_pd.qtd - i.qtd,' para ',it_pd.qtd)
          db.session.add(it_pd)
          db.session.commit()

      if index == 3: # Adicionar data de entrega
        ped_selec.data_entrega = datetime.now(pytz.timezone('America/Sao_Paulo')).replace(microsecond=0)
        # print(N_pedido,' finalizado (',ped_selec.data_entrega,')')
      
      ped_selec.status = stat
      db.session.add(ped_selec)
      db.session.commit()
    
    return render_template('pedidos/pedido_read.html', title='Pedidos realizados', ped=ped, st=st)



# Ver itens de um pedido
@bp_pedido.route('/veritens/<int:N_pedido>', methods=['GET', 'POST'])
def veritens(N_pedido):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  ped = Pedido.query.get(N_pedido)
  it = Itens_Pedido.query.filter_by(N_pedido=N_pedido)
  # print(it,' ',type(it))

  if request.method == 'GET':
      
      pd = Produto.query.all()
      pr = Produtor.query.all()
      # pr_filt = Itens_Pedido.query.filter_by(N_pedido=N_pedido).group_by(Itens_Pedido.produto_id).all()
      # pr_filt = Produtor.query.all() # type: <class 'sqlalchemy.orm.collections.InstrumentedList'>
      

      # for a in pr_filt: 
      #   print(a,' ',type(a))

    
      total=0 # Calcula o valor total
      # qtt=0 # Calcula a quantidade total, caso queira implementar
      lista_pr = [] # Lista de produtores
      for i in it:
        # print(i.nome, ' - ID produto ', i.produto_id)
        total += float(i.preco)*float(i.qtd)
        
        for a in pr:
          fil_pr = a.registra #
          for b in fil_pr: # Queria encontrar uma forma mais eficiente, mas pelo menos esta funciona
            if i.produto_id == b.id:
              # print('Produtor: ',a.nome_pr, ' - ID: ',b.id)
              lista_pr.append([b.id, a.nome_pr, a.endereco, a.telefone, a.email])
      total = round(total, 2) # deixar com 2 casas decimais
    
      '''
# Quando um cliente é deletado, pode gerar um erro:
      # /home/runner/ColetivoV02/pedidos/rotas_pedidos.py:184: SAWarning: fully NULL primary key identity cannot load any object.  This condition may raise an error in a future release.
      # cl =Cliente.query.get(ped.cliente_id)
'''

      if ped.cliente_id == None:
        cl = {'id':'Excluido','nome_cl':'Excluido','endereco':'Excluido',
              'telefone':'Excluido','email':'Excluido', 'cidade':'Excluido',
              'obs':'Excluido'}
      else:
        cl = Cliente.query.get(ped.cliente_id)
      return render_template('pedidos/pedido_veritens.html', pd=pd, ped=ped, it=it, cl=cl, total=total, pr=lista_pr)
      

  if request.method == 'POST':
    stat= request.form.get('stat') # Atualização de status do pedido
    anterior= request.form.get('anterior')

    if stat != None: # Status do pedido é atualizado
      sequencia = ["Cancelado","Em aberto","Em separação","Finalizado","Arquivado"]
      index= sequencia.index(stat)
      ped_selec = Pedido.query.get(N_pedido)

      if sequencia.index(anterior) <= 1 and sequencia.index(stat)>1: 
        # print(N_pedido,' estava em aberto e avançou na sequencia')
        # print(N_pedido,' alterado (',anterior,'->',stat,')')
        it = Itens_Pedido.query.filter_by(N_pedido=N_pedido)
        for i in it:
          it_pd =Produto.query.get(i.produto_id)
          it_pd.qtd = it_pd.qtd - i.qtd # Remove do estoque
          # print('(-) Estoque de',it_pd.nome_produto,'de ',it_pd.qtd + i.qtd,' para ',it_pd.qtd)
          db.session.add(it_pd)
          db.session.commit()

      if sequencia.index(anterior)>1 and sequencia.index(stat)<2: 
        # print(N_pedido,' foi cancelado ou voltou estar em aberto')
        print(N_pedido,' alterado (',anterior,'->',stat,')')
        it = Itens_Pedido.query.filter_by(N_pedido=N_pedido)
        for i in it:
          it_pd =Produto.query.get(i.produto_id)
          it_pd.qtd = it_pd.qtd + i.qtd # Adiciona de volta ao estoque
          # print('(+) Estoque de',it_pd.nome_produto,'de ',it_pd.qtd - i.qtd,' para ',it_pd.qtd)
          db.session.add(it_pd)
          db.session.commit()

      if sequencia.index(anterior)==3 and sequencia.index(stat)<3:
        # print(N_pedido,' alterado (',anterior,'->',stat,')')
        ped_selec.data_entrega = None

      if index == 3: # Adicionar data de entrega
        ped_selec.data_entrega = datetime.now(pytz.timezone('America/Sao_Paulo')).replace(microsecond=0)
        # print(N_pedido,' finalizado (',ped_selec.data_entrega,')')

      ped_selec.status = stat
      db.session.add(ped_selec)
      db.session.commit()
      return redirect('/pedidos/veritens/'+str(N_pedido))



# Gerar tabela excell
@bp_pedido.route('/gerar_excel/<int:opcao>')
def gerar_excel(opcao):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  if opcao == 1:
    ped = Pedido.query.order_by(Pedido.data_pedido.desc()).all()
  elif opcao == 2:
    ped = Pedido.query.filter_by(status="Finalizado").order_by(Pedido.data_pedido.desc()).all()
  else:
    print('Opção inválida')
    return redirect('/pedidos/read')
  itens = Itens_Pedido.query.all()
  if os.path.exists('arquivos/gerados/ListaPedidos.xlsx'):
    os.remove('arquivos/gerados/ListaPedidos.xlsx')
  excel=Workbook('arquivos/gerados/ListaPedidos.xlsx')
  ws1=excel.add_worksheet('Pedidos')
  ws1.write(0,0,'Lista dos Pedidos realizados - Coletivo Morro das Panelas')
  ws1.write(3,0, 'Nº Pedido')
  ws1.write(3,1, 'ID do Cliente')
  ws1.write(3,2, 'Status')
  ws1.write(3,3, 'Data e Hora do Pedido')
  ws1.write(3,4, 'Data e Hora da Entrega')
  ws1.write(3,5, 'Observações')
  # ws1.write(3,5, 'Itens')
  i=4
  for p in ped:
    # it = Itens_Pedido.query.filter_by(N_pedido=p.N_pedido)
    ws1.write(i,0, int(p.N_pedido))
    ws1.write(i,1, str(p.cliente_id))
    ws1.write(i,2, p.status)
    ws1.write(i,3, str(p.data_pedido))
    ws1.write(i,4, str(p.data_entrega))
    ws1.write(i,5, p.obs)
    i+=1
  ws1.write(i+1,0, 'OBS: Os itens de cada pedido podem ser vistos na aba [Itens] ')
  
  ws2=excel.add_worksheet('Itens')
  ws2.write(0,0,'Lista dos Itens dos Pedidos realizados - Coletivo Morro das Panelas')
  ws2.write(3,0, 'Nº Pedido')
  ws2.write(3,1, 'Nome do Produto')
  ws2.write(3,2, 'Quantidade')
  ws2.write(3,3, 'Preço (R$)')
  i=4
  for it in itens:
    ws2.write(i,0, int(it.N_pedido))
    ws2.write(i,1, it.nome)
    ws2.write(i,2, float(it.qtd))
    ws2.write(i,3, int(it.preco))
    i+=1
  excel.close()
  return redirect('/arquivos/baixar/ListaPedidos.xlsx')



# Deletar um pedido
@bp_pedido.route('/delete/<int:N_pedido>', methods=['GET', 'POST'])
def delete(N_pedido):
  if 'email_adm' not in session:
    return redirect('/adm/login_adm')
  
  ped = Pedido.query.get(N_pedido)
  if request.method == 'GET':
    return render_template('pedidos/pedido_delete.html', title='Excluir pedido', ped=ped)

  if request.method == 'POST':
    db.session.delete(ped)
    db.session.commit()
    # print(N_pedido,' foi excluído')
    return redirect('/pedidos/read')
 