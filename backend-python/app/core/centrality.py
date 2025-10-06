import os
import hashlib
import json
import logging
from typing import Tuple
import redis
from .config import settings

logger = logging.getLogger(__name__)

# Configuração
ENABLE = os.getenv("ENABLE_OSMNX_CENTRALITY", "false").lower() == "true"
CACHE_TTL = 604800  # 7 dias
TIMEOUT = 10  # segundos máximo para cálculo

# Redis cache
try:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis não disponível para centrality cache: {e}")
    r = None

def _make_cache_key(bbox: Tuple[float,float,float,float], center_lon: float, center_lat: float) -> str:
    """Gera chave de cache baseada em bbox e centro (arredondado)."""
    # Arredondar para 4 casas decimais (~11m de precisão)
    key_data = {
        "bbox": [round(x, 4) for x in bbox],
        "center": [round(center_lon, 4), round(center_lat, 4)]
    }
    key_str = json.dumps(key_data, sort_keys=True)
    hash_val = hashlib.sha1(key_str.encode('utf-8')).hexdigest()[:16]
    return f"centrality:{hash_val}"

def street_centrality_value(bbox: Tuple[float,float,float,float], center_lon: float, center_lat: float) -> float:
    """
    Calcula street centrality usando OSMnx betweenness centrality.
    
    - Retorna 0.0 se desabilitado via env var
    - Usa cache Redis (TTL 7 dias)
    - Timeout de 10 segundos
    - Fallback gracioso para 0.0 em caso de erro
    
    Args:
        bbox: (south, west, north, east)
        center_lon: longitude do ponto central
        center_lat: latitude do ponto central
        
    Returns:
        Valor de betweenness centrality (0.0-1.0) ou 0.0 se erro/desabilitado
    """
    if not ENABLE:
        return 0.0
    
    # Verificar cache
    cache_key = _make_cache_key(bbox, center_lon, center_lat)
    if r:
        try:
            cached = r.get(cache_key)
            if cached is not None:
                logger.debug(f"✅ Centrality cache HIT: {cache_key}")
                return float(cached)
        except Exception as e:
            logger.warning(f"Erro ao ler cache centrality: {e}")
    
    try:
        logger.info(f"🔄 Calculando street centrality (pode demorar)...")
        
        # Importar osmnx apenas quando necessário
        import osmnx as ox
        import signal
        
        # Função com timeout usando signal (Unix only)
        def handler(signum, frame):
            raise TimeoutError("Street centrality cálculo timeout")
        
        # Tentar calcular com timeout (apenas em sistemas Unix)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(TIMEOUT)
        
        try:
            north, south, east, west = bbox[2], bbox[0], bbox[3], bbox[1]
            G = ox.graph_from_bbox(north, south, east, west, network_type='walk', simplify=True)
            bc = ox.betweenness_centrality(G, weight='length', normalized=True, endpoints=False)
            center_node = ox.nearest_nodes(G, center_lon, center_lat)
            value = float(bc.get(center_node, 0.0))
            
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancelar alarm
            
            # Salvar em cache
            if r:
                try:
                    r.setex(cache_key, CACHE_TTL, str(value))
                    logger.info(f"✅ Centrality calculado e cacheado: {value:.3f}")
                except Exception as e:
                    logger.warning(f"Erro ao salvar cache centrality: {e}")
            
            return value
            
        except TimeoutError:
            logger.warning(f"⏱️ Street centrality timeout após {TIMEOUT}s - retornando 0.0")
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            return 0.0
            
    except Exception as e:
        logger.warning(f"❌ Erro ao calcular street centrality: {e} - retornando 0.0")
        return 0.0
