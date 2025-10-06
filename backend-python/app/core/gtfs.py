import os, zipfile
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import logging

logger = logging.getLogger(__name__)

# Estado global do GTFS
GTFS = {"stops": None, "loaded": False, "error": None}

def load_gtfs(zip_path: str) -> bool:
    """
    Carrega dados GTFS de um arquivo ZIP.
    
    Args:
        zip_path: Caminho para o arquivo GTFS.zip
        
    Returns:
        True se carregou com sucesso, False caso contrário
    """
    if not zip_path:
        logger.info("GTFS: Nenhum caminho fornecido. Usando Overpass API como fallback.")
        GTFS["error"] = "No GTFS path provided"
        return False
    
    if not os.path.exists(zip_path):
        logger.warning(f"GTFS: Arquivo não encontrado: {zip_path}. Usando Overpass API como fallback.")
        GTFS["error"] = f"File not found: {zip_path}"
        return False
    
    try:
        logger.info(f"GTFS: Carregando dados de {zip_path}...")
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Verificar se os arquivos necessários existem
            required_files = ['stops.txt', 'stop_times.txt']
            available_files = z.namelist()
            
            for req_file in required_files:
                if req_file not in available_files:
                    logger.error(f"GTFS: Arquivo {req_file} não encontrado no ZIP")
                    GTFS["error"] = f"Missing {req_file}"
                    return False
            
            # Carregar stops
            stops = pd.read_csv(z.open('stops.txt'))
            logger.info(f"GTFS: Carregados {len(stops)} stops")
            
            # Carregar stop_times
            stop_times = pd.read_csv(z.open('stop_times.txt'))
            logger.info(f"GTFS: Carregados {len(stop_times)} stop_times")
            
            # Calcular trips por stop
            trips_per_stop = stop_times.groupby('stop_id')['trip_id'].nunique().reset_index()
            trips_per_stop.columns = ['stop_id', 'trips_per_day']
            
            # Criar GeoDataFrame
            gdf = gpd.GeoDataFrame(
                stops, 
                geometry=gpd.points_from_xy(stops['stop_lon'], stops['stop_lat']), 
                crs='EPSG:4326'
            )
            
            # Merge com contagem de trips
            GTFS['stops'] = gdf.merge(trips_per_stop, on='stop_id', how='left').fillna({'trips_per_day': 0})
            GTFS['stops']['trips_per_hour'] = GTFS['stops']['trips_per_day'] / 16.0
            GTFS['loaded'] = True
            GTFS['error'] = None
            
            logger.info(f"✅ GTFS carregado com sucesso! {len(GTFS['stops'])} paradas disponíveis.")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao carregar GTFS: {e}")
        GTFS["error"] = str(e)
        GTFS["loaded"] = False
        return False

def is_gtfs_available() -> bool:
    """Verifica se dados GTFS estão disponíveis."""
    return GTFS.get("loaded", False) and GTFS.get("stops") is not None

def get_gtfs_status() -> dict:
    """Retorna status do GTFS para debugging."""
    return {
        "available": is_gtfs_available(),
        "stops_count": len(GTFS["stops"]) if is_gtfs_available() else 0,
        "error": GTFS.get("error")
    }
