from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions.database import engine
from sqlalchemy import text

emprestimo_bp = Blueprint("emprestimo", __name__, static_folder="static", template_folder="templates")

@emprestimo_bp.route('/cadastrar_emprestimo', methods = ['POST','GET'])
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

    with engine.connect() as conn:
        livros = conn.execute(text("SELECT ID_livro, Titulo FROM Livros ORDER BY Titulo")).mappings().fetchall()
        conn.close()        
    return render_template('cadastrar_emprestimo.html', livros=livros)

@emprestimo_bp.route('/emprestimos')
def listar_emprestimos():
    with engine.connect() as conn:
        query = text("SELECT * FROM Emprestimos")
        rows = conn.execute(query).mappings().fetchall()
    return render_template('lista_emprestimo.html', rows=rows)


@emprestimo_bp.route('/editar_emprestimo/<int:id>', methods = ['POST', 'GET'])
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

@emprestimo_bp.route('/deletar_emprestimo/<int:id>')
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

