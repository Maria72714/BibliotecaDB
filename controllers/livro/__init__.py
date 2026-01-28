from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from flask_login import login_required
from extensions.database import engine
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

livro_bp = Blueprint("livro", __name__, static_folder="static", template_folder="templates")


@livro_bp.route('/cadastro_livro', methods=['POST', 'GET'])
@login_required
def cadastro_livro():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor_id = request.form['autor']
        isbn = request.form['isbn']
        ano_publicacao = request.form['ano_publicacao']
        genero_id = request.form['genero']
        editora_id = request.form['editora']
        quantidade = request.form['qtd_disponivel'] 
        resumo = request.form['resumo']

        with engine.connect() as conn:
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

             if editora_id == 'none' or editora_id == '':
                flash('Editora não encontrada, cadastre para continuar!','error')
                return redirect(url_for('editora.cadastro_editora'))

             if genero_id == 'none' or genero_id == '':
                flash('Genero não encontrado, cadastre para continuar!', 'error')
                return redirect(url_for('genero.cadastro_genero'))

             if autor_id == 'none' or autor_id == '':
                flash('autor não encontrado, cadastre para continuar!', 'error')
                return redirect(url_for('autor.cadastro_autor'))

             try:
                autor_id = int(autor_id)
                editora_id = int(editora_id)
                genero_id = int(genero_id)
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
 
             except DBAPIError as e:
                mensagem = e.orig.args[1]
                flash(f"Erro ao cadastrar livro: {mensagem}", 'error')
                return redirect(url_for('livro.cadastro_livro'))
            
             finally:
                conn.close()

        return redirect(url_for('livro.listar_livros'))
    
    with engine.connect() as conn:
        generos = conn.execute(text("SELECT * FROM Generos ORDER BY Nome_genero")).mappings().fetchall()
        editoras = conn.execute(text("SELECT * FROM Editoras ORDER BY Nome_editora")).mappings().fetchall()
        autores = conn.execute(text("SELECT * FROM Autores ORDER BY Nome_autor")).mappings().fetchall() 
        conn.close()
    return render_template('cadastro_livro.html' , generos=generos, editoras=editoras, autores=autores)


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

            try:
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

            except DBAPIError as e:
                mensagem = e.orig.args[1]
                flash(f"Erro ao atualizar o livro: {mensagem}", 'error')
                return redirect(url_for('livro.editar_livro', id=id)) 

            finally:
                conn.close()
            
            return redirect(url_for('livro.listar_livros'))

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
            conn.execute(text("UPDATE Log_Livros SET Livro_id = NULL WHERE Livro_id = :id"), {"id": id})
            conn.execute(text("DELETE FROM Livros WHERE ID_livro = :id"), {"id": id})
            conn.commit()
        except DBAPIError as e:
            mensagem = e.orig.args[1]
            flash(f"Erro de integridade: {mensagem}", 'error')
        finally:
            conn.close()
    return redirect(url_for('livro.listar_livros'))
