from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required
from extensions.database import engine
from sqlalchemy import text

genero_bp = Blueprint("genero", __name__, static_folder="static", template_folder="templates")

@genero_bp.route('/cadastro_genero', methods=['POST', 'GET'])
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
        return redirect(url_for('livro.cadastro_livro'))
    return render_template('cadastro_genero.html')


@genero_bp.route('/listar_generos')
def listar_generos():
    with engine.connect() as conn:
        query = text("SELECT * FROM Generos")
        rows = conn.execute(query).mappings().fetchall()
    return render_template('lista_genero.html', rows=rows)


@genero_bp.route('/deletar_genero/<int:id>')
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
    return redirect(url_for('genero.listar_generos'))


@genero_bp.route('/editar_genero/<int:id>', methods=['GET', 'POST'])
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

            return redirect(url_for('genero.listar_generos'))

        
        genero = conn.execute(text("""
            SELECT * FROM Generos
            WHERE ID_genero = :id
        """), {"id": id}).mappings().fetchone()

    return render_template('editar_genero.html', genero=genero)