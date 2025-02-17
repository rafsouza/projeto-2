from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField

class RegistraCliente(Form):
    nome = StringField('Nome*', [validators.Length(min=2, max=100)])
    endereco = StringField('Endereço*', [validators.Length(min=2, max=100)])
    cidade = StringField('Cidade*', [validators.Length(min=2, max=100)])
    telefone = IntegerField('Telefone*', [validators.NumberRange(min=2)])
    email = StringField('E-mail*', [validators.Length(min=3, max=100)])
    obs = StringField('Observações')
    senha = PasswordField('Senha*', [
        validators.DataRequired(),
        validators.EqualTo('confirma', message='A senhas estão diferentes')
    ], description="Digite sua senha*" )
    confirma = PasswordField('Digite a senha novamente', description="Confirme sua senha")

class LoginCliente(Form):
    email = StringField('E-mail', [validators.Length(min=3, max=100)])
    senha = PasswordField('Senha', [validators.DataRequired()])

class AtualizaCliente(Form):
    nome = StringField('Nome*', [validators.Length(min=2, max=100)])
    endereco = StringField('Endereço*', [validators.Length(min=2, max=100)])
    cidade = StringField('Cidade*', [validators.Length(min=2, max=100)])
    telefone = IntegerField('Telefone*', [validators.NumberRange(min=2)])
    email = StringField('E-mail*', [validators.Length(min=3, max=100)])
    obs = StringField('Observações')

class SenhaCliente(Form):
    senha = PasswordField('Senha*', [
        validators.DataRequired(),
        validators.EqualTo('confirma', message='A senhas estão diferentes')
    ], description="Digite sua senha*" )
    confirma = PasswordField('Digite a senha novamente', description="Confirme sua senha")