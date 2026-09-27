from sqlalchemy.dialects.postgresql import Any
from pydantic import BaseModel
from typing import Optional, List
from models.earthquakes import Earthquakes
from geoalchemy2.shape import to_shape


class EarthquakeViewSchema(BaseModel):
    """ Define como um novo terremoto a ser inserido deve ser representado
    """
    id: int = 1
    magnitude: float = 5.0
    profundidade: str = "10.0"
    sismo_id: str = "s001ms0102"
    pais: str = "Brasil"
    place: str = "São Paulo"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_sismo: str = "2022-01-01T00:00:00.000Z"


class BuscaEarthquakeQuerySchema(BaseModel):
    latitude: float = 11.55
    longitude: float = -74.87

class ListagemEarthquakeSchema(BaseModel):
    """ Define como uma listagem de sismos será retornada.
    """
    earthquakes:List[EarthquakeViewSchema]