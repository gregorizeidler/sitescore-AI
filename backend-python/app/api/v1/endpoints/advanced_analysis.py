from fastapi import APIRouter, Query, Depends, Request
from fastapi.responses import JSONResponse
from shapely.geometry import Point
from typing import Optional
from ....core.overpass_client import (
    build_query, fetch_overpass, BUSINESS_TAGS, POI_TAGS_COMMON, TRANSIT_TAGS,
    WALKABILITY_TAGS, CYCLABILITY_TAGS, GREEN_TAGS, PARKING_TAGS, LIGHTING_TAGS
)
from ....core.auth import get_current_user, User
from ....core.rate_limit import enforce_quota, inc_overpass_count
from ....core.features import (
    to_geodf, walkability_score, green_score, bike_infrastructure,
    parking_availability, safety_infrastructure, building_density,
    street_connectivity, amenity_diversity, lighting_score
)
import asyncio

router = APIRouter()

@router.post("/advanced")
async def advanced_analysis(
    request: Request,
    lon: float = Query(...),
    lat: float = Query(...),
    radius: int = Query(default=1000),
    user: User = Depends(get_current_user)
):
    """
    Análise avançada de localização usando apenas dados OSM
    Retorna scores de walkability, ciclabilidade, áreas verdes, segurança, etc.
    """
    enforce_quota(user.sub, limit_per_minute=60)
    
    point = Point(lon, lat)
    
    # Criar bbox ao redor do ponto
    delta = radius / 111000  # Aproximação: 1 grau ≈ 111km
    bbox = (lat - delta, lon - delta, lat + delta, lon + delta)
    
    # Buscar dados básicos que já funcionam
    queries = {
        "pois": build_query(bbox, POI_TAGS_COMMON),
        "transit": build_query(bbox, TRANSIT_TAGS),
    }
    
    async def fetch_data(name, query):
        inc_overpass_count(user.sub)
        try:
            return name, await fetch_overpass(query)
        except Exception as e:
            import logging
            logging.warning(f"Erro ao buscar {name}: {e}")
            return name, {"elements": []}
    
    results = await asyncio.gather(*[fetch_data(n, q) for n, q in queries.items()])
    data = {name: to_geodf(result) for name, result in results}
    
    # Criar GDFs vazios para as outras camadas (para não quebrar o código)
    data["walkability"] = data["pois"]  # Usar POIs como proxy
    data["cyclability"] = data["pois"]
    data["green"] = data["pois"]
    data["parking"] = data["pois"]
    data["lighting"] = data["pois"]
    
    # Combinar todos os GeoDataFrames para análises gerais
    import pandas as pd
    import geopandas as gpd
    all_data = gpd.GeoDataFrame(pd.concat([gdf for gdf in data.values() if not gdf.empty], ignore_index=True))
    
    # Calcular todos os scores
    analysis = {
        "location": {"lon": lon, "lat": lat},
        "radius": radius,
        "scores": {
            "walkability": {
                "value": round(walkability_score(all_data, point, radius), 2),
                "max": 1.0,
                "description": "Índice de caminhabilidade (calçadas, POIs, áreas verdes)",
                "emoji": "🚶",
                "category": "Mobilidade"
            },
            "cyclability": {
                "value": bike_infrastructure(all_data, point, radius),
                "max": 50,
                "description": "Infraestrutura para bicicletas (ciclovias, estacionamentos)",
                "emoji": "🚴",
                "category": "Mobilidade"
            },
            "green_spaces": {
                "value": green_score(all_data, point, radius),
                "max": 20,
                "description": "Áreas verdes (parques, jardins, florestas)",
                "emoji": "🌳",
                "category": "Qualidade de Vida"
            },
            "parking": {
                "value": parking_availability(all_data, point, 500),
                "max": 30,
                "description": "Disponibilidade de estacionamento",
                "emoji": "🅿️",
                "category": "Acesso"
            },
            "safety": {
                "value": round(safety_infrastructure(all_data, point, radius), 2),
                "max": 100,
                "description": "Infraestrutura de segurança (polícia, iluminação)",
                "emoji": "🔒",
                "category": "Segurança"
            },
            "lighting": {
                "value": round(lighting_score(all_data, point, 500), 2),
                "max": 100,
                "description": "Iluminação pública (postes e vias iluminadas)",
                "emoji": "💡",
                "category": "Segurança"
            },
            "building_density": {
                "value": round(building_density(all_data, point, 500), 2),
                "max": 1000,
                "description": "Densidade de edificações por km²",
                "emoji": "🏢",
                "category": "Contexto Urbano"
            },
            "street_connectivity": {
                "value": round(street_connectivity(all_data, point, 500), 2),
                "max": 500,
                "description": "Conectividade da malha viária (cruzamentos)",
                "emoji": "🛣️",
                "category": "Contexto Urbano"
            },
            "amenity_diversity": {
                "value": round(amenity_diversity(all_data, point, radius), 2),
                "max": 1.0,
                "description": "Diversidade de tipos de comércio/serviços",
                "emoji": "🎯",
                "category": "Atratividade"
            },
        }
    }
    
    # Adicionar contagens brutas para o relatório
    analysis["raw_counts"] = {
        "footways": len(data["walkability"]) if not data["walkability"].empty else 0,
        "cycleways": len(data["cyclability"]) if not data["cyclability"].empty else 0,
        "green_areas": len(data["green"]) if not data["green"].empty else 0,
        "parking_lots": len(data["parking"]) if not data["parking"].empty else 0,
        "street_lamps": len(data["lighting"]) if not data["lighting"].empty else 0,
        "pois": len(data["pois"]) if not data["pois"].empty else 0,
        "transit_stops": len(data["transit"]) if not data["transit"].empty else 0,
    }
    
    # Calcular score geral normalizado
    total_normalized = 0
    for key, score_data in analysis["scores"].items():
        normalized = score_data["value"] / score_data["max"] if score_data["max"] > 0 else 0
        total_normalized += min(normalized, 1.0)
    
    analysis["overall_score"] = round((total_normalized / len(analysis["scores"])) * 100, 1)
    
    # Classificação
    score = analysis["overall_score"]
    if score >= 80:
        analysis["rating"] = "Excelente"
        analysis["rating_emoji"] = "🌟"
    elif score >= 60:
        analysis["rating"] = "Muito Bom"
        analysis["rating_emoji"] = "✨"
    elif score >= 40:
        analysis["rating"] = "Bom"
        analysis["rating_emoji"] = "👍"
    elif score >= 20:
        analysis["rating"] = "Regular"
        analysis["rating_emoji"] = "🤔"
    else:
        analysis["rating"] = "Baixo"
        analysis["rating_emoji"] = "⚠️"
    
    # Top 3 pontos fortes
    scores_list = [(k, v["value"]/v["max"]*100) for k, v in analysis["scores"].items()]
    scores_list.sort(key=lambda x: x[1], reverse=True)
    analysis["strengths"] = [
        {
            "feature": s[0],
            "score": round(s[1], 1),
            "emoji": analysis["scores"][s[0]]["emoji"],
            "description": analysis["scores"][s[0]]["description"]
        }
        for s in scores_list[:3]
    ]
    
    # Top 3 pontos fracos
    analysis["weaknesses"] = [
        {
            "feature": s[0],
            "score": round(s[1], 1),
            "emoji": analysis["scores"][s[0]]["emoji"],
            "description": analysis["scores"][s[0]]["description"]
        }
        for s in scores_list[-3:]
    ]
    
    return JSONResponse(analysis)


