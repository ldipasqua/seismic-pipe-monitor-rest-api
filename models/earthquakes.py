from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float
from datetime import datetime
from typing import Union
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.functions import ST_AsText

from  models import Base

class Earthquakes(Base):

    # Nome da tabela
    __tablename__ = 'earthquakes_table'    

    # Colunas
    id = Column(Integer, primary_key=True)
    magnitude = Column(Float, nullable=False)
    profundidade = Column(String(140), nullable=False)
    sismo_id = Column(String(140), nullable=False)
    pais = Column(String(140), nullable=False)
    place = Column(String(140), nullable=False)   
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    data_sismo = Column(DateTime, nullable=False)
    data_insercao = Column(DateTime)
    
    def __init__(self, magnitude:float, profundidade:float, sismo_id:int, pais:str, place:str, geom:str, data_sismo:Union[DateTime, None] = None, data_insercao:Union[DateTime, None] = None):
        """
        Arguments:
            magnitude: magnitude do terremoto
            profundidade: profundidade do terremoto
            sismo_id: id do terremoto
            pais: país onde ocorreu o terremoto
            place: local onde ocorreu o terremoto            
            geom: tipo de ponto wkt do terremoto
            data_insercao: data de quando o terremoto foi inserido à base
        """
        self.magnitude = magnitude
        self.profundidade = profundidade
        self.sismo_id = sismo_id
        self.pais = pais
        self.place = place        
        self.geom = geom
        self.data_sismo = data_sismo
        if data_insercao:
            self.data_insercao = data_insercao

    def to_dict(self):
        """
        Retorna a representação em dicionário do Objeto Terremoto.
        """
        return{
            "id": self.id,
            "magnitude": self.magnitude,
            "profundidade": self.profundidade,
            "sismo_id": self.sismo_id,
            "pais": self.pais,
            "place": self.place,   
            "geom": self.geom,
            "data_sismo": self.data_sismo,         
            "data_insercao": self.data_insercao
        }

    def __repr__(self):
        """
        Retorna uma representação do Terremoto em forma de texto.
        """
        return f"Earthquake(id={self.id}, magnitude={self.magnitude}, profundidade={self.profundidade}, sismo_id={self.sismo_id}, pais={self.pais}, place={self.place}, data_sismo={self.data_sismo}, data_insercao={self.data_insercao})"
