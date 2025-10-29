from sqlalchemy.orm import mapped_column, Mapped, declarative_base
from sqlalchemy import Integer, String, Date, Float, VARCHAR, DECIMAL
from datetime import date

Base = declarative_base()

class User(Base):
    __tablename__ = 'usuario'

    id_user:Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_user:Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    email:Mapped[str] = mapped_column(VARCHAR(255), nullable=False, unique=True)
    numero_telefone:Mapped[str] = mapped_column(VARCHAR(15), nullable=False)
    data_inscricao:Mapped[date] = mapped_column(Date, nullable=False)
    multa_atual:Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    