#!/usr/bin/env python3
"""
Script para importar dados GTFS para o sistema SiteScore AI.
Carrega stops (paradas) e calcula frequência de viagens.

Uso:
    python scripts/ingest_gtfs.py --gtfs /path/to/gtfs.zip --db postgresql://user:pass@localhost/sitescore

Exemplo:
    python scripts/ingest_gtfs.py --gtfs sao-paulo-gtfs.zip --db $DATABASE_URL
"""
import argparse
import zipfile
import os
import sys
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sqlalchemy import create_engine, text
from pathlib import Path


def validate_gtfs(zip_path: str) -> bool:
    """Valida se o arquivo GTFS contém os arquivos necessários"""
    required_files = ['stops.txt', 'stop_times.txt', 'trips.txt']
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            files = z.namelist()
            missing = [f for f in required_files if f not in files]
            
            if missing:
                print(f"❌ Arquivos faltando no GTFS: {', '.join(missing)}")
                return False
            
            print(f"✅ GTFS válido: {len(files)} arquivos encontrados")
            return True
    except Exception as e:
        print(f"❌ Erro ao ler GTFS: {e}")
        return False


def load_gtfs_data(zip_path: str):
    """Carrega dados do GTFS e calcula métricas"""
    print("📦 Carregando dados do GTFS...")
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        # Carregar stops (paradas)
        stops_df = pd.read_csv(z.open('stops.txt'))
        print(f"  ✓ {len(stops_df)} paradas carregadas")
        
        # Carregar stop_times (horários)
        stop_times_df = pd.read_csv(z.open('stop_times.txt'))
        print(f"  ✓ {len(stop_times_df)} horários carregados")
        
        # Carregar trips (viagens)
        trips_df = pd.read_csv(z.open('trips.txt'))
        print(f"  ✓ {len(trips_df)} viagens carregadas")
    
    # Calcular frequência de viagens por parada
    print("📊 Calculando frequências...")
    trips_per_stop = stop_times_df.groupby('stop_id')['trip_id'].nunique().reset_index()
    trips_per_stop.columns = ['stop_id', 'trips_per_day']
    
    # Merge stops com frequências
    stops_with_freq = stops_df.merge(trips_per_stop, on='stop_id', how='left')
    stops_with_freq['trips_per_day'] = stops_with_freq['trips_per_day'].fillna(0)
    stops_with_freq['trips_per_hour'] = stops_with_freq['trips_per_day'] / 16.0  # Assumindo 16h de operação
    
    # Criar GeoDataFrame
    gdf = gpd.GeoDataFrame(
        stops_with_freq,
        geometry=gpd.points_from_xy(stops_with_freq['stop_lon'], stops_with_freq['stop_lat']),
        crs='EPSG:4326'
    )
    
    print(f"  ✓ {len(gdf)} paradas com frequência calculada")
    print(f"  ✓ Média: {gdf['trips_per_hour'].mean():.1f} viagens/hora")
    print(f"  ✓ Máximo: {gdf['trips_per_hour'].max():.1f} viagens/hora")
    
    return gdf


