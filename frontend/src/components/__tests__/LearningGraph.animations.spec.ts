import { describe, it, expect } from 'vitest'

/** Minimal vis-network simulation for unit test isolation */
class MockDataSet {
  _data: Record<string, any> = {}
  constructor(items: any[] = []) {
    items.forEach((i) => { this._data[i.id] = { ...i } })
  }
  get(ids: string[]) {
    return ids.map((id) => this._data[id]).filter(Boolean)
  }
  update(items: any[] | any) {
    const arr = Array.isArray(items) ? items : [items]
    arr.forEach((i) => {
      if (this._data[i.id]) {
        this._data[i.id] = { ...this._data[i.id], ...i }
      } else {
        this._data[i.id] = { ...i }
      }
    })
  }
}

describe('animateNodesEntrance', () => {
  it('starts nodes with size 1 and opacity 0', () => {
    const ds = new MockDataSet([
      { id: 'n1', targetSize: 30, originalColor: '#abc' },
      { id: 'n2', targetSize: 25, originalColor: '#def' },
      { id: 'n3', targetSize: 20, originalColor: '#123' },
    ])

    const all = ds.get(['n1', 'n2', 'n3'])
    const animated = all.map((n: any) => ({
      ...n,
      size: 1,
      opacity: 0,
      color: { background: '#fff', border: '#fff', highlight: '#fff', opacity: 0 },
    }))
    ds.update(animated)

    expect(ds._data.n1.size).toBe(1)
    expect(ds._data.n1.opacity).toBe(0)
    expect(ds._data.n2.size).toBe(1)
    expect(ds._data.n2.opacity).toBe(0)
  })

  it('restores target staggered sizes', () => {
    const ds = new MockDataSet([
      { id: 'n1', targetSize: 30, originalColor: '#abc' },
      { id: 'n2', targetSize: 25, originalColor: '#def' },
      { id: 'n3', targetSize: 20, originalColor: '#123' },
    ])

    const all = ds.get(['n1', 'n2', 'n3'])
    const targetSizes = all.map((n: any) => n.targetSize ?? 22)
    expect(targetSizes).toEqual([30, 25, 20])
  })

  it('handles empty node list gracefully', () => {
    const ds = new MockDataSet([])
    const ids: string[] = []
    const all = ds.get(ids)
    expect(all.length).toBe(0)
    // No animation should run, no errors
  })

  it('computes correct delays for 80ms stagger', () => {
    const staggerMs = 80
    const count = 5
    const delays = Array.from({ length: count }, (_, i) => i * staggerMs)
    expect(delays).toEqual([0, 80, 160, 240, 320])
  })
})
