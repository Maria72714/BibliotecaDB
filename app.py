from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from configs.configs import engine
from sqlalchemy import text


app = Flask(__name__)
app.secret_key = 'secret_key_123'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@classmethod
def get(cls, user_id):
    with engine.connect() as conn:
        obj = conn.execute(text(f'SELECT * FROM Usuarios WHERE ID_usuario = {user_id}'))
        return obj

@login_manager.user_loader
def load_user(user_id):
    query = text("""
        SELECT id, nome, email, senha
        FROM usuarios
        WHERE id = :user_id
        LIMIT 1
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id})
        row = result.fetchone()

        if row:
            return dict(row._mapping)
        else:
            return None

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
        with engine.connect() as conn:
            query = text(f'''
                         INSERT INTO USUARIOS
                         VALUES (DEFAULT, {nome}, {email}, {senha_hash}, {telefone}, {data}, {multa})
                         ''')
            conn.execute(query)
            conn.commit()
        return redirect(url_for('login'))

    return render_template('cadastro_usuario.html')

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        with engine.connect() as conn:
            query = text(f'''
                    SELECT email, senha FROM Usuarios
                    WHERE email = {email}
                ''')
            usuario = conn.execute(query).fetchone()
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
    app.run(debug=True)