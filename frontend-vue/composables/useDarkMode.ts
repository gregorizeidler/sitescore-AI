import { ref, watch, onMounted } from 'vue'

const isDark = ref(false)

export const useDarkMode = () => {
  const toggle = () => {
    isDark.value = !isDark.value
    updateDOM()
    localStorage.setItem('darkMode', isDark.value ? 'true' : 'false')
  }

  const updateDOM = () => {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const init = () => {
    // Verificar localStorage
    const stored = localStorage.getItem('darkMode')
    if (stored !== null) {
      isDark.value = stored === 'true'
    } else {
      // Verificar preferência do sistema
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    updateDOM()
  }

  onMounted(() => {
    init()
  })

  return {
    isDark,
    toggle,
    init
  }
}

