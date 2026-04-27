/**
 * Graph API — fetch knowledge graph data for a document.
 */
import axios from 'axios'

export interface GraphNode {
  id: number
  label: string
  title?: string
  value?: number
  color: string
  group?: string
  font?: { color: string; face: string }
}

export interface GraphEdge {
  id: number
  from: number
  to: number
  width?: number
  color?: string
  arrows?: string
}

export interface GraphPayload {
  document_id: number
  nodes: GraphNode[]
  edges: GraphEdge[]
  node_count: number
  edge_count: number
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

export async function fetchGraph(docId: number): Promise<GraphPayload> {
  const { data } = await axios.get<GraphPayload>(`${API_BASE}/graphs/${docId}`)
  return data
}
