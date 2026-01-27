import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine
from urllib.parse import quote_plus

senha = quote_plus("29062007")  # Substitua 'sua_senha_aqui' pela senha correta do banco de dados
engine = create_engine(f'mysql+pymysql://root:{senha}@localhost/db_atividade17')
