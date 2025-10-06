<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h1 class="text-3xl font-bold text-slate-800">Comparador de Locais</h1>
            <p class="text-slate-600 mt-1">Compare até 3 localizações lado a lado</p>
          </div>
          <NuxtLink 
            to="/" 
            class="px-4 py-2 bg-white border-2 border-slate-300 rounded-xl font-semibold hover:bg-slate-50 transition-all"
          >
            ← Voltar ao Mapa
          </NuxtLink>
        </div>
      </div>

      <!-- Comparison Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div 
          v-for="(location, index) in locations" 
          :key="index"
          class="bg-white rounded-2xl shadow-xl border-2 border-slate-200 p-6 relative"
        >
          <button 
            v-if="location.score"
            @click="removeLocation(index)"
            class="absolute top-4 right-4 w-8 h-8 bg-red-500 text-white rounded-full hover:bg-red-600 transition-all"
          >
            ×
          </button>

          <div v-if="!location.score" class="text-center py-12">
            <div class="text-6xl mb-4">📍</div>
            <h3 class="text-lg font-semibold text-slate-700 mb-4">Local {{ index + 1 }}</h3>
            <div class="space-y-3">
              <!-- Campo de busca por endereço -->
              <div class="relative">
                <input 
                  v-model="location.searchQuery" 
                  @input="searchAddress(index)"
                  placeholder="🔍 Buscar endereço..." 
                  type="text"
                  class="w-full px-4 py-2 border-2 border-indigo-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all bg-indigo-50"
                />
                
                <!-- Dropdown de resultados -->
                <div 
                  v-if="location.searchResults && location.searchResults.length > 0"
                  class="absolute z-50 w-full mt-1 bg-white border-2 border-slate-200 rounded-lg shadow-xl max-h-60 overflow-y-auto"
                >
                  <button
                    v-for="(result, idx) in location.searchResults"
                    :key="idx"
                    @click="selectAddress(index, result)"
                    class="w-full px-4 py-3 text-left hover:bg-indigo-50 transition-colors border-b border-slate-100 last:border-0"
                  >
                    <div class="text-sm font-medium text-slate-800">{{ result.display_name }}</div>
                    <div class="text-xs text-slate-500 mt-1">
                      {{ result.lat.toFixed(6) }}, {{ result.lon.toFixed(6) }}
                    </div>
                  </button>
                </div>
              </div>
              
              <!-- Divisor -->
              <div class="flex items-center gap-2 my-3">
                <div class="flex-1 border-t border-slate-300"></div>
                <span class="text-xs text-slate-500 font-semibold">OU</span>
                <div class="flex-1 border-t border-slate-300"></div>
              </div>
              
              <!-- Coordenadas manuais -->
              <input 
                v-model="location.lat" 
                placeholder="Latitude" 
                type="number"
                step="0.000001"
                class="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all"
              />
              <input 
                v-model="location.lon" 
                placeholder="Longitude" 
                type="number"
                step="0.000001"
                class="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all"
              />
              <select 
                v-model="location.businessType"
                class="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all"
              >
                <option value="restaurante">Restaurante</option>
                <option value="academia">Academia</option>
                <option value="varejo_moda">Varejo de Moda</option>
                <option value="cafeteria">Cafeteria</option>
                <option value="farmacia">Farmácia</option>
              </select>
              <button 
                @click="analyzeLocation(index)"
                :disabled="!location.lat || !location.lon"
                class="w-full px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50"
              >
                Analisar
              </button>
            </div>
          </div>

          <div v-else class="space-y-4">
            <div class="text-center mb-4">
              <ScoreBadge :score="location.score.score" />
            </div>
            
            <div class="text-center">
              <div class="text-sm text-slate-500 mb-1">{{ location.businessType }}</div>
              <div class="text-xs text-slate-400">
                {{ location.lat.toFixed(4) }}, {{ location.lon.toFixed(4) }}
              </div>
            </div>

            <div class="bg-slate-50 rounded-lg p-3">
              <div class="text-xs font-semibold text-slate-500 mb-2">TOP 3 FEATURES</div>
              <div class="space-y-1">
                <div 
                  v-for="f in location.score.features.slice(0, 3)" 
                  :key="f.name"
                  class="flex justify-between text-xs"
                >
                  <span class="text-slate-700">{{ f.name }}</span>
                  <span 
                    class="font-bold"
                    :class="f.contribution > 0 ? 'text-green-600' : 'text-red-600'"
                  >
                    {{ f.contribution?.toFixed(3) ?? '—' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Comparison Table -->
      <div v-if="hasAnyScore" class="bg-white rounded-2xl shadow-xl border-2 border-slate-200 p-6">
        <h2 class="text-xl font-bold text-slate-800 mb-6">📊 Comparação Detalhada</h2>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b-2 border-slate-200">
                <th class="text-left py-3 px-4 text-sm font-semibold text-slate-600">Feature</th>
                <th 
                  v-for="(location, index) in locations.filter(l => l.score)" 
                  :key="index"
                  class="text-center py-3 px-4 text-sm font-semibold text-slate-600"
                >
                  Local {{ index + 1 }}
                </th>
                <th class="text-center py-3 px-4 text-sm font-semibold text-indigo-600">Melhor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="featureName in allFeatureNames" :key="featureName" class="border-b border-slate-100 hover:bg-slate-50">
                <td class="py-3 px-4 text-sm font-medium text-slate-700">{{ featureName }}</td>
                <td 
                  v-for="(location, index) in locations.filter(l => l.score)" 
                  :key="index"
                  class="text-center py-3 px-4 text-sm"
                  :class="isBestForFeature(location, featureName) ? 'bg-green-50 font-bold text-green-700' : 'text-slate-600'"
                >
                  {{ getFeatureValue(location, featureName) }}
                </td>
                <td class="text-center py-3 px-4 text-sm font-bold text-indigo-600">
                  {{ getBestLocationForFeature(featureName) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Winner -->
        <div v-if="winner" class="mt-8 p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border-2 border-green-200">
          <div class="flex items-center gap-4">
            <div class="text-5xl">🏆</div>
            <div>
              <div class="text-sm text-green-600 font-semibold">MELHOR LOCALIZAÇÃO</div>
              <div class="text-2xl font-bold text-slate-800">Local {{ winner.index + 1 }}</div>
              <div class="text-sm text-slate-600 mt-1">
                Score: {{ winner.score.score.toFixed(0) }}/100 | 
                {{ winner.lat.toFixed(4) }}, {{ winner.lon.toFixed(4) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useApi } from '~/composables/useApi'

const api = useApi()

const locations = ref([
  { 
    lat: null as number | null, 
    lon: null as number | null, 
    businessType: 'restaurante', 
    score: null as any,
    searchQuery: '',
    searchResults: [] as any[]
  },
  { 
    lat: null as number | null, 
    lon: null as number | null, 
    businessType: 'restaurante', 
    score: null as any,
    searchQuery: '',
    searchResults: [] as any[]
  },
  { 
    lat: null as number | null, 
    lon: null as number | null, 
    businessType: 'restaurante', 
    score: null as any,
    searchQuery: '',
    searchResults: [] as any[]
  },
])

// Debounce para busca de endereço
let searchTimers: any[] = [null, null, null]

async function searchAddress(index: number) {
  const loc = locations.value[index]
  const query = loc.searchQuery?.trim()
  
  // Limpar timer anterior
  if (searchTimers[index]) {
    clearTimeout(searchTimers[index])
  }
  
  // Se query muito curta, limpar resultados
  if (!query || query.length < 3) {
    loc.searchResults = []
    return
  }
  
  // Debounce de 500ms
  searchTimers[index] = setTimeout(async () => {
    try {
      const results = await api.geocode(query)
      loc.searchResults = results || []
    } catch (error) {
      console.error('Erro ao buscar endereço:', error)
      loc.searchResults = []
    }
  }, 500)
}

function selectAddress(index: number, result: any) {
  const loc = locations.value[index]
  loc.lat = result.lat
  loc.lon = result.lon
  loc.searchQuery = result.display_name
  loc.searchResults = []
}

async function analyzeLocation(index: number) {
  const loc = locations.value[index]
  if (!loc.lat || !loc.lon) return
  
  try {
    const payload = {
      geometry: {
        type: 'Point',
        coordinates: [loc.lon, loc.lat]
      },
      business_type: loc.businessType,
      name: `Local ${index + 1}`
    }
    
    const result = await api.scoreLocation(payload)
    loc.score = result
  } catch (error) {
    console.error('Erro ao analisar:', error)
    alert('Erro ao analisar localização')
  }
}

function removeLocation(index: number) {
  locations.value[index] = {
    lat: null,
    lon: null,
    businessType: 'restaurante',
    score: null,
    searchQuery: '',
    searchResults: []
  }
}

const hasAnyScore = computed(() => locations.value.some(l => l.score))

const allFeatureNames = computed(() => {
  const names = new Set<string>()
  locations.value.forEach(loc => {
    if (loc.score) {
      loc.score.features.forEach((f: any) => names.add(f.name))
    }
  })
  return Array.from(names)
})

function getFeatureValue(location: any, featureName: string): string {
  if (!location.score) return '—'
  const feature = location.score.features.find((f: any) => f.name === featureName)
  return feature ? feature.contribution?.toFixed(3) ?? '—' : '—'
}

function isBestForFeature(location: any, featureName: string): boolean {
  const locationsWithScore = locations.value.filter(l => l.score)
  if (locationsWithScore.length === 0) return false
  
  const values = locationsWithScore.map(l => {
    const feature = l.score.features.find((f: any) => f.name === featureName)
    return feature ? feature.contribution || 0 : 0
  })
  
  const maxValue = Math.max(...values)
  const locationValue = parseFloat(getFeatureValue(location, featureName))
  
  return !isNaN(locationValue) && Math.abs(locationValue - maxValue) < 0.001
}

function getBestLocationForFeature(featureName: string): string {
  const locationsWithScore = locations.value.filter(l => l.score)
  if (locationsWithScore.length === 0) return '—'
  
  let bestIndex = -1
  let maxValue = -Infinity
  
  locationsWithScore.forEach((loc, idx) => {
    const feature = loc.score.features.find((f: any) => f.name === featureName)
    const value = feature ? feature.contribution || 0 : 0
    if (value > maxValue) {
      maxValue = value
      bestIndex = locations.value.indexOf(loc)
    }
  })
  
  return bestIndex >= 0 ? `Local ${bestIndex + 1}` : '—'
}

const winner = computed(() => {
  const locationsWithScore = locations.value
    .map((loc, index) => ({ ...loc, index }))
    .filter(l => l.score)
  
  if (locationsWithScore.length === 0) return null
  
  return locationsWithScore.reduce((best, current) => {
    return current.score.score > best.score.score ? current : best
  })
})
</script>

