from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from models.models import engine, User, Base
from sqlalchemy.orm import Session


app = Flask(__name__)
app.secret_key = 'secret_key_123'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    with Session(bind=engine) as sessao:
        return sessao.query(User).get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods = ['POST','GET'])
def cadastro_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        telefone = request.form['numero_telefone']
        data = request.form["data_inscricao"]
        multa = request.form["multa_atual"]
        
        senha_hash = generate_password_hash(senha)
        with Session(bind = engine) as sessao:
            usuario = User(Nome_usuario = nome,
                           email = email,
                           senha = senha_hash,
                           Numero_telefone = telefone, 
                           data_inscricao = data, 
                           multa_atual = multa)
            
            sessao.add(usuario)
            sessao.commit()
            sessao.close()
            return redirect(url_for('login'))

    return render_template('cadastro_usuario.html')

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        with Session(bind = engine) as sessao:
            usuario = sessao.query(User).filter_by(email=email).first()
            if usuario and check_password_hash(usuario.senha, senha):
                login_user(usuario)
                return redirect(url_for('cadastro_livro'))
    return render_template('login.html')

@app.route('/cadastro_livro')
def cadastro_livro():
    return render_template('cadastro_livro.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":

    Base.metadata.create_all(engine)