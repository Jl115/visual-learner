/** Mastery state color constants per DESIGN.md tokens. */
export const MASTERY_COLORS = {
  new: '#DDA0DD',
  reviewing: '#FFDAB9',
  learned: '#9CAF88',
} as const

export type MasteryState = 'new' | 'reviewing' | 'learned'

export function getStateColor(state: MasteryState): string {
  return MASTERY_COLORS[state] || '#4ECDC4'
}
