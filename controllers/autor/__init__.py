from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required
from extensions.database import engine
from sqlalchemy import text

autor_bp = Blueprint("autor", __name__, static_folder="static", template_folder="templates")

@autor_bp.route('/cadastro_autor', methods=['POST', 'GET'])
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
            return redirect(url_for('livro.cadastro_livro'))
    return render_template('cadastro_autor.html')

@autor_bp.route('/lista_autores')
def lista_autores():
    with engine.connect() as conn:
        query = text("SELECT * FROM Autores")
        autores = conn.execute(query).mappings().fetchall()
    return render_template('lista_autores.html', autores=autores)

@autor_bp.route('/editar_autor/<int:id>', methods=['GET', 'POST'])
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

            return redirect(url_for('livro.listar_livros'))

        autores = conn.execute(text("""
            SELECT * FROM Autores
            WHERE ID_autor = :id
        """), {"id": id}).mappings().fetchone()

    return render_template('editar_autores.html', autores=autores)

@autor_bp.route('/deletar_autor/<int:id>')
@login_required
def deletar_autor(id):
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM Autores WHERE ID_autor = :id"), {"id": id})
            conn.commit()
        except Exception as e:
            flash(f"Erro de integridade {e}", "error")
        finally:
            conn.close()
    return redirect(url_for('autor.lista_autores'))
