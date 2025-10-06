<template>
  <div class="w-full h-64">
    <Radar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'
import { Radar } from 'vue-chartjs'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

const props = defineProps<{
  features: Array<{
    name: string
    value: number
    weight: number
    contribution: number
  }>
}>()

const chartData = computed(() => {
  const labels = props.features.map(f => f.name)
  const values = props.features.map(f => Math.abs(f.contribution || 0) * 100)
  
  return {
    labels,
    datasets: [{
      label: 'Impacto das Features',
      data: values,
      backgroundColor: 'rgba(99, 102, 241, 0.2)',
      borderColor: 'rgb(99, 102, 241)',
      borderWidth: 2,
      pointBackgroundColor: 'rgb(99, 102, 241)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgb(99, 102, 241)',
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      beginAtZero: true,
      ticks: {
        backdropColor: 'transparent'
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.1)'
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          return `Impacto: ${context.parsed.r.toFixed(2)}%`
        }
      }
    }
  }
}
</script>

