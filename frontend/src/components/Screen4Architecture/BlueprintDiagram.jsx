import styles from './BlueprintDiagram.module.css'
import { PAD, TB_H, TB_W, edgePath, layout } from './diagramLayout'

function NodeShape({ node }) {
  const { x, y, w, h, kind } = node

  if (kind === 'database') {
    const ry = 6
    return (
      <>
        <path
          className={styles.shapeDb}
          d={`M ${x} ${y + ry} A ${w / 2} ${ry} 0 0 1 ${x + w} ${y + ry} L ${x + w} ${y + h - ry} A ${w / 2} ${ry} 0 0 1 ${x} ${y + h - ry} Z`}
        />
        <path
          className={styles.shapeDbCap}
          d={`M ${x} ${y + ry} A ${w / 2} ${ry} 0 0 0 ${x + w} ${y + ry}`}
        />
      </>
    )
  }

  if (kind === 'gateway') {
    const c = 9
    return (
      <path
        className={styles.shapeGateway}
        d={`M ${x + c} ${y} L ${x + w} ${y} L ${x + w} ${y + h - c} L ${x + w - c} ${y + h} L ${x} ${y + h} L ${x} ${y + c} Z`}
      />
    )
  }

  if (kind === 'queue') {
    return (
      <>
        <rect className={styles.shapeQueue} x={x} y={y} width={w} height={h} />
        <line className={styles.shapeQueue} x1={x + w - 13} y1={y} x2={x + w - 13} y2={y + h} />
        <line className={styles.shapeQueue} x1={x + w - 21} y1={y} x2={x + w - 21} y2={y + h} />
      </>
    )
  }

  if (kind === 'client') {
    return (
      <>
        <rect className={styles.shapeClient} x={x} y={y} width={w} height={h} />
        <line className={styles.shapeClient} x1={x + 7} y1={y + h - 7} x2={x + w - 7} y2={y + h - 7} />
      </>
    )
  }

  return <rect className={styles.shapeService} x={x} y={y} width={w} height={h} />
}

export default function BlueprintDiagram({ diagram, title, sheet }) {
  const { nodes, edges, caption } = diagram
  const { placed, width, height } = layout(nodes, edges)

  const outDegree = new Map()
  edges.forEach(e => outDegree.set(e.source, (outDegree.get(e.source) || 0) + 1))

  const tbX = width - PAD - TB_W
  const tbY = height - PAD - TB_H

  return (
    <figure className={styles.frame}>
      <svg
        className={styles.canvas}
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={caption}
        preserveAspectRatio="xMidYMid meet"
      >
        <g>
          {edges.map((e, i) => {
            const source = placed.get(e.source)
            const target = placed.get(e.target)
            if (!source || !target) return null
            const delay = `${source.level * 0.09}s`
            return (
              <g key={i}>
                <path
                  className={styles.edge}
                  d={edgePath(source, target)}
                  pathLength="1"
                  style={{ animationDelay: delay }}
                />
                <path
                  className={styles.arrow}
                  d={`M ${target.cx - 4} ${target.y - 7} L ${target.cx + 4} ${target.y - 7} L ${target.cx} ${target.y} Z`}
                  style={{ animationDelay: `calc(${delay} + 0.55s)` }}
                />
              </g>
            )
          })}
        </g>

        {/* Junction dots mark where one source genuinely fans out to several targets. */}
        <g>
          {Array.from(placed.values())
            .filter(n => (outDegree.get(n.id) || 0) > 1)
            .map(n => (
              <circle
                key={n.id}
                className={styles.junction}
                cx={n.cx}
                cy={n.y + n.h}
                r="2.5"
                style={{ animationDelay: `${n.level * 0.09}s` }}
              />
            ))}
        </g>

        <g>
          {Array.from(placed.values()).map(n => (
            <g
              key={n.id}
              className={styles.node}
              style={{ animationDelay: `${0.3 + n.level * 0.09}s` }}
            >
              <NodeShape node={n} />
              <text
                className={styles.nodeLabel}
                x={n.cx}
                y={n.y + n.h / 2 + (n.lines.length > 1 ? -2 : 4)}
              >
                {n.lines.map((line, i) => (
                  <tspan key={i} x={n.cx} dy={i === 0 ? 0 : 13}>
                    {line}
                  </tspan>
                ))}
              </text>
            </g>
          ))}
        </g>

        {/* Title block — the metadata panel every technical drawing carries. */}
        <g className={styles.titleBlock}>
          <rect className={styles.tbBox} x={tbX} y={tbY} width={TB_W} height={TB_H} />
          <line className={styles.tbRule} x1={tbX} y1={tbY + 28} x2={tbX + TB_W} y2={tbY + 28} />
          <line className={styles.tbRule} x1={tbX} y1={tbY + 56} x2={tbX + TB_W} y2={tbY + 56} />
          <line className={styles.tbRule} x1={tbX + 152} y1={tbY + 56} x2={tbX + 152} y2={tbY + TB_H} />
          <text className={styles.tbTitle} x={tbX + 11} y={tbY + 19}>
            {title}
          </text>
          <text className={styles.tbData} x={tbX + 11} y={tbY + 46}>
            {nodes.length} NODES &nbsp; {edges.length} EDGES
          </text>
          <text className={styles.tbData} x={tbX + 11} y={tbY + 74}>
            SHEET {sheet}
          </text>
          <text className={styles.tbData} x={tbX + 163} y={tbY + 74}>
            ARCH GEN AI
          </text>
        </g>
      </svg>
      <figcaption className={styles.caption}>{caption}</figcaption>
    </figure>
  )
}
