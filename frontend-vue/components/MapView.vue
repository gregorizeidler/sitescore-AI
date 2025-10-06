<template>
  <div class="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100">
    <!-- Sidebar -->
    <div class="w-96 bg-white/80 backdrop-blur-xl border-r border-slate-200 shadow-2xl overflow-y-auto">
      <!-- Header -->
      <div class="p-6 border-b border-slate-200 bg-gradient-to-r from-indigo-600 to-purple-600">
        <div class="flex items-center justify-between mb-2">
          <h1 class="text-3xl font-bold text-white">SiteScore AI</h1>
          <DarkModeToggle />
        </div>
        <p class="text-indigo-100 text-sm">Análise Inteligente de Localização</p>
      </div>

      <div class="p-6 space-y-6">
        <!-- Loading Progress Bar -->
        <div v-if="isLoading" class="space-y-3 p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border-2 border-indigo-200 shadow-sm animate-fade-in">
          <div class="flex items-center justify-between">
            <span class="text-sm font-semibold text-indigo-700">{{ loadingStage }}</span>
            <span class="text-sm font-bold text-indigo-600">{{ loadingProgress }}%</span>
          </div>
          <div class="relative h-3 bg-white/60 rounded-full overflow-hidden shadow-inner">
            <div 
              class="absolute top-0 left-0 h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600 rounded-full transition-all duration-500 ease-out"
              :style="{ width: `${loadingProgress}%` }"
            >
              <div class="absolute inset-0 bg-white/30 animate-shimmer"></div>
            </div>
          </div>
          <div class="flex items-center gap-2 text-xs text-indigo-600">
            <div class="animate-spin">⏳</div>
            <span>Analisando dados geoespaciais...</span>
          </div>
        </div>

        <!-- Business Type -->
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <span class="text-lg">🏢</span>
            Tipo de Negócio
          </label>
          <select v-model="businessType" class="w-full px-4 py-3 bg-white border-2 border-slate-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all font-medium text-slate-700 shadow-sm">
            <optgroup label="🍽️ Alimentação">
              <option value="restaurante">Restaurante</option>
              <option value="cafeteria">Cafeteria</option>
              <option value="padaria">Padaria</option>
              <option value="lanchonete">Lanchonete</option>
              <option value="mercado">Mercado/Supermercado</option>
              <option value="bar">Bar/Pub</option>
            </optgroup>
            <optgroup label="💪 Saúde & Bem-estar">
              <option value="academia">Academia</option>
              <option value="farmacia">Farmácia</option>
              <option value="salao_beleza">Salão de Beleza</option>
            </optgroup>
            <optgroup label="🛍️ Varejo">
              <option value="varejo_moda">Varejo de Moda</option>
              <option value="eletronicos">Eletrônicos</option>
              <option value="livraria">Livraria</option>
            </optgroup>
            <optgroup label="⚙️ Serviços">
              <option value="pet_shop">Pet Shop</option>
              <option value="lavanderia">Lavanderia</option>
              <option value="coworking">Coworking</option>
            </optgroup>
            <optgroup label="🎬 Entretenimento">
              <option value="cinema">Cinema</option>
              <option value="hotel">Hotel</option>
            </optgroup>
          </select>
        </div>

        <!-- Search -->
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <span class="text-lg">🔍</span>
            Buscar Endereço
          </label>
          <div class="flex gap-2">
            <input 
              v-model="searchQuery" 
              @keyup.enter="runSearch" 
              placeholder="Ex: Avenida Paulista, SP" 
              class="flex-1 px-4 py-3 bg-white border-2 border-slate-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all placeholder-slate-400"
            />
            <button 
              @click="runSearch" 
              :disabled="isLoading"
              class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg hover:scale-105 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <LoadingSpinner v-if="isLoading" class="w-4 h-4" />
              <span>{{ isLoading ? 'Buscando...' : 'Buscar' }}</span>
            </button>
          </div>
          <div v-if="searchResults.length" class="mt-3 space-y-1 max-h-48 overflow-y-auto">
            <a 
              v-for="r in searchResults" 
              :key="r.display_name"
              href="#" 
              @click.prevent="gotoResult(r)"
              class="block px-4 py-2.5 bg-slate-50 hover:bg-indigo-50 rounded-lg text-sm text-slate-700 hover:text-indigo-700 transition-all border border-slate-200 hover:border-indigo-300"
            >
              📍 {{ r.display_name }}
            </a>
          </div>
        </div>

        <!-- Map Layers -->
        <!-- Filtros de POIs -->
        <div class="space-y-3 pb-4 border-b-2 border-slate-200">
          <label class="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <span class="text-lg">🔍</span>
            Filtrar POIs
          </label>
          <div class="space-y-2">
            <select v-model="poiFilter" @change="applyPOIFilter" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all">
              <option value="all">Todos os POIs</option>
              <option value="amenity=restaurant">🍽️ Restaurantes</option>
              <option value="amenity=cafe">☕ Cafeterias</option>
              <option value="amenity=bar">🍺 Bares</option>
              <option value="shop=supermarket">🛒 Supermercados</option>
              <option value="amenity=pharmacy">💊 Farmácias</option>
              <option value="amenity=bank">🏦 Bancos</option>
              <option value="amenity=school">🏫 Escolas</option>
              <option value="amenity=hospital">🏥 Hospitais</option>
              <option value="leisure=park">🌳 Parques</option>
              <option value="amenity=fuel">⛽ Postos de Gasolina</option>
            </select>
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-600">Raio:</span>
              <input 
                v-model.number="poiFilterRadius" 
                @input="applyPOIFilter" 
                type="range" 
                min="100" 
                max="2000" 
                step="100" 
                class="flex-1"
              />
              <span class="text-xs font-semibold text-indigo-600">{{ poiFilterRadius }}m</span>
            </div>
          </div>
        </div>

        <div class="space-y-3">
          <label class="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <span class="text-lg">🗂️</span>
            Camadas do Mapa
          </label>
          <div class="space-y-2">
            <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
              <input type="checkbox" v-model="layersState.competition" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
              <div class="w-3 h-3 rounded-full bg-red-500"></div>
              <span class="text-sm font-medium text-slate-700">Concorrência</span>
            </label>
            <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
              <input type="checkbox" v-model="layersState.pois" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
              <div class="w-3 h-3 rounded-full bg-purple-500"></div>
              <span class="text-sm font-medium text-slate-700">Pontos de Interesse</span>
            </label>
            <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
              <input type="checkbox" v-model="layersState.transit" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
              <div class="w-3 h-3 rounded-full bg-blue-500"></div>
              <span class="text-sm font-medium text-slate-700">Transporte Público</span>
            </label>
            <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
              <input type="checkbox" v-model="layersState.flow" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
              <div class="w-3 h-3 rounded-full bg-orange-500"></div>
              <span class="text-sm font-medium text-slate-700">Fluxo de Pessoas</span>
            </label>
            <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
              <input type="checkbox" v-model="layersState.buildings" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
              <div class="w-3 h-3 rounded-full bg-gray-500"></div>
              <span class="text-sm font-medium text-slate-700">Edifícios</span>
            </label>
          </div>
          
          <!-- Novas Camadas Avançadas -->
          <details class="group">
            <summary class="cursor-pointer text-xs font-semibold text-indigo-600 hover:text-indigo-700 transition-colors py-2 px-3 bg-indigo-50 rounded-lg">
              ✨ Camadas Avançadas (Novo!)
            </summary>
            <div class="mt-2 space-y-2">
              <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
                <input type="checkbox" v-model="layersState.walkability" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
                <div class="w-3 h-3 rounded-full bg-teal-500"></div>
                <span class="text-sm font-medium text-slate-700 flex items-center gap-1">
                  🚶 Caminhabilidade
                </span>
              </label>
              <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
                <input type="checkbox" v-model="layersState.cyclability" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
                <div class="w-3 h-3 rounded-full bg-cyan-500"></div>
                <span class="text-sm font-medium text-slate-700 flex items-center gap-1">
                  🚴 Ciclabilidade
                </span>
              </label>
              <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
                <input type="checkbox" v-model="layersState.greenSpaces" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
                <div class="w-3 h-3 rounded-full bg-green-500"></div>
                <span class="text-sm font-medium text-slate-700 flex items-center gap-1">
                  🌳 Áreas Verdes
                </span>
              </label>
              <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
                <input type="checkbox" v-model="layersState.parking" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
                <div class="w-3 h-3 rounded-full bg-amber-500"></div>
                <span class="text-sm font-medium text-slate-700 flex items-center gap-1">
                  🅿️ Estacionamento
                </span>
              </label>
              <label class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-all border border-slate-200">
                <input type="checkbox" v-model="layersState.lighting" class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500" />
                <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span class="text-sm font-medium text-slate-700 flex items-center gap-1">
                  💡 Iluminação
                </span>
              </label>
            </div>
          </details>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <button 
            @click="toggleDraw" 
            class="flex-1 px-4 py-3 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-200 active:scale-95"
          >
            ✏️ Desenhar Área
          </button>
          <button 
            @click="saveAnalysis" 
            :disabled="!lastScore"
            class="flex-1 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-200 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            💾 Salvar
          </button>
        </div>

        <!-- ML Segment (Advanced) -->
        <details class="group">
          <summary class="cursor-pointer text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors">
            ⚙️ Configurações Avançadas
          </summary>
          <div class="mt-3 space-y-2">
            <label class="text-xs font-medium text-slate-600">Segmento ML (opcional)</label>
            <input 
              v-model="segment" 
              placeholder="ex: fast_casual" 
              class="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all"
            />
          </div>
        </details>

        <!-- Score Result -->
        <div v-if="lastScore" class="space-y-4 pt-4 border-t-2 border-slate-200 animate-fade-in">
          <!-- Score Badge -->
          <div class="flex justify-center">
            <ScoreBadge :score="lastScore.score" />
          </div>

          <!-- Gauge Chart -->
          <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-lg">
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-4 text-center">
              Score de Viabilidade
            </div>
            <GaugeChart :score="lastScore.score" />
          </div>

            <!-- Análise Detalhada -->
            <div class="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-5 border border-indigo-200 shadow-sm">
              <div class="text-xs font-semibold text-indigo-600 uppercase tracking-wide mb-4 flex items-center gap-2">
                <span>📋</span> Relatório de Análise
              </div>
              <div class="prose prose-sm max-w-none">
                <div v-html="formatExplanation(lastScore.explanation)" class="text-sm text-slate-700 leading-relaxed space-y-3"></div>
              </div>
            </div>

          <!-- Relatório de Contagens (Novo) -->
          <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-lg">
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-4 flex items-center gap-2">
              <span>📊</span> Análise da Localização
            </div>
            <div class="grid grid-cols-2 gap-3">
              <!-- Concorrência -->
              <div class="bg-red-50 rounded-lg p-3 border border-red-100">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-red-600 text-xl">🏢</span>
                  <span class="text-2xl font-bold text-red-700">{{ getFeatureRawValue('competition') }}</span>
                </div>
                <div class="text-xs text-red-600 font-semibold">Concorrentes</div>
                <div class="text-xs text-slate-500 mt-1">Raio 500m</div>
              </div>

              <!-- Escritórios -->
              <div class="bg-blue-50 rounded-lg p-3 border border-blue-100">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-blue-600 text-xl">🏢</span>
                  <span class="text-2xl font-bold text-blue-700">{{ getFeatureRawValue('offices') }}</span>
                </div>
                <div class="text-xs text-blue-600 font-semibold">Escritórios</div>
                <div class="text-xs text-slate-500 mt-1">Raio 500m</div>
              </div>

              <!-- Escolas -->
              <div class="bg-green-50 rounded-lg p-3 border border-green-100">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-green-600 text-xl">🏫</span>
                  <span class="text-2xl font-bold text-green-700">{{ getFeatureRawValue('schools') }}</span>
                </div>
                <div class="text-xs text-green-600 font-semibold">Escolas</div>
                <div class="text-xs text-slate-500 mt-1">Raio 500m</div>
              </div>

              <!-- Parques -->
              <div class="bg-emerald-50 rounded-lg p-3 border border-emerald-100">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-emerald-600 text-xl">🌳</span>
                  <span class="text-2xl font-bold text-emerald-700">{{ getFeatureRawValue('parks') }}</span>
                </div>
                <div class="text-xs text-emerald-600 font-semibold">Parques</div>
                <div class="text-xs text-slate-500 mt-1">Raio 500m</div>
              </div>

              <!-- Transporte -->
              <div class="bg-purple-50 rounded-lg p-3 border border-purple-100">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-purple-600 text-xl">🚇</span>
                  <span class="text-2xl font-bold text-purple-700">{{ getFeatureRawValue('transit') }}</span>
                </div>
                <div class="text-xs text-purple-600 font-semibold">Transporte</div>
                <div class="text-xs text-slate-500 mt-1">Raio 300m</div>
              </div>

              <!-- Mix de Amenidades -->
              <div class="bg-amber-50 rounded-lg p-3 border border-amber-100">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-amber-600 text-xl">🎲</span>
                  <span class="text-2xl font-bold text-amber-700">{{ (getFeatureRawValue('mix') * 100).toFixed(0) }}%</span>
                </div>
                <div class="text-xs text-amber-600 font-semibold">Diversidade</div>
                <div class="text-xs text-slate-500 mt-1">Mix Score</div>
              </div>
            </div>

            <!-- Distância ao Transporte -->
            <div class="mt-3 bg-slate-50 rounded-lg p-3 border border-slate-200">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="text-slate-600 text-lg">📏</span>
                  <span class="text-xs text-slate-600 font-semibold">Distância ao Transporte</span>
                </div>
                <span class="text-lg font-bold text-slate-700">{{ formatDistance(getFeatureRawValue('dist_transit_m')) }}</span>
              </div>
            </div>

            <!-- Fluxo KDE -->
            <div class="mt-2 bg-gradient-to-r from-orange-50 to-pink-50 rounded-lg p-3 border border-orange-200">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="text-orange-600 text-lg">🌊</span>
                  <span class="text-xs text-orange-600 font-semibold">Fluxo Estimado (KDE)</span>
                </div>
                <span class="text-lg font-bold text-orange-700">{{ getFeatureRawValue('flow_kde')?.toFixed(1) || '0.0' }}</span>
              </div>
            </div>
          </div>

          <!-- Radar Chart -->
          <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-lg">
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-4">
              📊 Impacto das Features
            </div>
            <RadarChart :features="lastScore.features" />
          </div>

          <!-- Features Detalhadas -->
          <details class="group">
            <summary class="cursor-pointer text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors flex items-center gap-2">
              <span>📋 Ver Features Detalhadas</span>
              <svg class="w-4 h-4 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </summary>
            <div class="space-y-2 mt-3">
              <div 
                v-for="f in lastScore.features" 
                :key="f.name"
                class="bg-slate-50 rounded-lg p-3 border border-slate-200 hover:border-indigo-300 transition-all"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="text-sm font-semibold text-slate-700">{{ f.name }}</span>
                  <span 
                    class="text-xs font-bold px-2 py-1 rounded-full"
                    :class="f.contribution > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                  >
                    {{ f.contribution?.toFixed(3) ?? '—' }}
                  </span>
                </div>
                <div class="text-xs text-slate-500">
                  Valor: {{ f.value }} | Peso: {{ f.weight }}
                </div>
              </div>
            </div>
          </details>
          
          <!-- Botão para Análise Avançada -->
          <button 
            v-if="lastPoint"
            @click="runAdvancedAnalysis"
            :disabled="isLoadingAdvanced"
            class="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <span>✨</span>
            <span>{{ isLoadingAdvanced ? 'Analisando...' : 'Análise Avançada' }}</span>
          </button>
        </div>

        <!-- Advanced Analysis Panel -->
        <AdvancedAnalysisPanel v-if="advancedAnalysis" :analysis="advancedAnalysis" />

        <!-- Demographics Panel -->
        <DemographicsPanel v-if="demographics" :demographics="demographics" />

        <!-- Export Options (visible when score exists) -->
        <div v-if="lastScore" class="space-y-2 pt-4 border-t-2 border-slate-200">
          <div class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">💾 Exportar Dados</div>
          <div class="grid grid-cols-2 gap-2">
            <button
              @click="exportJSON"
              class="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition-all"
            >
              📄 JSON
            </button>
            <button
              @click="exportCSV"
              class="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-semibold transition-all"
            >
              📊 CSV
            </button>
          </div>
        </div>

        <!-- Links -->
        <div class="space-y-2 pt-4">
          <NuxtLink 
            to="/compare" 
            class="block w-full text-center px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-xl font-semibold transition-all shadow-lg"
          >
            ⚖️ Comparar Locais
          </NuxtLink>
          <NuxtLink 
            to="/dashboard" 
            class="block w-full text-center px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold transition-all border border-slate-300"
          >
            📊 Ver Dashboard
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Map -->
    <div class="flex-1 relative">
      <div ref="mapEl" class="w-full h-full"></div>
      <div class="absolute top-4 right-4 bg-white/90 backdrop-blur-lg rounded-xl shadow-xl px-4 py-2 border border-slate-200">
        <div class="text-xs font-semibold text-slate-600">SiteScore AI</div>
        <div class="text-xs text-slate-500">Powered by OpenStreetMap</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import maplibregl from 'maplibre-gl'
