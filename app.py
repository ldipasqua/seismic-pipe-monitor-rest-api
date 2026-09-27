from schemas.earthquakes import BuscaEarthquakeQuerySchema
from models import pipelines
import requests
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, request
from urllib.parse import unquote
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError

from models import Session, Earthquakes, Pipelines
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
earthquakes_tag = Tag(name="Earthquakes", description="Procura terremotos na API do USGS em um raio de 1000 km a partir da coordenada de início do pipeline")
pipelines_tag = Tag(name="Pipelines", description="Adição, visualização e remoção de tubérias à base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.get('/earthquake/usgs', tags=[earthquakes_tag],
         responses={"200": ListagemEarthquakeSchema, "404": ErrorSchema})
def get_earthquakes_usgs(query: BuscaEarthquakeQuerySchema):
    """
    Procura sismos recentes na API do USGS em um raio de 1000 km a partir da coordenada de início da pipeline, 
    e retorna a listagem sem salvar no banco de dados.
    """
    logger.info(f"Buscando sismos na API do USGS (Lat: {query.latitude}, Lon: {query.longitude}")  

    latitude = query.latitude
    longitude = query.longitude
    radius_fixo = 1000   

    usgs_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    # Parâmetros de busca na API da USGS: magnitude mínima de 2, nos últimos 15 dias e raio de 1000 km.
    params = {
        "format": "geojson",
        "minmagnitude": "2.0",
        "starttime": (datetime.utcnow() - timedelta(days=15)).strftime('%Y-%m-%d'),
        "latitude": latitude,
        "longitude": longitude,
        "maxradiuskm": radius_fixo
    }

    usgs_data = {"features": []}

    try:
        response = requests.get(usgs_url, params=params, timeout=10)
        response.raise_for_status()
        usgs_data = response.json()
        logger.info(f"Total recebido da API do USGS: {len(usgs_data.get('features', []))}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede/HTTP ao conectar com a API do USGS: {e}")
        return {"mesage": "Erro ao conectar com a API do USGS"}, 500
    except Exception as e:
        logger.error(f"Erro inesperado no processamento do USGS: {e}")
        return {"mesage": "Erro interno no servidor"}, 500

    # 2. Processar e formatar os dados diretamente para a resposta
    sismos_list = []
    
    for feature in usgs_data.get("features", []):
        sismo_id = feature.get("id")
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [0, 0, 0])
        
        place_text = properties.get("place", "") or ""
        pais_extraido = place_text.split(",")[-1].strip() if "," in place_text else "Desconhecido"
        wkt_geom = f"POINT({coordinates[0]} {coordinates[1]})"
        
        timestamp_ms = properties.get("time")
        data_sismo = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc) if timestamp_ms else None

        
        sismo_dict = {
            "sismo_id": sismo_id,
            "magnitude": properties.get("mag", 0.0),
            "profundidade": str(coordinates[2]) if len(coordinates) > 2 else "-",
            "pais": pais_extraido,
            "place": place_text,
            "geom": wkt_geom,
            "data_sismo": data_sismo.isoformat() if data_sismo else None,
            "data_insercao": datetime.now().isoformat()
        }
        
        sismos_list.append(sismo_dict)

    logger.info(f"Busca concluída. Sismos encontrados no raio do duto: {len(sismos_list)}")
    
    resultado = {"earthquakes": sismos_list}
    
    return resultado, 200


