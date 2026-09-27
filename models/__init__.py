from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_utils import models
import os

# # importando os elementos definidos no modelo
from models.base import Base
from models.earthquakes import Earthquakes
from models.pipelines import Pipelines

# Database URL from environment or default
db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:admin@127.0.0.1:5432/seismic_pipe_monitor?client_encoding=utf8")

# cria a engine de conexão com o banco
engine = create_engine(db_url, echo=False)

# Instancia um criador de sessão com o banco
Session = sessionmaker(bind=engine)

# cria o banco se ele não existir 
if not database_exists(engine.url):
    create_database(engine.url) 

# cria as tabelas do banco, caso não existam
Base.metadata.create_all(engine)