import Draw from '@mapbox/mapbox-gl-draw'
import { ref, reactive, onMounted, nextTick, createApp } from 'vue'
import { useApi } from '~/composables/useApi'
import { useMapLayers } from '~/composables/useMapLayers'
import { useToast } from '~/composables/useToast'
import { useExport } from '~/composables/useExport'
import POIPopup from './POIPopup.vue'
import AdvancedAnalysisPanel from './AdvancedAnalysisPanel.vue'
import DemographicsPanel from './DemographicsPanel.vue'

const { scoreLocation, getLayer, saveProject, geocode, getAdvancedAnalysis, getDemographics } = useApi()
const { addOrUpdateGeoJSON, removeLayerIfExists } = useMapLayers()
const { success, error, info } = useToast()
const { exportToJSON, exportToCSV } = useExport()
const config = useRuntimeConfig()

// Types
type BusinessType = 
  | 'restaurante' 
  | 'academia' 
  | 'varejo_moda'
  | 'cafeteria'
  | 'padaria'
  | 'lanchonete'
  | 'mercado'
  | 'farmacia'
  | 'pet_shop'
  | 'lavanderia'
  | 'salao_beleza'
  | 'livraria'
  | 'coworking'
  | 'eletronicos'
  | 'bar'
  | 'cinema'
  | 'hotel'

