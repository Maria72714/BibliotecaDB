from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions.database import engine
from sqlalchemy import text
from datetime import date
from sqlalchemy.exc import DBAPIError
from datetime import date


emprestimo_bp = Blueprint("emprestimo", __name__, static_folder="static", template_folder="templates")

@emprestimo_bp.route('/cadastrar_emprestimo', methods = ['POST','GET'])
@login_required
def cadastrar_emprestimo():
    if request.method == 'POST':
        id_livro = request.form['id_livro']
        data_devolucao_prevista = request.form['data_devolucao_prevista']
        # data_d
        # status_emprestimo = request.form['status_emprestimo']

        with engine.connect() as conn:
            try:
                qtd_livro = conn.execute(text('SELECT Quantidade_disponivel from Livros WHERE ID_livro = :id_livro'),{'id_livro':id_livro}).scalar()
                if qtd_livro == 0:
                    flash("livro não pode ser cadastrado, pois não há mais disponivel na biblioteca!", 'error')
                    return redirect(url_for('emprestimo.cadastrar_emprestimo'))
                conn.execute(text('''
                    INSERT INTO Emprestimos
                      (Usuario_id, Livro_id, Data_emprestimo,  Data_devolucao_prevista, Data_devolucao_real, Status_emprestimo)
                    VALUES
                      (:Usuario_id, :Livro_id, :Data_emprestimo, :Data_devolucao_prevista, NULL, :Status_emprestimo)
                '''), {
                    'Usuario_id': current_user.id,
                    'Livro_id': int(id_livro),
                    'Data_emprestimo': date.today(),
                    'Data_devolucao_prevista': data_devolucao_prevista,
                    'Status_emprestimo': 'pendente'
                })
                conn.commit()
            
            except DBAPIError as e:
                mensagem = e.orig.args[1]
                flash(f"Erro ao cadastrar empréstimo: {mensagem}", 'error')

            finally:
                conn.close()

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
            
            try:
                conn.execute(text("""
                    UPDATE Emprestimos
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

            except DBAPIError as e:
                mensagem = e.orig.args[1]
                flash(f"Erro ao atualizar empréstimo: {mensagem}", 'error')
            
            finally:
                conn.close()
                return redirect(url_for('emprestimo.listar_emprestimos'))

        with engine.connect() as conn:
            emprestimos = conn.execute(text("""
                    SELECT * FROM Emprestimos
                    WHERE ID_emprestimo = :id
                """), {"id": id}).mappings().fetchone()
            conn.close()

    return render_template('editar_emprestimo.html', Emprestimos = emprestimos)

@emprestimo_bp.route('/deletar_emprestimo/<int:id>')
@login_required
def deletar_emprestimo(id):
    with engine.connect() as conn:
        try:
            conn.execute(text("UPDATE   Log_Emprestimos SET Emprestimo_id = NULL WHERE Emprestimo_id = :id"), {"id": id})
            conn.execute(text("DELETE  FROM Emprestimos WHERE ID_emprestimo = :id"), {"id": id})
            
            # conn.execute(text("SELECT Livro_id from Emprestimos where ID_emprestimo = :id"), {"id": id})
            # conn.execute(text("UPDATE Livros SET Quantidade_disponivel = Quantidade_disponivel + 1"))
            conn.commit()
        except Exception as e:
            flash(f"Erro de integridade {e}",'error')
        finally:
            conn.close()
    return redirect(url_for('emprestimo.listar_emprestimos'))


@emprestimo_bp.route('/devolucao_emprestimo/<int:id>')
@login_required
def devolucao_emprestimo(id):
    with engine.connect() as conn:
        data_hoje = date.today()
        conn.execute(
                text("""
                    UPDATE Emprestimos
                    SET Data_devolucao_real = :data,
                        Status_emprestimo = 'devolvido'
                    WHERE ID_emprestimo = :id
                """),
                {"data": data_hoje, "id": id}
            )
        conn.commit()
        conn.close()
    return redirect(url_for('emprestimo.listar_emprestimos'))


@emprestimo_bp.route('/logs_emprestimo', methods = ['POST', 'GET'])
# @login_required
def logs_emprestimo():
    with engine.connect() as conn:
        logs = conn.execute(text('SELECT * from Log_Emprestimos'))
    return render_template('logs_emprestimo.html', logs = logs)