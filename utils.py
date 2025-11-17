from flask_login import LoginManager, UserMixin
from extensions.database import engine
from sqlalchemy import text

login_manager = LoginManager()
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