const mapEl = ref<HTMLDivElement | null>(null)
let map: maplibregl.Map
let draw: any

const businessType = ref<BusinessType>('restaurante')
const layersState = reactive({ 
  competition: true, 
  pois: false, 
  transit: true, 
  flow: false, 
  buildings: false,
  walkability: false,
  cyclability: false,
  greenSpaces: false,
  parking: false,
  lighting: false
})
const drawn = ref<any>(null)
const lastScore = ref<any>(null)
const segment = ref<string>('')
const isLoading = ref(false)
const loadingProgress = ref(0)
const loadingStage = ref('')

const searchQuery = ref('')
const searchResults = ref<any[]>([])

const selectedPOI = ref<any>(null)
let poiPopup: maplibregl.Popup | null = null
let isClickOnPOI = false

const poiFilter = ref('all')
const poiFilterRadius = ref(1000)
const lastPoint = ref<[number, number] | null>(null)

// Advanced Analysis
const advancedAnalysis = ref<any>(null)
const demographics = ref<any>(null)
const isLoadingAdvanced = ref(false)

const applyPOIFilter = async () => {
  if (!lastPoint.value) {
    info('Primeiro calcule um score no mapa!')
    return
  }
  
  info('Aplicando filtro...')
  
  try {
    const [lng, lat] = lastPoint.value
    const filter = poiFilter.value
    const radius = poiFilterRadius.value
    
    if (filter === 'all') {
      // Recarregar todas as camadas normalmente
      await refreshLayers()
    } else {
      // Filtrar POIs específicos - buscar do backend
      const bbox = currentBbox()
      const poiLayer = await getLayer('pois', { bbox, business_type: businessType.value })
      
      if (poiLayer?.features) {
        // Filtrar features pelo tag específico E por raio
        const [key, value] = filter.split('=')
        const filtered = poiLayer.features.filter((f: any) => {
          // Parse tags
          const tags = typeof f.properties.tags === 'string' 
            ? JSON.parse(f.properties.tags) 
            : f.properties.tags
          
          // Verificar se tem a tag correta
          if (!tags || tags[key] !== value) return false
          
          // Calcular distância do ponto de análise
          const coords = f.geometry.coordinates
          const dx = (coords[0] - lng) * 111320 * Math.cos(lat * Math.PI / 180)
          const dy = (coords[1] - lat) * 110540
          const distance = Math.sqrt(dx * dx + dy * dy)
          
          return distance <= radius
        })
        
        // Atualizar camada de POIs com dados filtrados
        addOrUpdateGeoJSON(map, 'pois', { type: 'FeatureCollection', features: filtered })
        
        success(`${filtered.length} POI(s) encontrado(s)`)
      }
    }
  } catch (err: any) {
    error('Erro ao filtrar POIs')
    console.error(err)
  }
}

