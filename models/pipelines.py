from sqlalchemy import Column, String, Integer, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.functions import ST_AsText

from  models import Base


class Pipelines(Base):

    __tablename__ = 'pipeline_details'

    id = Column("pk_pipeline", Integer, primary_key=True)

    pais = Column(String(140)) 
    operadora = Column(String(140))
    nome_duto = Column(String(140))
    produto = Column(String(140))    

    # Armazena uma sequência ordenada de pontos que formam a trajetória da tuberia
    geom = Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=False)

    # A data de inserção será o instante de inserção caso não tenha
    # um valor definido pelo usuário
    data_insercao = Column(DateTime, default=datetime.now)
    
    def __init__(self, nome_duto: str, operadora: str, produto: str, pais: str, geom:str, 
                 data_insercao:Union[DateTime, None] = None):
        """
        Cria um Pipeline

        Arguments:
            pais: país por onde passa a tuberia
            operadora: operadora da tuberia
            nome_duto: nome da tuberia
            produto: produto transportado pela tuberia
            geom: tipo de ponto wkt do duto
            data_insercao: data de quando o produto foi inserido à base
        """
        self.pais = pais
        self.operadora = operadora
        self.nome_duto = nome_duto
        self.produto = produto
        self.geom = geom

        # se não for informada, será o data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao

    def to_dict(self):
        """
        Retorna a representação em dicionário do Objeto Pipeline.
        """
        return{
            "id": self.id,
            "pais": self.pais,
            "operadora": self.operadora,
            "nome_duto": self.nome_duto,
            "produto": self.produto,
            "geom": self.geom,
            "data_insercao": self.data_insercao
        }

    def __repr__(self):
        """
        Retorna uma representação do Pipeline em forma de texto.
        """
        return f"Pipeline(id={self.id}, operadora={self.operadora}, nome_duto={self.nome_duto}, produto={self.produto}, pais={self.pais}, geom={self.geom})"
