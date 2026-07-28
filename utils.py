import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

load_dotenv()


db_username = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_db = os.environ.get("DB_DB")

USER = db_username
PASSWORD = db_password
HOST = db_host
PORT = db_port
DB = db_db

# Base de exemplo gerada por seed.py, usada quando não há Postgres configurado.
BASE_EXEMPLO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados_exemplo.db')

def conectar_banco_de_dados():
    if HOST:
        DATABASE_URL = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    elif os.path.exists(BASE_EXEMPLO):
        DATABASE_URL = f'sqlite:///{BASE_EXEMPLO}'
    else:
        raise RuntimeError(
            'Nenhuma base disponível. Configure o Postgres no .env '
            '(veja .env.example) ou rode "python seed.py" para gerar '
            'a base de exemplo.'
        )
    engine = create_engine(DATABASE_URL)
    return engine

def ler_tabela(colunas_selecionadas, nome_da_tabela):
    engine = conectar_banco_de_dados()
    query = f""" SELECT {colunas_selecionadas} FROM {nome_da_tabela}"""
    return pd.read_sql_query(query, engine)