function formatExplanation(text: string): string {
  if (!text) return ''
  
  // Converter markdown básico para HTML
  let html = text
    // Negrito: **texto** -> <strong>texto</strong>
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Quebras de linha duplas -> parágrafos
    .split('\n\n')
    .map(p => `<p class="mb-3">${p.trim()}</p>`)
    .join('')
  
  return html
}

const handlePOIClick = (event: CustomEvent) => {
  // Extrair dados do evento
  const { poi, coordinates } = event.detail
  
  // Marcar que clicou em um POI para evitar rodar o score
  isClickOnPOI = true
  setTimeout(() => { isClickOnPOI = false }, 100)
  
  console.log('POI clicado - abrindo popup:', poi)
  
  // Parse tags se for string JSON
  if (typeof poi.tags === 'string') {
    try {
      poi.tags = JSON.parse(poi.tags)
    } catch (e) {
      poi.tags = {}
    }
  }
  
  selectedPOI.value = poi
  
  // Mostrar toast de feedback
  info(`Exibindo: ${poi.name || poi.tags?.name || 'POI'}`, 1500)
  
  // Remover popup anterior se existir
  if (poiPopup) {
    poiPopup.remove()
  }
  
  // Criar div para o popup
  const popupDiv = document.createElement('div')
  popupDiv.id = 'poi-popup-container'
  
  // Criar popup do MapLibre
  poiPopup = new maplibregl.Popup({
    closeButton: false,
    closeOnClick: false,
    maxWidth: '400px',
    offset: 15
  })
    .setLngLat([coordinates.lng, coordinates.lat])
    .setDOMContent(popupDiv)
    .addTo(map)
  
  // Renderizar o componente Vue no popup
  nextTick(() => {
    const app = createApp(POIPopup, {
      poi: poi,
      onClose: () => {
        if (poiPopup) poiPopup.remove()
        selectedPOI.value = null
      }
    })
    app.mount('#poi-popup-container')
  })
}