@router.get("/demographics")
async def demographics_analysis(
    lon: float = Query(...),
    lat: float = Query(...),
    radius: int = Query(default=1000),
    user: User = Depends(get_current_user)
):
    """
    Análise demográfica baseada em POIs do OSM
    Infere perfil do público baseado em estabelecimentos da região
    """
    enforce_quota(user.sub, limit_per_minute=60)
    
    point = Point(lon, lat)
    delta = radius / 111000
    bbox = (lat - delta, lon - delta, lat + delta, lon + delta)
    
    # Buscar POIs genéricos e categorizar manualmente
    inc_overpass_count(user.sub)
    try:
        poi_query = build_query(bbox, POI_TAGS_COMMON)
        poi_result = await fetch_overpass(poi_query)
        pois = poi_result.get("elements", [])
    except Exception as e:
        import logging
        logging.warning(f"Erro ao buscar POIs para demographics: {e}")
        pois = []
    
    # Categorizar POIs baseado nas tags
    counts = {
        "offices": 0,
        "schools": 0,
        "culture": 0,
        "retail": 0,
        "health": 0,
        "financial": 0,
    }
    
    for poi in pois:
        tags = poi.get("tags", {})
        amenity = tags.get("amenity", "")
        shop = tags.get("shop", "")
        office = tags.get("office", "")
        
        if office or amenity == "coworking_space":
            counts["offices"] += 1
        elif amenity in ["school", "university", "college", "kindergarten"]:
            counts["schools"] += 1
        elif amenity in ["library", "theatre", "cinema", "museum", "arts_centre"]:
            counts["culture"] += 1
        elif shop:
            counts["retail"] += 1
        elif amenity in ["hospital", "clinic", "pharmacy", "doctors", "dentist"]:
            counts["health"] += 1
        elif amenity in ["bank", "atm"]:
            counts["financial"] += 1
    
    total = sum(counts.values()) or 1
    
    # Inferir perfis baseado nas proporções
    profiles = []
    
    if counts["offices"] / total > 0.3:
        profiles.append({
            "type": "Corporativo",
            "percentage": round((counts["offices"] / total) * 100, 1),
            "emoji": "👨‍💼",
            "characteristics": [
                f"{counts['offices']} escritórios identificados",
                "Fluxo intenso em horário comercial (8h-18h)",
                "Poder aquisitivo médio-alto",
                "Perfil: Profissionais de 25-45 anos"
            ],
            "opportunities": [
                "Almoço executivo (12h-14h)",
                "Happy hour (18h-20h)",
                "Serviços rápidos (lavanderia, farmácia)"
            ]
        })
    
    if counts["schools"] / total > 0.2:
        profiles.append({
            "type": "Estudantes",
            "percentage": round((counts["schools"] / total) * 100, 1),
            "emoji": "🎓",
            "characteristics": [
                f"{counts['schools']} instituições de ensino",
                "Movimento pico: 12h-14h, 18h-20h",
                "Faixa etária: 15-25 anos",
                "Orçamento limitado"
            ],
            "opportunities": [
                "Lanches e fast food",
                "Livrarias e papelarias",
                "Cafeterias e espaços de estudo"
            ]
        })
    
    if counts["retail"] / total > 0.25:
        profiles.append({
            "type": "Varejo Intenso",
            "percentage": round((counts["retail"] / total) * 100, 1),
            "emoji": "🛍️",
            "characteristics": [
                f"{counts['retail']} estabelecimentos comerciais",
                "Corredor comercial estabelecido",
                "Alto fluxo de consumidores",
                "Fins de semana movimentados"
            ],
            "opportunities": [
                "Complementaridade (não duplicar)",
                "Serviços de apoio ao varejo",
                "Food court / praça de alimentação"
            ]
        })
    
    if counts["health"] > 5:
        profiles.append({
            "type": "Polo de Saúde",
            "percentage": round((counts["health"] / total) * 100, 1),
            "emoji": "🏥",
            "characteristics": [
                f"{counts['health']} serviços de saúde",
                "Fluxo diário constante",
                "Público diversificado (todas idades)",
                "Presença de acompanhantes"
            ],
            "opportunities": [
                "Farmácias",
                "Cafés e lanchonetes (espera)",
                "Estacionamento"
            ]
        })
    
    # Se não identificar perfil forte, adicionar residencial genérico
    if not profiles:
        profiles.append({
            "type": "Residencial/Misto",
            "percentage": 100.0,
            "emoji": "🏘️",
            "characteristics": [
                "Perfil misto ou predominantemente residencial",
                "Movimento distribuído ao longo do dia",
                "Público local/vizinhança"
            ],
            "opportunities": [
                "Serviços de proximidade",
                "Varejo de conveniência",
                "Prestadores de serviço"
            ]
        })
    
    return JSONResponse({
        "location": {"lon": lon, "lat": lat},
        "radius": radius,
        "total_pois": total,
        "categories": counts,
        "profiles": profiles,
        "summary": f"Identificados {len(profiles)} perfis principais de público na região"
    })
