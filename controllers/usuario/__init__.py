from flask import Blueprint, request, render_template, flash, redirect, url_for
from extensions.database import engine
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from werkzeug.security import generate_password_hash

usuario_bp = Blueprint("usuario", __name__, static_folder="static", template_folder="templates")

@usuario_bp.route('/cadastro', methods = ['POST','GET'])
def cadastro_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        telefone = request.form['numero_telefone']
        
        senha_hash = generate_password_hash(senha)
        with engine.connect() as conn:
            sql = text("""
                   SELECT * FROM Usuarios WHERE Email = :email
                    """)
            user = conn.execute(sql, {"email":email}).fetchone()
            if user:
                flash('Usuário já cadastrado','error')
                return redirect(url_for('usuario.cadastro_usuario'))
            
            else:
                query = text("""
                            INSERT INTO Usuarios
                           (Nome_usuario, Email, Senha, Numero_telefone) VALUES
                              (:nome, :email, :senha_hash, :telefone) """)
                
                try:
                    conn.execute(query, {
                        "nome": nome,
                        "email": email,
                        "senha_hash": senha_hash,
                        "telefone": telefone
                    })

                except DBAPIError as e:
                    mensagem = e.orig.args[1]
                    flash(f'Erro ao cadastrar usuário: {mensagem}','error')
                    return redirect(url_for('usuario.cadastro_usuario'))
                
                finally:
                    conn.commit()
            return redirect(url_for('auth.login'))

    return render_template('cadastro_usuario.html')