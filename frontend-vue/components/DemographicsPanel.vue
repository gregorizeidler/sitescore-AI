<template>
  <div v-if="demographics" class="bg-white rounded-2xl p-6 shadow-xl border border-slate-200">
    <!-- Cabeçalho -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-slate-800 flex items-center gap-2 mb-2">
        <span>👥</span> Perfil do Público
      </h2>
      <p class="text-sm text-slate-600">{{ demographics.summary }}</p>
      <div class="text-xs text-slate-500 mt-1">
        Baseado em {{ demographics.total_pois }} pontos de interesse analisados
      </div>
    </div>

    <!-- Resumo de Categorias -->
    <div class="mb-6 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-100">
      <h3 class="text-sm font-semibold text-indigo-800 uppercase tracking-wide mb-3">
        📊 Categorias Encontradas
      </h3>
      <div class="grid grid-cols-2 gap-3">
        <div v-for="(count, key) in demographics.categories" :key="key"
             class="bg-white rounded-lg p-3 shadow-sm">
          <div class="text-2xl font-bold text-indigo-600">{{ count }}</div>
          <div class="text-xs text-slate-600 font-medium">{{ formatCategoryName(key) }}</div>
        </div>
      </div>
    </div>

    <!-- Perfis Identificados -->
    <div class="space-y-4">
      <div v-for="(profile, idx) in demographics.profiles" :key="idx"
           class="border-l-4 pl-4 py-3 rounded-r-xl transition-all duration-200 hover:bg-slate-50"
           :class="getProfileBorderColor(idx)">
        <!-- Cabeçalho do Perfil -->
        <div class="flex items-start gap-3 mb-3">
          <span class="text-4xl flex-shrink-0">{{ profile.emoji }}</span>
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <h3 class="text-lg font-bold text-slate-800">{{ profile.type }}</h3>
              <span class="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-full">
                {{ profile.percentage }}%
              </span>
            </div>
            <!-- Barra de Porcentagem -->
            <div class="w-full bg-slate-200 rounded-full h-2">
              <div 
                class="h-2 rounded-full transition-all duration-500"
                :class="getProfileBarColor(idx)"
                :style="`width: ${profile.percentage}%`"
              ></div>
            </div>
          </div>
        </div>

        <!-- Características -->
        <div class="mb-3">
          <h4 class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2 flex items-center gap-1">
            <span>📋</span> Características
          </h4>
          <ul class="space-y-1">
            <li v-for="(char, charIdx) in profile.characteristics" :key="charIdx"
                class="text-sm text-slate-600 flex items-start gap-2">
              <span class="text-indigo-500 flex-shrink-0">•</span>
              <span>{{ char }}</span>
            </li>
          </ul>
        </div>

        <!-- Oportunidades -->
        <div class="bg-green-50 rounded-lg p-3 border border-green-100">
          <h4 class="text-xs font-semibold text-green-800 uppercase tracking-wide mb-2 flex items-center gap-1">
            <span>💡</span> Oportunidades de Negócio
          </h4>
          <ul class="space-y-1">
            <li v-for="(opp, oppIdx) in profile.opportunities" :key="oppIdx"
                class="text-sm text-green-700 flex items-start gap-2">
              <span class="text-green-500 flex-shrink-0 font-bold">✓</span>
              <span class="font-medium">{{ opp }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Insights Gerais -->
    <div class="mt-6 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl p-4 border border-amber-200">
      <h3 class="text-sm font-semibold text-amber-800 uppercase tracking-wide mb-2 flex items-center gap-2">
        <span>💡</span> Insights
      </h3>
      <ul class="space-y-2 text-sm text-amber-900">
        <li v-if="hasCorporateProfile" class="flex items-start gap-2">
          <span>🎯</span>
          <span>Área corporativa: foque em almoço executivo e serviços rápidos</span>
        </li>
        <li v-if="hasRetailProfile" class="flex items-start gap-2">
          <span>🛍️</span>
          <span>Varejo intenso: evite duplicação, busque complementaridade</span>
        </li>
        <li v-if="hasStudentProfile" class="flex items-start gap-2">
          <span>🎓</span>
          <span>Público jovem: preços acessíveis e ambiente descontraído</span>
        </li>
        <li v-if="!hasCorporateProfile && !hasRetailProfile && !hasStudentProfile" class="flex items-start gap-2">
          <span>🏘️</span>
          <span>Área residencial: foque em serviços de proximidade e conveniência</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  demographics: any | null
}>()

const hasCorporateProfile = computed(() => 
  props.demographics?.profiles?.some((p: any) => p.type === 'Corporativo')
)

const hasRetailProfile = computed(() => 
  props.demographics?.profiles?.some((p: any) => p.type === 'Varejo Intenso')
)

const hasStudentProfile = computed(() => 
  props.demographics?.profiles?.some((p: any) => p.type === 'Estudantes')
)

function formatCategoryName(key: string): string {
  const names: Record<string, string> = {
    'offices': 'Escritórios',
    'schools': 'Escolas',
    'culture': 'Cultura & Lazer',
    'retail': 'Varejo',
    'health': 'Saúde',
    'financial': 'Serviços Financeiros'
  }
  return names[key] || key
}

function getProfileBorderColor(idx: number): string {
  const colors = [
    'border-blue-500',
    'border-purple-500',
    'border-pink-500',
    'border-orange-500',
    'border-teal-500'
  ]
  return colors[idx % colors.length]
}

function getProfileBarColor(idx: number): string {
  const colors = [
    'bg-gradient-to-r from-blue-500 to-blue-600',
    'bg-gradient-to-r from-purple-500 to-purple-600',
    'bg-gradient-to-r from-pink-500 to-pink-600',
    'bg-gradient-to-r from-orange-500 to-orange-600',
    'bg-gradient-to-r from-teal-500 to-teal-600'
  ]
  return colors[idx % colors.length]
}
</script>
