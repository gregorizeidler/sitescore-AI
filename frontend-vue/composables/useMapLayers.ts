// composables/useMapLayers.ts
import maplibregl from 'maplibre-gl'

export const useMapLayers = () => {
  // Cores bonitas por tipo de camada
  const layerColors: Record<string, string> = {
    competition: '#ef4444',    // Vermelho (concorrência)
    pois: '#8b5cf6',           // Roxo (pontos de interesse)
    transit: '#3b82f6',        // Azul (transporte)
    flow: '#f59e0b',           // Laranja (fluxo)
  }

  const addOrUpdateGeoJSON = (map: maplibregl.Map, id: string, data: any, type: 'circle'|'heatmap'='circle') => {
    const srcId = `${id}-src`
    if (map.getSource(srcId)) {
      (map.getSource(srcId) as maplibregl.GeoJSONSource).setData(data)
      return
    }
    
    map.addSource(srcId, { type: 'geojson', data })
    const layerId = `${id}-layer`
    const color = layerColors[id] || '#6366f1'
    
    if (type === 'heatmap') {
      map.addLayer({ 
        id: layerId, 
        type: 'heatmap', 
        source: srcId, 
        paint: { 
          'heatmap-weight': ['interpolate', ['linear'], ['get', 'value'], 0, 0, 50, 1],
          'heatmap-radius': 20, 
          'heatmap-intensity': 0.8, 
          'heatmap-opacity': 0.7,
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(99, 102, 241, 0)',
            0.2, 'rgba(99, 102, 241, 0.3)',
            0.4, 'rgba(139, 92, 246, 0.5)',
            0.6, 'rgba(168, 85, 247, 0.7)',
            0.8, 'rgba(217, 70, 239, 0.9)',
            1, 'rgba(236, 72, 153, 1)'
          ]
        } 
      })
    } else {
      map.addLayer({ 
        id: layerId, 
        type: 'circle', 
        source: srcId, 
        paint: { 
          'circle-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            10, 2,    // zoom 10 = raio 2px
            15, 4,    // zoom 15 = raio 4px  
            18, 6     // zoom 18 = raio 6px
          ],
          'circle-color': color,
          'circle-opacity': 0.6,
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff',
          'circle-stroke-opacity': 0.8
        } 
      })
      
      // Criar popup para hover (tooltip)
      const hoverPopup = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
        className: 'poi-tooltip'
      })
      
      // Adicionar efeito hover com tooltip
      map.on('mouseenter', layerId, (e: any) => {
        map.getCanvas().style.cursor = 'pointer'
        
        if (e.features && e.features[0]) {
          const feature = e.features[0]
          const props = feature.properties
          
          // Parse tags se necessário
          let tags = props.tags
          if (tags && typeof tags === 'string') {
            try {
              tags = JSON.parse(tags)
            } catch (err) {
              tags = {}
            }
          }
          
          // Montar conteúdo do tooltip com ícone por tipo de camada
          const name = props.name || tags?.name || 'Sem nome'
          const type = tags?.amenity || tags?.shop || tags?.leisure || tags?.tourism || tags?.office || 'POI'
          
          // Definir ícone e cor por camada
          let icon = '📍'
          let colorBadge = '#6366f1'
          let layerLabel = ''
          
          if (id === 'competition') {
            icon = '🏢'
            colorBadge = '#ef4444'
            layerLabel = 'Concorrência'
          } else if (id === 'pois') {
            icon = '⭐'
            colorBadge = '#8b5cf6'
            layerLabel = 'Ponto de Interesse'
          } else if (id === 'transit') {
            icon = '🚌'
            colorBadge = '#3b82f6'
            layerLabel = 'Transporte'
          }
          
          const html = `
            <div style="padding: 10px; max-width: 220px;">
              <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                <span style="font-size: 16px;">${icon}</span>
                <span style="
                  font-size: 9px; 
                  font-weight: 700; 
                  color: white; 
                  background-color: ${colorBadge}; 
                  padding: 2px 6px; 
                  border-radius: 4px;
                  text-transform: uppercase;
                  letter-spacing: 0.5px;
                ">
                  ${layerLabel}
                </span>
              </div>
              <div style="font-weight: 700; font-size: 14px; color: #1e293b; margin-bottom: 4px;">
                ${name}
              </div>
              <div style="font-size: 12px; color: #64748b;">
                ${type}
              </div>
            </div>
          `
          
          const coordinates = e.lngLat
          hoverPopup.setLngLat(coordinates).setHTML(html).addTo(map)
        }
      })
      
      map.on('mouseleave', layerId, () => {
        map.getCanvas().style.cursor = ''
        hoverPopup.remove()
      })
      
      // Adicionar click handler para mostrar popup
      map.on('click', layerId, (e: any) => {
        // IMPORTANTE: Prevenir propagação
        if (e.originalEvent) {
          e.originalEvent._poiClicked = true
          e.originalEvent.stopPropagation()
        }
        
        if (e.features && e.features[0]) {
          const feature = e.features[0]
          const properties = { ...feature.properties }
          
          // Parse tags se for string JSON (MapLibre serializa objetos)
          if (properties.tags && typeof properties.tags === 'string') {
            try {
              properties.tags = JSON.parse(properties.tags)
            } catch (err) {
              console.error('Erro ao parsear tags:', err)
              properties.tags = {}
            }
          }
          
          console.log('🎯 POI clicado (useMapLayers):', properties)
          
          // Emitir evento personalizado que o MapView vai capturar
          const event = new CustomEvent('poi-click', {
            detail: {
              poi: properties,
              coordinates: e.lngLat
            }
          })
          window.dispatchEvent(event)
        }
      })
    }
  }
  
  const removeLayerIfExists = (map: maplibregl.Map, id: string) => {
    const srcId = `${id}-src`
    const layerId = `${id}-layer`
    if (map.getLayer(layerId)) map.removeLayer(layerId)
    if (map.getSource(srcId)) map.removeSource(srcId)
  }
  
  return { addOrUpdateGeoJSON, removeLayerIfExists }
}
