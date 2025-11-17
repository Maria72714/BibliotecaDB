from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required
from extensions.database import engine
from sqlalchemy import text

livro_bp = Blueprint("livro", __name__, static_folder="static", template_folder="templates")


@livro_bp.route('/cadastro_livro', methods=['POST', 'GET'])
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


@livro_bp.route('/livros')
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


@livro_bp.route('/livros/editar/<int:id>', methods=['GET', 'POST'])
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


@livro_bp.route('/livros/deletar/<int:id>')
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