from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user
from extensions.database import engine
from sqlalchemy import text
from werkzeug.security import check_password_hash

from utils import User 

auth_bp = Blueprint("auth", __name__, static_folder="static", template_folder="templates")

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        with engine.connect() as conn:
            query = text("""
                    SELECT ID_usuario, Email, Senha FROM Usuarios
                    WHERE Email = :email
                    """)
            result = conn.execute(query, {"email": email})
            usuario = result.fetchone()
            
            if usuario and check_password_hash(usuario.Senha, senha):
                user = User.get_by_id(usuario.ID_usuario)
                login_user(user)
                return redirect(url_for('livro.cadastro_livro'))
            
            flash('Email ou senha inválidos', 'error')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))