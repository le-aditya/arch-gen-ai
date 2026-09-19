/* Pure layout maths for the blueprint diagram — no React, no DOM, so it can be
   exercised directly against real /analyze responses. */

export const NODE_H = 42
export const GAP_X = 30
export const GAP_V = 58
export const PAD = 28
export const TB_W = 248
export const TB_H = 84
// Clearance between the lowest node row and the title block.
export const TB_GAP = 32
const CHAR_W = 6.6

/* Longest-path layering: a node sits one level below its deepest parent, so
   edges always point downward and never skip backwards. */
export function computeLevels(nodes, edges) {
  const incoming = new Map(nodes.map(n => [n.id, 0]))
  edges.forEach(e => incoming.set(e.target, (incoming.get(e.target) || 0) + 1))

  const level = new Map()
  nodes.filter(n => incoming.get(n.id) === 0).forEach(n => level.set(n.id, 0))

  let changed = true
  while (changed) {
    changed = false
    edges.forEach(e => {
      if (level.has(e.source)) {
        const candidate = level.get(e.source) + 1
        if (!level.has(e.target) || level.get(e.target) < candidate) {
          level.set(e.target, candidate)
          changed = true
        }
      }
    })
  }

  const maxLevel = Math.max(0, ...Array.from(level.values()))
  const rows = Array.from({ length: maxLevel + 1 }, () => [])
  nodes.forEach(n => rows[level.get(n.id) ?? 0].push(n))
  return rows
}

/* Generated labels can run long ("Docker + Docker Compose + Stripe SDK"), which
   would otherwise stretch one box far wider than the rest of its row. Break at
   the word boundary nearest the middle so the two lines come out even. */
export function wrapLabel(label, maxChars = 24) {
  if (label.length <= maxChars) return [label]
  const words = label.split(' ')
  if (words.length < 2) return [label]

  const mid = label.length / 2
  let breakAt = 0
  let bestDistance = Infinity
  let consumed = 0
  for (let i = 0; i < words.length - 1; i++) {
    consumed += words[i].length + 1
    const distance = Math.abs(consumed - mid)
    if (distance < bestDistance) {
      bestDistance = distance
      breakAt = i
    }
  }
  return [words.slice(0, breakAt + 1).join(' '), words.slice(breakAt + 1).join(' ')]
}

export function layout(nodes, edges) {
  const rows = computeLevels(nodes, edges)
  const sized = rows.map(row =>
    row.map(n => {
      const lines = wrapLabel(n.label)
      const widest = Math.max(...lines.map(l => l.length))
      return { ...n, lines, w: Math.max(104, widest * CHAR_W + 34), h: NODE_H }
    })
  )
  const rowWidths = sized.map(
    row => row.reduce((sum, n) => sum + n.w, 0) + GAP_X * Math.max(0, row.length - 1)
  )
  const contentW = Math.max(520, ...rowWidths)
  const width = contentW + PAD * 2
  const height =
    PAD + sized.length * NODE_H + (sized.length - 1) * GAP_V + TB_GAP + TB_H + PAD

  const placed = new Map()
  sized.forEach((row, levelIndex) => {
    let x = PAD + (contentW - rowWidths[levelIndex]) / 2
    const y = PAD + levelIndex * (NODE_H + GAP_V)
    row.forEach(n => {
      placed.set(n.id, { ...n, x, y, cx: x + n.w / 2, level: levelIndex })
      x += n.w + GAP_X
    })
  })

  return { placed, width, height }
}

/* Orthogonal routing: down out of the source, across at the midpoint between
   the two levels, then down into the target. Right angles only. */
export function edgePath(source, target) {
  const sy = source.y + source.h
  const ty = target.y
  if (Math.abs(source.cx - target.cx) < 1) return `M ${source.cx} ${sy} L ${source.cx} ${ty}`
  const midY = sy + (ty - sy) / 2
  return `M ${source.cx} ${sy} L ${source.cx} ${midY} L ${target.cx} ${midY} L ${target.cx} ${ty}`
}
