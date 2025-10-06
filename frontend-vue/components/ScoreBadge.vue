<template>
  <div 
    class="inline-flex items-center justify-center px-6 py-3 rounded-2xl font-bold text-2xl shadow-lg"
    :class="badgeClass"
  >
    <span class="mr-2">{{ grade }}</span>
    <span class="text-sm font-normal opacity-90">{{ Math.round(score) }}/100</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
}>()

const grade = computed(() => {
  if (props.score >= 90) return 'A+'
  if (props.score >= 80) return 'A'
  if (props.score >= 70) return 'B+'
  if (props.score >= 60) return 'B'
  if (props.score >= 50) return 'C+'
  if (props.score >= 40) return 'C'
  if (props.score >= 30) return 'D'
  return 'E'
})

const badgeClass = computed(() => {
  if (props.score >= 80) return 'bg-gradient-to-r from-green-500 to-emerald-600 text-white'
  if (props.score >= 60) return 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-white'
  if (props.score >= 40) return 'bg-gradient-to-r from-orange-400 to-orange-600 text-white'
  return 'bg-gradient-to-r from-red-500 to-red-700 text-white'
})
</script>

