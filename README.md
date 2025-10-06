# SiteScore AI 🗺️

<div align="center">

**SaaS de Seleção de Local Comercial impulsionado por OSM + Machine Learning**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com)
[![Vue 3](https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

SiteScore AI traduz dados geoespaciais do **OpenStreetMap** (via Overpass API) em *insights acionáveis* para auxiliar na escolha estratégica de pontos comerciais. Utilizando análise geoespacial avançada e machine learning, o sistema avalia localizações baseado em concorrência, fluxo de pessoas, transporte público, e mix de amenidades.

---

## 📸 Screenshots

### Interface Principal

<div align="center">
<img src="docs/screenshots/Interface inicial.png" alt="Interface Inicial" width="800"/>
<p><em>Interface inicial do SiteScore AI com mapa interativo</em></p>
</div>

### Jornada de Análise

<div align="center">
<img src="docs/screenshots/Selecionar ponto abertura negocio.png" alt="Selecionando Ponto" width="800"/>
<p><em>Selecionando ponto para abertura do negócio no mapa</em></p>
</div>

<div align="center">
<img src="docs/screenshots/Selecionando tipo de negocio.png" alt="Tipo de Negócio" width="800"/>
<p><em>Escolhendo o tipo de negócio para análise</em></p>
</div>

<div align="center">
<img src="docs/screenshots/Escolhendo Raio análise.png" alt="Raio de Análise" width="800"/>
<p><em>Definindo o raio de análise da localização</em></p>
</div>

### Busca e Geocoding

<div align="center">
<img src="docs/screenshots/Selecionando endereço desejado.png" alt="Selecionando Endereço" width="800"/>
<p><em>Buscando endereço via geocoding</em></p>
</div>

<div align="center">
<img src="docs/screenshots/vendo lista de endereço encontrados.png" alt="Lista de Endereços" width="800"/>
<p><em>Visualizando lista de endereços encontrados</em></p>
</div>

### Visualização de Dados

<div align="center">
<img src="docs/screenshots/vendo os concorrentes.png" alt="Concorrentes" width="800"/>
<p><em>Mapa mostrando concorrentes na região (Competition Layer)</em></p>
</div>

<div align="center">
<img src="docs/screenshots/vendos pontos de interesse.png" alt="POIs" width="800"/>
<p><em>Visualização de pontos de interesse (POIs Layer)</em></p>
</div>

### Relatório de Análise

<div align="center">
<img src="docs/screenshots/Relatorio parte 1.png" alt="Relatório Parte 1" width="800"/>
<p><em>Relatório de análise - Score e métricas principais</em></p>
</div>

<div align="center">
<img src="docs/screenshots/Relatorio parte 2.png" alt="Relatório Parte 2" width="800"/>
<p><em>Relatório de análise - Detalhes e insights</em></p>
</div>

---

## 📋 Índice

- [Screenshots](#-screenshots)
- [Arquitetura](#-arquitetura)
- [Frontend - Componentes e Features](#-frontend---componentes-e-features)
- [Jornadas do Usuário](#-jornadas-do-usuário)
- [Stack Tecnológica](#-stack-tecnológica)
- [Fluxo de Scoring](#-fluxo-de-scoring)
- [Modelo de Features](#-modelo-de-features)
- [API Endpoints](#-api-endpoints)
  - [Core Endpoints (Score, Advanced, Demographics)](#core-endpoints)
  - [Geocoding e Layers](#get-apiv1geocode)
  - [Projetos e Health](#post-apiv1projects)
- [Pipeline de Machine Learning](#-pipeline-de-machine-learning)
- [Cache e Performance](#-cache-e-performance)
- [Segurança e Rate Limiting](#-segurança-e-rate-limiting)
- [Como Executar](#-como-executar)
- [Observabilidade](#-observabilidade)
- [Overpass API - Queries](#-overpass-api--queries-e-boas-práticas)
- [Testes](#-testes)
- [Integração GTFS](#-integração-gtfs-transporte-público)
- [Roadmap](#-roadmap-e-features-implementadas)

---

## 🏗️ Arquitetura

### Visão Geral do Sistema

```mermaid
graph TB
    subgraph Frontend["🎨 Frontend - Nuxt 3"]
        A[MapLibre GL JS<br/>Interface Interativa]
        B[Vue Components]
        C[Composables API]
    end
    
    subgraph Backend["⚡ Backend - FastAPI"]
        D[API Gateway<br/>FastAPI + CORS]
        E[Auth Middleware<br/>JWT/JWKS]
        F[Rate Limiter<br/>Redis]
        G[Score Engine]
        H[Feature Extractor]
        I[ML Predictor<br/>Scikit-learn]
    end
    
    subgraph Data["💾 Data Layer"]
        J[(PostgreSQL<br/>+ PostGIS)]
        K[(Redis<br/>Cache + Quotas)]
        L[Overpass API<br/>OpenStreetMap]
    end
    
    subgraph Obs["📊 Observability"]
        M[Prometheus<br/>Métricas]
        N[Grafana<br/>Dashboards]
    end
    
    A --> B --> C --> D
    D --> E --> F --> G
    G --> H --> I
    H <--> L
    G --> J
    F --> K
    H --> K
    D --> M --> N
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style B fill:#81D4FA,stroke:#0288D1,stroke-width:2px,color:#000
    style C fill:#81D4FA,stroke:#0288D1,stroke-width:2px,color:#000
    style D fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style E fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style F fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style G fill:#FF7043,stroke:#D84315,stroke-width:3px,color:#000
    style H fill:#FFB74D,stroke:#F57C00,stroke-width:3px,color:#000
    style I fill:#9575CD,stroke:#512DA8,stroke-width:3px,color:#fff
    style J fill:#42A5F5,stroke:#1976D2,stroke-width:3px,color:#000
    style K fill:#FFA726,stroke:#F57C00,stroke-width:3px,color:#000
    style L fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style M fill:#EC407A,stroke:#C2185B,stroke-width:2px,color:#fff
    style N fill:#EC407A,stroke:#C2185B,stroke-width:2px,color:#fff
    style Frontend fill:#E1F5FE,stroke:#4FC3F7,stroke-width:4px,color:#000
    style Backend fill:#E8F5E9,stroke:#66BB6A,stroke-width:4px,color:#000
    style Data fill:#E3F2FD,stroke:#42A5F5,stroke-width:4px,color:#000
    style Obs fill:#FCE4EC,stroke:#EC407A,stroke-width:4px,color:#000
```

### Estrutura de Diretórios

```
sitescore-ai-saas-pro/
├─ backend-python/              # Backend em Python
│  ├─ app/
│  │  ├─ api/v1/endpoints/      # Endpoints REST
│  │  │  ├─ scoring.py          # POST /score - Motor de análise
│  │  │  ├─ layers.py           # GET /layers/* - Dados geoespaciais
│  │  │  ├─ projects.py         # CRUD de projetos salvos
│  │  │  ├─ geocode.py          # Geocoding via Nominatim
│  │  │  └─ health.py           # Healthcheck
│  │  ├─ core/                  # Lógica de negócio
│  │  │  ├─ config.py           # Configurações (Pydantic Settings)
│  │  │  ├─ db.py               # SQLAlchemy + GeoAlchemy2
│  │  │  ├─ cache.py            # Redis cache (TTL 7 dias)
│  │  │  ├─ overpass_client.py  # Cliente Overpass + retry
│  │  │  ├─ features.py         # Extração de features geoespaciais
│  │  │  ├─ scoring_model.py    # Modelo baseline explicável
│  │  │  ├─ auth.py             # JWT/JWKS validation
│  │  │  ├─ rate_limit.py       # Quotas por usuário/IP
│  │  │  ├─ audit.py            # Log de chamadas Overpass
│  │  │  ├─ metrics.py          # Prometheus instrumentação
│  │  │  ├─ centrality.py       # Street centrality (osmnx)
│  │  │  └─ gtfs.py             # Parser GTFS para transporte
│  │  ├─ models/                # Modelos SQLAlchemy
│  │  │  ├─ project.py          # Projetos salvos
│  │  │  ├─ cache_entry.py      # Cache persistente
│  │  │  └─ overpass_audit.py   # Auditoria API
│  │  ├─ ml/                    # Machine Learning
│  │  │  ├─ train.py            # Pipeline de treino (GBR)
│  │  │  └─ README.md           # Documentação ML
│  │  ├─ models_store/          # Modelos treinados (.joblib)
│  │  ├─ scripts/
│  │  │  └─ seed.py             # Seeds de dados
│  │  ├─ tests/                 # Testes Pytest
│  │  │  ├─ test_features.py
│  │  │  └─ test_scoring.py
│  │  ├─ schemas.py             # Pydantic schemas
│  │  └─ main.py                # Entry point FastAPI
│  ├─ requirements.txt          # Dependências Python
│  └─ Dockerfile                # Container backend
│
├─ frontend-vue/                # Frontend em Vue 3
│  ├─ components/
│  │  ├─ MapView.vue            # 🗺️ Componente principal do mapa
│  │  ├─ AdvancedAnalysisPanel.vue  # 📊 Painel de análise avançada
│  │  ├─ DemographicsPanel.vue  # 👥 Painel de perfil demográfico
│  │  ├─ GaugeChart.vue         # 📊 Gráfico semi-circular de score
│  │  ├─ RadarChart.vue         # 🕸️ Gráfico radar de features
│  │  ├─ ScoreBadge.vue         # 🏆 Badge visual de score
│  │  ├─ POIPopup.vue           # 📍 Popup de detalhes de POI
│  │  ├─ LoadingSpinner.vue     # ⏳ Indicador de carregamento
│  │  ├─ SkeletonCard.vue       # 💀 Loading placeholder
│  │  ├─ ToastContainer.vue     # 🍞 Notificações toast
│  │  └─ DarkModeToggle.vue     # 🌙 Toggle de modo escuro
│  ├─ composables/
│  │  ├─ useApi.ts              # 🌐 Client HTTP
│  │  ├─ useMapLayers.ts        # 🗺️ Gerenciamento de camadas
│  │  ├─ useDarkMode.ts         # 🌙 Controle de tema escuro
│  │  ├─ useExport.ts           # 📥 Exportação JSON/CSV
│  │  └─ useToast.ts            # 🍞 Sistema de notificações
│  ├─ pages/
│  │  ├─ index.vue              # 🏠 Página principal do mapa
│  │  ├─ dashboard.vue          # 📊 Dashboard de projetos
│  │  └─ compare.vue            # ⚖️ Comparador de locais
│  ├─ plugins/
│  │  └─ maplibre.client.ts     # Plugin MapLibre
│  ├─ assets/css/
│  │  └─ main.css               # Estilos globais
│  ├─ nuxt.config.ts            # Configuração Nuxt
│  ├─ tailwind.config.js        # Configuração Tailwind CSS
│  ├─ package.json
│  └─ Dockerfile                # Container frontend
│
├─ prometheus/
│  └─ prometheus.yml            # Config Prometheus
├─ docker-compose.yml           # Orquestração de serviços
├─ Makefile                     # Comandos de desenvolvimento
├─ .env.example                 # Variáveis de ambiente
└─ LICENSE                      # MIT License
```

---

## 🎨 Frontend - Componentes e Features

### Componentes Vue 3

#### Visualização de Dados
| Componente | Descrição | Tecnologia |
|-----------|-----------|------------|
| **GaugeChart.vue** | Gráfico semi-circular (gauge) para exibir score 0-100 | Chart.js + vue-chartjs |
| **RadarChart.vue** | Gráfico radar multi-dimensional para features | Chart.js RadialScale |
| **ScoreBadge.vue** | Badge visual colorido com classificação do score | Tailwind CSS |
| **AdvancedAnalysisPanel.vue** | Painel completo com 9 métricas de análise avançada | Vue 3 Composition API |
| **DemographicsPanel.vue** | Painel de perfil demográfico com insights de público | Vue 3 + Tailwind |

#### Mapa e Interação
| Componente | Descrição |
|-----------|-----------|
| **MapView.vue** | Componente principal do mapa interativo (MapLibre GL JS) |
| **POIPopup.vue** | Popup com detalhes de POIs ao clicar no mapa |

#### UI/UX
| Componente | Descrição |
|-----------|-----------|
| **LoadingSpinner.vue** | Indicador de carregamento animado |
| **SkeletonCard.vue** | Loading placeholder para melhor UX |
| **ToastContainer.vue** | Sistema de notificações não-intrusivas |
| **DarkModeToggle.vue** | Toggle entre modo claro/escuro |

### Composables (Lógica Reutilizável)

#### `useApi.ts`
Client HTTP para comunicação com backend.
```typescript
const api = useApi()
const result = await api.scoreLocation(lat, lon, businessType)
```

#### `useMapLayers.ts`
Gerenciamento de camadas do mapa (competition, POIs, transit, flow).

#### `useDarkMode.ts`
**Dark Mode com persistência**
```typescript
const { isDark, toggle, init } = useDarkMode()
// Detecta preferência do sistema
// Persiste em localStorage
// Aplica classe 'dark' no DOM
```

#### `useExport.ts`
**Exportação de dados**
```typescript
const { exportToJSON, exportToCSV, captureScreenshot } = useExport()

// Exportar análise
exportToJSON(scoreData, 'analise-site.json')
exportToCSV(projectsList, 'projetos.csv')
```

Funcionalidades:
- Exportação JSON com formatação
- Exportação CSV com escape de caracteres especiais
- Download automático via Blob API

#### `useToast.ts`
**Sistema de notificações**
```typescript
const { success, error, warning, info } = useToast()

success('Análise concluída!')
error('Erro ao carregar dados', 5000)
```

---

## 🧭 Jornadas do Usuário

### Jornada 1: Análise Rápida de Local

```mermaid
flowchart TD
    A[👤 Usuário abre app] --> B[🗺️ Visualiza mapa]
    B --> C{Como buscar?}
    
    C -->|Clique| D[🖱️ Clica no mapa]
    C -->|Busca| E[🔍 Busca endereço]
    C -->|Desenho| F[✏️ Desenha polígono]
    
    D --> G[🏢 Seleciona tipo de negócio]
    E --> G
    F --> G
    
    G --> H[📊 Clica Analisar]
    H --> I[⏳ Loading 3-5s]
    I --> J[✅ Exibe Score + Report]
    
    J --> K{Ação do usuário}
    
    K -->|Ver mais| L[📊 Abre análise avançada]
    K -->|Demográfico| M[👥 Abre perfil de público]
    K -->|Salvar| N[💾 Salva projeto]
    K -->|Exportar| O[📥 Exporta JSON/CSV]
    K -->|Nova análise| B
    
    L --> P[Visualiza 9 dimensões<br/>walkability, safety, etc.]
    M --> Q[Visualiza perfis<br/>corporativo, estudantes, etc.]
    N --> R[Dashboard de projetos]
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style J fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style L fill:#9C27B0,stroke:#7B1FA2,stroke-width:3px,color:#fff
    style M fill:#FF9800,stroke:#F57C00,stroke-width:3px,color:#000
    style N fill:#2196F3,stroke:#1976D2,stroke-width:3px,color:#fff
```

### Jornada 2: Comparação de Múltiplos Locais

```mermaid
flowchart TD
    A[👤 Usuário no Dashboard] --> B[⚖️ Clica Comparador]
    B --> C[📍 Card 1: Insere lat/lon]
    C --> D[📍 Card 2: Insere lat/lon]
    D --> E[📍 Card 3: Insere lat/lon opcional]
    
    E --> F[🏢 Seleciona business_type<br/>para cada local]
    F --> G[📊 Clica Analisar em cada card]
    
    G --> H[⏳ Análises paralelas]
    H --> I[✅ Exibe 3 scores lado a lado]
    
    I --> J[📊 Tabela comparativa<br/>feature por feature]
    J --> K[🏆 Destaca melhor local]
    K --> L[💡 Insights automáticos]
    
    L --> M{Ação}
    M -->|Remover| N[❌ Remove local]
    M -->|Salvar melhor| O[💾 Salva vencedor]
    M -->|Exportar| P[📥 Exporta comparação]
    M -->|Nova comparação| C
    
    N --> C
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style I fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style K fill:#FFC107,stroke:#FFA000,stroke-width:3px,color:#000
    style L fill:#9C27B0,stroke:#7B1FA2,stroke-width:3px,color:#fff
```

### Jornada 3: Dashboard de Projetos Salvos

```mermaid
flowchart TD
    A[👤 Usuário logado] --> B[📊 Acessa Dashboard]
    B --> C[📋 Lista de projetos salvos]
    
    C --> D{Ação na lista}
    
    D -->|Ver detalhes| E[🔍 Abre projeto]
    D -->|Filtrar| F[🔎 Filtra por business_type/score]
    D -->|Ordenar| G[📊 Ordena por data/score]
    D -->|Novo projeto| H[➕ Volta ao mapa]
    
    E --> I[📄 Visualiza análise completa]
    I --> J[🗺️ Mapa com marcador]
    J --> K[📊 Scores e features]
    K --> L[📈 Histórico de mudanças]
    
    L --> M{Ações do projeto}
    
    M -->|Re-analisar| N[🔄 Nova análise<br/>dados atualizados]
    M -->|Editar| O[✏️ Edita nome/notas]
    M -->|Deletar| P[🗑️ Remove projeto]
    M -->|Exportar| Q[📥 Exporta relatório]
    M -->|Comparar| R[⚖️ Vai para comparador]
    
    N --> I
    R --> S[Adiciona ao comparador]
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style C fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style I fill:#9C27B0,stroke:#7B1FA2,stroke-width:3px,color:#fff
    style N fill:#FF9800,stroke:#F57C00,stroke-width:3px,color:#000
```

### Jornada 4: Análise Avançada + Demografia

```mermaid
flowchart TD
    A[👤 Usuário na tela de análise] --> B[📊 Vê score básico]
    B --> C[🎯 Clica Ver Análise Avançada]
    
    C --> D[⏳ Chama /api/v1/advanced]
    D --> E[✅ Recebe 9 dimensões]
    
    E --> F[📊 Exibe AdvancedAnalysisPanel]
    F --> G[Visualiza scores por categoria:<br/>Mobilidade, Segurança,<br/>Contexto Urbano, etc.]
    
    G --> H[✨ Pontos Fortes destacados]
    H --> I[⚠️ Pontos de Atenção destacados]
    I --> J[📈 Dados detalhados expandíveis]
    
    J --> K[👥 Clica Ver Perfil de Público]
    K --> L[⏳ Chama /api/v1/demographics]
    L --> M[✅ Recebe perfis identificados]
    
    M --> N[📊 Exibe DemographicsPanel]
    N --> O[Categorias de POIs<br/>offices, schools, retail, etc.]
    O --> P[Perfis com %:<br/>👨‍💼 Corporativo 35%<br/>🎓 Estudantes 25%<br/>🛍️ Varejo 40%]
    
    P --> Q[💡 Oportunidades de negócio<br/>por perfil]
    Q --> R[🎯 Insights automáticos]
    
    R --> S{Ação final}
    S -->|Salvar completo| T[💾 Salva com análises]
    S -->|Exportar tudo| U[📥 PDF/JSON completo]
    S -->|Nova localização| V[🗺️ Volta ao mapa]
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style F fill:#9C27B0,stroke:#7B1FA2,stroke-width:3px,color:#fff
    style N fill:#FF9800,stroke:#F57C00,stroke-width:3px,color:#000
    style Q fill:#4CAF50,stroke:#388E3C,stroke-width:3px,color:#fff
```

### Jornada 5: Visualização de Layers no Mapa

```mermaid
flowchart TD
    A[👤 Usuário no mapa<br/>após análise] --> B[🗺️ Vê resultado do score]
    B --> C[🎛️ Painel de Layers]
    
    C --> D{Seleciona Layer}
    
    D -->|Competition| E[🏪 Layer de Concorrentes]
    D -->|POIs| F[🏢 Layer de POIs]
    D -->|Transit| G[🚇 Layer de Transporte]
    D -->|Flow| H[🌊 Heatmap de Fluxo]
    
    E --> I[Marcadores vermelhos<br/>no mapa]
    F --> J[Marcadores azuis<br/>no mapa]
    G --> K[Marcadores verdes<br/>paradas de transporte]
    H --> L[Gradiente de calor<br/>vermelho → azul]
    
    I --> M[🖱️ Clica em marcador]
    J --> M
    K --> M
    
    M --> N[📍 POIPopup aparece]
    N --> O[Nome do local<br/>Tags OSM<br/>Distância]
    
    O --> P{Ação}
    P -->|Fecha popup| Q[❌ Fecha]
    P -->|Alterna layer| D
    P -->|Desativa layer| R[👁️ Oculta layer]
    
    R --> D
    Q --> B
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style H fill:#FF5722,stroke:#D84315,stroke-width:3px,color:#fff
    style N fill:#9C27B0,stroke:#7B1FA2,stroke-width:3px,color:#fff
    style O fill:#4CAF50,stroke:#388E3C,stroke-width:3px,color:#fff
```

### Jornada 6: Dark Mode e Preferências

```mermaid
flowchart TD
    A[👤 Usuário acessa app] --> B[🌐 Sistema detecta preferência]
    
    B --> C{Preferência OS}
    
    C -->|Dark| D[🌙 Ativa Dark Mode]
    C -->|Light| E[☀️ Ativa Light Mode]
    C -->|Nenhuma| F[☀️ Light Mode padrão]
    
    D --> G[Verifica localStorage]
    E --> G
    F --> G
    
    G --> H{Tem preferência salva?}
    
    H -->|Sim| I[Usa preferência salva]
    H -->|Não| J[Usa preferência do OS]
    
    I --> K[🎨 Aplica tema]
    J --> K
    
    K --> L[Usuário navega]
    
    L --> M[🌙 Clica DarkModeToggle]
    
    M --> N[⚡ Toggle isDark]
    N --> O[Aplica classe 'dark' no DOM]
    O --> P[💾 Salva em localStorage]
    
    P --> Q[🎨 Transição suave<br/>transition-colors 300ms]
    
    Q --> R{Continua usando?}
    R -->|Sim| L
    R -->|Fecha app| S[💾 Preferência persistida]
    
    S --> T[🔄 Próxima visita]
    T --> G
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style D fill:#1A237E,stroke:#0D47A1,stroke-width:3px,color:#fff
    style E fill:#FFF9C4,stroke:#FBC02D,stroke-width:3px,color:#000
    style M fill:#9C27B0,stroke:#7B1FA2,stroke-width:3px,color:#fff
    style Q fill:#4CAF50,stroke:#388E3C,stroke-width:3px,color:#fff
```

### Jornada 7: Sistema de Notificações (Toasts)

```mermaid
flowchart TD
    A[⚡ Evento na aplicação] --> B{Tipo de evento}
    
    B -->|Sucesso| C[✅ toast.success]
    B -->|Erro| D[❌ toast.error]
    B -->|Aviso| E[⚠️ toast.warning]
    B -->|Info| F[ℹ️ toast.info]
    
    C --> G[Cria objeto Toast<br/>id, message, type, duration]
    D --> G
    E --> G
    F --> G
    
    G --> H[Adiciona ao array toasts]
    H --> I[ToastContainer renderiza]
    
    I --> J[🎨 Animação de entrada<br/>slide-in-right]
    
    J --> K[🕐 Timer inicia<br/>duration: 3000ms padrão]
    
    K --> L{Usuário interage?}
    
    L -->|Clica X| M[❌ Remove toast imediatamente]
    L -->|Hover| N[⏸️ Pausa timer opcional]
    L -->|Aguarda| O[⏱️ Timer completa]
    
    N --> P[Mouse sai<br/>retoma timer]
    P --> O
    
    O --> Q[🎨 Animação de saída<br/>fade-out]
    Q --> R[Remove do array toasts]
    
    M --> R
    
    R --> S{Mais toasts?}
    S -->|Sim| T[Mostra próximo<br/>Stack de até 5]
    S -->|Não| U[Container vazio]
    
    T --> K
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style C fill:#4CAF50,stroke:#388E3C,stroke-width:3px,color:#fff
    style D fill:#F44336,stroke:#C62828,stroke-width:3px,color:#fff
    style E fill:#FF9800,stroke:#F57C00,stroke-width:3px,color:#000
    style F fill:#2196F3,stroke:#1976D2,stroke-width:3px,color:#fff
    style J fill:#9C27B0,stroke:#7B1FA2,stroke-width:3px,color:#fff
```

### Jornada 8: Exportação de Dados

```mermaid
flowchart TD
    A[👤 Usuário com dados<br/>análise ou projetos] --> B{Formato de exportação}
    
    B -->|JSON| C[📥 Clica Exportar JSON]
    B -->|CSV| D[📥 Clica Exportar CSV]
    
    C --> E[useExport.exportToJSON]
    D --> F[useExport.exportToCSV]
    
    E --> G[Serializa dados<br/>JSON.stringify com indent 2]
    F --> H[Converte para CSV]
    
    H --> I[Extrai keys únicos<br/>de todos objetos]
    I --> J[Cria header CSV<br/>keys.join]
    J --> K[Mapeia cada objeto<br/>para linha CSV]
    K --> L[Escapa vírgulas e aspas<br/>RFC 4180]
    
    G --> M[Cria Blob<br/>type: application/json]
    L --> N[Cria Blob<br/>type: text/csv]
    
    M --> O[URL.createObjectURL]
    N --> O
    
    O --> P[Cria elemento <a><br/>invisível]
    P --> Q[Define href = blobURL]
    Q --> R[Define download = filename]
    R --> S[Adiciona ao DOM<br/>document.body.appendChild]
    
    S --> T[🖱️ Simula click<br/>link.click]
    T --> U[⬇️ Browser inicia download]
    
    U --> V[Remove do DOM<br/>removeChild]
    V --> W[Revoga blobURL<br/>URL.revokeObjectURL]
    
    W --> X[✅ Toast de sucesso<br/>Arquivo baixado!]
    
    X --> Y{Erro?}
    Y -->|Sim| Z[❌ Toast de erro<br/>Falha ao exportar]
    Y -->|Não| AA[✅ Download completo]
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style C fill:#4CAF50,stroke:#388E3C,stroke-width:3px,color:#fff
    style D fill:#2196F3,stroke:#1976D2,stroke-width:3px,color:#fff
    style L fill:#FF9800,stroke:#F57C00,stroke-width:3px,color:#000
    style U fill:#9C27B0,stroke:#7B1FA2,stroke-width:3px,color:#fff
    style X fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
```

### Jornada 9: Geocoding (Busca de Endereço)

```mermaid
flowchart TD
    A[👤 Usuário no mapa] --> B[🔍 Clica na barra de busca]
    B --> C[⌨️ Digite endereço<br/>Ex: Av Paulista, SP]
    
    C --> D[Pressiona Enter<br/>ou clica Buscar]
    
    D --> E[🔍 Verifica cache Redis<br/>key: geocode:av+paulista+sp]
    
    E --> F{Cache hit?}
    
    F -->|Sim ✅| G[Retorna do cache<br/>~10ms]
    F -->|Não ❌| H[Chama Nominatim API]
    
    H --> I[⏳ Aguarda resposta<br/>~500-1000ms]
    
    I --> J{Resultado encontrado?}
    
    J -->|Sim| K[Parseia resposta<br/>lat, lon, display_name, bbox]
    J -->|Não| L[❌ Toast: Endereço não encontrado]
    
    K --> M[💾 Salva no cache<br/>TTL: 24 horas]
    
    M --> N[Retorna coordenadas]
    G --> N
    
    N --> O[🗺️ Centraliza mapa<br/>flyTo lat, lon]
    O --> P[📍 Adiciona marcador]
    P --> Q[🎯 Zoom nível 15]
    
    Q --> R[Pré-preenche coordenadas<br/>no formulário de análise]
    
    R --> S{Usuário ação}
    S -->|Analisa| T[📊 Inicia análise]
    S -->|Nova busca| B
    S -->|Ajusta posição| U[🖱️ Arrasta mapa]
    
    L --> B
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style G fill:#4CAF50,stroke:#388E3C,stroke-width:3px,color:#fff
    style H fill:#FF9800,stroke:#F57C00,stroke-width:3px,color:#000
    style L fill:#F44336,stroke:#C62828,stroke-width:3px,color:#fff
    style O fill:#9C27B0,stroke:#7B1FA2,stroke-width:3px,color:#fff
    style T fill:#2196F3,stroke:#1976D2,stroke-width:3px,color:#fff
```

---

## 🔧 Stack Tecnológica

### Backend
| Tecnologia | Versão | Propósito |
|-----------|--------|-----------|
| **FastAPI** | 0.115.0 | Framework web assíncrono de alta performance |
| **SQLAlchemy** | 2.0.35 | ORM para persistência de dados |
| **GeoAlchemy2** | 0.15.2 | Extensão geoespacial para SQLAlchemy |
| **PostgreSQL + PostGIS** | 16-3.4 | Banco de dados com extensões geoespaciais |
| **Redis** | 7 | Cache em memória e rate limiting |
| **GeoPandas** | 1.0.1 | Análise de dados geoespaciais |
| **Shapely** | 2.0.4 | Manipulação de geometrias |
| **Scikit-learn** | 1.5.2 | Machine learning (Gradient Boosting) |
| **OSMnx** | 1.9.3 | Análise de redes de ruas |
| **Tenacity** | 8.2.3 | Retry com exponential backoff |
| **Prometheus** | - | Coleta de métricas |

### Frontend
| Tecnologia | Versão | Propósito |
|-----------|--------|-----------|
| **Nuxt 3** | 3.x | Framework Vue SSR/SSG |
| **Vue.js** | 3.x | Framework reativo |
| **MapLibre GL JS** | - | Renderização de mapas interativos |
| **TypeScript** | - | Type safety |

### Infraestrutura
- **Docker & Docker Compose**: Containerização e orquestração
- **Uvicorn**: ASGI server (2 workers)
- **Grafana**: Visualização de métricas

---

## 🎯 Fluxo de Scoring

### Diagrama de Sequência Completo

```mermaid
%%{init: {'theme':'default'}}%%
sequenceDiagram
    autonumber
    participant U as 👤 Usuário
    participant F as 🎨 Frontend<br/>(Nuxt 3)
    participant A as ⚡ API Gateway<br/>(FastAPI)
    participant Auth as 🔐 Auth Middleware<br/>(JWT)
    participant RL as 🚦 Rate Limiter<br/>(Redis)
    participant SE as 🎯 Score Engine
    participant FE as 🗺️ Feature Extractor
    participant Cache as 💾 Redis Cache
    participant OSM as 🌍 Overpass API<br/>(OSM)
    participant ML as 🤖 ML Predictor
    participant DB as 🗄️ PostgreSQL<br/>(PostGIS)
    
    U->>F: 🖱️ Clica no mapa / Desenha polígono
    U->>F: 🏢 Seleciona tipo de negócio
    F->>A: 📤 POST /api/v1/score<br/>{geometry, business_type}
    
    A->>Auth: 🔍 Valida JWT Token
    Auth-->>A: ✅ user.sub
    
    A->>RL: ⏱️ Verifica quota (60/min)
    RL-->>A: ✅ Autorizado
    
    A->>SE: ⚙️ Processa requisição
    SE->>FE: 📊 Extrai features
    
    rect rgb(230, 245, 255)
        Note over FE,OSM: 🔄 CONSULTAS PARALELAS (asyncio.gather)
        
        FE->>Cache: 🔍 Busca cache (competition)
        alt Cache Hit
            Cache-->>FE: ✅ Dados em cache
        else Cache Miss
            FE->>OSM: 📡 Query 1: Concorrentes<br/>(restaurante/academia/varejo)
            OSM-->>FE: 📦 GeoJSON elements
            FE->>Cache: 💾 Salva cache (TTL 7 dias)
        end
        
        FE->>Cache: 🔍 Busca cache (POIs)
        alt Cache Hit
            Cache-->>FE: ✅ Dados em cache
        else Cache Miss
            FE->>OSM: 📡 Query 2: POIs<br/>(escritórios/escolas/parques)
            OSM-->>FE: 📦 GeoJSON elements
            FE->>Cache: 💾 Salva cache (TTL 7 dias)
        end
        
        FE->>Cache: 🔍 Busca cache (transit)
        alt Cache Hit
            Cache-->>FE: ✅ Dados em cache
        else Cache Miss
            FE->>OSM: 📡 Query 3: Transporte<br/>(paradas/metrô/estações)
            OSM-->>FE: 📦 GeoJSON elements
            FE->>Cache: 💾 Salva cache (TTL 7 dias)
        end
    end
    
    FE->>DB: 📝 Log auditoria Overpass
    
    rect rgb(255, 230, 230)
        Note over FE: 🗺️ PROCESSAMENTO GEOESPACIAL (GeoPandas)
        FE->>FE: 📐 to_geodf() → GeoDataFrame
        FE->>FE: 🔍 Filtra por polígono/bbox
        FE->>FE: 📏 count_within_radius(500m)
        FE->>FE: 📍 nearest_distance_meters()
        FE->>FE: 🌊 kde_value() → flow heatmap
        FE->>FE: 🎲 entropy_mix() → diversidade
        FE->>FE: 🛣️ street_centrality() → osmnx
    end
    
    FE-->>SE: 📊 raw_features dict
    
    rect rgb(230, 255, 230)
        Note over SE,ML: 🎯 CÁLCULO DE SCORE
        SE->>ML: 🔍 Verifica modelo treinado<br/>(models_store/*.joblib)
        
        alt Modelo ML Disponível
            ML->>ML: 🤖 model.predict(features)
            ML-->>SE: 📈 score (0-100) + "ML model"
        else Baseline Explicável
            SE->>SE: 🧮 compute_score()<br/>pesos por business_type
            SE->>SE: 📊 Normaliza features
            SE->>SE: ➕ Weighted sum → score
            SE-->>SE: 🏆 Top 3 contribuições
        end
    end
    
    SE-->>A: 📤 {score, features, explanation, center}
    A-->>F: 📥 JSON Response
    F->>F: 🎨 Renderiza relatório visual
    F->>F: 🗺️ Exibe layers no mapa
    F-->>U: 📊 Score + Insights
    
    opt Salvar Projeto
        U->>F: 💾 Clica "Salvar"
        F->>A: 📤 POST /api/v1/projects
        A->>DB: 💾 INSERT project
        DB-->>A: ✅ Salvo
        A-->>F: 🆔 project_id
        F-->>U: ✅ Projeto salvo
    end
```

### Pipeline de Features (Detalhado)

```mermaid
flowchart LR
    subgraph Entrada["📍 1. Entrada"]
        A1[GeoJSON<br/>Geometry]
        A2[business_type<br/>string]
    end
    
    subgraph Espacial["🗺️ 2. Processamento Espacial"]
        B1[to_geodf<br/>GeoDataFrame]
        B2[Filtrar por<br/>Polígono/Bbox]
        B3[Reprojetar<br/>EPSG:3857]
    end
    
    subgraph Concorrencia["🏪 3. Análise de Concorrência"]
        C1[Buscar tags<br/>por business_type]
        C2[count_within_radius<br/>500m]
        C3{Densidade<br/>Alta?}
    end
    
    subgraph POIs["🏢 4. POIs e Amenidades"]
        D1[Escritórios<br/>office=*]
        D2[Escolas<br/>amenity=school/university]
        D3[Parques<br/>leisure=park]
        D4[entropy_mix<br/>Diversidade]
    end
    
    subgraph Transporte["🚇 5. Transporte"]
        E1[Paradas<br/>highway=bus_stop]
        E2[Metrô/Trem<br/>railway=*]
        E3[count_within_radius<br/>300m]
        E4[nearest_distance<br/>metros]
    end
    
    subgraph Fluxo["🚶 6. Fluxo de Pessoas"]
        F1[KDE Heatmap<br/>bandwidth 200m]
        F2[Proxies:<br/>transit+offices+comp]
        F3[Gaussian Kernel<br/>exp-d²/2σ²]
    end
    
    subgraph Network["🛣️ 7. Street Network"]
        G1[OSMnx<br/>download_graph]
        G2[Betweenness<br/>Centrality]
        G3[Valor no<br/>ponto central]
    end
    
    subgraph Features["📊 8. Features Brutas"]
        H1[competition: int]
        H2[offices: int]
        H3[schools: int]
        H4[parks: int]
        H5[transit: int]
        H6[flow_kde: float]
        H7[mix: float 0-1]
        H8[street_centrality: float]
        H9[dist_transit_m: float]
    end
    
    A1 --> B1 --> B2 --> B3
    A2 --> C1
    
    B3 --> C1 --> C2 --> C3
    B3 --> D1 & D2 & D3
    D1 & D2 & D3 --> D4
    
    B3 --> E1 & E2
    E1 & E2 --> E3 & E4
    
    B3 --> F2
    F2 --> F1 --> F3
    
    B2 --> G1 --> G2 --> G3
    
    C2 --> H1
    D1 --> H2
    D2 --> H3
    D3 --> H4
    E3 --> H5
    F3 --> H6
    D4 --> H7
    G3 --> H8
    E4 --> H9
    
    style A1 fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style A2 fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    style B1 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style B2 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style B3 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style C1 fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    style C2 fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    style C3 fill:#FF7043,stroke:#D84315,stroke-width:3px,color:#000
    style D1 fill:#AED581,stroke:#689F38,stroke-width:2px,color:#000
    style D2 fill:#AED581,stroke:#689F38,stroke-width:2px,color:#000
    style D3 fill:#AED581,stroke:#689F38,stroke-width:2px,color:#000
    style D4 fill:#9CCC65,stroke:#689F38,stroke-width:2px,color:#000
    style E1 fill:#5C6BC0,stroke:#3F51B5,stroke-width:2px,color:#fff
    style E2 fill:#5C6BC0,stroke:#3F51B5,stroke-width:2px,color:#fff
    style E3 fill:#5C6BC0,stroke:#3F51B5,stroke-width:2px,color:#fff
    style E4 fill:#5C6BC0,stroke:#3F51B5,stroke-width:2px,color:#fff
    style F1 fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style F2 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style F3 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style G1 fill:#FFD54F,stroke:#FFA000,stroke-width:2px,color:#000
    style G2 fill:#FFD54F,stroke:#FFA000,stroke-width:2px,color:#000
    style G3 fill:#FFD54F,stroke:#FFA000,stroke-width:2px,color:#000
    style H1 fill:#E0E0E0,stroke:#616161,stroke-width:2px,color:#000
    style H2 fill:#E0E0E0,stroke:#616161,stroke-width:2px,color:#000
    style H3 fill:#E0E0E0,stroke:#616161,stroke-width:2px,color:#000
    style H4 fill:#E0E0E0,stroke:#616161,stroke-width:2px,color:#000
    style H5 fill:#E0E0E0,stroke:#616161,stroke-width:2px,color:#000
    style H6 fill:#E0E0E0,stroke:#616161,stroke-width:2px,color:#000
    style H7 fill:#E0E0E0,stroke:#616161,stroke-width:2px,color:#000
    style H8 fill:#E0E0E0,stroke:#616161,stroke-width:2px,color:#000
    style H9 fill:#E0E0E0,stroke:#616161,stroke-width:2px,color:#000
    style Entrada fill:#E1F5FE,stroke:#4FC3F7,stroke-width:4px,color:#000
    style Espacial fill:#E8F5E9,stroke:#66BB6A,stroke-width:4px,color:#000
    style Concorrencia fill:#FFF3E0,stroke:#FFB74D,stroke-width:4px,color:#000
    style POIs fill:#F1F8E9,stroke:#9CCC65,stroke-width:4px,color:#000
    style Transporte fill:#E8EAF6,stroke:#7986CB,stroke-width:4px,color:#000
    style Fluxo fill:#E8F5E9,stroke:#66BB6A,stroke-width:4px,color:#000
    style Network fill:#FFFDE7,stroke:#FFD54F,stroke-width:4px,color:#000
    style Features fill:#FAFAFA,stroke:#9E9E9E,stroke-width:4px,color:#000
```

---

## 📊 Modelo de Features

### Features Extraídas (9 dimensões)

| Feature | Tipo | Descrição | Cap/Range | Método |
|---------|------|-----------|-----------|--------|
| `competition` | int | Número de concorrentes em 500m | 0-50+ | `count_within_radius(500)` |
| `offices` | int | Escritórios em 500m | 0-300+ | `filter_by_tag('office')` |
| `schools` | int | Escolas/universidades em 500m | 0-20+ | `filter_by_tag('amenity', ['school','university'])` |
| `parks` | int | Parques em 500m | 0-10+ | `filter_by_tag('leisure', ['park'])` |
| `transit` | int | Paradas de transporte em 300m | 0-40+ | Overpass `highway=bus_stop` + `railway=*` |
| `dist_transit_m` | float | Distância ao transporte mais próximo | 0-∞ m | `nearest_distance_meters()` |
| `flow_kde` | float | Densidade de fluxo estimado (KDE) | 0-50+ | Gaussian KDE (bandwidth 200m) |
| `mix` | float | Entropia de mix de amenidades | 0.0-1.0 | Shannon entropy normalizada |
| `street_centrality` | float | Betweenness centrality (osmnx) | 0.0-1.0 | Rede de ruas (opcional) |

### Modelo de Scoring Baseline (Explicável)

**Sistema de pesos por tipo de negócio:**

```mermaid
graph TD
    subgraph Rest["🍽️ Restaurante"]
        R1["✅ flow_kde: +0.35<br/>💡 Fluxo mais importante"]
        R2["✅ transit: +0.20<br/>💡 Acesso fácil"]
        R3["✅ offices: +0.25<br/>💡 Clientes corporativos"]
        R4["✅ mix: +0.10<br/>💡 Variedade"]
        R5["⚠️ competition: -0.20<br/>💡 Penalidade concorrência"]
    end
    
    subgraph Acad["💪 Academia"]
        A1["✅ parks: +0.25<br/>💡 Proximidade verde"]
        A2["✅ transit: +0.15<br/>💡 Acessibilidade"]
        A3["✅ flow_kde: +0.20<br/>💡 Movimento"]
        A4["✅ schools: +0.10<br/>💡 Público jovem"]
        A5["⚠️ competition: -0.20<br/>💡 Penalidade concorrência"]
        A6["✅ mix: +0.10<br/>💡 Variedade"]
    end
    
    subgraph Varejo["👗 Varejo de Moda"]
        V1["✅ flow_kde: +0.30<br/>💡 Alto movimento"]
        V2["✅ offices: +0.20<br/>💡 Poder aquisitivo"]
        V3["✅ transit: +0.20<br/>💡 Fácil acesso"]
        V4["✅ mix: +0.15<br/>💡 Mix comercial"]
        V5["⚠️ competition: -0.25<br/>💡 Maior penalidade"]
    end
    
    style R1 fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style R2 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style R3 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style R4 fill:#A5D6A7,stroke:#388E3C,stroke-width:2px,color:#000
    style R5 fill:#FF7043,stroke:#D84315,stroke-width:3px,color:#000
    
    style A1 fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style A2 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style A3 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style A4 fill:#A5D6A7,stroke:#388E3C,stroke-width:2px,color:#000
    style A5 fill:#FF7043,stroke:#D84315,stroke-width:3px,color:#000
    style A6 fill:#A5D6A7,stroke:#388E3C,stroke-width:2px,color:#000
    
    style V1 fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style V2 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style V3 fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style V4 fill:#A5D6A7,stroke:#388E3C,stroke-width:2px,color:#000
    style V5 fill:#EF5350,stroke:#C62828,stroke-width:3px,color:#fff
    
    style Rest fill:#FFF3E0,stroke:#FFB74D,stroke-width:4px,color:#000
    style Acad fill:#E1F5FE,stroke:#4FC3F7,stroke-width:4px,color:#000
    style Varejo fill:#FCE4EC,stroke:#EC407A,stroke-width:4px,color:#000
```

**Fórmula de cálculo:**

1. **Normalização**: `norm(x) = min(x, cap) / cap` para cada feature
2. **Weighted Sum**: `total = Σ(weight_i × norm(feature_i))`
3. **Score final**: `score = max(0, min(100, (total + 1) × 50))`
4. **Explicação**: Top 3 contribuições por valor absoluto

**Exemplo (Restaurante):**
```python
raw_features = {
    "flow_kde": 25.0,      # → norm = 25/50 = 0.50 → contrib = 0.50 × 0.35 = +0.175
    "transit": 8,          # → norm = 8/40 = 0.20  → contrib = 0.20 × 0.20 = +0.040
    "offices": 45,         # → norm = 45/300 = 0.15 → contrib = 0.15 × 0.25 = +0.038
    "mix": 0.72,           # → norm = 0.72 (já normalizado) → contrib = 0.72 × 0.10 = +0.072
    "competition": 12      # → norm = 12/50 = 0.24 → contrib = 0.24 × -0.20 = -0.048
}
# total = 0.175 + 0.040 + 0.038 + 0.072 - 0.048 = 0.277
# score = (0.277 + 1) × 50 = 63.85 ≈ 64
```

---

## 📡 API Endpoints

### Core Endpoints

#### `POST /api/v1/score`
Calcula score de viabilidade para uma localização.

#### `POST /api/v1/advanced`
**Análise Avançada Multi-Dimensional**

Retorna análise completa com 9 dimensões de qualidade urbana:
- 🚶 **Walkability** - Caminhabilidade e POIs
- 🚴 **Cyclability** - Infraestrutura para bicicletas
- 🌳 **Green Spaces** - Áreas verdes e parques
- 🅿️ **Parking** - Disponibilidade de estacionamento
- 🔒 **Safety** - Infraestrutura de segurança
- 💡 **Lighting** - Iluminação pública
- 🏢 **Building Density** - Densidade urbana
- 🛣️ **Street Connectivity** - Conectividade viária
- 🎯 **Amenity Diversity** - Diversidade de serviços

**Query Params:**
- `lon` (float, required): Longitude
- `lat` (float, required): Latitude  
- `radius` (int, optional): Raio de análise em metros (default: 1000)

**Response:**
```json
{
  "location": {"lon": -46.6333, "lat": -23.5505},
  "radius": 1000,
  "overall_score": 67.5,
  "rating": "Muito Bom",
  "rating_emoji": "✨",
  "scores": {
    "walkability": {
      "value": 0.85,
      "max": 1.0,
      "description": "Índice de caminhabilidade",
      "emoji": "🚶",
      "category": "Mobilidade"
    },
    // ... outros scores
  },
  "strengths": [
    {
      "feature": "walkability",
      "score": 85.0,
      "emoji": "🚶",
      "description": "Excelente caminhabilidade"
    }
  ],
  "weaknesses": [...],
  "raw_counts": {
    "footways": 45,
    "cycleways": 12,
    "green_areas": 3,
    "parking_lots": 8,
    "street_lamps": 120,
    "pois": 234,
    "transit_stops": 15
  }
}
```

---

#### `GET /api/v1/demographics`
**Análise Demográfica e Perfil do Público**

Infere perfil do público baseado em estabelecimentos da região (POIs do OSM).

**Query Params:**
- `lon` (float, required): Longitude
- `lat` (float, required): Latitude
- `radius` (int, optional): Raio de análise (default: 1000m)

**Perfis Identificados:**
- 👨‍💼 **Corporativo** - Alta concentração de escritórios
- 🎓 **Estudantes** - Escolas e universidades
- 🛍️ **Varejo Intenso** - Corredor comercial estabelecido
- 🏥 **Polo de Saúde** - Serviços de saúde concentrados
- 🏘️ **Residencial/Misto** - Perfil misto

**Response:**
```json
{
  "location": {"lon": -46.6333, "lat": -23.5505},
  "radius": 1000,
  "total_pois": 156,
  "categories": {
    "offices": 45,
    "schools": 12,
    "culture": 8,
    "retail": 78,
    "health": 5,
    "financial": 8
  },
  "profiles": [
    {
      "type": "Corporativo",
      "percentage": 35.2,
      "emoji": "👨‍💼",
      "characteristics": [
        "45 escritórios identificados",
        "Fluxo intenso em horário comercial (8h-18h)",
        "Poder aquisitivo médio-alto"
      ],
      "opportunities": [
        "Almoço executivo (12h-14h)",
        "Happy hour (18h-20h)",
        "Serviços rápidos"
      ]
    }
  ],
  "summary": "Identificados 2 perfis principais de público na região"
}
```

---

**Request Body:**
```json
{
  "geometry": {
    "type": "Point",
    "coordinates": [-46.6333, -23.5505]
  },
  "business_type": "restaurante"  // ou "academia", "varejo_moda"
}
```

**Response (200):**
```json
{
  "score": 67.5,
  "features": [
    {
      "name": "flow_kde",
      "value": 32.4,
      "weight": 0.35,
      "contribution": 0.227,
      "description": "flow_kde (norm=0.65) com peso +0.35"
    },
    // ... outras features
  ],
  "explanation": "Principais fatores: flow_kde (+0.227), offices (+0.042), transit (+0.036).",
  "center": [-46.6333, -23.5505],
  "layer_refs": {
    "competition": "/api/v1/layers/competition",
    "pois": "/api/v1/layers/pois",
    "transit": "/api/v1/layers/transit",
    "flow": "/api/v1/layers/flow"
  }
}
```

**Query Params (Opcional):**
- `?segment=premium` - Usa modelo treinado específico para segmento

---

#### `GET /api/v1/geocode`
Geocodifica endereços via Nominatim.

**Query Params:**
- `q` (string, required): Endereço a buscar

**Response:**
```json
{
  "display_name": "Av. Paulista, São Paulo, Brasil",
  "lat": "-23.5613",
  "lon": "-46.6563",
  "bbox": ["-46.657", "-23.562", "-46.655", "-23.560"]
}
```

**Cache:** TTL 24h (Redis)

---

#### `GET /api/v1/layers/{layer_type}`
Retorna dados geoespaciais por tipo.

**Layer Types:**
- `competition` - Concorrentes
- `pois` - Pontos de interesse
- `transit` - Transporte público
- `flow` - Heatmap de fluxo

---

#### `POST /api/v1/projects`
Salva um projeto de análise.

**Request:**
```json
{
  "name": "Restaurante Vila Madalena",
  "geometry": {...},
  "business_type": "restaurante",
  "score": 67.5,
  "features": {...}
}
```

---

#### `GET /api/v1/health`
Healthcheck do sistema.

**Response:**
```json
{
  "status": "ok",
  "overpass_url": "https://overpass-api.de/api/interpreter",
  "db": "connected",
  "redis": "connected"
}
```

---

## 🤖 Pipeline de Machine Learning

### Arquitetura do Modelo

```mermaid
flowchart TB
    subgraph Dados["📊 1. Coleta de Dados"]
        A1[Dados Históricos<br/>CSV/Database]
        A2[Features: 8 dimensões]
        A3[Target: faturamento/<br/>footfall/sucesso]
    end
    
    subgraph Prep["🔧 2. Pré-processamento"]
        B1[Limpeza de dados]
        B2[Feature Engineering]
        B3[Train/Test Split<br/>80/20]
    end
    
    subgraph Train["🎯 3. Treino"]
        C1[GradientBoostingRegressor<br/>sklearn]
        C2[Hyperparameter Tuning]
        C3[Cross-Validation]
    end
    
    subgraph Eval["📈 4. Avaliação"]
        D1[Métricas:<br/>R², MAE, RMSE]
        D2[Feature Importance<br/>Permutation/SHAP]
        D3[Residual Analysis]
    end
    
    subgraph Deploy["🚀 5. Deploy"]
        E1[Serialização<br/>joblib.dump]
        E2[models_store/<br/>business_type.joblib]
        E3[Auto-load em<br/>scoring.py]
    end
    
    subgraph Infer["⚡ 6. Inferência"]
        F1[Requisição<br/>POST /score]
        F2[Carrega modelo]
        F3[model.predict]
        F4[Score 0-100]
    end
    
    A1 --> A2 & A3
    A2 & A3 --> B1 --> B2 --> B3
    B3 --> C1 --> C2 --> C3
    C3 --> D1 & D2 & D3
    D1 --> E1 --> E2 --> E3
    E3 --> F1 --> F2 --> F3 --> F4
    
    style A1 fill:#42A5F5,stroke:#1976D2,stroke-width:3px,color:#000
    style A2 fill:#64B5F6,stroke:#1976D2,stroke-width:2px,color:#000
    style A3 fill:#64B5F6,stroke:#1976D2,stroke-width:2px,color:#000
    style B1 fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    style B2 fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    style B3 fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    style C1 fill:#AB47BC,stroke:#7B1FA2,stroke-width:3px,color:#fff
    style C2 fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px,color:#fff
    style C3 fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px,color:#fff
    style D1 fill:#26A69A,stroke:#00695C,stroke-width:2px,color:#fff
    style D2 fill:#26A69A,stroke:#00695C,stroke-width:2px,color:#fff
    style D3 fill:#26A69A,stroke:#00695C,stroke-width:2px,color:#fff
    style E1 fill:#66BB6A,stroke:#388E3C,stroke-width:2px,color:#000
    style E2 fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style E3 fill:#66BB6A,stroke:#388E3C,stroke-width:2px,color:#000
    style F1 fill:#EC407A,stroke:#C2185B,stroke-width:2px,color:#fff
    style F2 fill:#EC407A,stroke:#C2185B,stroke-width:2px,color:#fff
    style F3 fill:#EC407A,stroke:#C2185B,stroke-width:2px,color:#fff
    style F4 fill:#EC407A,stroke:#C2185B,stroke-width:3px,color:#fff
    style Dados fill:#E3F2FD,stroke:#42A5F5,stroke-width:4px,color:#000
    style Prep fill:#FFF3E0,stroke:#FFB74D,stroke-width:4px,color:#000
    style Train fill:#F3E5F5,stroke:#AB47BC,stroke-width:4px,color:#000
    style Eval fill:#E0F2F1,stroke:#26A69A,stroke-width:4px,color:#000
    style Deploy fill:#E8F5E9,stroke:#66BB6A,stroke-width:4px,color:#000
    style Infer fill:#FCE4EC,stroke:#EC407A,stroke-width:4px,color:#000
```

### Como Treinar um Modelo

**1. Preparar dados de treino (CSV):**
```csv
competition,offices,schools,parks,transit,flow_kde,mix,street_centrality,target
12,45,2,1,8,25.3,0.72,0.15,68.5
5,120,5,3,15,42.1,0.85,0.42,85.2
...
```

**2. Executar script de treino:**
```bash
python backend-python/app/ml/train.py \
  --csv dados_restaurantes.csv \
  --business_type restaurante \
  --out backend-python/app/models_store
```

**3. Modelo salvo automaticamente:**
- `models_store/restaurante.joblib`
- Será carregado automaticamente pela API

**4. Treino por segmento (opcional):**
```bash
python backend-python/app/ml/train.py \
  --csv dados_restaurantes_premium.csv \
  --business_type restaurante \
  --segment premium \
  --out backend-python/app/models_store
```
Gera: `models_store/restaurante_premium.joblib`

### Algoritmo: Gradient Boosting Regressor

**Parâmetros padrão:**
```python
GradientBoostingRegressor(
    n_estimators=100,        # Número de árvores
    learning_rate=0.1,       # Taxa de aprendizado
    max_depth=3,             # Profundidade das árvores
    random_state=42,
    loss='squared_error'
)
```

**Features utilizadas (ordem fixa):**
```python
['competition', 'offices', 'schools', 'parks', 
 'transit', 'flow_kde', 'mix', 'street_centrality']
```

**Target:** Score 0-100 (pode ser faturamento normalizado, footfall, ou métrica de sucesso)

---

## ⚡ Cache e Performance

### Estratégia de Cache Multi-Camadas

```mermaid
graph TB
    subgraph Client["👤 Cliente"]
        A["Requisições HTTP<br/>GET/POST"]
    end
    
    subgraph Redis["💾 L1: Redis Cache"]
        B1["Overpass Queries<br/>🕐 TTL: 7 dias"]
        B2["Geocoding<br/>🕐 TTL: 24 horas"]
        B3["Rate Limit Counters<br/>🕐 TTL: 60s"]
    end
    
    subgraph Memory["⚡ L2: Application Cache"]
        C1["ML Models<br/>🧠 Memory"]
        C2["GTFS Data<br/>🚇 Memory"]
    end
    
    subgraph DB["🗄️ L3: PostgreSQL"]
        D1["Projects<br/>💾 Persistente"]
        D2["Audit Logs<br/>📊 Persistente"]
    end
    
    subgraph External["🌐 External APIs"]
        E1["Overpass API<br/>🗺️ OpenStreetMap"]
        E2["Nominatim<br/>📍 Geocoding"]
    end
    
    A --> B1 & B2 & B3
    B1 -->|Cache Miss| E1
    B2 -->|Cache Miss| E2
    E1 -.->|Cache Write| B1
    E2 -.->|Cache Write| B2
    C1 -.->|Load once| Disk
    C2 -.->|Load once| Disk
    A --> D1 & D2
    
    style A fill:#4FC3F7,stroke:#0288D1,stroke-width:3px,color:#000
    
    style B1 fill:#FFA726,stroke:#F57C00,stroke-width:3px,color:#000
    style B2 fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    style B3 fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    
    style C1 fill:#9575CD,stroke:#512DA8,stroke-width:3px,color:#fff
    style C2 fill:#9575CD,stroke:#512DA8,stroke-width:3px,color:#fff
    
    style D1 fill:#42A5F5,stroke:#1976D2,stroke-width:3px,color:#000
    style D2 fill:#42A5F5,stroke:#1976D2,stroke-width:3px,color:#000
    
    style E1 fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    style E2 fill:#66BB6A,stroke:#388E3C,stroke-width:3px,color:#000
    
    style Client fill:#E1F5FE,stroke:#4FC3F7,stroke-width:4px,color:#000
    style Redis fill:#FFF3E0,stroke:#FFA726,stroke-width:4px,color:#000
    style Memory fill:#F3E5F5,stroke:#9575CD,stroke-width:4px,color:#000
    style DB fill:#E3F2FD,stroke:#42A5F5,stroke-width:4px,color:#000
    style External fill:#E8F5E9,stroke:#66BB6A,stroke-width:4px,color:#000
```

### Implementação do Cache

**Redis Cache (TTL 7 dias):**
```python
# core/cache.py
def make_cache_key(namespace: str, query: dict) -> str:
    payload = json.dumps(query, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return f"{namespace}:{h}"

def set_cache(namespace: str, query: dict, data, ttl_seconds: int = 604800):
    key = make_cache_key(namespace, query)
    r.setex(key, ttl_seconds, json.dumps(data, ensure_ascii=False))
```

**Key Pattern:**
```
overpass:a3f2b8c1d4e5f6... → {GeoJSON data}
geocode:rua+paulista+sp    → {lat, lon, display_name}
rate_limit:user:sub123     → 45 (contador)
```

### Otimizações Implementadas

1. **Consultas Paralelas (asyncio):**
   ```python
   comp_json, poi_json, transit_json = await asyncio.gather(
       fetch_overpass(q_comp),
       fetch_overpass(q_pois),
       fetch_overpass(q_tran)
   )
   ```

2. **Retry com Exponential Backoff (Tenacity):**
   ```python
   @retry(
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=1, min=2, max=20),
       retry=retry_if_exception_type(OverpassError)
   )
   async def fetch_overpass(query: str):
       # ...
   ```

3. **Projeção EPSG:3857 para cálculos métricos:**
   ```python
   gdf_m = gdf.to_crs(3857)  # Web Mercator (metros)
   ```

4. **Spatial Indexing (Rtree via GeoPandas)**

---

## 🔐 Segurança e Rate Limiting

### Autenticação JWT/JWKS

```mermaid
sequenceDiagram
    participant C as Cliente
    participant A as API
    participant Auth as Auth Provider<br/>(Auth0/Keycloak)
    participant Redis as Redis
    
    C->>Auth: Login
    Auth-->>C: JWT Token
    
    C->>A: Request + Bearer Token
    A->>A: Decode JWT header
    A->>Auth: Fetch JWKS keys<br/>(cached 1h)
    Auth-->>A: Public keys
    A->>A: Verify signature<br/>+ claims (aud, iss, exp)
    
    alt Token válido
        A->>Redis: Check rate limit
        alt Quota OK
            A->>A: Process request
            A-->>C: 200 Response
        else Quota excedida
            A-->>C: 429 Too Many Requests
        end
    else Token inválido
        A-->>C: 401 Unauthorized
    end
```

**Variáveis de ambiente:**
```bash
AUTH_JWKS_URL=https://your-auth0.auth0.com/.well-known/jwks.json
AUTH_AUDIENCE=sitescore-api
AUTH_ISSUER=https://your-auth0.auth0.com/
```

### Rate Limiting (Redis)

**Quotas implementadas:**
- **Por usuário (autenticado):** 60 requisições/minuto
- **Overpass calls:** Contador separado por usuário
- **TTL:** 60 segundos (janela deslizante)

**Implementação:**
```python
# core/rate_limit.py
def enforce_quota(user_sub: str, limit_per_minute: int = 60):
    key = f"rate_limit:user:{user_sub}"
    current = r.get(key)
    if current and int(current) >= limit_per_minute:
        raise HTTPException(status_code=429, detail="Quota excedida")
    r.incr(key)
    r.expire(key, 60)
```

### Auditoria de Uso

Todas as chamadas à Overpass API são registradas:
```python
# models/overpass_audit.py
class OverpassAudit(Base):
    id: int
    user_sub: str
    query: str
    bbox: str
    status: str  # 'success' | 'error'
    timestamp: datetime
```

**Consulta de audit logs:**
```sql
SELECT user_sub, COUNT(*) as calls, 
       DATE(timestamp) as date
FROM overpass_audit
GROUP BY user_sub, date
ORDER BY date DESC, calls DESC;
```

---

## 🚀 Como Executar

### Pré-requisitos

- Docker & Docker Compose
- 4GB RAM mínimo (8GB recomendado)
- Portas livres: 3000, 8000, 5432, 6379, 9090, 3001

### Passo a Passo

**1. Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/sitescore-ai-saas-pro.git
cd sitescore-ai-saas-pro
```

**2. Configure variáveis de ambiente:**
```bash
cp .env.example .env
```

Edite `.env`:
```bash
# Database
POSTGRES_DB=sitescore
POSTGRES_USER=postgres
POSTGRES_PASSWORD=senha_forte_aqui

# Redis
REDIS_URL=redis://redis:6379/0

# API
OVERPASS_URL=https://overpass-api.de/api/interpreter
CORS_ORIGINS=http://localhost:3000

# Auth (opcional, comentar para desabilitar)
# AUTH_JWKS_URL=https://your-auth0.auth0.com/.well-known/jwks.json
# AUTH_AUDIENCE=sitescore-api
# AUTH_ISSUER=https://your-auth0.auth0.com/

# GTFS (opcional)
# GTFS_ZIP_PATH=/path/to/gtfs.zip
```

**3. Suba os serviços:**
```bash
docker compose up --build
```

Ou use o Makefile:
```bash
make up
```

**4. Aguarde inicialização (~30s):**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

**5. Acesse a aplicação:**
Abra http://localhost:3000 no navegador.

### Comandos Úteis (Makefile)

```bash
make up          # Sobe todos os serviços
make down        # Para todos os serviços
make logs        # Mostra logs
make test        # Roda testes (pytest)
make seed        # Alimenta banco com dados de exemplo
make gtfs GTFS=/path/to/feed.zip  # Importa dados GTFS
```

### Docker Compose Services

```yaml
services:
  db:           # PostgreSQL 16 + PostGIS 3.4
  redis:        # Redis 7
  backend:      # FastAPI (port 8000)
  frontend:     # Nuxt 3 (port 3000)
  prometheus:   # Prometheus (port 9090)
  grafana:      # Grafana (port 3001)
```

---

## 📈 Observabilidade

### Métricas Prometheus

**Endpoint:** http://localhost:8000/metrics

**Métricas coletadas:**
- `http_requests_total` - Total de requisições HTTP
- `http_request_duration_seconds` - Latência de requisições
- `overpass_api_calls_total` - Chamadas à Overpass API
- `cache_hits_total` / `cache_misses_total` - Taxa de cache hit
- `active_users` - Usuários ativos
- `score_calculations_total` - Total de scores calculados

### Grafana Dashboards

**URL:** http://localhost:3001 (admin/admin)

**Dashboards pré-configurados:**
1. **API Performance**
   - Request rate (req/s)
   - P95/P99 latency
   - Error rate

2. **Cache Performance**
   - Hit rate %
   - Memory usage
   - TTL distribution

3. **Overpass Usage**
   - Calls per minute
   - Average response time
   - Quota consumption

4. **ML Model Performance**
   - Predictions/minute
   - Model load time
   - Feature distribution

### Exemplo de Query PromQL

**Taxa de requisições por endpoint:**
```promql
rate(http_requests_total[5m])
```

**Cache hit rate:**
```promql
sum(rate(cache_hits_total[5m])) / 
(sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m])))
```

---

## 🗺️ Overpass API – Queries e Boas Práticas

### Exemplos de Queries Implementadas

#### 1. Concorrentes (Restaurantes)
```overpassql
[out:json][timeout:180];
(
  node["amenity"="restaurant"](S,W,N,E);
  way["amenity"="restaurant"](S,W,N,E);
  relation["amenity"="restaurant"](S,W,N,E);
  
  node["amenity"="fast_food"](S,W,N,E);
  way["amenity"="fast_food"](S,W,N,E);
  relation["amenity"="fast_food"](S,W,N,E);
  
  node["amenity"="cafe"](S,W,N,E);
  way["amenity"="cafe"](S,W,N,E);
  relation["amenity"="cafe"](S,W,N,E);
);
out tags center;
```

#### 2. Transporte Público
```overpassql
[out:json][timeout:180];
(
  node["highway"="bus_stop"](S,W,N,E);
  way["highway"="bus_stop"](S,W,N,E);
  
  node["public_transport"="platform"](S,W,N,E);
  way["public_transport"="platform"](S,W,N,E);
  
  node["railway"="station"](S,W,N,E);
  way["railway"="station"](S,W,N,E);
  
  node["railway"="stop"](S,W,N,E);
  node["railway"="subway_entrance"](S,W,N,E);
  
  node["amenity"="bus_station"](S,W,N,E);
  way["amenity"="bus_station"](S,W,N,E);
);
out tags center;
```

#### 3. POIs (Escritórios, Escolas, Parques)
```overpassql
[out:json][timeout:180];
(
  node["office"](S,W,N,E);
  way["office"](S,W,N,E);
  
  node["amenity"="school"](S,W,N,E);
  way["amenity"="school"](S,W,N,E);
  
  node["amenity"="university"](S,W,N,E);
  way["amenity"="university"](S,W,N,E);
  
  node["leisure"="park"](S,W,N,E);
  way["leisure"="park"](S,W,N,E);
  
  node["shop"](S,W,N,E);
  way["shop"](S,W,N,E);
);
out tags center;
```

### Estratégia de Caching

**Cache key pattern:**
```
overpass:{sha1(query+bbox)} → {GeoJSON response}
TTL: 604800 segundos (7 dias)
```

**Vantagens:**
- Reduz latência de ~5s para ~10ms (cache hit)
- Diminui carga na Overpass API pública
- Evita throttling/rate limiting
- Economiza banda

### Tags por Tipo de Negócio

| Business Type | Tags OSM | Uso |
|---------------|----------|-----|
| `restaurante` | `amenity=restaurant`, `amenity=fast_food`, `amenity=cafe` | Análise de concorrência |
| `academia` | `leisure=fitness_centre`, `sport=fitness` | Análise de concorrência |
| `varejo_moda` | `shop=clothes`, `shop=shoes`, `shop=boutique`, `shop=fashion` | Análise de concorrência |

---

## 🧪 Testes

### Executar Testes

```bash
# Via Docker
docker compose run backend pytest

# Via Makefile
make test

# Localmente (com venv)
cd backend-python
pytest -v
```

### Cobertura de Testes

```bash
pytest --cov=app --cov-report=html
```

### Estrutura de Testes

```
backend-python/app/tests/
├─ test_features.py       # Testes de extração geoespacial
├─ test_scoring.py        # Testes do modelo de scoring
├─ test_api.py            # Testes de endpoints
└─ README.md              # Documentação de testes
```

**Exemplos de testes implementados:**
- `test_count_within_radius()` - Validação de contagem em raio
- `test_nearest_distance_meters()` - Cálculo de distâncias
- `test_kde_value()` - Kernel Density Estimation
- `test_entropy_mix()` - Cálculo de entropia
- `test_compute_score()` - Scoring baseline

---

## 🚇 Integração GTFS (Transporte Público)

### O que é GTFS?

GTFS (General Transit Feed Specification) é o formato padrão para dados de transporte público. Integrar GTFS ao SiteScore AI melhora significativamente a precisão da análise de acessibilidade.

### Dados Incluídos
- ✅ Paradas de ônibus, metrô, trem
- ✅ Rotas e itinerários
- ✅ Horários de operação
- ✅ Frequência de viagens (trips/hora)

### Como Importar GTFS

**1. Baixar dados GTFS**

**Brasil:**
- **São Paulo (SPTrans)**: https://www.sptrans.com.br/desenvolvedores/
- **Rio de Janeiro**: https://www.data.rio/
- **Outras cidades**: https://transitfeeds.com/l/165-brazil

**Internacional:**
- **Mobility Database**: https://mobilitydatabase.org/
- **TransitFeeds**: https://transitfeeds.com/

**2. Validar GTFS**
```bash
make gtfs GTFS=/path/to/feed.zip --validate-only
```

**3. Importar para o banco**
```bash
# Via Makefile (recomendado)
make gtfs GTFS=/path/to/sao-paulo-gtfs.zip

# Ou via Docker
docker compose exec backend python app/scripts/ingest_gtfs.py \
  --gtfs sao-paulo-gtfs.zip \
  --db $DATABASE_URL
```

**4. Configurar no `.env`**
```bash
USE_GTFS=true
GTFS_ZIP_PATH=/app/data/gtfs.zip
```

**5. Reiniciar backend**
```bash
docker compose restart backend
```

### Melhorias com GTFS

Com GTFS importado, o sistema calcula:

| Métrica | Sem GTFS | Com GTFS |
|---------|----------|----------|
| **Contagem de paradas** | Simples contagem | Ponderada por frequência |
| **Transit score** | Baseado em proximidade | Baseado em acessibilidade real |
| **Flow KDE** | Proxy genérico | Considera viagens/hora |
| **Peso de parada** | Todas iguais | Proporcional ao movimento |

**Exemplo:**
- Parada com 5 viagens/hora: peso 1.0
- Parada com 50 viagens/hora: peso 10.0

### Estrutura de Dados

**Tabela `gtfs_stops`:**
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
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Queries úteis:**
```sql
-- Paradas mais movimentadas
SELECT stop_name, trips_per_hour
FROM gtfs_stops
ORDER BY trips_per_hour DESC
LIMIT 10;

-- Paradas em 500m de um ponto
SELECT COUNT(*) 
FROM gtfs_stops
WHERE ST_DWithin(
    geom,
    ST_SetSRID(ST_MakePoint(-46.6333, -23.5505), 4326)::geography,
    500
);
```

### Atualização Periódica

GTFS deve ser atualizado mensalmente/trimestralmente:
```bash
# Baixar novo feed
wget https://exemplo.com/gtfs-novo.zip

# Re-importar (UPSERT automático)
make gtfs GTFS=gtfs-novo.zip
```

**📚 Documentação Completa:** Veja [docs/GTFS_SETUP.md](docs/GTFS_SETUP.md)

---

## 🛣️ Roadmap e Features Implementadas

### ✅ Implementado

- [x] **Core Scoring Engine**
  - [x] Extração de 9 features geoespaciais básicas
  - [x] Modelo baseline explicável com pesos por business_type
  - [x] Suporte a 5 tipos de negócio (restaurante, academia, varejo_moda, cafeteria, farmácia)
  - [x] Sistema de contribuições por feature (top 3)
  - [x] Normalização e cálculo de score 0-100
  
- [x] **Análise Avançada**
  - [x] **Endpoint `/advanced`** - 9 dimensões de análise urbana
  - [x] Walkability score (caminhabilidade)
  - [x] Cyclability (infraestrutura para bicicletas)
  - [x] Green spaces score (áreas verdes)
  - [x] Parking availability
  - [x] Safety infrastructure
  - [x] Lighting score (iluminação pública)
  - [x] Building density
  - [x] Street connectivity
  - [x] Amenity diversity
  - [x] Overall score com rating (Excelente/Bom/Regular)
  - [x] Top 3 pontos fortes e fracos
  
- [x] **Análise Demográfica**
  - [x] **Endpoint `/demographics`** - Perfil do público
  - [x] Identificação de 5 perfis: Corporativo, Estudantes, Varejo Intenso, Polo de Saúde, Residencial
  - [x] Categorização automática de POIs
  - [x] Percentual de cada perfil
  - [x] Características por perfil
  - [x] Oportunidades de negócio por perfil
  - [x] Insights automáticos
  
- [x] **Cache e Performance**
  - [x] Redis cache multi-camada (Overpass, Geocoding)
  - [x] TTL configurável (7 dias Overpass / 24h Geocoding)
  - [x] Consultas paralelas com asyncio.gather
  - [x] Retry com exponential backoff (Tenacity)
  - [x] Cache key SHA1 hash
  - [x] Cache hit/miss tracking
  
- [x] **Machine Learning**
  - [x] Pipeline de treino completo (train.py)
  - [x] Gradient Boosting Regressor
  - [x] Auto-load de modelos (.joblib)
  - [x] Suporte a segmentação (business_type + segment)
  - [x] Métricas: R², MAE, RMSE
  - [x] Feature importance
  - [x] Fallback para modelo baseline
  
- [x] **Segurança e Auth**
  - [x] JWT/JWKS authentication completo
  - [x] Rate limiting por usuário (60 req/min)
  - [x] Auditoria de uso Overpass (tabela overpass_audit)
  - [x] CORS configurável
  - [x] Middleware de autenticação
  - [x] User tracking por sub
  
- [x] **Observabilidade**
  - [x] Prometheus metrics integration
  - [x] 4 Grafana dashboards pré-configurados
  - [x] Healthcheck endpoint
  - [x] Logging estruturado
  - [x] Request/response tracking
  - [x] Cache hit rate metrics
  - [x] Overpass API call metrics
  
- [x] **Geolocalização**
  - [x] Geocoding via Nominatim (cached)
  - [x] **Suporte completo a GTFS** (script ingest_gtfs.py)
  - [x] Importação de stops com frequência
  - [x] Tabela gtfs_stops com geometrias
  - [x] Street centrality via osmnx
  - [x] Análise de redes viárias
  
- [x] **Frontend - Visualização**
  - [x] **Mapa interativo** (MapLibre GL JS)
  - [x] **Comparador de locais** (até 3 locais lado a lado)
  - [x] **Dashboard de projetos** salvos
  - [x] **GaugeChart** (semi-circular score display)
  - [x] **RadarChart** (multi-dimensional features)
  - [x] **AdvancedAnalysisPanel** (9 dimensões)
  - [x] **DemographicsPanel** (perfis de público)
  - [x] **ScoreBadge** (classificação visual)
  - [x] **POIPopup** (detalhes ao clicar)
  - [x] Visualização de 4 layers (competition, POIs, transit, flow)
  - [x] Heatmap de fluxo (KDE)
  
- [x] **Frontend - UX**
  - [x] **Dark Mode** (toggle com persistência)
  - [x] **Toast notifications** (success/error/warning/info)
  - [x] **LoadingSpinner** e **SkeletonCard**
  - [x] Sistema de notificações não-intrusivo
  - [x] Preferência de sistema respeitada
  - [x] LocalStorage persistence
  
- [x] **Frontend - Funcionalidades**
  - [x] **Exportação JSON/CSV** (useExport composable)
  - [x] **Busca de endereços** (geocoding)
  - [x] **Desenho de polígonos** no mapa
  - [x] **Clique no mapa** para análise
  - [x] **Salvar projetos** (CRUD completo)
  - [x] **Comparação multi-local** (página /compare)
  - [x] **Análise avançada** integrada
  - [x] **Perfil demográfico** integrado
  
- [x] **Infraestrutura**
  - [x] Docker Compose completo (6 services)
  - [x] PostgreSQL 16 + PostGIS 3.4
  - [x] Redis 7
  - [x] Prometheus + Grafana
  - [x] Makefile com 10+ comandos úteis
  - [x] Auto-provisioning de dashboards
  - [x] Healthchecks em todos os services
  
- [x] **Scripts e Automação**
  - [x] **seed.py** - Seeds de dados de exemplo
  - [x] **ingest_gtfs.py** - Importação GTFS completa
  - [x] **train.py** - Pipeline de ML
  - [x] Validação de GTFS
  - [x] UPSERT automático de dados
  
- [x] **Documentação**
  - [x] README principal completo
  - [x] **docs/GTFS_SETUP.md** - Guia GTFS detalhado
  - [x] **app/ml/README.md** - Documentação ML
  - [x] **app/tests/README.md** - Guia de testes
  - [x] Diagramas Mermaid (8+ fluxogramas)
  - [x] Exemplos de código
  - [x] Guias de instalação

### 🚧 Próximos Passos (Sugestões)

- [ ] **Expansão de Features**
  - [ ] Análise de horário de pico
  - [ ] Dados demográficos (renda média)
  - [ ] Análise de aluguéis (scrapers)
  - [ ] Histórico de estabelecimentos fechados
  
- [ ] **ML Avançado**
  - [ ] XGBoost/LightGBM
  - [ ] SHAP values para explainability
  - [ ] Ensemble de modelos
  - [ ] Online learning
  
- [ ] **UI/UX**
  - [ ] Comparação lado-a-lado
  - [ ] Exportação de relatórios PDF
  - [ ] Heatmaps 3D
  - [ ] Mobile app (React Native)
  
- [ ] **Integrações**
  - [ ] Google Places API
  - [ ] Waze data
  - [ ] Instagram location data
  - [ ] Webhook notifications

---

## 📄 Licença

MIT License

Copyright (c) 2025 SiteScore AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 📊 Resumo do Projeto

### Estatísticas Gerais

| Categoria | Quantidade | Detalhes |
|-----------|------------|----------|
| **Backend Endpoints** | 8 | `/score`, `/advanced`, `/demographics`, `/geocode`, `/layers/*`, `/projects`, `/health` |
| **Features Geoespaciais** | 9 | competition, offices, schools, parks, transit, flow_kde, mix, street_centrality, dist_transit |
| **Análises Avançadas** | 9 dimensões | walkability, cyclability, green_spaces, parking, safety, lighting, density, connectivity, diversity |
| **Perfis Demográficos** | 5 tipos | Corporativo, Estudantes, Varejo Intenso, Polo de Saúde, Residencial/Misto |
| **Componentes Vue** | 11 | MapView, AdvancedAnalysisPanel, DemographicsPanel, GaugeChart, RadarChart, ScoreBadge, POIPopup, LoadingSpinner, SkeletonCard, ToastContainer, DarkModeToggle |
| **Composables** | 5 | useApi, useMapLayers, useDarkMode, useExport, useToast |
| **Páginas Frontend** | 3 | Mapa Principal (`/`), Dashboard (`/dashboard`), Comparador (`/compare`) |
| **Tipos de Negócio** | 5 | Restaurante, Academia, Varejo de Moda, Cafeteria, Farmácia |
| **Métricas Prometheus** | 6+ | requests_total, duration_seconds, overpass_calls, cache_hits, cache_misses, active_users |
| **Dashboards Grafana** | 4 | API Performance, Cache Performance, Overpass Usage, ML Model Performance |
| **Comandos Makefile** | 10+ | up, down, logs, test, seed, gtfs, metrics, clean, backend, frontend |
| **Scripts Utilitários** | 3 | seed.py, ingest_gtfs.py, train.py |
| **Documentos** | 4 | README.md, docs/GTFS_SETUP.md, app/ml/README.md, app/tests/README.md |

### Capacidades do Sistema

#### 🎯 O que o usuário PODE fazer:

**Análise de Localização:**
- ✅ Clicar no mapa para analisar qualquer ponto
- ✅ Buscar endereço via geocoding
- ✅ Desenhar polígonos customizados
- ✅ Escolher entre 5 tipos de negócio
- ✅ Ver score 0-100 com explicação
- ✅ Visualizar top 3 features que mais contribuíram

**Análise Avançada:**
- ✅ Ver 9 dimensões de qualidade urbana
- ✅ Identificar pontos fortes (top 3)
- ✅ Identificar pontos de atenção (top 3)
- ✅ Expandir dados detalhados (raw counts)
- ✅ Rating automático (Excelente/Muito Bom/Bom/Regular/Baixo)

**Perfil Demográfico:**
- ✅ Identificar perfis de público predominantes
- ✅ Ver percentual de cada perfil
- ✅ Entender características do público
- ✅ Receber sugestões de oportunidades de negócio
- ✅ Insights automáticos por perfil

**Comparação:**
- ✅ Comparar até 3 localizações lado a lado
- ✅ Tabela comparativa feature por feature
- ✅ Identificação automática da melhor localização
- ✅ Destacar melhor local por feature
- ✅ Remover e adicionar locais dinamicamente

**Gerenciamento:**
- ✅ Salvar projetos com nome personalizado
- ✅ Dashboard de projetos salvos
- ✅ Filtrar e ordenar projetos
- ✅ Re-analisar localizações
- ✅ Editar e deletar projetos
- ✅ Exportar para JSON/CSV

**Visualização:**
- ✅ Mapa interativo com 4 layers (competition, POIs, transit, flow)
- ✅ Heatmap de fluxo (KDE)
- ✅ Popup com detalhes de POIs
- ✅ Gráficos: Gauge (semi-circular), Radar (multi-dimensional)
- ✅ Dark mode com detecção de preferência do sistema
- ✅ Notificações toast não-intrusivas

**Exportação:**
- ✅ Exportar análise completa em JSON
- ✅ Exportar lista de projetos em CSV
- ✅ Download automático via browser

### Fluxo Completo de Possibilidades

```mermaid
graph TB
    Start[👤 Usuário acessa SiteScore AI] --> Map[🗺️ Mapa Principal]
    
    Map --> A1[🖱️ Clique no mapa]
    Map --> A2[🔍 Busca endereço]
    Map --> A3[✏️ Desenha polígono]
    Map --> A4[📊 Vai para Dashboard]
    Map --> A5[⚖️ Vai para Comparador]
    
    A1 --> Business[🏢 Seleciona tipo negócio]
    A2 --> Business
    A3 --> Business
    
    Business --> Analyze[📊 Analisa]
    
    Analyze --> Basic[Score Básico 0-100]
    Basic --> B1[📊 Análise Avançada<br/>9 dimensões]
    Basic --> B2[👥 Perfil Demográfico<br/>5 perfis]
    Basic --> B3[💾 Salva Projeto]
    Basic --> B4[📥 Exporta JSON/CSV]
    Basic --> B5[🗺️ Visualiza Layers]
    
    B1 --> B1a[Walkability, Cyclability<br/>Green Spaces, etc.]
    B1a --> B1b[Top 3 Fortes/Fracos]
    B1b --> B1c[Rating Automático]
    
    B2 --> B2a[Corporativo 35%<br/>Estudantes 25%<br/>Varejo 40%]
    B2a --> B2b[Características]
    B2b --> B2c[Oportunidades de Negócio]
    B2c --> B2d[Insights Automáticos]
    
    B3 --> Dashboard[📊 Dashboard]
    A4 --> Dashboard
    
    Dashboard --> D1[📋 Lista Projetos]
    D1 --> D2[🔍 Filtrar/Ordenar]
    D1 --> D3[🔄 Re-analisar]
    D1 --> D4[✏️ Editar]
    D1 --> D5[🗑️ Deletar]
    D1 --> D6[⚖️ Comparar]
    
    A5 --> Compare[⚖️ Comparador]
    D6 --> Compare
    
    Compare --> C1[📍 Local 1]
    Compare --> C2[📍 Local 2]
    Compare --> C3[📍 Local 3 opcional]
    
    C1 --> CompResult[📊 Análise Paralela]
    C2 --> CompResult
    C3 --> CompResult
    
    CompResult --> CR1[📊 Tabela Comparativa]
    CR1 --> CR2[🏆 Melhor Local]
    CR2 --> CR3[💡 Insights]
    CR3 --> CR4[💾 Salvar Vencedor]
    
    B5 --> L1[🏪 Competition Layer]
    B5 --> L2[🏢 POIs Layer]
    B5 --> L3[🚇 Transit Layer]
    B5 --> L4[🌊 Flow Heatmap]
    
    style Start fill:#4FC3F7,stroke:#0288D1,stroke-width:4px,color:#000
    style Map fill:#66BB6A,stroke:#388E3C,stroke-width:4px,color:#000
    style Basic fill:#9C27B0,stroke:#7B1FA2,stroke-width:4px,color:#fff
    style B1 fill:#FF9800,stroke:#F57C00,stroke-width:3px,color:#000
    style B2 fill:#F44336,stroke:#C62828,stroke-width:3px,color:#fff
    style Dashboard fill:#2196F3,stroke:#1976D2,stroke-width:4px,color:#fff
    style Compare fill:#FFC107,stroke:#FFA000,stroke-width:4px,color:#000
    style CR2 fill:#4CAF50,stroke:#388E3C,stroke-width:4px,color:#fff
```

### Diferenciais Técnicos

#### 🚀 Performance
- Cache Redis multi-camada (hit rate ~80%)
- Consultas paralelas (3-4 queries simultâneas)
- TTL otimizado (7 dias Overpass, 24h Geocoding)
- Retry exponencial automático
- Projeção EPSG:3857 para cálculos métricos precisos

#### 🧠 Inteligência
- Modelo ML com fallback explicável
- 9 features geoespaciais engineered
- Pesos customizados por business_type
- Análise demográfica automatizada
- Insights contextuais por perfil

#### 🎨 UX/UI
- Design moderno com Tailwind CSS
- Dark mode inteligente (sistema + localStorage)
- Notificações não-intrusivas
- Loading states (spinner + skeleton)
- Visualizações interativas (Chart.js)

#### 🔒 Segurança e Confiabilidade
- Autenticação JWT/JWKS
- Rate limiting por usuário
- Auditoria completa de API calls
- CORS configurável
- Healthchecks em todos os services

#### 📊 Observabilidade
- 6+ métricas Prometheus
- 4 dashboards Grafana pré-configurados
- Tracking de cache hit/miss
- Monitoring de latência (P95/P99)
- Logs estruturados

#### 🗺️ Dados Geoespaciais
- OpenStreetMap via Overpass API
- PostGIS para queries espaciais
- GTFS para transporte real
- GeoPandas para análise
- OSMnx para redes viárias

### Como o Sistema se Destaca

| Aspecto | Solução Tradicional | SiteScore AI |
|---------|---------------------|--------------|
| **Análise** | Básica (1-2 métricas) | **9 dimensões + demografia** |
| **Dados** | Estáticos | **OSM (atualizado diariamente)** |
| **Transporte** | Apenas contagem | **GTFS com frequência real** |
| **Explicabilidade** | Caixa preta | **Top 3 features + pesos** |
| **Comparação** | Manual | **Lado a lado automático** |
| **Perfil Público** | Não disponível | **5 perfis + oportunidades** |
| **Cache** | Sem cache | **Redis multi-camada** |
| **Performance** | Lenta (10-30s) | **Rápida (3-5s cached)** |
| **Visualização** | Tabelas | **Mapas + Gráficos interativos** |
| **Exportação** | Não disponível | **JSON/CSV pronto** |
| **Dark Mode** | Não disponível | **Com detecção de sistema** |
| **Observabilidade** | Logs básicos | **Prometheus + Grafana** |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Guidelines

- Mantenha o código limpo e documentado
- Adicione testes para novas features
- Siga o style guide (PEP 8 para Python)
- Atualize o README se necessário

---

## 🙏 Agradecimentos

- **OpenStreetMap Contributors** - Dados geoespaciais
- **Overpass API** - Query engine OSM
- **FastAPI Community** - Framework web
- **GeoPandas Team** - Análise geoespacial
- **Scikit-learn** - Machine learning toolkit

---

<div align="center">

[⬆️ Voltar ao topo](#sitescore-ai-)

</div>