def save_to_database(gdf: gpd.GeoDataFrame, db_url: str):
    """Salva dados no PostgreSQL/PostGIS"""
    print("💾 Salvando no banco de dados...")
    
    engine = create_engine(db_url)
    
    # Criar tabela gtfs_stops se não existir
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS gtfs_stops (
                id SERIAL PRIMARY KEY,
                stop_id VARCHAR(255) UNIQUE NOT NULL,
                stop_name VARCHAR(255),
                stop_lat DOUBLE PRECISION,
                stop_lon DOUBLE PRECISION,
                trips_per_day INTEGER,
                trips_per_hour DOUBLE PRECISION,
                geom GEOMETRY(POINT, 4326),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        conn.commit()
        
        # Criar índice espacial
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_gtfs_stops_geom ON gtfs_stops USING GIST(geom);"))
        conn.commit()
        
        print("  ✓ Tabela gtfs_stops criada/verificada")
    
    # Preparar dados para inserção
    data_to_insert = gdf[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'trips_per_day', 'trips_per_hour']].copy()
    data_to_insert['geom'] = gdf.geometry.apply(lambda g: f"SRID=4326;{g.wkt}")
    
    # Inserir dados (usando UPSERT para evitar duplicatas)
    with engine.connect() as conn:
        for idx, row in data_to_insert.iterrows():
            conn.execute(text("""
                INSERT INTO gtfs_stops (stop_id, stop_name, stop_lat, stop_lon, trips_per_day, trips_per_hour, geom)
                VALUES (:stop_id, :stop_name, :stop_lat, :stop_lon, :trips_per_day, :trips_per_hour, ST_GeomFromEWKT(:geom))
                ON CONFLICT (stop_id) 
                DO UPDATE SET 
                    stop_name = EXCLUDED.stop_name,
                    trips_per_day = EXCLUDED.trips_per_day,
                    trips_per_hour = EXCLUDED.trips_per_hour,
                    geom = EXCLUDED.geom;
            """), {
                'stop_id': row['stop_id'],
                'stop_name': row['stop_name'],
                'stop_lat': row['stop_lat'],
                'stop_lon': row['stop_lon'],
                'trips_per_day': int(row['trips_per_day']),
                'trips_per_hour': float(row['trips_per_hour']),
                'geom': row['geom']
            })
        conn.commit()
    
    print(f"  ✓ {len(data_to_insert)} paradas salvas no banco")


def export_to_cache(gdf: gpd.GeoDataFrame, output_path: str = None):
    """Exporta GeoDataFrame para cache em memória (pickle)"""
    if not output_path:
        output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'gtfs_cache.pkl')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    gdf.to_pickle(output_path)
    print(f"💾 Cache exportado para: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Importa dados GTFS para o SiteScore AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Importar GTFS do sistema de transporte de São Paulo
  python scripts/ingest_gtfs.py --gtfs sao-paulo-gtfs.zip --db $DATABASE_URL
  
  # Importar e criar cache local
  python scripts/ingest_gtfs.py --gtfs sp-gtfs.zip --db $DATABASE_URL --cache gtfs_cache.pkl
  
  # Validar GTFS sem importar
  python scripts/ingest_gtfs.py --gtfs sp-gtfs.zip --validate-only
        """
    )
    
    parser.add_argument('--gtfs', required=True, help='Caminho para arquivo GTFS (.zip)')
    parser.add_argument('--db', help='Database URL (postgresql://...)')
    parser.add_argument('--cache', help='Caminho para salvar cache (opcional)')
    parser.add_argument('--validate-only', action='store_true', help='Apenas validar GTFS sem importar')
    
    args = parser.parse_args()
    
    # Validar arquivo GTFS
    if not os.path.exists(args.gtfs):
        print(f"❌ Arquivo não encontrado: {args.gtfs}")
        sys.exit(1)
    
    if not validate_gtfs(args.gtfs):
        sys.exit(1)
    
    if args.validate_only:
        print("✅ GTFS válido! (modo validação apenas)")
        sys.exit(0)
    
    # Carregar dados
    gdf = load_gtfs_data(args.gtfs)
    
    # Salvar no banco se URL fornecida
    if args.db:
        save_to_database(gdf, args.db)
    else:
        print("⚠️  Database URL não fornecida (--db), pulando salvamento no banco")
    
    # Exportar cache se solicitado
    if args.cache:
        export_to_cache(gdf, args.cache)
    
    print("\n✅ Importação GTFS concluída com sucesso!")
    print("\n📝 Próximos passos:")
    print("  1. Configure GTFS_ZIP_PATH no .env para usar os dados")
    print("  2. Reinicie o backend: docker compose restart backend")
    print("  3. Os dados de transporte agora estarão disponíveis nas análises")


if __name__ == '__main__':
    main()

