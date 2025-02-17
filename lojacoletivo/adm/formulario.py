from wtforms import Form, BooleanField, StringField, PasswordField, validators

class RegistraFormulario(Form):
    nome = StringField('Nome', [validators.Length(min=2, max=100)])
    usuario_adm = StringField('Usuário', [validators.Length(min=2, max=100)])
    email_adm = StringField('E-mail', [validators.Length(min=3, max=100)])
    senha = PasswordField('Senha', [
        validators.DataRequired(),
        validators.EqualTo('confirma', message='A senhas estão diferentes')
    ], description="Digite sua senha" )
    confirma = PasswordField('Digite a senha novamente', description="Confirme sua senha")
    principal = BooleanField('Principal')
    obs = StringField('Observações', [validators.Length(min=0, max=128)])

class AtualizaAdm(Form):
    nome = StringField('Nome*', [validators.Length(min=2, max=100)])
    usuario_adm = StringField('Usuário', [validators.Length(min=2, max=100)])
    email_adm = StringField('E-mail', [validators.Length(min=3, max=100)])
    obs = StringField('Observações', [validators.Length(min=0, max=128)])
    principal = BooleanField('Principal')

class SenhaAdm(Form):
    senha = PasswordField('Senha*', [
        validators.DataRequired(),
        validators.EqualTo('confirma', message='A senhas estão diferentes')
    ], description="Digite sua senha*" )
    confirma = PasswordField('Digite a senha novamente', description="Confirme sua senha")


class LoginFormulario(Form):
    email_adm = StringField('E-mail', [validators.Length(min=3, max=100)])
    senha = PasswordField('Senha', [validators.DataRequired()])