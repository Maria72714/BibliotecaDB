from extensions import app
from utils import login_manager
from controllers import auth, autor, editora, emprestimo, genero, livro, usuario

app.secret_key = 'secret_key_123'

login_manager.init_app(app)

app.register_blueprint(auth.auth_bp)
app.register_blueprint(autor.autor_bp)
app.register_blueprint(editora.editora_bp)
app.register_blueprint(emprestimo.emprestimo_bp)
app.register_blueprint(genero.genero_bp)
app.register_blueprint(livro.livro_bp)
app.register_blueprint(usuario.usuario_bp)


if __name__ == "__main__":
    app.run(debug=True)
    