onMounted(() => {
  // Listener para cliques em POIs
  window.addEventListener('poi-click', handlePOIClick as any)
  
  map = new maplibregl.Map({
    container: mapEl.value!,
    style: {
      version: 8,
      sources: { 'osm': { type: 'raster', tiles: [config.public.basemapUrl], tileSize: 256, attribution: '&copy; OpenStreetMap' } },
      layers: [{ id: 'osm', type: 'raster', source: 'osm' }]
    },
    center: [-46.633, -23.55], // São Paulo
    zoom: 12
  })
  map.addControl(new maplibregl.NavigationControl(), 'top-left')

  draw = new Draw({ displayControlsDefault: false, controls: { polygon: true, trash: true } })
  map.addControl(draw, 'top-left')

  map.on('click', async (e) => {
    // MÉTODO 1: Verificar flag customizada do originalEvent
    if (e.originalEvent && (e.originalEvent as any)._poiClicked) {
      console.log('🛑 Click em POI detectado via flag, ignorando score')
      return
    }
    
    // MÉTODO 2: Verificar flag global temporária
    if (isClickOnPOI) {
      console.log('🛑 Click em POI detectado via flag global, ignorando score')
      return
    }
    
    // MÉTODO 3: Verificar se o click foi em alguma feature das layers
    // IMPORTANTE: Os IDs das layers têm o sufixo "-layer"
    const features = map.queryRenderedFeatures(e.point, {
      layers: ['competition-layer', 'pois-layer', 'transit-layer']
    })
    
    // Se clicou em uma feature de POI/Competition/Transit, não rodar score
    if (features && features.length > 0) {
      console.log('🛑 Click em feature detectado via query, ignorando score:', features[0].layer.id)
      return
    }
    
    // Se chegou aqui, é um click em área vazia - pode rodar o score
    console.log('✅ Click em área vazia, rodando score...')
    const geom = { type: 'Point', coordinates: [e.lngLat.lng, e.lngLat.lat] }
    await runScore(geom)
  })

  let refreshTimer:any = null
  const refreshDebounced = () => { 
    clearTimeout(refreshTimer); 
    refreshTimer = setTimeout(refreshLayers, 1000) // Aumentado para 1 segundo para reduzir requisições
  }
  map.on('moveend', refreshDebounced)
  map.on('draw.create', (e:any) => { if (e.features && e.features[0]) runScore(e.features[0].geometry) })
  map.on('draw.update', (e:any) => { if (e.features && e.features[0]) runScore(e.features[0].geometry) })
  watch(layersState, () => refreshLayers(), { deep: true })
  watch(businessType, () => refreshLayers())

  refreshLayers()
})

