// composables/useApi.ts
const safeFetch = async (fn: () => Promise<any>) => {
  try {
    return await fn()
  } catch (err) {
    console.error('API Error:', err)
    return null
  }
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase
  const scoreLocation = async (payload: any, segment?: string) => {
    const qs = segment ? `?segment=${encodeURIComponent(segment)}` : ''
    return await $fetch(`${base}/score${qs}`, { method: 'POST', body: payload })
  }
  const getLayer = async (name: string, params: Record<string, string|number>) => {
    const qs = new URLSearchParams(params as any).toString()
    return await safeFetch(() => $fetch(`${base}/layers/${name}?${qs}`))
  }
  const listProjects = async () => safeFetch(() => $fetch(`${base}/projects`))
  const getProject = async (id: number) => $fetch(`${base}/projects/${id}`)
  const saveProject = async (payload: any) => safeFetch(() => $fetch(`${base}/projects`, { method: 'POST', body: payload }))
  const geocode = async (q: string) => {
    try {
      return await $fetch(`${base}/geocode?q=${encodeURIComponent(q)}`)
    } catch (err) {
      console.error('Geocode error:', err)
      return []
    }
  }
  
  const getAdvancedAnalysis = async (lon: number, lat: number, radius: number = 1000) => {
    return await safeFetch(() => $fetch(`${base}/analysis/advanced`, {
      method: 'POST',
      query: { lon, lat, radius }
    }))
  }
  
  const getDemographics = async (lon: number, lat: number, radius: number = 1000) => {
    return await safeFetch(() => $fetch(`${base}/analysis/demographics`, {
      query: { lon, lat, radius }
    }))
  }
  
  return { 
    scoreLocation, 
    getLayer, 
    listProjects, 
    getProject, 
    saveProject, 
    geocode,
    getAdvancedAnalysis,
    getDemographics
  }
}
