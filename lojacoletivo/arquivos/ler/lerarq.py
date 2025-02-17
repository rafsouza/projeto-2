# python3 lerarq.py
import csv
import os



# Lendo arquivo csv e enviando dados ao banco de dados
# /arquivos/dbload
arquivo = "dbproduto"
pasta = "arquivos/ler/"
arq_path = os.path.join(pasta, arquivo)
# print(arq_path)

arq_path = os.path.join(pasta, arquivo) # Produto
if os.path.isfile(arq_path):
    with open(arq_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
          print(row)
          # pd = Produto(nome_produto, qtd, porcao, preco, categoria)
          pd = Produto(row[0], float(row[1]), row[2], float(row[3]), row[4], row[5], row[6])
          db.session.add(pd)
          db.session.commit()
          print("Dados inseridos com sucesso!")

'''arquivo = "dbpr"
arq_path = os.path.join(pasta, arquivo) # Produtor
if os.path.isfile(arq_path):
    with open(arq_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
          print(row)
          # pd = Produtor(CPF, nome_pr, endereco, telefone, email)
          pd = Produtor(int(row[0]), row[1], row[2], int(row[3]), row[4])
          db.session.add(pd)
          db.session.commit()
          print("Produtores inseridos com sucesso!")'''