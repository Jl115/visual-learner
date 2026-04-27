/** Mastery API — fetch and update node mastery states. */
import axios from 'axios'

export interface MasteryState {
  id: number
  node_id: number
  state: 'new' | 'reviewing' | 'learned'
  last_reviewed: string | null
  review_count: number
  created_at: string | null
}

export interface MasteryStats {
  document_id: number
  total_nodes: number
  new_count: number
  reviewing_count: number
  learned_count: number
  mastery_percent: number
}

export interface NodeWithState {
  id: number
  label: string
  color: string
  state: 'new' | 'reviewing' | 'learned'
  review_count: number
  last_reviewed: string | null
}

export interface GraphWithStates {
  document_id: number
  nodes: NodeWithState[]
  edges: { id: number; from: number; to: number; color?: string }[]
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

export async function fetchMasteryGraph(docId: number): Promise<GraphWithStates> {
  const { data } = await axios.get<GraphWithStates>(`${API_BASE}/mastery/graph/${docId}`)
  return data
}

export async function fetchMasteryStats(docId: number): Promise<MasteryStats> {
  const { data } = await axios.get<MasteryStats>(`${API_BASE}/mastery/stats/${docId}`)
  return data
}

export async function fetchNodeState(nodeId: number): Promise<MasteryState> {
  const { data } = await axios.get<MasteryState>(`${API_BASE}/mastery/node/${nodeId}`)
  return data
}

export async function updateNodeState(nodeId: number, state: 'new' | 'reviewing' | 'learned'): Promise<MasteryState> {
  const { data } = await axios.post<MasteryState>(`${API_BASE}/mastery/node`, { node_id: nodeId, state })
  return data
}

export async function recordNodeAttempt(nodeId: number, score: number, total: number): Promise<MasteryState> {
  const { data } = await axios.post<MasteryState>(`${API_BASE}/mastery/node/${nodeId}/attempt?score=${score}&total=${total}`)
  return data
}

export async function resetNodeState(nodeId: number): Promise<MasteryState> {
  const { data } = await axios.post<MasteryState>(`${API_BASE}/mastery/node/${nodeId}/reset`)
  return data
}
