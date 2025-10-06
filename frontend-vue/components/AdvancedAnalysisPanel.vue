<template>
  <div v-if="analysis" class="bg-white rounded-2xl p-6 shadow-xl border border-slate-200">
    <!-- Cabeçalho com Score Geral -->
    <div class="text-center mb-6 pb-6 border-b border-slate-200">
      <div class="flex items-center justify-center gap-3 mb-3">
        <span class="text-5xl">{{ analysis.rating_emoji }}</span>
        <div>
          <div class="text-5xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            {{ analysis.overall_score }}
          </div>
          <div class="text-xs text-slate-500 uppercase tracking-wide">de 100</div>
        </div>
      </div>
      <div class="text-xl font-semibold text-slate-700">{{ analysis.rating }}</div>
      <div class="text-sm text-slate-500 mt-1">Análise Completa da Localização</div>
    </div>

    <!-- Grid de Scores -->
    <div class="mb-6">
      <h3 class="text-sm font-semibold text-slate-700 uppercase tracking-wide mb-4 flex items-center gap-2">
        <span>📊</span> Análise por Categoria
      </h3>
      <div class="grid grid-cols-2 lg:grid-cols-3 gap-3">
        <div v-for="(score, key) in analysis.scores" :key="key" 
             class="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-4 hover:shadow-md transition-shadow duration-200">
          <div class="flex items-start justify-between mb-2">
            <span class="text-3xl">{{ score.emoji }}</span>
            <div class="text-right">
              <div class="text-2xl font-bold" :class="getScoreColor(score.value, score.max)">
                {{ Math.round((score.value / score.max) * 100) }}%
              </div>
              <div class="text-xs text-slate-500">{{ score.category }}</div>
            </div>
          </div>
          
          <div class="text-xs text-slate-600 font-medium mb-2 line-clamp-2">
            {{ score.description }}
          </div>
          
          <!-- Barra de Progresso -->
          <div class="w-full bg-slate-200 rounded-full h-2">
            <div 
              class="h-2 rounded-full transition-all duration-500"
              :class="getProgressBarColor(score.value, score.max)"
              :style="`width: ${Math.min((score.value / score.max) * 100, 100)}%`"
            ></div>
          </div>
          
          <div class="text-xs text-slate-500 mt-1">
            {{ score.value.toFixed(1) }} / {{ score.max }}
          </div>
        </div>
      </div>
    </div>

    <!-- Pontos Fortes -->
    <div class="mb-6">
      <h3 class="text-sm font-semibold text-green-700 uppercase tracking-wide mb-3 flex items-center gap-2">
        <span>✨</span> Pontos Fortes
      </h3>
      <div class="space-y-2">
        <div v-for="(strength, idx) in analysis.strengths" :key="idx"
             class="flex items-center gap-3 bg-gradient-to-r from-green-50 to-emerald-50 p-3 rounded-xl border border-green-100">
          <div class="flex-shrink-0 text-2xl">{{ strength.emoji }}</div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-semibold text-green-800 truncate">
              {{ formatFeatureName(strength.feature) }}
            </div>
            <div class="text-xs text-green-600">{{ strength.description }}</div>
          </div>
          <div class="flex-shrink-0">
            <div class="text-lg font-bold text-green-700">{{ strength.score.toFixed(0) }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pontos de Atenção -->
    <div class="mb-6">
      <h3 class="text-sm font-semibold text-orange-700 uppercase tracking-wide mb-3 flex items-center gap-2">
        <span>⚠️</span> Pontos de Atenção
      </h3>
      <div class="space-y-2">
        <div v-for="(weakness, idx) in analysis.weaknesses" :key="idx"
             class="flex items-center gap-3 bg-gradient-to-r from-orange-50 to-red-50 p-3 rounded-xl border border-orange-100">
          <div class="flex-shrink-0 text-2xl">{{ weakness.emoji }}</div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-semibold text-orange-800 truncate">
              {{ formatFeatureName(weakness.feature) }}
            </div>
            <div class="text-xs text-orange-600">{{ weakness.description }}</div>
          </div>
          <div class="flex-shrink-0">
            <div class="text-lg font-bold text-orange-700">{{ weakness.score.toFixed(0) }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contagens Brutas (Expandível) -->
    <details class="bg-slate-50 rounded-xl p-4 border border-slate-200">
      <summary class="cursor-pointer text-sm font-semibold text-slate-700 uppercase tracking-wide flex items-center gap-2">
        <span>📈</span> Dados Detalhados
        <span class="ml-auto text-xs text-slate-500">(clique para expandir)</span>
      </summary>
      <div class="mt-4 grid grid-cols-2 gap-3">
        <div v-for="(count, key) in analysis.raw_counts" :key="key"
             class="bg-white rounded-lg p-3 border border-slate-200">
          <div class="text-2xl font-bold text-indigo-600">{{ count }}</div>
          <div class="text-xs text-slate-600 font-medium">{{ formatRawCountName(key) }}</div>
        </div>
      </div>
    </details>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  analysis: any | null
}>()

function getScoreColor(value: number, max: number): string {
  const percentage = (value / max) * 100
  if (percentage >= 80) return 'text-green-600'
  if (percentage >= 60) return 'text-emerald-600'
  if (percentage >= 40) return 'text-yellow-600'
  if (percentage >= 20) return 'text-orange-600'
  return 'text-red-600'
}

function getProgressBarColor(value: number, max: number): string {
  const percentage = (value / max) * 100
  if (percentage >= 80) return 'bg-gradient-to-r from-green-500 to-emerald-500'
  if (percentage >= 60) return 'bg-gradient-to-r from-emerald-500 to-teal-500'
  if (percentage >= 40) return 'bg-gradient-to-r from-yellow-500 to-amber-500'
  if (percentage >= 20) return 'bg-gradient-to-r from-orange-500 to-red-500'
  return 'bg-gradient-to-r from-red-500 to-rose-500'
}

function formatFeatureName(key: string): string {
  const names: Record<string, string> = {
    'walkability': 'Caminhabilidade',
    'cyclability': 'Ciclabilidade',
    'green_spaces': 'Áreas Verdes',
    'parking': 'Estacionamento',
    'safety': 'Segurança',
    'lighting': 'Iluminação',
    'building_density': 'Densidade Urbana',
    'street_connectivity': 'Conectividade Viária',
    'amenity_diversity': 'Diversidade de Serviços'
  }
  return names[key] || key
}

function formatRawCountName(key: string): string {
  const names: Record<string, string> = {
    'footways': 'Calçadas',
    'cycleways': 'Ciclovias',
    'green_areas': 'Áreas Verdes',
    'parking_lots': 'Estacionamentos',
    'street_lamps': 'Postes de Luz',
    'pois': 'Pontos de Interesse',
    'transit_stops': 'Paradas de Transporte'
  }
  return names[key] || key
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

details summary::-webkit-details-marker {
  display: none;
}

details[open] summary span:last-child::before {
  content: '(clique para recolher)';
}

details:not([open]) summary span:last-child::before {
  content: '(clique para expandir)';
}
</style>
