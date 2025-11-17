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
        # Faz o JOIN para trazer nomes de autor e editora
        query = text("""
            SELECT 
                l.ID_livro,
                l.Titulo,
                a.Nome_autor AS Autor,
                e.Nome_editora AS Editora,
                g.Nome_genero AS Genero,
                l.ISBN,
                l.Ano_publicacao,
                l.Resumo,
                l.Quantidade_disponivel
            FROM Livros l
            JOIN Autores a ON l.Autor_id = a.ID_autor
            JOIN Editoras e ON l.Editora_id = e.ID_editora
            JOIN Generos g ON l.Genero_id = g.ID_genero
            ORDER BY l.ID_livro DESC
        """)
        rows = conn.execute(query).mappings().fetchall()

    return render_template('lista_livros.html', rows=rows)

@app.route('/editoras')
def listar_editoras():
    with engine.connect() as conn:
        query = text("SELECT * FROM Editoras")
        rows = conn.execute(query).mappings().fetchall()
    return render_template('lista_editoras.html', rows=rows) 

@app.route('/editar_editoras/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_editoras(id):
    with engine.connect() as conn:
        if request.method == 'POST':
            nome = request.form['nome']
            endereco = request.form['endereco']

            conn.execute(text("""
                UPDATE Editoras
                SET Nome_editora = :nome,
                    Endereco_editora = :endereco
                WHERE ID_editora = :id
            """), {"nome": nome, "endereco": endereco ,"id": id})
            conn.commit()

            return redirect(url_for('listar_editoras'))

        editora = conn.execute(text("""
            SELECT * FROM Editoras
            WHERE ID_editora = :id
        """), {"id": id}).mappings().fetchone()

    return render_template('editar_editora.html', editora=editora)

@app.route('/deletar_editoras/<int:id>')
@login_required
def deletar_editoras(id):
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM Editoras WHERE ID_editora = :id"), {"id": id})
            conn.commit()
        except Exception as e:
            flash(f"Erro de integridade {e}")
        finally:
            conn.close()
    return redirect(url_for('listar_editoras'))

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
            sql = text("""
                   SELECT * FROM Usuarios WHERE Email = :email
                    """)
            user = conn.execute(sql, {"email":email}).fetchone()
            if user:
                flash('Usuário já cadastrado')
                return redirect(url_for('cadastro_usuario'))
            
            else:
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
                return redirect(url_for('cadastro_editora'))
                '''sql = text("""
                    INSERT INTO Editoras 
                    VALUES (DEFAULT, :editora, NULL)
                """)
                conn.execute(sql, {"editora":editora})
                flash("editora ainda não cadastrada")'''
                
            if not genero_id:
                return redirect(url_for('cadastro_genero'))
                '''sql = text("""
                    INSERT INTO Generos 
                    VALUES (DEFAULT, :genero)
                """)
                conn.execute(sql, {"genero":genero})
                flash("gênero ainda não cadastrado")'''
            if not autor_id:
                return redirect(url_for('cadastro_autor'))
                '''sql = text("""
                    INSERT INTO Autores 
                    VALUES (DEFAULT, :autor, NULL, NULL, NULL)
                """)
                conn.execute(sql, {"autor":autor})
                flash("autor ainda não cadastrado")'''
            

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

@app.route('/livros/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_livro(id):
    with engine.connect() as conn:
        if request.method == 'POST':
            titulo = request.form['titulo']
            isbn = request.form['isbn']
            ano = request.form['ano_publicacao']
            resumo = request.form['resumo']
            qtd = request.form['qtd_disponivel']

            conn.execute(text("""
                UPDATE Livros
                SET Titulo = :titulo,
                    ISBN = :isbn,
                    Ano_publicacao = :ano,
                    Resumo = :resumo,
                    Quantidade_disponivel = :qtd
                WHERE ID_livro = :id
            """), {"titulo": titulo, "isbn": isbn, "ano": ano, "resumo": resumo, "qtd": qtd, "id": id})
            conn.commit()

            return redirect(url_for('listar_livros'))

        #  Quando for GET (abrir a página), busca o livro no banco:
        livro = conn.execute(text("""
            SELECT 
                l.ID_livro,
                l.Titulo,
                a.Nome_autor AS Autor,
                e.Nome_editora AS Editora,
                l.ISBN,
                l.Ano_publicacao,
                g.Nome_genero AS Genero,
                l.Resumo,
                l.Quantidade_disponivel
            FROM Livros l
            JOIN Autores a ON l.Autor_id = a.ID_autor
            JOIN Editoras e ON l.Editora_id = e.ID_editora
            JOIN Generos g ON l.Genero_id = g.ID_genero
            WHERE l.ID_livro = :id
        """), {"id": id}).mappings().fetchone()

    return render_template('editar_livro.html', livro=livro)

@app.route('/livros/deletar/<int:id>')
@login_required
def deletar_livro(id):
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM Livros WHERE ID_livro = :id"), {"id": id})
            conn.commit()
        except Exception as e:
            flash(f"Erro de integridade {e}")
        finally:
            conn.close()
    return redirect(url_for('listar_livros'))

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


@app.route('/listar_generos')
def listar_generos():
    with engine.connect() as conn:
        query = text("SELECT * FROM Generos")
        rows = conn.execute(query).mappings().fetchall()
    return render_template('lista_genero.html', rows=rows)

@app.route('/deletar_genero/<int:id>')
@login_required
def deletar_genero(id):
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM Generos WHERE ID_genero = :id"), {"id": id})
            conn.commit()
        except Exception as e:
            flash(f"Erro de integridade {e}")
        finally:
            conn.close()
    return redirect(url_for('listar_generos'))

@app.route('/editar_genero/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_genero(id):
    with engine.connect() as conn:
        
        if request.method == 'POST':
            nome = request.form['nome_genero']

            conn.execute(text("""
                UPDATE Generos
                SET Nome_genero = :nome
                WHERE ID_genero = :id
            """), {"nome": nome, "id": id})
            conn.commit()

            return redirect(url_for('listar_generos'))

        
        genero = conn.execute(text("""
            SELECT * FROM Generos
            WHERE ID_genero = :id
        """), {"id": id}).mappings().fetchone()

    return render_template('editar_genero.html', genero=genero)

@app.route('/editar_autor/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_autor(id):
    with engine.connect() as conn:
        if request.method == 'POST':
            nome = request.form['nome']
            nacionalidade = request.form['nacionalidade']
            data_nascimento = request.form['data_nascimento']
            biografia = request.form['biografia']

            conn.execute(text("""
                UPDATE Autores
                SET Nome_autor = :nome,
                    Nacionalidade = :nacionalidade,
                    Data_nascimento = :data_nascimento,
                    Biografia = :biografia
                WHERE ID_autor = :id
            """), {
                "nome": nome,
                "nacionalidade": nacionalidade,
                "data_nascimento": data_nascimento,
                "biografia": biografia,
                "id": id
            })
            conn.commit()

            return redirect(url_for('listar_livros'))

        autores = conn.execute(text("""
            SELECT * FROM Autores
            WHERE ID_autor = :id
        """), {"id": id}).mappings().fetchone()

    return render_template('editar_autores.html', autores=autores)

@app.route('/deletar_autor/<int:id>')
@login_required
def deletar_autor(id):
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM Autores WHERE ID_autor = :id"), {"id": id})
            conn.commit()
        except Exception as e:
            flash(f"Erro de integridade {e}")
        finally:
            conn.close()
    return redirect(url_for('lista_autores'))


@app.route('/lista_autores')
def lista_autores():
    with engine.connect() as conn:
        query = text("SELECT * FROM Autores")
        autores = conn.execute(query).mappings().fetchall()
    return render_template('lista_autores.html', autores=autores)


@app.route('/cadastrar_emprestimo', methods = ['POST','GET'])
@login_required
def cadastrar_emprestimo():
    if request.method == 'POST':
        isbn = request.form['ISBN']
        data_emprestimo = request.form['data_emprestimo']
        data_devolucao = request.form['data_devolucao']
        data_devolucao_real = request.form['data_devolucao_real']
        status_emprestimo = request.form['status_emprestimo']

        with engine.connect() as conn:
            
            livro = conn.execute(text('select ID_livro from Livros where ISBN = :isbn '),{'isbn':isbn}).scalar()
            
            qtd_livro = conn.execute(text('SELECT Quantidade_disponivel from Livros WHERE ID_livro = :id_livro'),{'id_livro':livro}).scalar()
            if qtd_livro < 1:
                flash("livro não pode ser cadastrado, pois não há mais disponivel na biblioteca!")
                return redirect(url_for('cadastrar_emprestimo'))
            conn.execute(text('INSERT INTO Emprestimos VALUES(DEFAULT, :Usuario_id, :Livro_id, :Data_emprestimo,:Data_devolucao_prevista, :Data_devoluçao_real,:Status_emprestimo)'),
            {'Usuario_id' : current_user.id,'Livro_id' : livro, 'Data_emprestimo' : data_emprestimo, 'Data_devolucao_prevista': data_devolucao, 'Data_devoluçao_real': data_devolucao_real , 'Status_emprestimo' : status_emprestimo})
            #atualizando a quantidade de livros
            conn.execute(text("""
                        UPDATE Livros
                        SET Quantidade_disponivel = Quantidade_disponivel - 1
                        WHERE ISBN = :isbn"""), { 'isbn':isbn})
            conn.commit()
    return render_template('cadastrar_emprestimo.html')

@app.route('/emprestimos')
def listar_emprestimos():
    with engine.connect() as conn:
        query = text("SELECT * FROM Emprestimos")
        rows = conn.execute(query).mappings().fetchall()
    return render_template('lista_emprestimo.html', rows=rows)


@app.route('/deletar_emprestimo/<int:id>')
@login_required
def deletar_emprestimo(id):
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM Emprestimos WHERE ID_emprestimo = :id"), {"id": id})
            conn.commit()
        except Exception as e:
            flash(f"Erro de integridade {e}")
        finally:
            conn.close()
    return redirect(url_for('listar_emprestimos'))

@app.route('/editar_emprestimo/<int:id>', methods = ['POST', 'GET'])
@login_required
def editar_emprestimo(id):
    with engine.connect() as conn:
        if request.method == 'POST':
            data_emprestimo = request.form['Data_emprestimo']
            data_devolucao_prevista = request.form['Data_devolucao_prevista']
            data_devolucao_real = request.form['Data_devolucao_real']
            status_emprestimo = request.form['Status_emprestimo']

            conn.execute(text("""
                UPDATE emprestimos
                SET Data_emprestimo = :data_emprestimo,
                    Data_devolucao_prevista = :data_devolucao_prevista,
                    Data_devolucao_real = :data_devolucao_real,
                    Status_emprestimo = :status_emprestimo
                WHERE ID_emprestimo = :id
            """), {
                "data_emprestimo": data_emprestimo,
                "data_devolucao_prevista": data_devolucao_prevista,
                "data_devolucao_real": data_devolucao_real,
                "status_emprestimo": status_emprestimo,
                "id": id
            })
            conn.commit()


        emprestimos = conn.execute(text("""
                SELECT * FROM Emprestimos
                WHERE ID_emprestimo = :id
            """), {"id": id}).mappings().fetchone()

    return render_template('editar_emprestimo.html', Emprestimos = emprestimos)




if __name__ == "__main__":
    app.run(debug=True)
    
