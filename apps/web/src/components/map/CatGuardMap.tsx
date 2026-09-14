import { useCallback, useState } from "react"
import Map, { Source, Layer, NavigationControl, ScaleControl, Popup, type MapLayerMouseEvent } from "react-map-gl/maplibre"
import "maplibre-gl/dist/maplibre-gl.css"
import { useMapStore } from "@/store/mapStore"
import type { Sensor, Detection } from "@/types"
import { sensorTypeIcon } from "@/lib/utils"

const MAP_STYLES: Record<string, string> = {
  satellite: "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
  terrain: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  streets: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
}

interface CatGuardMapProps {
  sensors?: Sensor[]
  detections?: Detection[]
  zones?: Array<{ id: string; name: string; status: string }>
  height?: string
  onSensorClick?: (sensor: Sensor) => void
  onDetectionClick?: (detection: Detection) => void
}

export function CatGuardMap({ sensors = [], detections = [], zones = [], height = "100%", onSensorClick, onDetectionClick }: CatGuardMapProps) {
  const { mapStyle, layers, viewState, setViewState, setSelectedZone } = useMapStore()
  const [popup, setPopup] = useState<{ lng: number; lat: number; content: React.ReactNode } | null>(null)

  const sensorsGeoJSON = {
    type: "FeatureCollection" as const,
    features: sensors.map((s) => ({
      type: "Feature" as const,
      geometry: { type: "Point" as const, coordinates: [0, 0] },
      properties: { id: s.id, name: s.name, type: s.sensor_type, battery: s.battery_level, active: s.is_active },
    })),
  }

  const detectionsGeoJSON = {
    type: "FeatureCollection" as const,
    features: detections.map((d) => ({
      type: "Feature" as const,
      geometry: { type: "Point" as const, coordinates: d.location ? [d.location.lng, d.location.lat] : [0, 0] },
      properties: { id: d.id, type: d.detection_type, confidence: d.confidence, severity: d.severity },
    })),
  }

  const severityColor = (severity: string) => {
    const colors: Record<string, string> = { critical: "#ef4444", high: "#f97316", medium: "#eab308", low: "#3b82f6" }
    return colors[severity] ?? "#6b7280"
  }

  return (
    <div style={{ height, width: "100%" }} className="relative">
      <Map
        {...viewState}
        onMove={(e) => setViewState(e.viewState)}
        mapStyle={MAP_STYLES[mapStyle] ?? MAP_STYLES.satellite}
        style={{ width: "100%", height: "100%" }}
      >
        <NavigationControl position="top-right" />
        <ScaleControl position="bottom-left" />

        {layers.sensors && (
          <Source id="sensors" type="geojson" data={sensorsGeoJSON}>
            <Layer
              id="sensors-layer"
              type="circle"
              paint={{
                "circle-radius": 8,
                "circle-color": "#16a34a",
                "circle-stroke-width": 2,
                "circle-stroke-color": "#ffffff",
              }}
            />
          </Source>
        )}

        {layers.detections && (
          <Source id="detections" type="geojson" data={detectionsGeoJSON}>
            <Layer
              id="detections-layer"
              type="circle"
              paint={{
                "circle-radius": ["interpolate", ["linear"], ["get", "confidence"], 0.5, 6, 1.0, 16],
                "circle-color": ["match", ["get", "severity"],
                  "critical", "#ef4444", "high", "#f97316", "medium", "#eab308", "#3b82f6"],
                "circle-opacity": 0.8,
                "circle-stroke-width": 2,
                "circle-stroke-color": "#ffffff",
              }}
            />
          </Source>
        )}

        {popup && (
          <Popup longitude={popup.lng} latitude={popup.lat} onClose={() => setPopup(null)} closeButton={true}>
            {popup.content}
          </Popup>
        )}
      </Map>

      {/* Layer Toggle Controls */}
      <div className="absolute top-4 left-4 z-10 bg-white rounded-lg shadow-lg p-3 space-y-2">
        <p className="text-xs font-semibold text-muted-foreground uppercase">Layers</p>
        {(["sensors", "detections", "zones", "heatmap"] as const).map((layer) => (
          <label key={layer} className="flex items-center gap-2 text-xs cursor-pointer">
            <input
              type="checkbox"
              checked={layers[layer]}
              onChange={() => useMapStore.getState().toggleLayer(layer)}
              className="accent-forest-700"
            />
            <span className="capitalize">{layer}</span>
          </label>
        ))}
      </div>

      {/* Style Switcher */}
      <div className="absolute bottom-8 left-4 z-10 bg-white rounded-lg shadow-lg p-2 flex gap-1">
        {(["satellite", "terrain", "streets"] as const).map((style) => (
          <button
            key={style}
            onClick={() => useMapStore.getState().setMapStyle(style)}
            className={`px-2 py-1 text-xs rounded capitalize ${mapStyle === style ? "bg-forest-700 text-white" : "hover:bg-muted"}`}
          >
            {style}
          </button>
        ))}
      </div>
    </div>
  )
}