function toggleDraw() {
  if (!drawn.value) {
    draw.changeMode('draw_polygon')
  } else {
    draw.delete(drawn.value.id)
    drawn.value = null
  }
}

async function runScore(geom: any) {
  isLoading.value = true
  loadingProgress.value = 0
  
  try {
    // Etapa 1: Inicializando
    loadingStage.value = '🔍 Inicializando análise...'
    loadingProgress.value = 10
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // Etapa 2: Buscando dados
    loadingStage.value = '🗺️ Buscando dados do OpenStreetMap...'
    loadingProgress.value = 30
    info('Coletando dados geoespaciais...', 1500)
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // Etapa 3: Calculando features
    loadingStage.value = '📊 Extraindo features geoespaciais...'
    loadingProgress.value = 50
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // Etapa 4: Processando score (requisição real)
    loadingStage.value = '🎯 Calculando score de viabilidade...'
    loadingProgress.value = 70
    const payload = { geometry: geom, business_type: businessType.value, name: 'Análise rápida' }
    lastScore.value = await scoreLocation(payload, segment.value || undefined)
    
    // Etapa 5: Finalizando
    loadingStage.value = '✨ Finalizando análise...'
    loadingProgress.value = 90
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // Etapa 6: Concluído
    loadingStage.value = '✅ Análise concluída!'
    loadingProgress.value = 100
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // Salvar último ponto para uso nos filtros
    if (lastScore.value.center) {
      lastPoint.value = [lastScore.value.center[0], lastScore.value.center[1]]
    }
    
    success(`Score calculado: ${lastScore.value.score.toFixed(0)}/100 🎉`)
  } catch (err) {
    error('Erro ao calcular score')
    console.error(err)
    loadingStage.value = '❌ Erro na análise'
    loadingProgress.value = 0
  } finally {
    // Manter barra visível por mais um momento antes de remover
    await new Promise(resolve => setTimeout(resolve, 500))
    isLoading.value = false
    loadingProgress.value = 0
    loadingStage.value = ''
  }
}

function currentBbox() {
  const b = map.getBounds()
  return `${b.getWest()},${b.getSouth()},${b.getEast()},${b.getNorth()}`
}

// Cache simples para evitar requisições duplicadas (30 segundos)
const layerCache = new Map<string, { data: any, timestamp: number }>()
const CACHE_TTL = 30000 // 30 segundos