@app.post('/pipeline', tags=[pipelines_tag],
          responses={"200": PipelineViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_pipeline(form: PipelineSchema):
    """Adiciona um novo pipeline à base de dados
    
    Retorna uma representação do pipeline criado.
    """
    logger.info(f"Adicionando pipeline '{form.nome_duto}' à base de dados")

    wkt_line = f"LINESTRING({form.longitude_inicio} {form.latitude_inicio}, {form.longitude_fim} {form.latitude_fim})"
    geom_duto = WKTElement(wkt_line, srid=4326)
    
    session = Session()

    try:
        # Opcional: verificar se já existe um pipeline com o mesmo nome para evitar duplicidade
        pipeline_existente = session.query(Pipelines).filter(Pipelines.nome_duto == form.nome_duto).first()
        if pipeline_existente:
            error_msg = f"Pipeline '{form.nome_duto}' já cadastrado na base!"
            logger.warning(f"Tentativa de duplicidade: {error_msg}")
            return {"message": error_msg}, 409

        # Instanciando o novo pipeline a partir do formulário/schema
        pipeline = Pipelines(
            pais=form.pais,
            operadora=form.operadora,
            nome_duto=form.nome_duto,
            produto=form.produto,
            geom=geom_duto
        )

        session.add(pipeline)
        session.commit()

        logger.info(f"Adicionado pipeline com sucesso: #{pipeline.id} - {pipeline.nome_duto}")
        return apresenta_pipeline(pipeline), 200

    except IntegrityError as e:
        session.rollback()
        error_msg = "Erro de integridade ao salvar o pipeline no banco de dados."
        logger.error(f"{error_msg}: {str(e)}")
        return {"message": error_msg}, 409

    except Exception as e:
        session.rollback()
        error_msg = "Não foi possível salvar o novo pipeline."
        logger.error(f"{error_msg}: {str(e)}")
        return {"message": error_msg}, 400

    finally:
        session.close()
    

@app.delete('/pipeline', tags=[pipelines_tag],
            responses={"200": PipelineDelSchema, "404": ErrorSchema})
def del_pipeline(query: PipelineBuscaPoridSchema):
    """Deleta um Pipeline a partir do nome informado

    Retorna uma mensagem de confirmação da remoção.
    """
    pipeline_id = int(query.id)
    logger.info(f"Deletando dados sobre o duto #{pipeline_id}")
    # criando conexão com a base
    session = Session()
    try:
        # 1. Procuramos o primeiro duto
        pipeline = session.query(Pipelines).filter(Pipelines.id == pipeline_id).first()

        if pipeline:
            # 2. Deletamos o duto
            session.delete(pipeline)
            session.commit()
            
            logger.info(f"Deletado o duto {pipeline_id} com sucesso!")
            return {"message": "O duto foi removido", "pipeline_id": pipeline_id}, 200
            
        else:
            error_msg = "O duto não foi encontrado na base"
            logger.warning(f"Erro ao deletar o duto {pipeline_id}: {error_msg}")
            return {"message": error_msg}, 404
            
    except Exception as e:
        session.rollback()
        logger.error(f"Erro interno ao deletar duto: {e}")
        return {"message": "Erro interno no servidor ao tentar deletar"}, 500
    finally:
        session.close()

@app.put('/pipeline', tags=[pipelines_tag],
         responses={"200": PipelineViewSchema, "404": ErrorSchema, "400": ErrorSchema})
def update_pipeline(form: PipelineSchema):
    """Atualiza um pipeline existente na base de dados
    
    Retorna uma representação do pipeline atualizado.
    """
    logger.info(f"Atualizando pipeline {form.id}")
    
    session = Session()
    logger.info("sesion iniciada")
    try:
        # Procura pelo pipeline na base de dados baseado no id
        pipeline = session.query(Pipelines).filter(Pipelines.id == form.id).first()
        logger.info("pipeline encontrado")
        
        if not pipeline:
            error_msg = f"Pipeline #'{form.id}' não encontrado na base!"
            logger.warning(f"Tentativa de atualização de pipeline inexistente: {error_msg}")
            return {"message": error_msg}, 404

        
        # Atualiza os campos do pipeline com base nos dados do formulário
        pipeline.pais = form.pais
        pipeline.operadora = form.operadora
        pipeline.nome_duto = form.nome_duto
        pipeline.produto = form.produto
      
        if (form.latitude_inicio and form.longitude_inicio and 
            form.latitude_fim and form.longitude_fim):
            wkt_geom = f"LINESTRING({form.longitude_inicio} {form.latitude_inicio}, \
                                    {form.longitude_fim} {form.latitude_fim})"    
            pipeline.geom = wkt_geom
            logger.info("geom atualizado")
        # Commita as alterações no banco de dados
        session.commit()
        logger.info("commit realizado")

        logger.info(f"Pipeline {pipeline.id} atualizado com sucesso!")
        return apresenta_pipeline(pipeline), 200

    except IntegrityError as e:
        session.rollback()
        error_msg = "Erro de integridade ao atualizar o pipeline."
        logger.error(f"{error_msg}: {str(e)}")
        return {"message": error_msg}, 409

    except Exception as e:
        session.rollback()
        error_msg = "Não foi possível atualizar o pipeline."
        logger.error(f"{error_msg}: {str(e)}")
        return {"message": error_msg}, 400

    finally:
        session.close()

@app.get('/pipelines', tags=[pipelines_tag],
         responses={"200": ListagemPipelinesSchema, "404": ErrorSchema})
def get_pipelines():
    """Retorna todos os pipelines da base de dados.
    
    Retorna uma lista de representações de pipelines.
    """
      
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    pipelines = session.query(Pipelines).all()

    if not pipelines:
        # se não há produtos cadastrados
        return {"pipelines": []}, 200
    else:
        
        # retorna a representação de produto
        print(pipelines)
        return apresenta_pipelines(pipelines), 200
