<template>
  <div class="p-6 max-w-5xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">Dashboard de Projetos</h1>
    <table class="min-w-full border">
      <thead>
        <tr class="bg-gray-100">
          <th class="p-2 border">Sel</th>
          <th class="p-2 border">ID</th>
          <th class="p-2 border">Nome</th>
          <th class="p-2 border">Tipo</th>
          <th class="p-2 border">Score</th>
          <th class="p-2 border">Criado em</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in projects" :key="p.id">
          <td class="p-2 border"><input type="checkbox" v-model="selected" :value="p.id" /></td>
          <td class="p-2 border">{{ p.id }}</td>
          <td class="p-2 border">{{ p.name }}</td>
          <td class="p-2 border">{{ p.business_type }}</td>
          <td class="p-2 border">{{ p.score.toFixed(0) }}</td>
          <td class="p-2 border">{{ new Date(p.created_at).toLocaleString() }}</td>
        </tr>
      </tbody>
    </table>

    <div class="mt-6" v-if="selected.length >= 2">
      <h2 class="text-xl font-semibold mb-2">Comparação lado a lado</h2>
      <table class="min-w-full border">
        <thead>
          <tr class="bg-gray-100">
            <th class="p-2 border">Feature</th>
            <th v-for="id in selected" :key="'h'+id" class="p-2 border">Projeto #{{ id }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in featureKeys" :key="f">
            <td class="p-2 border font-semibold">{{ f }}</td>
            <td v-for="id in selected" :key="id+f" class="p-2 border">{{ projectFeatures[id]?.[f] ?? '-' }}</td>
          </tr>
          <tr>
            <td class="p-2 border font-semibold">Score</td>
            <td v-for="id in selected" :key="'s'+id" class="p-2 border">{{ projectScores[id] ?? '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <NuxtLink to="/" class="underline block mt-4">Voltar ao mapa</NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { useApi } from '~/composables/useApi'
const { listProjects, getProject } = useApi()
const projects = ref<any[]>([])
const selected = ref<number[]>([])
const projectFeatures = reactive<Record<number, any>>({})
const projectScores = reactive<Record<number, number>>({})
const featureKeys = ref<string[]>(['competition','offices','schools','parks','transit','flow_kde','mix','street_centrality'])

onMounted(async () => {
  projects.value = await listProjects()
  watch(selected, async (val) => {
    for (const id of val) {
      if (!projectFeatures[id]) {
        const data = await getProject(id)
        projectFeatures[id] = data.features
        projectScores[id] = data.score
      }
    }
  }, { deep: true })
})
</script>