async function getCachedLayer(name: string, params: any) {
  const cacheKey = `${name}-${JSON.stringify(params)}`
  const cached = layerCache.get(cacheKey)
  
  // Se está no cache e não expirou, retornar do cache
  if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
    return cached.data
  }
  
  // Senão, buscar da API
  const data = await getLayer(name, params)
  
  // Se retornou erro de rate limit, não cachear e mostrar mensagem
  if (data && (data as any).error === 'rate_limit_exceeded') {
    error('⏱️ Limite de requisições atingido. Aguarde alguns segundos...')
    return null
  }
  
  // Cachear resultado
  layerCache.set(cacheKey, { data, timestamp: Date.now() })
  return data
}

async function refreshLayers() {
  const bbox = currentBbox()
  
  // Preparar requisições em paralelo apenas para camadas ativas
  const layerPromises: Array<Promise<void>> = []
  
  // Competition
  if (layersState.competition) {
    layerPromises.push(
      getCachedLayer('competition', { bbox, business_type: businessType.value })
        .then(gj => gj && addOrUpdateGeoJSON(map, 'competition', gj, 'circle'))
    )
  } else {
    removeLayerIfExists(map, 'competition')
  }
  
  // POIs
  if (layersState.pois) {
    layerPromises.push(
      getCachedLayer('pois', { bbox, business_type: businessType.value })
        .then(gj => gj && addOrUpdateGeoJSON(map, 'pois', gj, 'circle'))
    )
  } else {
    removeLayerIfExists(map, 'pois')
  }
  
  // Transit
  if (layersState.transit) {
    layerPromises.push(
      getCachedLayer('transit', { bbox, business_type: businessType.value })
        .then(gj => gj && addOrUpdateGeoJSON(map, 'transit', gj, 'circle'))
    )
  } else {
    removeLayerIfExists(map, 'transit')
  }
  
  // Flow (heatmap) - opcional
  if (layersState.flow) {
    layerPromises.push(
      getCachedLayer('flow', { bbox, business_type: businessType.value })
        .then(gj => gj && addOrUpdateGeoJSON(map, 'flow', gj, 'heatmap'))
    )
  } else {
    removeLayerIfExists(map, 'flow')
  }
  
  // Buildings
  if (layersState.buildings) {
    layerPromises.push(
      getCachedLayer('buildings', { bbox }).then(gj => {
        if (gj) {
          const srcId = 'buildings-src'
          const layerId = 'buildings-layer'
          
          if (map.getSource(srcId)) {
            (map.getSource(srcId) as any).setData(gj)
          } else {
            map.addSource(srcId, { type: 'geojson', data: gj })
            map.addLayer({
              id: layerId,
              type: 'fill',
              source: srcId,
              paint: {
                'fill-color': '#94a3b8',
                'fill-opacity': 0.3,
                'fill-outline-color': '#475569'
              }
            })
          }
        }
      })
    )
  } else {
    const srcId = 'buildings-src'
    const layerId = 'buildings-layer'
    if (map.getLayer(layerId)) map.removeLayer(layerId)
    if (map.getSource(srcId)) map.removeSource(srcId)
  }
  
  // Walkability
  if (layersState.walkability) {
    layerPromises.push(
      getCachedLayer('walkability', { bbox })
        .then(gj => gj && addOrUpdateGeoJSON(map, 'walkability', gj, 'circle', { color: '#14b8a6' }))
    )
  } else {
    removeLayerIfExists(map, 'walkability')
  }
  
  // Cyclability
  if (layersState.cyclability) {
    layerPromises.push(
      getCachedLayer('cyclability', { bbox })
        .then(gj => gj && addOrUpdateGeoJSON(map, 'cyclability', gj, 'circle', { color: '#06b6d4' }))
    )
  } else {
    removeLayerIfExists(map, 'cyclability')
  }
  
  // Green Spaces
  if (layersState.greenSpaces) {
    layerPromises.push(
      getCachedLayer('green_spaces', { bbox })
        .then(gj => gj && addOrUpdateGeoJSON(map, 'greenSpaces', gj, 'circle', { color: '#22c55e' }))
    )
  } else {
    removeLayerIfExists(map, 'greenSpaces')
  }
  
  // Parking
  if (layersState.parking) {
    layerPromises.push(
      getCachedLayer('parking', { bbox })
        .then(gj => gj && addOrUpdateGeoJSON(map, 'parking', gj, 'circle', { color: '#f59e0b' }))
    )
  } else {
    removeLayerIfExists(map, 'parking')
  }
  
  // Lighting
  if (layersState.lighting) {
    layerPromises.push(
      getCachedLayer('lighting', { bbox })
        .then(gj => gj && addOrUpdateGeoJSON(map, 'lighting', gj, 'circle', { color: '#eab308' }))
    )
  } else {
    removeLayerIfExists(map, 'lighting')
  }
  
  // Aguardar todas as requisições em paralelo
  await Promise.all(layerPromises)
}

