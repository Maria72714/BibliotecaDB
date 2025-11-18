from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required
from extensions.database import engine
from sqlalchemy import text

editora_bp = Blueprint("editora", __name__, static_folder="static", template_folder="templates")

@editora_bp.route('/cadastro_editora', methods=['POST', 'GET'])
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
        return redirect(url_for('livro.cadastro_livro'))
    return render_template('cadastro_editora.html')  

@editora_bp.route('/editoras')
def listar_editoras():
    with engine.connect() as conn:
        query = text("SELECT * FROM Editoras")
        rows = conn.execute(query).mappings().fetchall()
    return render_template('lista_editoras.html', rows=rows)   

@editora_bp.route('/editar_editoras/<int:id>', methods=['GET', 'POST'])
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

            return redirect(url_for('editora.listar_editoras'))

        editora = conn.execute(text("""
            SELECT * FROM Editoras
            WHERE ID_editora = :id
        """), {"id": id}).mappings().fetchone()

    return render_template('editar_editora.html', editora=editora)

@editora_bp.route('/deletar_editoras/<int:id>')
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
    return redirect(url_for('editora.listar_editoras'))
