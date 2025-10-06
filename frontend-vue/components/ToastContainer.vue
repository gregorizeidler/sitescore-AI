<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="min-w-80 px-6 py-4 rounded-xl shadow-2xl backdrop-blur-xl border-2 flex items-center gap-3 animate-slide-up"
        :class="toastClasses(toast.type)"
      >
        <div class="text-2xl">{{ toastIcon(toast.type) }}</div>
        <div class="flex-1 text-sm font-medium">{{ toast.message }}</div>
        <button 
          @click="remove(toast.id)" 
          class="w-6 h-6 rounded-full hover:bg-black/10 transition-all flex items-center justify-center"
        >
          ×
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '~/composables/useToast'

const { toasts, remove } = useToast()

const toastClasses = (type: string) => {
  const classes = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  }
  return classes[type as keyof typeof classes] || classes.info
}

const toastIcon = (type: string) => {
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  }
  return icons[type as keyof typeof icons] || icons.info
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100px) scale(0.8);
}
</style>

