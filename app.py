from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from models.models import engine, User
from sqlalchemy.orm import Session


app = Flask(__name__)
app.secret_key = 'secret_key_123'



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
        
        with Session(bind = engine) as sessao:
            usuario = User(Nome_usuario = nome, email = email,senha = senha ,Numero_telefone = telefone, data_inscricao = data, multa_atual = multa)
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
            usuario = sessao.query(User).filter_by(email = email, senha = senha)
            if usuario:
                return redirect(url_for('cadastro_livro'))
    return render_template('login.html')

@app.route('/cadastro_livro')
def cadastro_livro():
    return render_template('cadastro_livro.html')