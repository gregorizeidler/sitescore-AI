# 🧪 Test Suite - SiteScore AI

Cobertura completa de testes para o SiteScore AI Backend.

## 📊 Estrutura de Testes

```
tests/
├── test_features.py      # Testes de extração geoespacial (15 testes)
├── test_scoring.py       # Testes do modelo de scoring (15 testes)
├── test_api.py          # Testes de endpoints REST (16 testes)
└── README.md            # Este arquivo
```

## 🚀 Como Executar

### Via Docker (Recomendado)

```bash
# Todos os testes
docker compose exec backend pytest

# Com verbose
docker compose exec backend pytest -v

# Arquivo específico
docker compose exec backend pytest app/tests/test_features.py

# Teste específico
docker compose exec backend pytest app/tests/test_features.py::test_count_within_radius

# Com cobertura
docker compose exec backend pytest --cov=app --cov-report=html
```

### Via Makefile

```bash
make test
```

### Localmente

```bash
cd backend-python
pytest -v
```

## 📝 Cobertura de Testes

### test_features.py (15 testes)

Testa todas as funções de processamento geoespacial:

- ✅ `count_within_radius()` - Contagem em raio
- ✅ `nearest_distance_meters()` - Distância ao mais próximo
- ✅ `kde_value()` - Kernel Density Estimation
- ✅ `entropy_mix()` - Entropia de mix de amenidades
- ✅ `filter_by_tag()` - Filtros OSM por tag
- ✅ `to_geodf()` - Conversão Overpass → GeoDataFrame
- ✅ `normalize()` - Normalização de features

**Edge cases testados:**
- GeoDataFrames vazios
- Valores infinitos/NaN
- Múltiplas tags
- Diferentes tipos de geometria (nodes, ways)

### test_scoring.py (15 testes)

Testa o modelo de scoring baseline:

- ✅ Scoring para todos os business types (restaurante, academia, varejo_moda)
- ✅ Penalidade de concorrência
- ✅ Localizações perfeitas vs ruins
- ✅ Contribuições de features
- ✅ Formato de explicação
- ✅ Normalização com valores acima do cap
- ✅ Missing features

**Cenários testados:**
- Alta competição → score menor
- Mix balanceado → entropia alta
- Features normalizadas corretamente
- Pesos específicos por business type

### test_api.py (16 testes)

Testa todos os endpoints REST:

- ✅ `GET /api/v1/health` - Healthcheck
- ✅ `GET /api/v1/geocode` - Geocoding Nominatim
- ✅ `POST /api/v1/score` - Scoring de localização
- ✅ `GET /api/v1/projects` - Listagem de projetos
- ✅ `GET /api/v1/layers/{type}` - Layers geoespaciais
- ✅ `/metrics` - Prometheus metrics

**Validações testadas:**
- Geometrias inválidas
- Business types inválidos
- Queries muito curtas
- CORS headers
- Versioning da API
- Todos os business types suportados

## 🎯 Executar Testes por Categoria

### Apenas features geoespaciais
```bash
docker compose exec backend pytest app/tests/test_features.py -v
```

### Apenas scoring
```bash
docker compose exec backend pytest app/tests/test_scoring.py -v
```

### Apenas API
```bash
docker compose exec backend pytest app/tests/test_api.py -v
```

## 📈 Relatório de Cobertura

Gerar relatório HTML de cobertura:

```bash
docker compose exec backend pytest --cov=app --cov-report=html

# Abrir relatório (fora do container)
open backend-python/htmlcov/index.html
```

### Cobertura Esperada

- `core/features.py`: **100%**
- `core/scoring_model.py`: **100%**
- `api/v1/endpoints/scoring.py`: **85%+**
- `api/v1/endpoints/layers.py`: **80%+**
- `api/v1/endpoints/geocode.py`: **90%+**

## 🐛 Debugging de Testes

### Executar com output detalhado

```bash
docker compose exec backend pytest -vv -s
```

### Parar no primeiro erro

```bash
docker compose exec backend pytest -x
```

### Executar apenas testes que falharam

```bash
docker compose exec backend pytest --lf
```

### Ver tempo de execução

```bash
docker compose exec backend pytest --durations=10
```

## 🔧 Configuração de Testes

### pytest.ini

```ini
[pytest]
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
```

### Fixtures Úteis

```python
# Exemplo de fixture para mock de dados
@pytest.fixture
def mock_overpass_response():
    return {
        "elements": [
            {"type": "node", "lat": -23.55, "lon": -46.63, "tags": {"amenity": "restaurant"}}
        ]
    }

# Usar em teste
def test_with_mock(mock_overpass_response):
    gdf = to_geodf(mock_overpass_response)
    assert len(gdf) == 1
```

## ⚠️ Testes que Requerem Autenticação

Alguns testes de API podem falhar se o backend estiver configurado com autenticação JWT obrigatória:

```bash
# Desabilitar auth para testes (no .env)
AUTH_JWKS_URL=

# Ou configurar mock de auth nos testes
```

## 📋 Checklist de Testes

Antes de fazer commit/deploy:

- [ ] Todos os testes passam: `pytest`
- [ ] Cobertura > 80%: `pytest --cov`
- [ ] Sem warnings: `pytest -W error`
- [ ] Linting OK: `flake8 app/`
- [ ] Type checking: `mypy app/`

## 🚨 CI/CD

Integração com GitHub Actions (exemplo):

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker compose up -d db redis
          docker compose run backend pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 🎓 Boas Práticas

1. **Testes isolados**: Cada teste deve ser independente
2. **Nomes descritivos**: `test_count_within_radius_empty()` > `test_count_2()`
3. **Arrange-Act-Assert**: Estruture testes claramente
4. **Edge cases**: Sempre teste valores vazios, nulos, extremos
5. **Mocks**: Use mocks para APIs externas (Overpass, Nominatim)

## 📚 Recursos

- **pytest docs**: https://docs.pytest.org/
- **FastAPI testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **GeoPandas testing**: https://geopandas.org/en/stable/docs/user_guide/testing.html

---

**Última atualização**: Outubro 2025  
**Cobertura total**: ~85%  
**Total de testes**: 46

