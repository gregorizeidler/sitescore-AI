<template>
  <button
    @click="toggle"
    class="w-14 h-7 bg-slate-300 dark:bg-slate-600 rounded-full relative transition-all duration-300 focus:ring-4 focus:ring-indigo-100"
    :class="{ 'bg-indigo-600': isDark }"
  >
    <div
      class="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow-md transition-all duration-300 flex items-center justify-center text-xs"
      :class="{ 'translate-x-7': isDark }"
    >
      <span v-if="isDark">🌙</span>
      <span v-else>☀️</span>
    </div>
  </button>
</template>

<script setup lang="ts">
import { useDarkMode } from '~/composables/useDarkMode'

const { isDark, toggle } = useDarkMode()
</script>

