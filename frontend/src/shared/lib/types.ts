export enum DocumentState {
  UPLOADED = 'uploaded',
  READING = 'reading',
  PARSING = 'parsing',
  ANALYZING = 'analyzing',
  GRAPH_BUILDING = 'graph_building',
  QUIZ_GENERATING = 'quiz_generating',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export const STATE_METADATA: Record<
  DocumentState,
  { label: string; color: string; bgClass: string }
> = {
  [DocumentState.UPLOADED]: {
    label: 'Uploaded',
    color: '#a0a0a0',
    bgClass: 'bg-surface text-text-muted',
  },
  [DocumentState.READING]: {
    label: 'Reading',
    color: '#87CEEB',
    bgClass: 'bg-bg-surface text-accent-sky',
  },
  [DocumentState.PARSING]: {
    label: 'Parsing',
    color: '#FFE66D',
    bgClass: 'bg-bg-surface text-accent-yellow',
  },
  [DocumentState.ANALYZING]: {
    label: 'Analyzing',
    color: '#FFE66D',
    bgClass: 'bg-bg-surface text-accent-yellow',
  },
  [DocumentState.GRAPH_BUILDING]: {
    label: 'Building Graph',
    color: '#4ECDC4',
    bgClass: 'bg-bg-surface text-accent-teal',
  },
  [DocumentState.QUIZ_GENERATING]: {
    label: 'Generating Quiz',
    color: '#DDA0DD',
    bgClass: 'bg-bg-surface text-accent-lavender',
  },
  [DocumentState.COMPLETED]: {
    label: 'Completed',
    color: '#95E1D3',
    bgClass: 'bg-bg-surface text-accent-mint',
  },
  [DocumentState.FAILED]: {
    label: 'Failed',
    color: '#FF6B6B',
    bgClass: 'bg-bg-surface text-accent-coral',
  },
}

export function getStateMeta(state: DocumentState) {
  return STATE_METADATA[state] ?? STATE_METADATA[DocumentState.UPLOADED]
}
