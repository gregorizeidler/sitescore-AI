// nuxt.config.ts
export default defineNuxtConfig({
  devtools: { enabled: false },
  modules: ['@nuxtjs/tailwindcss'],
  css: [
    'maplibre-gl/dist/maplibre-gl.css',
    '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css',
    '~/assets/css/main.css'
  ],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
      basemapUrl: process.env.NUXT_PUBLIC_BASEMAP_URL || 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    }
  },
  nitro: {
    experimental: {
      database: false
    }
  }
})
