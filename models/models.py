from sqlalchemy.orm import mapped_column, Mapped, declarative_base, Session,relationship
from sqlalchemy import Integer, String, Date, Float, VARCHAR, DECIMAL, create_engine,ForeignKey,Text
from datetime import date
from flask_login import UserMixin

engine = create_engine('mysql://root:@localhost/db_atividade17')

Base = declarative_base()

class User(Base,UserMixin):
    __tablename__ = 'usuarios'

    id_user:Mapped[int] = mapped_column(Integer, primary_key=True)
    Nome_usuario:Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    email:Mapped[str] = mapped_column(VARCHAR(255), nullable=False, unique=True)
    senha : Mapped[int] = mapped_column(VARCHAR(60), nullable= False)
    Numero_telefone:Mapped[str] = mapped_column(VARCHAR(15), nullable=False)
    data_inscricao:Mapped[date] = mapped_column(Date, nullable=False)
    multa_atual:Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)

    @classmethod
    def get(cls, user_id):
        with Session(bind = engine) as sessao:
            obj = sessao.query(User).where(User.id_user == user_id).first()
            sessao.close()
            return obj
class Autores(Base):
    __tablename__ = 'autores'
    id_autor:Mapped[int] = mapped_column(Integer, primary_key=True)
    Nome_autor:Mapped[str] = mapped_column(VARCHAR(255), nullable=False)                
    Nacionalidade:Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    Data_nascimento:Mapped[date] = mapped_column(Date, nullable=False)
    Biografia:Mapped[str] = mapped_column(VARCHAR(500), nullable=False)

class Genero(Base):
    __tablename__= 'generos'
    id_genero:Mapped[int] = mapped_column(Integer,primary_key=True)
    Nome_genero:Mapped[str] = mapped_column(VARCHAR(255),nullable=False)

class Editora(Base):
    __tablename__= 'editoras'
    id_editora:Mapped[int] = mapped_column(Integer,primary_key=True)
    Nome_editora:Mapped[str] = mapped_column(VARCHAR(255),nullable=False)
    Endereco_editora:Mapped[str] = mapped_column(VARCHAR(255),nullable=True)

class Livro(Base):
    __tablename__ = 'livros'
    id_livro:Mapped[int] = mapped_column(Integer,primary_key=True)
    Titulo:Mapped[str] = mapped_column(VARCHAR(255),nullable=False)
    Autor_id: Mapped[int] = mapped_column(Integer,ForeignKey('autores.id_autor'))
    Autor = relationship("Autores") 
    ISBN:Mapped[str] = mapped_column(VARCHAR(13),nullable=False)
    Ano_publicacao:Mapped[int] = mapped_column(Integer)
    Genero_id: Mapped[int] = mapped_column(Integer,ForeignKey('generos.id_genero'))
    Genero = relationship("Genero") 
    Editora_id: Mapped[int] = mapped_column(Integer,ForeignKey('editoras.id_editora'))
    Editora = relationship("Editora") 
    Quantidade_disponivel: Mapped[int] = mapped_column(Integer)
    Resumo:Mapped[str] = mapped_column(Text)

class Emprestimos(Base):
    __tablename__ = 'emprestimos'
    ID_emprestimo:Mapped[int] = mapped_column(Integer, primary_key=True)
    Usuario_id: Mapped[int] = mapped_column(Integer,ForeignKey('usuarios.id_user'))
    Usuario = relationship("User") 
    Livro_id: Mapped[int] = mapped_column(Integer,ForeignKey('livros.id_livro'))
    Livro = relationship("Livro") 
    Data_emprestimo:Mapped[date] = mapped_column(Date, nullable=False)
    Data_devolucao_prevista:Mapped[date] = mapped_column(Date, nullable=False)
    Data_devolucao_real:Mapped[date] = mapped_column(Date, nullable=True)
    Status_emprestimo:Mapped[str] = mapped_column(VARCHAR(20), nullable=False)

if __name__ == "__main__":

    Base.metadata.create_all(engine)
  
