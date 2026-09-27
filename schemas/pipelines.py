from sqlalchemy.dialects.postgresql import Any
from pydantic import BaseModel
from typing import Optional, List
from models.pipelines import Pipelines
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement



class PipelineSchema(BaseModel):
    """ Define como uma nova tuberia a ser inserida deve ser representada
    """
    id: int = 1
    pais: str = "Colombia"
    operadora: str = "Transportadora de Gás da Colómbia"
    nome_duto: str = "Gasoduto da Colómbia"
    produto: str = "Gás"
    latitude_inicio: float = 2.594
    longitude_inicio: float = -75.540
    latitude_fim: float = 5.0542
    longitude_fim: float = -77.013

class PipelineViewSchema(BaseModel):
    """ Define como um pipeline será retornado.
    """
    id: int = 1
    pais: str = "Colombia"
    operadora: str = "Transportadora de Gás da Colómbia"
    nome_duto: str = "Gasoduto da Colómbia"
    produto: str = "Gás"
    latitude_inicio: float = 2.594
    longitude_inicio: float = -75.540
    latitude_fim: float = 5.0542
    longitude_fim: float = -77.013 

class PipelineBuscaPoridSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base na operadora da tuberia.
    """
    id: int = 1 


class ListagemPipelinesSchema(BaseModel):
    """ Define como uma listagem de tubrerias será retornada.
    """
    pipelines:List[PipelineViewSchema]


class PipelineDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    message: str
    id: int

def apresenta_pipelines(pipelines: List[Pipelines]):
    """ Retorna uma representação do produto seguindo o schema definido em
        ListagemPipelinesSchema.
    """
    result = []
    for pipeline in pipelines:
        shape = to_shape(pipeline.geom) if pipeline.geom else None
    
        coords = list(shape.coords) if shape else []
        lon_ini, lat_ini = coords[0] if len(coords) > 0 else (None, None)
        lon_fim, lat_fim = coords[-1] if len(coords) > 1 else (None, None)

        result.append({
            "id": pipeline.id,
            "operadora": pipeline.operadora,
            "nome_duto": pipeline.nome_duto,
            "produto": pipeline.produto,
            "pais": pipeline.pais,
            "latitude_inicio": lat_ini,
            "longitude_inicio": lon_ini,
            "latitude_fim": lat_fim,
            "longitude_fim": lon_fim
        })

    return {"pipelines": result}





def apresenta_pipeline(pipeline: Pipelines):
    """ Retorna uma representação do pipeline seguindo o schema definido em
        PipelineViewSchema.
    """
    shape = to_shape(pipeline.geom) if pipeline.geom else None    
    
    coords = list(shape.coords) if shape else []
    lon_ini, lat_ini = coords[0] if len(coords) > 0 else (None, None)
    lon_fim, lat_fim = coords[-1] if len(coords) > 1 else (None, None)

    return {
        "id": pipeline.id,
        "operadora": pipeline.operadora,
        "nome_duto": pipeline.nome_duto,
        "produto": pipeline.produto,
        "pais": pipeline.pais,
        "latitude_inicio": lat_ini,
        "longitude_inicio": lon_ini,
        "latitude_fim": lat_fim,
        "longitude_fim": lon_fim
    }

