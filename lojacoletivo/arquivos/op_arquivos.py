from flask import Blueprint, make_response, send_file, redirect, session, request
import os
import csv
# from lojacoletivo import db
from lojacoletivo.models import db, Produto, Produtor, Cliente


bp_arquivos = Blueprint('arquivos', __name__, template_folder='templates')

# Fazer download de um arquivo
@bp_arquivos.route("/baixar/<string:arquivo>", methods=['GET'])
def baixar(arquivo):
  if request.method == 'GET':
    if 'email_adm' not in session:
      return redirect('/adm/login_adm')
  pasta="lojacoletivo/arquivos/gerados/"
  try:
      # arquivo = secure_filename(arquivo)  
      arq_path = os.path.join(pasta, arquivo)
      if os.path.isfile(arq_path):
          return send_file(arq_path, as_attachment=True)
      else:
          return make_response(f"O arquivo '{arquivo}' não foi encontrado.", 404)
  except Exception as e:
      return make_response(f"Error: {str(e)}", 500)

# Fazer backup do banco de dados
@bp_arquivos.route("/backupdb", methods=['GET'])
def backupdb():
  # pasta="instance/"
  if request.method == 'GET':
    if 'email_adm' not in session:
     return redirect('/adm/login_adm')
  try:
      # arq_path = os.path.join(pasta/arquivo)
      arq_path = "instance/banco.db"
      if os.path.isfile(arq_path):
          return send_file(arq_path, as_attachment=True)
      else:
          return make_response("O arquivo banco.db não foi encontrado.", 404)
  except Exception as e:
      return make_response(f"Error: {str(e)}", 500)

# Carregar banco de dados do Produto - /arquivos/dbload
@bp_arquivos.route("/dbload", methods=['GET'])
def dbload():    
    if request.method == 'GET':
      if 'email_adm' not in session:
        return redirect('/adm/login_adm')
    arq_path = "lojacoletivo/arquivos/ler/dbproduto"
    if os.path.isfile(arq_path):
        with open(arq_path, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
              print(row)
              pd = Produto(row[0], float(row[1]), row[2], float(row[3]), row[4], row[5], row[6])
              db.session.add(pd)
              db.session.commit()
              print("Produtos inseridos com sucesso!")
    
    arq_path = "lojacoletivo/arquivos/ler/dbpr" # Produtores
    if os.path.isfile(arq_path):
        with open(arq_path, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
              print(row)
              pd = Produtor(int(row[0]), row[1], row[2], int(row[3]), row[4])
              db.session.add(pd)
              db.session.commit()
              print("Produtores inseridos com sucesso!")
    
    arq_path = "lojacoletivo/arquivos/ler/dbcl" # Clientes
    if os.path.isfile(arq_path):
        with open(arq_path, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
              print(row)
              pd = Cliente(row[0], row[1], row[2], row[3], int(row[4]), row[5], row[6], row[7]) # id, nome_cl, endereco, cidade, telefone, email, obs, senha
              db.session.add(pd)
              db.session.commit()
              print("Clientes inseridos com sucesso!")
    return redirect('/')