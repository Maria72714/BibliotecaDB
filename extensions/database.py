import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine
from urllib.parse import quote_plus

senha = quote_plus("24092001")  # Substitua 'sua_senha_aqui' pela senha correta do banco de dados
engine = create_engine(f'mysql+pymysql://root:{senha}@localhost:3306/db_atividade17')
