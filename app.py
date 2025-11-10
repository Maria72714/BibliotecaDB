from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from configs.engine import engine
from sqlalchemy import text


app = Flask(__name__)
app.secret_key = 'secret_key_123'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, nome=None, email=None, senha=None):
        self.id = str(id) if id is not None else None
        self.nome = nome
        self.email = email
        self.senha = senha

    @classmethod
    def get_by_id(cls, user_id):
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT ID_usuario, Nome_usuario, Email, Senha FROM Usuarios WHERE ID_usuario = :id"),
                {"id": user_id}
            ).fetchone()

            if result:
                return cls(*result)
            return None
            
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

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
            query = text("""
                         INSERT INTO Usuarios (ID_usuario, Nome_usuario, Email, Senha, Numero_telefone, Data_inscricao, Multa_atual)
                         VALUES (DEFAULT, :nome, :email, :senha_hash, :telefone, :data, :multa)
                         """)
            conn.execute(query, {
                "nome": nome,
                "email": email,
                "senha_hash": senha_hash,
                "telefone": telefone,
                "data": data,
                "multa": multa
            })
            conn.commit()
        return redirect(url_for('login'))

    return render_template('cadastro_usuario.html')

@app.route('/login', methods = ['POST','GET'])
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
                return redirect(url_for('cadastro_livro'))
            
            flash('Email ou senha inválidos')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/cadastro_livro', methods=['POST', 'GET'])
@login_required
def cadastro_livro():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        isbn = request.form['isbn']
        ano_publicacao = request.form['ano_publicacao']
        genero = request.form['genero']
        editora = request.form['editora']
        quantidade = request.form['qtd_disponivel'] 
        resumo = request.form['resumo']

        with engine.connect() as conn:
            query_editora = text("""
                SELECT ID_editora FROM Editoras
                WHERE Nome_editora = :editora
            """)

            query_genero = text("""
                SELECT ID_genero FROM Generos
                WHERE Nome_genero = :genero
            """)

            query_autor = text("""
                SELECT ID_autor from Autores
                WHERE Nome_autor = :autor
            """)

            query = text("""
                INSERT INTO Livros
                VALUES (
                      DEFAULT,
                      :titulo, 
                      :autor, 
                      :isbn, 
                      :publicacao, 
                      :genero,
                      :editora,
                      :quantidade,
                      :resumo
                      )
            """)

            editora_id = conn.execute(query_editora, {"editora": editora}).scalar()
            genero_id = conn.execute(query_genero, {"genero": genero}).scalar()
            autor_id = conn.execute(query_autor, {"autor": autor}).scalar()

            if not editora_id:
                return redirect(url_for('cadastro_editora'))
            elif not genero_id:
                 return redirect(url_for('cadastro_genero'))
            elif not autor_id:
                return redirect(url_for('cadastro_autor'))
            else:
                conn.execute(query, {
                    'titulo': titulo,
                    'autor': autor_id,
                    'isbn': isbn,
                    'publicacao': ano_publicacao,
                    'genero': genero_id,
                    'editora': editora_id,
                    'quantidade': quantidade,
                    'resumo': resumo
                })
                conn.commit()
        return redirect(url_for('index'))
    return render_template('cadastro_livro.html')

@app.route('/cadastro_autor', methods=['POST', 'GET'])
@login_required
def cadastro_autor():
    if request.method == 'POST':
        nome = request.form['nome']
        nacionalidade = request.form['nacionalidade']
        data_nascimento = request.form['data_nascimento']
        biografia = request.form['biografia']

        with engine.connect() as conn:
            sql = text("""
                INSERT INTO Autores 
                VALUES(DEFAULT, :nome, :nacionalidade, :nascimento, :biografia)
            """)
            conn.execute(sql, {'nome': nome,
                               'nacionalidade': nacionalidade,
                               'nascimento': data_nascimento, 
                               'biografia': biografia})
            conn.commit()
            return redirect(url_for('cadastro_livro'))
    return render_template('cadastro_autor.html')

@app.route('/cadastro_genero', methods=['POST', 'GET'])
@login_required
def cadastro_genero():
    if request.method == 'POST':
        genero = request.form['nome']

        with engine.connect() as conn:
            sql = text("""
                INSERT INTO Generos 
                VALUES(DEFAULT, :genero)
            """)
            conn.execute(sql, {'genero': genero})
            conn.commit()
        return redirect(url_for('cadastro_livro'))
    return render_template('cadastro_genero.html')

@app.route('/cadastro_editora', methods=['POST', 'GET'])
@login_required
def cadastro_editora():
    if request.method == 'POST':
        editora = request.form['nome']
        endereco = request.form['endereco']

        with engine.connect() as conn:
            sql = text("""
                INSERT INTO Editoras 
                VALUES(DEFAULT, :editora, :endereco)
            """)
            conn.execute(sql, {'editora': editora, 'endereco': endereco})
            conn.commit()
        return redirect(url_for('cadastro_livro'))
    return render_template('cadastro_editora.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)