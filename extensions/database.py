import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root@localhost/db_atividade17')
