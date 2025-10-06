# 🚇 Configuração de Dados GTFS (Transporte Público)

Este guia explica como integrar dados de transporte público (GTFS) no SiteScore AI para melhorar a precisão da análise de acessibilidade.

## O que é GTFS?

GTFS (General Transit Feed Specification) é um formato padrão para dados de transporte público, incluindo:
- Paradas de ônibus, metrô, trem
- Rotas e itinerários
- Horários de operação
- Frequência de viagens

## 📥 Onde Baixar Dados GTFS

### Brasil

#### São Paulo (SPTrans)
- **Fonte**: SPTrans (Prefeitura de SP)
- **URL**: https://www.sptrans.com.br/desenvolvedores/
- **Formato**: ZIP com feeds GTFS

#### Rio de Janeiro
- **Fonte**: Data.Rio
- **URL**: https://www.data.rio/datasets/
- **Buscar**: "GTFS transporte"

#### Outras cidades brasileiras
- **Repositório**: https://transitfeeds.com/l/165-brazil
- Contém feeds de várias cidades brasileiras

### Internacional

- **TransitFeeds**: https://transitfeeds.com/
- **Mobility Database**: https://mobilitydatabase.org/
- Cobertura global com milhares de cidades

## 🔧 Como Importar GTFS

### Passo 1: Baixar o arquivo GTFS

```bash
# Exemplo: Baixar GTFS de São Paulo
wget https://exemplo.com/sao-paulo-gtfs.zip -O gtfs-sp.zip
```

### Passo 2: Validar o GTFS

```bash
# Via Docker
docker compose exec backend python app/scripts/ingest_gtfs.py \
  --gtfs gtfs-sp.zip \
  --validate-only

# Localmente
python backend-python/app/scripts/ingest_gtfs.py \
  --gtfs gtfs-sp.zip \
  --validate-only
```

### Passo 3: Importar para o banco de dados

```bash
# Via Makefile (recomendado)
make gtfs GTFS=/path/to/gtfs-sp.zip

# Ou via Docker diretamente
docker compose exec backend python app/scripts/ingest_gtfs.py \
  --gtfs gtfs-sp.zip \
  --db $DATABASE_URL
```

### Passo 4: Configurar no backend

Edite o arquivo `.env`:

```bash
# Habilitar uso de GTFS
USE_GTFS=true

# Caminho para arquivo GTFS (opcional, se não importou para DB)
GTFS_ZIP_PATH=/app/data/gtfs-sp.zip
```

### Passo 5: Reiniciar backend

```bash
docker compose restart backend
```

## 📊 O que o GTFS adiciona?

Com dados GTFS importados, o SiteScore AI irá:

1. **Maior precisão nas features de transporte**
   - Contagem de paradas com frequência real de viagens
   - Peso baseado na quantidade de linhas que passam

2. **Métricas adicionais**
   - `trips_per_hour`: Viagens por hora em cada parada
   - `transit_density`: Densidade de transporte na área

3. **Melhor cálculo de flow_kde**
   - Paradas com mais viagens contribuem mais para o heatmap de fluxo

## 🗂️ Estrutura de Dados Importados

### Tabela `gtfs_stops`

```sql
CREATE TABLE gtfs_stops (
    id SERIAL PRIMARY KEY,
    stop_id VARCHAR(255) UNIQUE,
    stop_name VARCHAR(255),
    stop_lat DOUBLE PRECISION,
    stop_lon DOUBLE PRECISION,
    trips_per_day INTEGER,
    trips_per_hour DOUBLE PRECISION,
    geom GEOMETRY(POINT, 4326),
    created_at TIMESTAMP
);
```

### Consulta de exemplo

```sql
-- Ver paradas mais movimentadas
SELECT stop_name, trips_per_hour
FROM gtfs_stops
ORDER BY trips_per_hour DESC
LIMIT 10;

-- Contar paradas em um raio
SELECT COUNT(*) 
FROM gtfs_stops
WHERE ST_DWithin(
    geom,
    ST_SetSRID(ST_MakePoint(-46.6333, -23.5505), 4326)::geography,
    500
);
```

## 🔄 Atualização de Dados

GTFS deve ser atualizado periodicamente (mensal/trimestral):

```bash
# Baixar novo GTFS
wget https://exemplo.com/novo-gtfs.zip -O gtfs-novo.zip

# Re-importar (atualiza automático via UPSERT)
make gtfs GTFS=gtfs-novo.zip
```

## 🧪 Teste de Integração

Após importar, teste a integração:

```python
from app.core.gtfs import GTFS, load_gtfs

# Carregar GTFS
load_gtfs("/path/to/gtfs.zip")

# Verificar
print(f"Paradas carregadas: {len(GTFS['stops'])}")
print(f"Média viagens/hora: {GTFS['stops']['trips_per_hour'].mean():.1f}")
```

## 📝 Formato de Arquivo GTFS

Um arquivo GTFS válido deve conter:

```
gtfs.zip
├── agency.txt          # Agências de transporte
├── stops.txt           # Paradas (OBRIGATÓRIO)
├── routes.txt          # Rotas/linhas
├── trips.txt           # Viagens (OBRIGATÓRIO)
├── stop_times.txt      # Horários (OBRIGATÓRIO)
├── calendar.txt        # Calendário de operação
├── calendar_dates.txt  # Exceções de calendário
└── shapes.txt          # Geometrias de rotas (opcional)
```

### Exemplo: stops.txt

```csv
stop_id,stop_name,stop_lat,stop_lon,stop_desc
1001,Praça da Sé,-23.5505,-46.6333,Estação de Metrô
1002,Av. Paulista 1000,-23.5613,-46.6563,Ponto de Ônibus
```

### Exemplo: stop_times.txt

```csv
trip_id,arrival_time,departure_time,stop_id,stop_sequence
trip_1,08:00:00,08:00:00,1001,1
trip_1,08:10:00,08:10:00,1002,2
```

## ⚠️ Problemas Comuns

### 1. Erro: "GTFS inválido"
- **Solução**: Verifique se o ZIP contém `stops.txt`, `trips.txt`, `stop_times.txt`

### 2. Erro: "Database connection failed"
- **Solução**: Verifique `DATABASE_URL` no `.env`

### 3. Importação lenta
- **Solução**: Arquivo GTFS muito grande. Use `--cache` para criar cache local:
  ```bash
  python scripts/ingest_gtfs.py --gtfs huge.zip --cache gtfs_cache.pkl
  ```

### 4. Dados não aparecem na análise
- **Solução**: Reinicie o backend após importação:
  ```bash
  docker compose restart backend
  ```

## 📚 Recursos Adicionais

- **Especificação GTFS**: https://gtfs.org/
- **Validador GTFS**: https://gtfs-validator.mobilitydata.org/
- **Tutorial GTFS**: https://developers.google.com/transit/gtfs/

## 💡 Dica: GTFS em Produção

Para produção, considere:
1. **Atualização automática**: Script cron para baixar GTFS periodicamente
2. **CDN**: Hospedar GTFS em CDN para acesso rápido
3. **Cache Redis**: Cachear consultas frequentes de paradas
4. **Índices**: Criar índices espaciais otimizados

```sql
-- Índice otimizado para consultas de raio
CREATE INDEX idx_gtfs_stops_geom_gist ON gtfs_stops USING GIST(geom);

-- Índice para consultas por frequência
CREATE INDEX idx_gtfs_stops_trips ON gtfs_stops(trips_per_hour DESC);
```

---

Feito com ❤️ para melhorar a análise de localização comercial