async function saveAnalysis() {
  if (!lastScore.value) return
  try {
    info('Salvando análise...', 2000)
    const payload = {
      name: 'Análise salva',
      business_type: businessType.value,
      geometry: { type: 'Point', coordinates: lastScore.value.center },
      features: Object.fromEntries(lastScore.value.features.map((f:any)=>[f.name, f.value])),
      score: lastScore.value.score
    }
    await saveProject(payload)
    success('Análise salva com sucesso! 🎉')
  } catch (err) {
    error('Erro ao salvar análise')
    console.error(err)
  }
}

async function runAdvancedAnalysis() {
  if (!lastPoint.value) {
    error('Primeiro calcule um score no mapa!')
    return
  }
  
  isLoadingAdvanced.value = true
  info('Executando análise avançada...', 2000)
  
  try {
    const [lng, lat] = lastPoint.value
    const radius = 1000 // 1km
    
    // Chamar ambas APIs em paralelo
    const [advanced, demo] = await Promise.all([
      getAdvancedAnalysis(lng, lat, radius),
      getDemographics(lng, lat, radius)
    ])
    
    advancedAnalysis.value = advanced
    demographics.value = demo
    
    success('Análise avançada concluída! ✨')
  } catch (err) {
    error('Erro ao executar análise avançada')
    console.error(err)
  } finally {
    isLoadingAdvanced.value = false
  }
}

async function runSearch() {
  console.log('runSearch chamado! Query:', searchQuery.value)
  if (!searchQuery.value) {
    console.log('Query vazia, abortando')
    return
  }
  
  isLoading.value = true
  loadingProgress.value = 0
  
  try {
    // Etapa 1: Preparando busca
    loadingStage.value = '🔍 Preparando busca...'
    loadingProgress.value = 20
    await new Promise(resolve => setTimeout(resolve, 150))
    
    // Etapa 2: Geocodificando
    loadingStage.value = '🗺️ Geocodificando endereço...'
    loadingProgress.value = 50
    info('Buscando endereço...', 1500)
    console.log('Chamando geocode...')
    const results = await geocode(searchQuery.value)
    console.log('Resultados recebidos:', results)
    
    // Etapa 3: Processando resultados
    loadingStage.value = '✨ Processando resultados...'
    loadingProgress.value = 80
    await new Promise(resolve => setTimeout(resolve, 150))
    
    searchResults.value = results || []
    console.log('searchResults.value atualizado:', searchResults.value)
    
    // Etapa 4: Concluído
    loadingStage.value = '✅ Busca concluída!'
    loadingProgress.value = 100
    await new Promise(resolve => setTimeout(resolve, 200))
    
    if (searchResults.value && searchResults.value.length > 0) {
      success(`${searchResults.value.length} resultado(s) encontrado(s) 📍`)
    } else {
      error('Nenhum resultado encontrado')
    }
  } catch (err) {
    error('Erro ao buscar endereço')
    console.error(err)
    loadingStage.value = '❌ Erro na busca'
    loadingProgress.value = 0
  } finally {
    await new Promise(resolve => setTimeout(resolve, 300))
    isLoading.value = false
    loadingProgress.value = 0
    loadingStage.value = ''
  }
}
function gotoResult(r:any) {
  console.log('Indo para resultado:', r)
  map.flyTo({ center: [r.lon, r.lat], zoom: 16 })
  searchResults.value = []
}

function exportJSON() {
  if (!lastScore.value) return
  const data = {
    timestamp: new Date().toISOString(),
    businessType: businessType.value,
    score: lastScore.value.score,
    explanation: lastScore.value.explanation,
    features: lastScore.value.features,
    center: lastScore.value.center
  }
  exportToJSON(data, `sitescore-${businessType.value}-${Date.now()}.json`)
  success('Dados exportados em JSON! 📄')
}

function exportCSV() {
  if (!lastScore.value) return
  const data = lastScore.value.features.map((f: any) => ({
    feature_name: f.name,
    value: f.value,
    weight: f.weight,
    contribution: f.contribution,
    description: f.description
  }))
  exportToCSV(data, `sitescore-features-${businessType.value}-${Date.now()}.csv`)
  success('Dados exportados em CSV! 📊')
}

// Helper: Obter valor bruto de uma feature
function getFeatureRawValue(featureName: string): number {
  if (!lastScore.value?.features) return 0
  const feature = lastScore.value.features.find((f: any) => f.name === featureName)
  return feature?.value ?? 0
}

// Helper: Formatar distância em metros
function formatDistance(meters: number): string {
  if (!meters || meters === Infinity) return '—'
  if (meters < 1000) return `${Math.round(meters)}m`
  return `${(meters / 1000).toFixed(1)}km`
}
</script>

<style>
html, body, #__nuxt { height: 100%; margin: 0; }
</style>
