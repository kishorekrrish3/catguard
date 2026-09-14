import { create } from "zustand"

type LayerKey = "sensors" | "detections" | "heatmap" | "zones"
type MapStyle = "satellite" | "terrain" | "streets"

interface MapState {
  selectedZoneId: string | null
  mapStyle: MapStyle
  layers: Record<LayerKey, boolean>
  viewState: { longitude: number; latitude: number; zoom: number }
  setSelectedZone: (id: string | null) => void
  setMapStyle: (style: MapStyle) => void
  toggleLayer: (layer: LayerKey) => void
  setViewState: (vs: Partial<MapState["viewState"]>) => void
}

export const useMapStore = create<MapState>((set) => ({
  selectedZoneId: null,
  mapStyle: "satellite",
  layers: { sensors: true, detections: true, heatmap: false, zones: true },
  viewState: { longitude: 76.75, latitude: 10.5, zoom: 9 },
  setSelectedZone: (id) => set({ selectedZoneId: id }),
  setMapStyle: (style) => set({ mapStyle: style }),
  toggleLayer: (layer) => set((s) => ({ layers: { ...s.layers, [layer]: !s.layers[layer] } })),
  setViewState: (vs) => set((s) => ({ viewState: { ...s.viewState, ...vs } })),
}))