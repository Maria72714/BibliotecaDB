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

@app.route('/livros')
def listar_livros():
    with engine.connect() as conn:
        # Descobre dinamicamente colunas na tabela Livros e monta JOINs opcionais
        db_name = conn.execute(text("SELECT DATABASE()")).scalar()
        colnames = set()
        if db_name:
            cols = conn.execute(
                text(
                    """
                    SELECT COLUMN_NAME
                    FROM information_schema.columns
                    WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = 'Livros'
                    """
                ), {"schema": db_name}
            ).fetchall()
            colnames = {c[0] for c in cols}

        # Candidatos para cada campo
        quantity_candidates = ['Qtd_disponivel', 'Quantidade', 'Disponivel', 'Qtd', 'Qtd_estoque', 'Quantidade_disponivel']
        autor_fk_candidates = ['Autor', 'ID_autor', 'Autor_id', 'AutorID', 'id_autor', 'fk_autor', 'Autor_fk', 'IDAutor']
        genero_fk_candidates = ['Genero', 'ID_genero', 'Genero_id', 'GeneroID', 'id_genero', 'fk_genero', 'Genero_fk', 'IDGenero']
        editora_fk_candidates = ['Editora', 'ID_editora', 'Editora_id', 'EditoraID', 'id_editora', 'fk_editora', 'Editora_fk', 'IDEditora']

        def pick(colset, candidates):
            for c in candidates:
                if c in colset:
                    return c
            return None

        qty_col = pick(colnames, quantity_candidates)
        autor_fk = pick(colnames, autor_fk_candidates)
        genero_fk = pick(colnames, genero_fk_candidates)
        editora_fk = pick(colnames, editora_fk_candidates)

        # Campos base (usa NULL se não existir para evitar quebrar)
        id_expr = 'l.ID_livro' if 'ID_livro' in colnames else 'NULL'
        titulo_expr = 'l.Titulo' if 'Titulo' in colnames else 'NULL'
        isbn_expr = 'l.ISBN' if 'ISBN' in colnames else 'NULL'
        ano_expr = 'l.Ano_publicacao' if 'Ano_publicacao' in colnames else 'NULL'
        resumo_expr = 'l.Resumo' if 'Resumo' in colnames else 'NULL'
        qtd_expr = f"l.{qty_col}" if qty_col else 'NULL'

        select_parts = [
            f"{id_expr} AS ID_livro",
            f"{titulo_expr} AS Titulo",
            f"{isbn_expr} AS ISBN",
            f"{ano_expr} AS Ano_publicacao",
            f"{resumo_expr} AS Resumo",
            f"{qtd_expr} AS Qtd",
        ]

        joins = []
        if autor_fk:
            joins.append(f"LEFT JOIN Autores a ON l.{autor_fk} = a.ID_autor")
            select_parts.append("a.Nome_autor AS Autor")
        else:
            select_parts.append("NULL AS Autor")

        if genero_fk:
            joins.append(f"LEFT JOIN Generos g ON l.{genero_fk} = g.ID_genero")
            select_parts.append("g.Nome_genero AS Genero")
        else:
            select_parts.append("NULL AS Genero")

        if editora_fk:
            joins.append(f"LEFT JOIN Editoras e ON l.{editora_fk} = e.ID_editora")
            select_parts.append("e.Nome_editora AS Editora")
        else:
            select_parts.append("NULL AS Editora")

        order_expr = 'l.ID_livro' if 'ID_livro' in colnames else ('l.Titulo' if 'Titulo' in colnames else '1')

        sql_str = (
            "SELECT " + ",\n                ".join(select_parts) +
            "\nFROM Livros l\n" +
            ("\n".join(joins) + "\n" if joins else "") +
            f"ORDER BY {order_expr} DESC"
        )

        result = conn.execute(text(sql_str))
        livros = result.fetchall()

        # Tabela genérica: cabeçalhos e linhas reais da tabela Livros (SELECT *)
        headers = []
        rows = []
        if db_name:
            header_rows = conn.execute(
                text(
                    """
                    SELECT COLUMN_NAME
                    FROM information_schema.columns
                    WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = 'Livros'
                    ORDER BY ORDINAL_POSITION
                    """
                ), {"schema": db_name}
            ).fetchall()
            headers = [h[0] for h in header_rows]
        rows = conn.execute(text("SELECT * FROM Livros"))
        rows = rows.fetchall()

    return render_template('lista_livros.html', livros=livros, headers=headers, rows=rows)

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
                         INSERT INTO Usuarios
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

            # Auto-cria vinculados se não existirem
            if not editora_id:
                ins_e = text("INSERT INTO Editoras (Nome_editora, Endereco) VALUES (:editora, :endereco)")
                res_e = conn.execute(ins_e, {"editora": editora, "endereco": ""})
                conn.commit()
                editora_id = conn.execute(query_editora, {"editora": editora}).scalar()

            if not genero_id:
                ins_g = text("INSERT INTO Generos (Nome_genero) VALUES (:genero)")
                res_g = conn.execute(ins_g, {"genero": genero})
                conn.commit()
                genero_id = conn.execute(query_genero, {"genero": genero}).scalar()

            if not autor_id:
                ins_a = text("INSERT INTO Autores (Nome_autor, Nacionalidade, Data_nascimento, Biografia) VALUES (:autor, NULL, NULL, NULL)")
                res_a = conn.execute(ins_a, {"autor": autor})
                conn.commit()
                autor_id = conn.execute(query_autor, {"autor": autor}).scalar()

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