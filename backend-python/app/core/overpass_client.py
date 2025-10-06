from typing import Dict, List, Tuple
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import settings

BUSINESS_TAGS = {
    "restaurante": [
        ('amenity', 'restaurant'),
        ('amenity', 'fast_food'),
        ('amenity', 'cafe'),
    ],
    "academia": [
        ('leisure', 'fitness_centre'),
        ('sport', 'fitness'),
    ],
    "varejo_moda": [
        ('shop', 'clothes'),
        ('shop', 'shoes'),
        ('shop', 'boutique'),
        ('shop', 'fashion')
    ],
    "cafeteria": [
        ('amenity', 'cafe'),
        ('shop', 'coffee'),
    ],
    "padaria": [
        ('shop', 'bakery'),
    ],
    "lanchonete": [
        ('amenity', 'fast_food'),
    ],
    "mercado": [
        ('shop', 'supermarket'),
        ('shop', 'convenience'),
        ('shop', 'grocery'),
    ],
    "farmacia": [
        ('amenity', 'pharmacy'),
    ],
    "pet_shop": [
        ('shop', 'pet'),
    ],
    "lavanderia": [
        ('shop', 'laundry'),
        ('shop', 'dry_cleaning'),
    ],
    "salao_beleza": [
        ('shop', 'hairdresser'),
        ('shop', 'beauty'),
    ],
    "livraria": [
        ('shop', 'books'),
    ],
    "coworking": [
        ('office', 'coworking'),
        ('amenity', 'coworking_space'),
    ],
    "eletronicos": [
        ('shop', 'electronics'),
        ('shop', 'computer'),
        ('shop', 'mobile_phone'),
    ],
    "bar": [
        ('amenity', 'bar'),
        ('amenity', 'pub'),
    ],
    "cinema": [
        ('amenity', 'cinema'),
    ],
    "hotel": [
        ('tourism', 'hotel'),
        ('tourism', 'hostel'),
        ('tourism', 'guest_house'),
    ],
}

POI_TAGS_COMMON = [
    ('office', None),
    ('amenity', 'school'),
    ('amenity', 'university'),
    ('leisure', 'park'),
    ('shop', None)
]

# SAÚDE E BEM-ESTAR
POI_TAGS_HEALTH = [
    ('amenity', 'hospital'),
    ('amenity', 'clinic'),
    ('amenity', 'doctors'),
    ('amenity', 'dentist'),
    ('amenity', 'pharmacy'),
    ('amenity', 'veterinary'),
    ('healthcare', 'doctor'),
    ('healthcare', 'physiotherapist'),
    ('shop', 'optician'),
    ('shop', 'medical_supply'),
]

# CULTURA E LAZER
POI_TAGS_CULTURE = [
    ('tourism', 'museum'),
    ('tourism', 'gallery'),
    ('tourism', 'attraction'),
    ('tourism', 'viewpoint'),
    ('tourism', 'artwork'),
    ('tourism', 'theme_park'),
    ('tourism', 'zoo'),
    ('amenity', 'theatre'),
    ('amenity', 'cinema'),
    ('amenity', 'arts_centre'),
    ('amenity', 'community_centre'),
    ('amenity', 'nightclub'),
    ('leisure', 'playground'),
    ('leisure', 'sports_centre'),
    ('leisure', 'swimming_pool'),
    ('leisure', 'stadium'),
]

# FINANCEIRO
POI_TAGS_FINANCIAL = [
    ('amenity', 'bank'),
    ('amenity', 'atm'),
    ('amenity', 'bureau_de_change'),
    ('office', 'financial'),
    ('office', 'insurance'),
    ('office', 'accountant'),
]

# SEGURANÇA E SERVIÇOS PÚBLICOS
POI_TAGS_SECURITY = [
    ('amenity', 'police'),
    ('amenity', 'fire_station'),
    ('amenity', 'post_office'),
    ('emergency', 'fire_hydrant'),
]

# INFRAESTRUTURA E MOBILIDADE
POI_TAGS_INFRASTRUCTURE = [
    ('amenity', 'parking'),
    ('amenity', 'bicycle_parking'),
    ('amenity', 'charging_station'),
    ('amenity', 'fuel'),
    ('amenity', 'car_wash'),
    ('amenity', 'taxi'),
]

# VAREJO DETALHADO
POI_TAGS_RETAIL = [
    ('shop', 'supermarket'),
    ('shop', 'convenience'),
    ('shop', 'mall'),
    ('shop', 'department_store'),
    ('shop', 'bakery'),
    ('shop', 'butcher'),
    ('shop', 'greengrocer'),
    ('shop', 'electronics'),
    ('shop', 'furniture'),
    ('shop', 'hardware'),
    ('shop', 'sports'),
    ('shop', 'books'),
    ('shop', 'jewelry'),
    ('shop', 'florist'),
    ('shop', 'pet'),
    ('shop', 'toys'),
]

