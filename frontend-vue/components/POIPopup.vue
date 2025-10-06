<template>
  <div class="bg-white rounded-xl shadow-2xl border-2 border-slate-200 overflow-hidden max-w-sm animate-scale-in">
    <!-- Header -->
    <div class="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3 flex items-start justify-between">
      <div class="flex-1">
        <h3 class="text-white font-bold text-lg leading-tight">
          {{ poi.name || poi.tags?.name || getType(poi) || 'Ponto de Interesse' }}
        </h3>
        <p class="text-indigo-100 text-xs mt-1">{{ getCategory(poi) }}</p>
      </div>
      <button @click="$emit('close')" class="text-white hover:bg-white/20 rounded-full w-6 h-6 flex items-center justify-center transition-all">
        ×
      </button>
    </div>

    <!-- Content -->
    <div class="p-4 space-y-3 max-h-96 overflow-y-auto">
      <!-- Tipo -->
      <div v-if="poi.tags" class="flex items-start gap-2">
        <div class="text-indigo-600 text-lg">🏷️</div>
        <div class="flex-1">
          <div class="text-xs text-slate-500 font-semibold uppercase">Tipo</div>
          <div class="text-sm text-slate-700">{{ getType(poi) }}</div>
        </div>
      </div>

      <!-- Endereço -->
      <div v-if="getAddress(poi)" class="flex items-start gap-2">
        <div class="text-indigo-600 text-lg">📍</div>
        <div class="flex-1">
          <div class="text-xs text-slate-500 font-semibold uppercase">Endereço</div>
          <div class="text-sm text-slate-700">{{ getAddress(poi) }}</div>
        </div>
      </div>

      <!-- Telefone -->
      <div v-if="poi.tags?.phone || poi.tags?.['contact:phone']" class="flex items-start gap-2">
        <div class="text-indigo-600 text-lg">📞</div>
        <div class="flex-1">
          <div class="text-xs text-slate-500 font-semibold uppercase">Telefone</div>
          <div class="text-sm text-slate-700">{{ poi.tags.phone || poi.tags['contact:phone'] }}</div>
        </div>
      </div>

      <!-- Website -->
      <div v-if="poi.tags?.website || poi.tags?.['contact:website']" class="flex items-start gap-2">
        <div class="text-indigo-600 text-lg">🌐</div>
        <div class="flex-1">
          <div class="text-xs text-slate-500 font-semibold uppercase">Website</div>
          <a :href="poi.tags.website || poi.tags['contact:website']" target="_blank" class="text-sm text-indigo-600 hover:underline break-all">
            {{ poi.tags.website || poi.tags['contact:website'] }}
          </a>
        </div>
      </div>

      <!-- Horário -->
      <div v-if="poi.tags?.opening_hours" class="flex items-start gap-2">
        <div class="text-indigo-600 text-lg">🕐</div>
        <div class="flex-1">
          <div class="text-xs text-slate-500 font-semibold uppercase">Horário</div>
          <div class="text-sm text-slate-700 whitespace-pre-line">{{ formatHours(poi.tags.opening_hours) }}</div>
        </div>
      </div>

      <!-- Culinária (para restaurantes) -->
      <div v-if="poi.tags?.cuisine" class="flex items-start gap-2">
        <div class="text-indigo-600 text-lg">🍽️</div>
        <div class="flex-1">
          <div class="text-xs text-slate-500 font-semibold uppercase">Culinária</div>
          <div class="text-sm text-slate-700">{{ poi.tags.cuisine }}</div>
        </div>
      </div>

      <!-- Coordenadas -->
      <div class="flex items-start gap-2">
        <div class="text-indigo-600 text-lg">🎯</div>
        <div class="flex-1">
          <div class="text-xs text-slate-500 font-semibold uppercase">Coordenadas</div>
          <div class="text-xs text-slate-600 font-mono">
            {{ poi.lat?.toFixed(6) }}, {{ poi.lon?.toFixed(6) }}
          </div>
        </div>
      </div>

      <!-- Distância (se fornecida) -->
      <div v-if="distance" class="flex items-start gap-2">
        <div class="text-indigo-600 text-lg">📏</div>
        <div class="flex-1">
          <div class="text-xs text-slate-500 font-semibold uppercase">Distância</div>
          <div class="text-sm text-slate-700">{{ distance }}m do ponto de análise</div>
        </div>
      </div>

      <!-- Tags extras -->
      <details v-if="poi.tags && Object.keys(poi.tags).length > 0" class="group">
        <summary class="cursor-pointer text-xs font-semibold text-slate-600 hover:text-indigo-600 transition-colors">
          Ver todas as tags OSM ({{ Object.keys(poi.tags).length }})
        </summary>
        <div class="mt-2 space-y-1 max-h-32 overflow-y-auto">
          <div v-for="[key, value] in Object.entries(poi.tags)" :key="key" class="flex gap-2 text-xs">
            <span class="text-slate-500 font-mono">{{ key }}:</span>
            <span class="text-slate-700 break-all">{{ value }}</span>
          </div>
        </div>
      </details>
    </div>

    <!-- Footer com ações -->
    <div class="px-4 py-3 bg-slate-50 border-t border-slate-200 flex gap-2">
      <a 
        :href="`https://www.google.com/maps/search/?api=1&query=${poi.lat},${poi.lon}`"
        target="_blank"
        class="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold text-center transition-all"
      >
        🗺️ Google Maps
      </a>
      <a 
        :href="`https://www.openstreetmap.org/${poi.type}/${poi.id}`"
        target="_blank"
        class="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-semibold text-center transition-all"
      >
        🌍 Ver no OSM
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

const props = defineProps<{
  poi: any
  distance?: number
}>()

onMounted(() => {
  console.log('POIPopup montado com dados:', props.poi)
})

const getCategory = (poi: any) => {
  const tags = poi.tags || {}
  if (tags.amenity) return `Amenity: ${tags.amenity}`
  if (tags.shop) return `Shop: ${tags.shop}`
  if (tags.leisure) return `Leisure: ${tags.leisure}`
  if (tags.tourism) return `Tourism: ${tags.tourism}`
  if (tags.office) return `Office: ${tags.office}`
  if (tags.building) return `Building: ${tags.building}`
  return 'POI'
}

const getType = (poi: any) => {
  const tags = poi.tags || {}
  const types = []
  if (tags.amenity) types.push(tags.amenity)
  if (tags.shop) types.push(tags.shop)
  if (tags.leisure) types.push(tags.leisure)
  if (tags.tourism) types.push(tags.tourism)
  if (tags.office) types.push(tags.office)
  return types.join(', ') || 'Desconhecido'
}

const getAddress = (poi: any) => {
  const tags = poi.tags || {}
  const parts = []
  if (tags['addr:street']) parts.push(tags['addr:street'])
  if (tags['addr:housenumber']) parts.push(tags['addr:housenumber'])
  if (tags['addr:neighbourhood']) parts.push(tags['addr:neighbourhood'])
  if (tags['addr:city']) parts.push(tags['addr:city'])
  return parts.join(', ') || null
}

const formatHours = (hours: string) => {
  // Tentar formatar horários de forma mais legível
  return hours.replace(/;/g, '\n').replace(/,/g, ', ')
}
</script>

<style scoped>
.animate-scale-in {
  animation: scaleIn 0.2s ease-out;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>

