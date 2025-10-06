<template>
  <div class="relative w-full h-48 flex items-center justify-center">
    <Doughnut :data="chartData" :options="chartOptions" />
    <div class="absolute inset-0 flex flex-col items-center justify-center pt-8">
      <div class="text-5xl font-bold" :class="scoreColor">{{ Math.round(score) }}</div>
      <div class="text-sm text-slate-500 font-medium">{{ scoreLabel }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  score: number
}>()

const scoreColor = computed(() => {
  if (props.score >= 80) return 'text-green-600'
  if (props.score >= 60) return 'text-yellow-600'
  if (props.score >= 40) return 'text-orange-600'
  return 'text-red-600'
})

const scoreLabel = computed(() => {
  if (props.score >= 80) return 'Excelente'
  if (props.score >= 60) return 'Bom'
  if (props.score >= 40) return 'Regular'
  return 'Ruim'
})

const chartData = computed(() => {
  const value = props.score
  const remaining = 100 - value
  
  let color = ''
  if (value >= 80) color = 'rgb(34, 197, 94)'
  else if (value >= 60) color = 'rgb(234, 179, 8)'
  else if (value >= 40) color = 'rgb(249, 115, 22)'
  else color = 'rgb(239, 68, 68)'
  
  return {
    datasets: [{
      data: [value, remaining],
      backgroundColor: [color, 'rgba(226, 232, 240, 0.3)'],
      borderWidth: 0,
      circumference: 180,
      rotation: 270,
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '75%',
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: false
    }
  }
}
</script>