# EDUCAÇÃO COMPLETA
POI_TAGS_EDUCATION = [
    ('amenity', 'school'),
    ('amenity', 'kindergarten'),
    ('amenity', 'college'),
    ('amenity', 'university'),
    ('amenity', 'library'),
    ('amenity', 'language_school'),
    ('building', 'school'),
    ('building', 'university'),
]

TRANSIT_TAGS = [
    ('highway', 'bus_stop'),
    ('public_transport', 'platform'),
    ('railway', 'station'),
    ('railway', 'stop'),
    ('railway', 'subway_entrance'),
    ('railway', 'tram_stop'),
    ('amenity', 'bus_station'),
    ('amenity', 'taxi'),
]

# WALKABILITY - Infraestrutura para pedestres
WALKABILITY_TAGS = [
    ('highway', 'footway'),
    ('highway', 'pedestrian'),
    ('highway', 'steps'),
    ('highway', 'crossing'),
    ('highway', 'traffic_signals'),
    ('crossing', 'traffic_signals'),
    ('crossing', 'zebra'),
    ('crossing', 'uncontrolled'),
    ('footway', 'sidewalk'),
]

# CICLABILIDADE - Infraestrutura para bikes
CYCLABILITY_TAGS = [
    ('highway', 'cycleway'),
    ('cycleway', 'lane'),
    ('cycleway', 'track'),
    ('cycleway', 'shared_lane'),
    ('amenity', 'bicycle_parking'),
    ('amenity', 'bicycle_rental'),
    ('amenity', 'bicycle_repair_station'),
]

# ILUMINAÇÃO E SEGURANÇA
LIGHTING_TAGS = [
    ('highway', 'street_lamp'),
    ('lit', 'yes'),
    ('amenity', 'police'),
    ('emergency', 'fire_hydrant'),
    ('surveillance', 'public'),
    ('surveillance', 'outdoor'),
]

# ESTACIONAMENTO E ACESSO VEICULAR
PARKING_TAGS = [
    ('amenity', 'parking'),
    ('parking', 'surface'),
    ('parking', 'underground'),
    ('parking', 'multi-storey'),
    ('amenity', 'motorcycle_parking'),
    ('amenity', 'fuel'),
    ('amenity', 'charging_station'),
]

# ÁREAS VERDES E QUALIDADE AMBIENTAL
GREEN_TAGS = [
    ('leisure', 'park'),
    ('leisure', 'garden'),
    ('leisure', 'nature_reserve'),
    ('natural', 'wood'),
    ('natural', 'tree'),
    ('natural', 'tree_row'),
    ('landuse', 'forest'),
    ('landuse', 'grass'),
    ('landuse', 'meadow'),
]

# ACESSIBILIDADE
ACCESSIBILITY_TAGS = [
    # Buscar nós/ways com wheelchair tags
    ('wheelchair', 'yes'),
    ('wheelchair', 'limited'),
    ('wheelchair', 'no'),
]

POI_TAGS_OFFICES = [('office', None)]
POI_TAGS_SCHOOLS = [('amenity','school'), ('amenity','university'), ('amenity','kindergarten'), ('amenity','college')]
POI_TAGS_PARKS   = [('leisure','park'), ('leisure','playground'), ('leisure','garden')]

def build_clause(tag):
    k, v = tag
    if v is None:
        return f'["{k}"]'
    return f'["{k}"="{v}"]'

def build_query(bbox, tags):
    S,W,N,E = bbox
    clauses = "\n  ".join([f'node{build_clause(t)}({S},{W},{N},{E});\n  way{build_clause(t)}({S},{W},{N},{E});\n  relation{build_clause(t)}({S},{W},{N},{E});' for t in tags])
    q = f'''
[out:json][timeout:180];
(
  {clauses}
);
out tags center;
'''
    return q

class OverpassError(Exception): ...
class OverpassRateLimitError(Exception): ...

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=2, min=4, max=60), 
    retry=retry_if_exception_type(OverpassRateLimitError)
)
async def fetch_overpass(query: str) -> Dict:
    async with httpx.AsyncClient(timeout=180) as client:
        resp = await client.post(settings.OVERPASS_URL, data={'data': query})
        
        # Se for 429 (rate limit), tentar novamente com backoff exponencial
        if resp.status_code == 429:
            import logging
            logging.warning(f"Overpass rate limit atingido, aguardando retry...")
            raise OverpassRateLimitError(f"Rate limit excedido, tentando novamente...")
        
        # Para outros erros, não fazer retry
        if resp.status_code != 200:
            import logging
            logging.error(f"Erro Overpass: HTTP {resp.status_code}: {resp.text[:200]}")
            raise OverpassError(f"HTTP {resp.status_code}: {resp.text[:200]}")
        
        data = resp.json()
        if 'elements' not in data:
            raise OverpassError("Resposta Overpass inesperada")
        return data
